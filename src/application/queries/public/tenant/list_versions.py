from dataclasses import dataclass
from typing import Any
from uuid import UUID

from application.dto import LimitOffsetPaginator, TenantSimpleDTO
from application.errors import AppInvalidDataError
from application.queries.base import BaseUseCase
from domain.tenant import TenantID, TenantState, TenantStatus
from domain.value_objects import Version


@dataclass
class TenantVersionsQuery:
    user_id: UUID
    tenant_id: UUID
    paginator: LimitOffsetPaginator
    statuses: list[str] | None
    states: list[str] | None
    from_version: int | None
    to_version: int | None


class TenantVersionsUseCase(BaseUseCase):
    async def execute(
        self, query: TenantVersionsQuery
    ) -> tuple[list[TenantSimpleDTO], int]:
        action = "получение нескольких версий арендатора"
        async with self._uow as uow:
            initiator_id = TenantID(query.user_id)
            filtering_data = self._cast_data_from_query(query)
            initiator = await uow.tenant_repositories.read.by_id(initiator_id)
            if initiator is None:
                raise AppInvalidDataError(
                    msg="инициатор не существует",
                    action=action,
                    data={"tenant": {"tenant_id": query.user_id}},
                )
            if query.user_id == query.tenant_id:
                initiator.raise_access_read()
            else:
                initiator.raise_staff()
            tenant_versions, count = await uow.tenant_repositories.version.filters(
                **filtering_data
            )
            return [
                TenantSimpleDTO.from_domain(tenant) for tenant in tenant_versions
            ], count

    def _cast_data_from_query(self, query: TenantVersionsQuery) -> dict[str, Any]:
        data = {"paginator": query.paginator, "tenant_id": TenantID(query.tenant_id)}
        if query.statuses is not None:
            data["statuses"] = [TenantStatus(status) for status in query.statuses]
        if query.states is not None:
            data["states"] = [TenantState(state) for state in query.states]
        if query.from_version is not None:
            data["from_version"] = Version(query.from_version)
        if query.to_version is not None:
            data["to_version"] = Version(query.to_version)
        return data
