from dataclasses import dataclass
from typing import Any
from uuid import UUID

from application.dto.paginators import LimitOffsetPaginator
from application.dto.tenant import TenantSimpleDTO
from application.queries.base import BaseUseCase
from domain.tenant import TenantID, TenantState, TenantStatus


@dataclass(slots=True, frozen=True)
class ListTenantLastVersionsQuery:
    initiator_id: UUID
    paginator: LimitOffsetPaginator
    tenant_ids: list[UUID] | None
    statuses: list[str] | None
    states: list[str] | None


class ListTenantLastVersionsUseCase(BaseUseCase):
    async def execute(
        self, query: ListTenantLastVersionsQuery
    ) -> tuple[list[TenantSimpleDTO], int]:
        action = "получение последних версий арендаторов"
        initiator_id = TenantID(query.initiator_id)
        filtering_data = self._filtering_data(query)
        async with self._uow as uow:
            initiator = await self._initiator(uow, initiator_id, action)
            if (
                query.tenant_ids is not None
                and len(query.tenant_ids) == 1
                and query.initiator_id == query.tenant_ids[0]
            ):
                initiator.raise_access_read()
            else:
                initiator.raise_staff()
            tenants, count = await uow.tenant_repositories.read.filters(
                **filtering_data
            )
            return [TenantSimpleDTO.from_domain(tenant) for tenant in tenants], count

    def _filtering_data(self, query: ListTenantLastVersionsQuery) -> dict[str, Any]:
        data: dict[str, Any] = {"paginator": query.paginator}
        if query.tenant_ids is not None:
            data["tenant_ids"] = [TenantID(tenant_id) for tenant_id in query.tenant_ids]
        if query.statuses is not None:
            data["statuses"] = [TenantStatus(status) for status in query.statuses]
        if query.states is not None:
            data["states"] = [TenantState(state) for state in query.states]
        return data
