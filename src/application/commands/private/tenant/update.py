from dataclasses import asdict, dataclass
from uuid import UUID

from application.commands.base import BaseUseCase
from application.dto import TenantSimpleDTO
from application.errors import AppNotFoundError
from domain.errors import EntityIdempotentError
from domain.tenant import TenantID, TenantState
from domain.user import UserID


@dataclass
class TenantUpdateCommand:
    user_id: UUID


class TenantUpdateUseCase(BaseUseCase):
    async def execute(self, command: TenantUpdateCommand) -> TenantSimpleDTO:
        action_name = "обновление арендатора"
        async with self._uow as uow:
            user = await uow.user_repositories.read.by_id(UserID(command.user_id))
            if user is None:
                raise AppNotFoundError(
                    msg=f"пользователь с {command.user_id} не существует",
                    action=action_name,
                    data={"user": asdict(command)},
                )
            tenant = await uow.tenant_repositories.read.by_id(TenantID(command.user_id))
            if tenant is None:
                raise AppNotFoundError(
                    msg=f"арендатор с {command.user_id} не существует",
                    action=action_name,
                    data={"tenant": {"tenant_id": command.user_id}},
                )
            try:
                tenant.new_state(TenantState.from_str(user.state.value))
                await uow.tenant_repositories.read.save(tenant)
                await uow.tenant_repositories.version.save(tenant)
            except EntityIdempotentError:
                pass
            return TenantSimpleDTO.from_domain(tenant)
