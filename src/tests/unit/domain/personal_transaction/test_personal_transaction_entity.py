from datetime import datetime
from decimal import Decimal

import pytest

from domain.personal_transaction.errors import PersonalTransactionIdempotentError
from domain.personal_transaction.value_objects import (
    Currency,
    MoneyAmount,
    PersonalTransactionDescription,
    PersonalTransactionName,
    PersonalTransactionState,
    PersonalTransactionTime,
    PersonalTransactionType,
)
from domain.transaction_category.value_objects import TransactionCategoryID


def test_personal_transaction_exposes_created_state(personal_transaction_factory) -> None:
    transaction = personal_transaction_factory()

    assert transaction.name == PersonalTransactionName("Coffee")
    assert transaction.description == PersonalTransactionDescription("Morning coffee")
    assert transaction.transaction_type == PersonalTransactionType.EXPENSE
    assert transaction.money_amount == MoneyAmount(Decimal("100"), Currency.RUBLE)
    assert transaction.transaction_time == PersonalTransactionTime(datetime(2026, 4, 5, 12, 0, 0))
    assert transaction.state == PersonalTransactionState.ACTIVE
    assert transaction.version.version == 1
    assert transaction.original_version.version == 1


@pytest.mark.parametrize(
    ("method_name", "value", "expected_attr"),
    [
        ("new_name", PersonalTransactionName("Taxi"), "name"),
        (
            "new_description",
            PersonalTransactionDescription("Ride to office"),
            "description",
        ),
        ("new_transaction_type", PersonalTransactionType.INCOME, "transaction_type"),
        (
            "new_money_amount",
            MoneyAmount(amount=Decimal("250"), currency=Currency.DOLLAR),
            "money_amount",
        ),
        (
            "new_transaction_time",
            PersonalTransactionTime(datetime(2026, 4, 6, 15, 30, 0)),
            "transaction_time",
        ),
    ],
    ids=["change-name", "change-description", "change-type", "change-amount", "change-time"],
)
def test_personal_transaction_updates_fields_once_per_cycle(
    personal_transaction_factory,
    method_name: str,
    value,
    expected_attr: str,
) -> None:
    transaction = personal_transaction_factory()

    getattr(transaction, method_name)(value)
    transaction.delete()

    assert getattr(transaction, expected_attr) == value
    assert transaction.version.version == 2
    assert transaction.original_version.version == 1


def test_personal_transaction_updates_category_ids_once_per_cycle(
    personal_transaction_factory,
    user_id_factory,
) -> None:
    transaction = personal_transaction_factory()
    category_ids = {
        TransactionCategoryID(user_id_factory().user_id),
        TransactionCategoryID(user_id_factory().user_id),
    }

    transaction.new_category_ids(category_ids)
    transaction.delete()

    assert transaction.category_ids == category_ids
    assert transaction.version.version == 2
    assert transaction.original_version.version == 1


@pytest.mark.parametrize(
    ("method_name", "value"),
    [
        ("new_name", PersonalTransactionName("Coffee")),
        ("new_description", PersonalTransactionDescription("Morning coffee")),
        ("new_transaction_type", PersonalTransactionType.EXPENSE),
        (
            "new_money_amount",
            MoneyAmount(amount=Decimal("100"), currency=Currency.RUBLE),
        ),
        (
            "new_transaction_time",
            PersonalTransactionTime(datetime(2026, 4, 5, 12, 0, 0)),
        ),
    ],
    ids=["same-name", "same-description", "same-type", "same-amount", "same-time"],
)
def test_personal_transaction_rejects_idempotent_field_changes(
    personal_transaction_factory,
    method_name: str,
    value,
) -> None:
    transaction = personal_transaction_factory()

    with pytest.raises(PersonalTransactionIdempotentError):
        getattr(transaction, method_name)(value)


def test_personal_transaction_rejects_idempotent_category_ids_change(
    personal_transaction_factory,
) -> None:
    transaction = personal_transaction_factory()

    with pytest.raises(PersonalTransactionIdempotentError):
        transaction.new_category_ids(transaction.category_ids)


@pytest.mark.parametrize(
    ("method_name", "initial_state", "expected_state"),
    [
        ("activate", PersonalTransactionState.DELETED, PersonalTransactionState.ACTIVE),
        ("delete", PersonalTransactionState.ACTIVE, PersonalTransactionState.DELETED),
    ],
    ids=["activate-transaction", "delete-transaction"],
)
def test_personal_transaction_changes_state(
    personal_transaction_factory,
    method_name: str,
    initial_state: PersonalTransactionState,
    expected_state: PersonalTransactionState,
) -> None:
    transaction = personal_transaction_factory(state=initial_state)

    getattr(transaction, method_name)()
    transaction.new_name(PersonalTransactionName("Taxi"))

    assert transaction.state == expected_state
    assert transaction.version.version == 2
    assert transaction.original_version.version == 1


@pytest.mark.parametrize(
    ("method_name", "state"),
    [
        ("activate", PersonalTransactionState.ACTIVE),
        ("delete", PersonalTransactionState.DELETED),
    ],
    ids=["activate-active", "delete-deleted"],
)
def test_personal_transaction_rejects_idempotent_state_changes(
    personal_transaction_factory,
    method_name: str,
    state: PersonalTransactionState,
) -> None:
    transaction = personal_transaction_factory(state=state)

    with pytest.raises(PersonalTransactionIdempotentError):
        getattr(transaction, method_name)()


def test_personal_transaction_starts_new_version_cycle_after_persist(
    personal_transaction_factory,
) -> None:
    transaction = personal_transaction_factory()

    transaction.new_name(PersonalTransactionName("Taxi"))
    transaction.mark_persisted()
    transaction.new_description(PersonalTransactionDescription("Ride to office"))

    assert transaction.version.version == 3
    assert transaction.original_version.version == 2
