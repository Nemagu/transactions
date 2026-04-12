from uuid import UUID

from src.domain.user.projection import User
from src.domain.user.value_objects import UserID, UserState
from src.domain.value_objects import Version


class UserFactory:
    @staticmethod
    def new(user_id: UUID, state: str, version: int) -> User:
        return User(
            user_id=UserID(user_id),
            state=UserState.from_str(state),
            version=Version(version),
        )

    @staticmethod
    def restore(user_id: UUID, state: str, version: int) -> User:
        return User(
            user_id=UserID(user_id),
            state=UserState.from_str(state),
            version=Version(version),
        )
