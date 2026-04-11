from uuid import uuid4

import pytest

from src.domain.errors import ValueObjectInvalidDataError
from src.domain.user.factory import UserFactory
from src.domain.user.value_objects import UserState, UserStatus


def test_user_factory_new_creates_default_user() -> None:
    user_id = uuid4()

    user = UserFactory.new(user_id=user_id, first_name=" Ivan ", last_name=" Petrov ")

    assert user.user_id.user_id == user_id
    assert user.first_name.first_name == "Ivan"
    assert user.last_name.last_name == "Petrov"
    assert user.status == UserStatus.USER
    assert user.state == UserState.ACTIVE
    assert user.version.version == 1
    assert user.original_version.version == 1


def test_user_factory_restore_recreates_user_from_primitives() -> None:
    user_id = uuid4()

    user = UserFactory.restore(
        user_id=user_id,
        first_name="Ivan",
        last_name="Petrov",
        status="ADMIN",
        state="FROZEN",
        version=3,
    )

    assert user.user_id.user_id == user_id
    assert user.status == UserStatus.ADMIN
    assert user.state == UserState.FROZEN
    assert user.version.version == 3
    assert user.original_version.version == 3


def test_user_factory_restore_raises_error_for_invalid_status() -> None:
    with pytest.raises(ValueObjectInvalidDataError):
        UserFactory.restore(
            user_id=uuid4(),
            first_name="Ivan",
            last_name="Petrov",
            status="manager",
            state="active",
            version=1,
        )
