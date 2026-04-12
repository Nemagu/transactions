from dataclasses import dataclass
from uuid import UUID

from application.commands.base import BaseUseCase
from application.dto import TenantSimpleDTO
from application.errors import AppNotFoundError
from domain.tenant import TenantID


@dataclass
class TenantAppointmentAdminCommand:
    initiator_id: UUID
    tenant_id: UUID


class TenantAppointmentAdminUseCase(BaseUseCase):
    async def execute(self, command: TenantAppointmentAdminCommand) -> TenantSimpleDTO:
        action_name = "назначение арендатора администратором"
        async with self._uow as uow:
            initiator = await uow.tenant_repositories.read.by_id(
                TenantID(command.initiator_id)
            )
            if initiator is None:
                raise AppNotFoundError(
                    msg=f"инициатор с {command.tenant_id} не существует",
                    action=action_name,
                    data={"tenant": {"tenant_id": command.initiator_id}},
                )
            initiator.raise_staff()
            tenant = await uow.tenant_repositories.read.by_id(
                TenantID(command.tenant_id)
            )
            if tenant is None:
                raise AppNotFoundError(
                    msg=f"арендатор с {command.tenant_id} не существует",
                    action=action_name,
                    data={"tenant": {"tenant_id": command.tenant_id}},
                )
            tenant.appoint_admin()
            await uow.tenant_repositories.read.save(tenant)
            await uow.tenant_repositories.version.save(tenant)
            return TenantSimpleDTO.from_domain(tenant)
