import pytest

from domain.transaction_category.errors import TransactionCategoryIdempotentError
from domain.transaction_category.value_objects import (
    TransactionCategoryDescription,
    TransactionCategoryName,
    TransactionCategoryState,
)


def test_transaction_category_exposes_created_state(transaction_category_factory) -> None:
    category = transaction_category_factory()

    assert category.name == TransactionCategoryName("Food")
    assert category.description == TransactionCategoryDescription("Daily expenses")
    assert category.state == TransactionCategoryState.ACTIVE
    assert category.version.version == 1
    assert category.original_version.version == 1


@pytest.mark.parametrize(
    ("method_name", "value", "expected_attr"),
    [
        ("new_name", TransactionCategoryName("Transport"), "name"),
        (
            "new_description",
            TransactionCategoryDescription("Taxi and bus rides"),
            "description",
        ),
    ],
    ids=["change-name", "change-description"],
)
def test_transaction_category_updates_fields_once_per_cycle(
    transaction_category_factory,
    method_name: str,
    value: TransactionCategoryName | TransactionCategoryDescription,
    expected_attr: str,
) -> None:
    category = transaction_category_factory()

    getattr(category, method_name)(value)
    if method_name == "new_name":
        category.new_description(TransactionCategoryDescription("Taxi and bus rides"))
    else:
        category.new_name(TransactionCategoryName("Transport"))

    assert getattr(category, expected_attr) == value
    assert category.version.version == 2
    assert category.original_version.version == 1


@pytest.mark.parametrize(
    ("method_name", "value"),
    [
        ("new_name", TransactionCategoryName("Food")),
        ("new_description", TransactionCategoryDescription("Daily expenses")),
    ],
    ids=["same-name", "same-description"],
)
def test_transaction_category_rejects_idempotent_field_changes(
    transaction_category_factory,
    method_name: str,
    value: TransactionCategoryName | TransactionCategoryDescription,
) -> None:
    category = transaction_category_factory()

    with pytest.raises(TransactionCategoryIdempotentError):
        getattr(category, method_name)(value)


@pytest.mark.parametrize(
    ("method_name", "initial_state", "expected_state"),
    [
        ("activate", TransactionCategoryState.DELETED, TransactionCategoryState.ACTIVE),
        ("delete", TransactionCategoryState.ACTIVE, TransactionCategoryState.DELETED),
    ],
    ids=["activate-category", "delete-category"],
)
def test_transaction_category_changes_state(
    transaction_category_factory,
    method_name: str,
    initial_state: TransactionCategoryState,
    expected_state: TransactionCategoryState,
) -> None:
    category = transaction_category_factory(state=initial_state)

    getattr(category, method_name)()
    category.new_name(TransactionCategoryName("Transport"))

    assert category.state == expected_state
    assert category.version.version == 2
    assert category.original_version.version == 1


@pytest.mark.parametrize(
    ("method_name", "state"),
    [
        ("activate", TransactionCategoryState.ACTIVE),
        ("delete", TransactionCategoryState.DELETED),
    ],
    ids=["activate-active", "delete-deleted"],
)
def test_transaction_category_rejects_idempotent_state_changes(
    transaction_category_factory,
    method_name: str,
    state: TransactionCategoryState,
) -> None:
    category = transaction_category_factory(state=state)

    with pytest.raises(TransactionCategoryIdempotentError):
        getattr(category, method_name)()
