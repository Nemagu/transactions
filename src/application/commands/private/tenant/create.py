from dataclasses import asdict, dataclass
from uuid import UUID

from application.commands.base import BaseUseCase
from application.dto import TenantSimpleDTO
from application.errors import AppNotFoundError
from domain.tenant import TenantCreationService
from domain.user import UserID


@dataclass
class TenantCreationCommand:
    user_id: UUID
    state: str


class TenantCreationUseCase(BaseUseCase):
    async def execute(self, command: TenantCreationCommand) -> TenantSimpleDTO:
        async with self._uow as uow:
            user = await uow.user_repositories.read.by_id(UserID(command.user_id))
            if user is None:
                raise AppNotFoundError(
                    msg=f"пользователь с {command.user_id} не существует",
                    action="создание арендатора",
                    data={"user": asdict(command)},
                )
            service = TenantCreationService(uow.tenant_repositories.read)
            tenant = await service.create(user)
            await uow.tenant_repositories.read.save(tenant)
            await uow.tenant_repositories.version.save(tenant)
            await uow.subscription_repositories.common.subscribe(tenant, user)
            return TenantSimpleDTO.from_domain(tenant)
