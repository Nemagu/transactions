from dataclasses import dataclass
from uuid import UUID

from application.commands.base import BaseUseCase
from application.dto.tenant import TenantSimpleDTO
from application.errors import AppNotFoundError
from application.ports.repositories import TenantEvent
from domain.tenant import TenantID


@dataclass(slots=True, frozen=True)
class DemoteTenantAdminCommand:
    initiator_id: UUID
    tenant_id: UUID


class DemoteTenantAdminUseCase(BaseUseCase):
    async def execute(self, command: DemoteTenantAdminCommand) -> TenantSimpleDTO:
        action_name = "удаление арендатора из администраторов"
        initiator_id = TenantID(command.initiator_id)
        async with self._uow as uow:
            initiator = await self._initiator(uow, initiator_id, action_name)
            initiator.raise_staff()
            tenant = await uow.tenant_repositories.read.by_id(
                TenantID(command.tenant_id)
            )
            if tenant is None:
                raise AppNotFoundError(
                    msg="арендатор не существует",
                    action=action_name,
                    data={"tenant": {"tenant_id": command.tenant_id}},
                )
            tenant.appoint_tenant()
            await uow.tenant_repositories.read.save(tenant)
            await uow.tenant_repositories.version.save(
                tenant, TenantEvent.UPDATED, initiator.tenant_id
            )
            return TenantSimpleDTO.from_domain(tenant)
