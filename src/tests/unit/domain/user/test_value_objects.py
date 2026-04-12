from uuid import uuid4

import pytest

from domain.errors import DomainError, ValueObjectInvalidDataError
from domain.user.value_objects import UserID, UserState


def test_user_id_keeps_uuid_value() -> None:
    value = uuid4()

    user_id = UserID(value)

    assert user_id.user_id == value


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("ACTIVE", UserState.ACTIVE),
        ("frozen", UserState.FROZEN),
        ("deleted", UserState.DELETED),
    ],
    ids=["active", "frozen", "deleted"],
)
def test_user_state_restores_from_string(value: str, expected: UserState) -> None:
    assert UserState.from_str(value) == expected


@pytest.mark.parametrize(
    ("enum_value", "method_name"),
    [
        (UserState.ACTIVE, "is_active"),
        (UserState.FROZEN, "is_frozen"),
        (UserState.DELETED, "is_deleted"),
    ],
    ids=["is-active", "is-frozen", "is-deleted"],
)
def test_user_state_helper_methods(enum_value, method_name: str) -> None:
    assert getattr(enum_value, method_name)() is True


def test_user_state_raises_for_unknown_string() -> None:
    with pytest.raises(ValueObjectInvalidDataError) as exc_info:
        UserState.from_str("archived")

    assert isinstance(exc_info.value, DomainError)
