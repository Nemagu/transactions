from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from src.domain.errors import DomainError, ValueObjectInvalidDataError
from src.domain.personal_transaction.value_objects import (
    Currency,
    MoneyAmount,
    PersonalTransactionDescription,
    PersonalTransactionID,
    PersonalTransactionName,
    PersonalTransactionTime,
    PersonalTransactionType,
)


def test_personal_transaction_id_keeps_uuid_value() -> None:
    value = uuid4()

    transaction_id = PersonalTransactionID(value)

    assert transaction_id.transaction_id == value


def test_personal_transaction_description_keeps_value() -> None:
    description = PersonalTransactionDescription("Lunch with team")

    assert description.description == "Lunch with team"


def test_personal_transaction_time_keeps_datetime_value() -> None:
    transaction_time = datetime(2026, 4, 5, 12, 30, 45)

    value_object = PersonalTransactionTime(transaction_time)

    assert value_object.transaction_time == transaction_time


def test_personal_transaction_name_strips_whitespace() -> None:
    transaction_name = PersonalTransactionName(" Coffee ")

    assert transaction_name.name == "Coffee"


def test_personal_transaction_name_rejects_too_long_value() -> None:
    with pytest.raises(ValueObjectInvalidDataError):
        PersonalTransactionName("a" * 101)


@pytest.mark.parametrize(
    ("enum_cls", "value", "expected"),
    [
        (PersonalTransactionType, "EXPENSE", PersonalTransactionType.EXPENSE),
        (PersonalTransactionType, "income", PersonalTransactionType.INCOME),
        (Currency, "RUBLE", Currency.RUBLE),
        (Currency, "dollar", Currency.DOLLAR),
        (Currency, "euro", Currency.EURO),
        (Currency, "yuan", Currency.YUAN),
    ],
    ids=[
        "type-expense",
        "type-income",
        "currency-ruble",
        "currency-dollar",
        "currency-euro",
        "currency-yuan",
    ],
)
def test_enums_restore_from_string(enum_cls, value: str, expected) -> None:
    assert enum_cls.from_str(value) == expected


@pytest.mark.parametrize(
    ("enum_value", "method_name"),
    [
        (PersonalTransactionType.EXPENSE, "is_expense"),
        (PersonalTransactionType.INCOME, "is_income"),
    ],
    ids=["is-expense", "is-income"],
)
def test_enum_helper_methods(enum_value, method_name: str) -> None:
    assert getattr(enum_value, method_name)() is True


@pytest.mark.parametrize(
    ("enum_cls", "value"),
    [
        (PersonalTransactionType, "transfer"),
        (Currency, "tenge"),
    ],
    ids=["unknown-type", "unknown-currency"],
)
def test_enums_raise_for_unknown_string(enum_cls, value: str) -> None:
    with pytest.raises(ValueObjectInvalidDataError) as exc_info:
        enum_cls.from_str(value)

    assert isinstance(exc_info.value, DomainError)


def test_money_amount_accepts_zero_and_positive_amount() -> None:
    assert MoneyAmount(amount=Decimal("0"), currency=Currency.RUBLE).amount == Decimal("0")
    assert (
        MoneyAmount(amount=Decimal("125.50"), currency=Currency.DOLLAR).amount
        == Decimal("125.50")
    )


def test_money_amount_rejects_negative_amount() -> None:
    with pytest.raises(ValueObjectInvalidDataError):
        MoneyAmount(amount=Decimal("-1"), currency=Currency.RUBLE)
