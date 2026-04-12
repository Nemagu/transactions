from src.domain.errors import EntityAlreadyExistsError
from src.domain.user.repository import UserReadRepository
from src.domain.user.value_objects import UserID


class UserUniquenessService:
    def __init__(self, read_repository: UserReadRepository) -> None:
        self._read_repo = read_repository

    async def validate_user_id(self, user_id: UserID) -> None:
        existing_user = await self._read_repo.by_id(user_id)
        if existing_user:
            raise EntityAlreadyExistsError(
                msg=f'пользователь с id "{existing_user.user_id.user_id}" уже существует',
                struct_name=existing_user.projection_name.name,
                data={"user": {"user_id": str(existing_user.user_id.user_id)}},
            )
