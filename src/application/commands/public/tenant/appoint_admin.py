from dataclasses import asdict, dataclass
from uuid import UUID

from application.commands.base import BaseUseCase
from application.dto import TenantSimpleDTO
from application.errors import AppNotFoundError
from domain.tenant import TenantID


@dataclass
class TenantAppointingAdminCommand:
    initiator_id: UUID
    tenant_id: UUID


class TenantAppointingAdminUseCase(BaseUseCase):
    async def execute(self, command: TenantAppointingAdminCommand) -> TenantSimpleDTO:
        action_name = "назначение арендатора администратором"
        async with self._uow as uow:
            initiator = await uow.tenant_repositories.read.by_id(
                TenantID(command.initiator_id)
            )
            if initiator is None:
                raise AppNotFoundError(
                    msg=f"инициатор с {command.tenant_id} не существует",
                    action=action_name,
                    data={"tenant": asdict(command)},
                )
            initiator.raise_staff()
            tenant = await uow.tenant_repositories.read.by_id(
                TenantID(command.tenant_id)
            )
            if tenant is None:
                raise AppNotFoundError(
                    msg=f"арендатор с {command.tenant_id} не существует",
                    action=action_name,
                    data={"tenant": asdict(command)},
                )
            tenant.appoint_admin()
            await uow.tenant_repositories.read.save(tenant)
            await uow.tenant_repositories.version.save(tenant)
            return TenantSimpleDTO.from_domain(tenant)
