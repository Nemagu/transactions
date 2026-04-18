from uuid import uuid7

import pytest

from domain.errors import ValueObjectInvalidDataError
from domain.user.factory import UserFactory
from domain.user.value_objects import UserState


def test_user_factory_new_creates_projection() -> None:
    user_id = uuid7()

    user = UserFactory.new(user_id=user_id, state="active", version=1)

    assert user.user_id.user_id == user_id
    assert user.state == UserState.ACTIVE
    assert user.version.version == 1


def test_user_factory_restore_recreates_projection() -> None:
    user_id = uuid7()

    user = UserFactory.restore(user_id=user_id, state="FROZEN", version=3)

    assert user.user_id.user_id == user_id
    assert user.state == UserState.FROZEN
    assert user.version.version == 3


def test_user_factory_restore_rejects_invalid_state() -> None:
    with pytest.raises(ValueObjectInvalidDataError):
        UserFactory.restore(user_id=uuid7(), state="archived", version=1)
