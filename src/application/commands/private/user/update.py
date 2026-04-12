from dataclasses import asdict, dataclass
from uuid import UUID

from application.commands.base import BaseUseCase
from application.dto import UserSimpleDTO
from application.errors import AppNotFoundError
from domain.errors import EntityIdempotentError, EntityVersionLessThenCurrentError
from domain.user import UserID, UserState
from domain.value_objects import Version


@dataclass
class UserUpdatingCommand:
    user_id: UUID
    state: str
    version: int


class UserUpdatingUseCase(BaseUseCase):
    async def execute(self, command: UserUpdatingCommand) -> UserSimpleDTO:
        async with self._uow as uow:
            user = await uow.user_repositories.read.by_id(UserID(command.user_id))
            if user is None:
                raise AppNotFoundError(
                    msg=f"пользователь с {command.user_id} не существует",
                    action="обновление пользователя",
                    data={"user": asdict(command)},
                )
            state = UserState.from_str(command.state)
            version = Version(command.version)
            try:
                user.new_state(state)
                user.new_version(version)
                await uow.user_repositories.read.save(user)
            except EntityIdempotentError, EntityVersionLessThenCurrentError:
                pass
            return UserSimpleDTO.from_domain(user)
