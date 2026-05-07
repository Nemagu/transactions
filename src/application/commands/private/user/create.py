from dataclasses import dataclass
from uuid import UUID

from application.commands.base import BaseUseCase
from application.dto.user import UserSimpleDTO
from domain.user import UserFactory, UserID, UserUniquenessService


@dataclass(slots=True, frozen=True)
class CreateUserCommand:
    user_id: UUID
    state: str
    version: int


class CreateUserUseCase(BaseUseCase):
    async def execute(self, command: CreateUserCommand) -> UserSimpleDTO:
        async with self._uow as uow:
            service = UserUniquenessService(uow.user_repositories.read)
            await service.validate_user_id(UserID(command.user_id))
            user = UserFactory.new(command.user_id, command.state, command.version)
            await uow.user_repositories.read.save(user)
            return UserSimpleDTO.from_domain(user)
