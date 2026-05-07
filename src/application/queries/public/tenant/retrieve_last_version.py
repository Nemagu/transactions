from dataclasses import dataclass
from uuid import UUID

from application.dto.tenant import TenantSimpleDTO
from application.errors import AppNotFoundError
from application.queries.base import BaseUseCase
from domain.tenant import TenantID


@dataclass(slots=True, frozen=True)
class GetTenantLastVersionQuery:
    initiator_id: UUID
    tenant_id: UUID


class GetTenantLastVersionUseCase(BaseUseCase):
    async def execute(self, query: GetTenantLastVersionQuery) -> TenantSimpleDTO:
        action = "получение последней версии арендатора"
        initiator_id = TenantID(query.initiator_id)
        tenant_id = TenantID(query.tenant_id)
        async with self._uow as uow:
            initiator = await self._initiator(uow, initiator_id, action)
            if query.initiator_id == query.tenant_id:
                initiator.raise_access_read()
                return TenantSimpleDTO.from_domain(initiator)
            initiator.raise_staff()
            tenant = await uow.tenant_repositories.read.by_id(tenant_id)
            if tenant is None:
                raise AppNotFoundError(
                    msg="арендатор не существует",
                    action=action,
                    data={"tenant": {"tenant_id": query.tenant_id}},
                )
            return TenantSimpleDTO.from_domain(tenant)
