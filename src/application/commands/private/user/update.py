from dataclasses import dataclass
from uuid import UUID

from application.commands.base import BaseUseCase
from application.dto.user import UserSimpleDTO
from application.errors import AppNotFoundError
from domain.errors import EntityIdempotentError, EntityVersionLessThenCurrentError
from domain.user import UserID, UserState
from domain.value_objects import Version


@dataclass(slots=True, frozen=True)
class UpdateUserCommand:
    user_id: UUID
    state: str
    version: int


class UpdateUserUseCase(BaseUseCase):
    async def execute(self, command: UpdateUserCommand) -> UserSimpleDTO:
        async with self._uow as uow:
            user = await uow.user_repositories.read.by_id(UserID(command.user_id))
            if user is None:
                raise AppNotFoundError(
                    msg="пользователь не существует",
                    action="обновление пользователя",
                    data={"user": {"user_id": command.user_id}},
                )
            state = UserState.from_str(command.state)
            version = Version(command.version)
            try:
                user.new_state(state)
                user.new_version(version)
                await uow.user_repositories.read.save(user)
            except (EntityIdempotentError, EntityVersionLessThenCurrentError):
                pass
            return UserSimpleDTO.from_domain(user)
