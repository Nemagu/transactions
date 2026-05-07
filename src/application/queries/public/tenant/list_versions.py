from dataclasses import dataclass
from typing import Any
from uuid import UUID

from application.dto.paginators import LimitOffsetPaginator
from application.dto.tenant import TenantVersionSimpleDTO
from application.queries.base import BaseUseCase
from domain.tenant import TenantID, TenantState, TenantStatus
from domain.value_objects import Version


@dataclass(slots=True, frozen=True)
class ListTenantVersionsQuery:
    initiator_id: UUID
    tenant_id: UUID
    paginator: LimitOffsetPaginator
    statuses: list[str] | None
    states: list[str] | None
    from_version: int | None
    to_version: int | None


class ListTenantVersionsUseCase(BaseUseCase):
    async def execute(
        self, query: ListTenantVersionsQuery
    ) -> tuple[list[TenantVersionSimpleDTO], int]:
        action = "получение нескольких версий арендатора"
        initiator_id = TenantID(query.initiator_id)
        filtering_data = self._filtering_data(query)
        async with self._uow as uow:
            initiator = await self._initiator(uow, initiator_id, action)
            if query.initiator_id == query.tenant_id:
                initiator.raise_access_read()
            else:
                initiator.raise_staff()
            tenant_versions, count = await uow.tenant_repositories.version.filters(
                **filtering_data
            )
            return [
                TenantVersionSimpleDTO.from_dto(version) for version in tenant_versions
            ], count

    def _filtering_data(self, query: ListTenantVersionsQuery) -> dict[str, Any]:
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
