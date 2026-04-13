from dataclasses import dataclass
from typing import Any
from uuid import UUID

from application.dto import LimitOffsetPaginator, TenantSimpleDTO
from application.errors import AppInvalidDataError
from application.queries.base import BaseUseCase
from domain.tenant import TenantID, TenantState, TenantStatus


@dataclass
class TenantLastVersionsQuery:
    user_id: UUID
    paginator: LimitOffsetPaginator
    tenant_ids: list[UUID] | None
    statuses: list[str] | None
    states: list[str] | None


class TenantLastVersionsUseCase(BaseUseCase):
    async def execute(
        self, query: TenantLastVersionsQuery
    ) -> tuple[list[TenantSimpleDTO], int]:
        action = "получение последних версий арендаторов"
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
            if (
                query.tenant_ids is not None
                and len(query.tenant_ids) == 1
                and query.user_id == query.tenant_ids[0]
            ):
                initiator.raise_access_read()
            else:
                initiator.raise_staff()
            tenants, count = await uow.tenant_repositories.read.filters(
                **filtering_data
            )
            return [TenantSimpleDTO.from_domain(tenant) for tenant in tenants], count

    def _cast_data_from_query(self, query: TenantLastVersionsQuery) -> dict[str, Any]:
        data: dict[str, Any] = {"paginator": query.paginator}
        if query.tenant_ids is not None:
            data["tenant_ids"] = [TenantID(tenant_id) for tenant_id in query.tenant_ids]
        if query.statuses is not None:
            data["statuses"] = [TenantStatus(status) for status in query.statuses]
        if query.states is not None:
            data["states"] = [TenantState(state) for state in query.states]
        return data
