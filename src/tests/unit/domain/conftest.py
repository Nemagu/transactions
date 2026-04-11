from collections.abc import Callable
from uuid import UUID, uuid4

import pytest

from src.domain.user.entity import User
from src.domain.user.value_objects import (
    FirstName,
    LastName,
    UserID,
    UserState,
    UserStatus,
)
from src.domain.value_objects import Version


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
