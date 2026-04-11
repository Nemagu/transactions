import pytest

from src.domain.errors import ValueObjectInvalidDataError
from src.domain.value_objects import AggregateName, State, Version


def test_version_accepts_positive_number() -> None:
    assert Version(1).version == 1
    assert Version(7).version == 7


def test_version_rejects_zero_and_negative_number() -> None:
    with pytest.raises(ValueObjectInvalidDataError):
        Version(0)

    with pytest.raises(ValueObjectInvalidDataError):
        Version(-1)


def test_aggregate_name_strips_whitespace() -> None:
    value_object = AggregateName(" пользователь ")

    assert value_object.name == "пользователь"


@pytest.mark.parametrize(
    "value",
    ["", " ", "a" * 51],
    ids=["empty", "blank", "too-long"],
)
def test_aggregate_name_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ValueObjectInvalidDataError):
        AggregateName(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [("ACTIVE", State.ACTIVE), ("deleted", State.DELETED)],
    ids=["active", "deleted"],
)
def test_state_from_str_restores_enum(value: str, expected: State) -> None:
    assert State.from_str(value) == expected


def test_state_helper_methods() -> None:
    assert State.ACTIVE.is_active() is True
    assert State.ACTIVE.is_deleted() is False
    assert State.DELETED.is_deleted() is True
    assert State.DELETED.is_active() is False


def test_state_from_str_rejects_unknown_value() -> None:
    with pytest.raises(ValueObjectInvalidDataError):
        State.from_str("archived")
