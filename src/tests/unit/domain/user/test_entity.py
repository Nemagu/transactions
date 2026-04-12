import pytest

from domain.errors import EntityIdempotentError
from domain.user.value_objects import UserState
from domain.value_objects import Version


def test_user_projection_exposes_created_state(user_factory) -> None:
    user = user_factory()

    assert user.state == UserState.ACTIVE
    assert user.version.version == 1


def test_user_projection_changes_state_without_version_update(user_factory) -> None:
    user = user_factory(state=UserState.ACTIVE, version=2)

    user.new_state(UserState.FROZEN)

    assert user.state == UserState.FROZEN
    assert user.version == Version(2)


def test_user_projection_rejects_idempotent_state_change(user_factory) -> None:
    user = user_factory(state=UserState.ACTIVE)

    with pytest.raises(EntityIdempotentError):
        user.new_state(UserState.ACTIVE)
