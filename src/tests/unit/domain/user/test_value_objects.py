from uuid import uuid4

import pytest

from src.domain.errors import DomainError, ValueObjectInvalidDataError
from src.domain.user.value_objects import (
    FirstName,
    LastName,
    UserID,
    UserState,
    UserStatus,
)


def test_user_id_keeps_uuid_value() -> None:
    value = uuid4()

    user_id = UserID(value)

    assert user_id.user_id == value


@pytest.mark.parametrize(
    ("cls", "field_name"),
    [(FirstName, "first_name"), (LastName, "last_name")],
    ids=["first-name", "last-name"],
)
def test_name_value_objects_strip_whitespace(cls, field_name: str) -> None:
    value_object = cls(" Ivan ")

    assert getattr(value_object, field_name) == "Ivan"


@pytest.mark.parametrize(
    ("cls", "field_name"),
    [
        (FirstName, "first_name"),
        (LastName, "last_name"),
    ],
    ids=["too-long-first-name", "too-long-last-name"],
)
def test_name_value_objects_reject_too_long_value(
    cls,
    field_name: str,
) -> None:
    long_value = "a" * 51

    with pytest.raises(ValueObjectInvalidDataError):
        cls(long_value)


@pytest.mark.parametrize(
    ("enum_cls", "value", "expected"),
    [
        (UserStatus, "ADMIN", UserStatus.ADMIN),
        (UserStatus, "user", UserStatus.USER),
        (UserState, "ACTIVE", UserState.ACTIVE),
        (UserState, "frozen", UserState.FROZEN),
        (UserState, "deleted", UserState.DELETED),
    ],
    ids=["status-admin", "status-user", "state-active", "state-frozen", "state-deleted"],
)
def test_enums_restore_from_string(enum_cls, value: str, expected) -> None:
    assert enum_cls.from_str(value) == expected


@pytest.mark.parametrize(
    ("enum_value", "method_name"),
    [
        (UserStatus.ADMIN, "is_admin"),
        (UserStatus.USER, "is_user"),
        (UserState.ACTIVE, "is_active"),
        (UserState.FROZEN, "is_frozen"),
        (UserState.DELETED, "is_deleted"),
    ],
    ids=["is-admin", "is-user", "is-active", "is-frozen", "is-deleted"],
)
def test_enum_helper_methods(enum_value, method_name: str) -> None:
    assert getattr(enum_value, method_name)() is True


@pytest.mark.parametrize(
    ("enum_cls", "value"),
    [
        (UserStatus, "manager"),
        (UserState, "archived"),
    ],
    ids=["unknown-status", "unknown-state"],
)
def test_enums_raise_for_unknown_string(enum_cls, value: str) -> None:
    with pytest.raises(ValueObjectInvalidDataError) as exc_info:
        enum_cls.from_str(value)

    assert isinstance(exc_info.value, DomainError)
