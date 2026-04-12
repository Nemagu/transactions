import pytest

from src.domain.errors import ValueObjectInvalidDataError
from src.domain.value_objects import AggregateName, ProjectionName, State, Version


def test_version_accepts_positive_number() -> None:
    assert Version(1).version == 1
    assert Version(7).version == 7


@pytest.mark.parametrize(
    "value",
    [0, -1],
    ids=["zero", "negative"],
)
def test_version_rejects_invalid_number(value: int) -> None:
    with pytest.raises(ValueObjectInvalidDataError):
        Version(value)


@pytest.mark.parametrize(
    ("cls", "value"),
    [
        (AggregateName, " агрегат "),
        (ProjectionName, " проекция "),
    ],
    ids=["aggregate-name", "projection-name"],
)
def test_name_value_objects_strip_whitespace(cls, value: str) -> None:
    assert cls(value).name == value.strip()


@pytest.mark.parametrize(
    ("cls", "value"),
    [
        (AggregateName, ""),
        (AggregateName, " "),
        (AggregateName, "a" * 51),
        (ProjectionName, ""),
        (ProjectionName, " "),
        (ProjectionName, "a" * 51),
    ],
    ids=[
        "aggregate-empty",
        "aggregate-blank",
        "aggregate-too-long",
        "projection-empty",
        "projection-blank",
        "projection-too-long",
    ],
)
def test_name_value_objects_reject_invalid_values(cls, value: str) -> None:
    with pytest.raises(ValueObjectInvalidDataError):
        cls(value)


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
