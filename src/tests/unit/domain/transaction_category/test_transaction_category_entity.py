import pytest

from src.domain.errors import EntityIdempotentError, EntityInvalidDataError
from src.domain.transaction_category.value_objects import (
    TransactionCategoryDescription,
    TransactionCategoryName,
)
from src.domain.value_objects import State


def test_transaction_category_exposes_created_state(transaction_category_factory) -> None:
    category = transaction_category_factory()

    assert category.name == TransactionCategoryName("Food")
    assert category.description == TransactionCategoryDescription("Daily expenses")
    assert category.state == State.ACTIVE
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

    with pytest.raises(EntityIdempotentError):
        getattr(category, method_name)(value)


@pytest.mark.parametrize(
    ("method_name", "initial_state", "expected_state"),
    [
        ("activate", State.DELETED, State.ACTIVE),
        ("delete", State.ACTIVE, State.DELETED),
    ],
    ids=["activate-category", "delete-category"],
)
def test_transaction_category_changes_state(
    transaction_category_factory,
    method_name: str,
    initial_state: State,
    expected_state: State,
) -> None:
    category = transaction_category_factory(state=initial_state)

    getattr(category, method_name)()

    assert category.state == expected_state
    assert category.version.version == 2
    assert category.original_version.version == 1


@pytest.mark.parametrize(
    ("method_name", "state"),
    [
        ("activate", State.ACTIVE),
        ("delete", State.DELETED),
    ],
    ids=["activate-active", "delete-deleted"],
)
def test_transaction_category_rejects_idempotent_state_changes(
    transaction_category_factory,
    method_name: str,
    state: State,
) -> None:
    category = transaction_category_factory(state=state)

    with pytest.raises(EntityIdempotentError):
        getattr(category, method_name)()


@pytest.mark.parametrize(
    "method_name",
    ["new_name", "new_description"],
    ids=["change-name", "change-description"],
)
def test_transaction_category_rejects_changes_when_deleted(
    transaction_category_factory,
    method_name: str,
) -> None:
    category = transaction_category_factory(state=State.DELETED)
    value = (
        TransactionCategoryName("Transport")
        if method_name == "new_name"
        else TransactionCategoryDescription("Taxi and bus rides")
    )

    with pytest.raises(EntityInvalidDataError):
        getattr(category, method_name)(value)
