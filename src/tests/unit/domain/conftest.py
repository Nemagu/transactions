from collections.abc import Callable
from uuid import UUID, uuid4

import pytest

from domain.user.entity import User
from domain.user.repository import UserRepository
from domain.user.value_objects import FirstName, LastName, UserID, UserState, UserStatus
from domain.value_objects import Version


class InMemoryUserRepository(UserRepository):
    def __init__(self, users: dict[UserID, User] | None = None) -> None:
        self._users = users or {}
        self.saved_users: list[User] = []

    def next_id(self) -> UserID:
        return UserID(uuid4())

    async def by_id(self, user_id: UserID) -> User | None:
        return self._users.get(user_id)

    async def save(self, user: User) -> None:
        self.saved_users.append(user)
        user.mark_persisted()
        self._users[user.user_id] = user


@pytest.fixture
def user_id_factory() -> Callable[[UUID | None], UserID]:
    def factory(value: UUID | None = None) -> UserID:
        return UserID(value or uuid4())

    return factory


@pytest.fixture
def user_factory(
    user_id_factory: Callable[[UUID | None], UserID],
) -> Callable[..., User]:
    def factory(
        *,
        user_id: UserID | None = None,
        first_name: str = "Ivan",
        last_name: str = "Petrov",
        status: UserStatus = UserStatus.USER,
        state: UserState = UserState.ACTIVE,
        version: int = 1,
    ) -> User:
        return User(
            user_id=user_id or user_id_factory(),
            first_name=FirstName(first_name),
            last_name=LastName(last_name),
            status=status,
            state=state,
            version=Version(version),
        )

    return factory


@pytest.fixture
def user_repository_factory() -> Callable[
    [dict[UserID, User] | None], InMemoryUserRepository
]:
    def factory(users: dict[UserID, User] | None = None) -> InMemoryUserRepository:
        return InMemoryUserRepository(users=users)

    return factory
