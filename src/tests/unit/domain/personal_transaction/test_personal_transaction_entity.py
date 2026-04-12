from datetime import datetime
from decimal import Decimal

import pytest

from src.domain.errors import EntityIdempotentError, EntityInvalidDataError
from src.domain.personal_transaction.value_objects import (
    Currency,
    MoneyAmount,
    PersonalTransactionDescription,
    PersonalTransactionName,
    PersonalTransactionTime,
    PersonalTransactionType,
)
from src.domain.value_objects import State


def test_personal_transaction_exposes_created_state(personal_transaction_factory) -> None:
    transaction = personal_transaction_factory()

    assert transaction.name == PersonalTransactionName("Coffee")
    assert transaction.description == PersonalTransactionDescription("Morning coffee")
    assert transaction.transaction_type == PersonalTransactionType.EXPENSE
    assert transaction.money_amount == MoneyAmount(Decimal("100"), Currency.RUBLE)
    assert transaction.transaction_time == PersonalTransactionTime(
        datetime(2026, 4, 5, 12, 0, 0)
    )
    assert transaction.state == State.ACTIVE
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

    assert getattr(transaction, expected_attr) == value
    assert transaction.version.version == 2
    assert transaction.original_version.version == 1


def test_personal_transaction_updates_categories_once_per_cycle(
    personal_transaction_factory,
    transaction_category_set_factory,
    tenant_id_factory,
) -> None:
    owner_id = tenant_id_factory()
    transaction = personal_transaction_factory(owner_id=owner_id, category_ids=set())
    categories = transaction_category_set_factory(
        owner_id=owner_id,
        names=("Taxi", "Transport"),
    )

    transaction.new_categories(categories)

    assert transaction.category_ids == {category.category_id for category in categories}
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

    with pytest.raises(EntityIdempotentError):
        getattr(transaction, method_name)(value)


def test_personal_transaction_rejects_idempotent_categories_change(
    personal_transaction_factory,
    transaction_category_set_factory,
    tenant_id_factory,
) -> None:
    owner_id = tenant_id_factory()
    categories = transaction_category_set_factory(owner_id=owner_id, names=("Food",))
    transaction = personal_transaction_factory(
        owner_id=owner_id,
        category_ids={category.category_id for category in categories},
    )

    with pytest.raises(EntityInvalidDataError):
        transaction.new_categories(categories)


@pytest.mark.parametrize(
    ("method_name", "initial_state", "expected_state"),
    [
        ("activate", State.DELETED, State.ACTIVE),
        ("delete", State.ACTIVE, State.DELETED),
    ],
    ids=["activate-transaction", "delete-transaction"],
)
def test_personal_transaction_changes_state(
    personal_transaction_factory,
    method_name: str,
    initial_state: State,
    expected_state: State,
) -> None:
    transaction = personal_transaction_factory(state=initial_state)

    getattr(transaction, method_name)()

    assert transaction.state == expected_state
    assert transaction.version.version == 2
    assert transaction.original_version.version == 1


@pytest.mark.parametrize(
    ("method_name", "state"),
    [
        ("activate", State.ACTIVE),
        ("delete", State.DELETED),
    ],
    ids=["activate-active", "delete-deleted"],
)
def test_personal_transaction_rejects_idempotent_state_changes(
    personal_transaction_factory,
    method_name: str,
    state: State,
) -> None:
    transaction = personal_transaction_factory(state=state)

    with pytest.raises(EntityIdempotentError):
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


@pytest.mark.parametrize(
    "method_name",
    [
        "new_description",
        "new_categories",
        "add_categories",
        "remove_categories",
        "new_transaction_type",
        "new_money_amount",
        "new_transaction_time",
    ],
    ids=[
        "change-description",
        "change-categories",
        "add-categories",
        "remove-categories",
        "change-type",
        "change-amount",
        "change-time",
    ],
)
def test_personal_transaction_rejects_changes_when_deleted(
    personal_transaction_factory,
    transaction_category_set_factory,
    tenant_id_factory,
    method_name: str,
) -> None:
    owner_id = tenant_id_factory()
    transaction = personal_transaction_factory(state=State.DELETED, owner_id=owner_id)
    value_map = {
        "new_description": PersonalTransactionDescription("Ride to office"),
        "new_categories": transaction_category_set_factory(
            owner_id=owner_id,
            names=("Taxi", "Office"),
        ),
        "add_categories": transaction_category_set_factory(
            owner_id=owner_id,
            names=("Taxi",),
        ),
        "remove_categories": transaction_category_set_factory(
            owner_id=owner_id,
            names=("Food",),
        ),
        "new_transaction_type": PersonalTransactionType.INCOME,
        "new_money_amount": MoneyAmount(
            amount=Decimal("250"),
            currency=Currency.DOLLAR,
        ),
        "new_transaction_time": PersonalTransactionTime(
            datetime(2026, 4, 6, 15, 30, 0)
        ),
    }

    with pytest.raises(EntityInvalidDataError):
        getattr(transaction, method_name)(value_map[method_name])


@pytest.mark.parametrize(
    "method_name",
    ["add_categories", "remove_categories"],
    ids=["add-empty", "remove-empty"],
)
def test_personal_transaction_rejects_empty_categories_operations(
    personal_transaction_factory,
    method_name: str,
) -> None:
    transaction = personal_transaction_factory()

    with pytest.raises(EntityInvalidDataError):
        getattr(transaction, method_name)(set())


def test_personal_transaction_rejects_foreign_categories(
    personal_transaction_factory,
    transaction_category_set_factory,
    tenant_id_factory,
) -> None:
    transaction_owner_id = tenant_id_factory()
    category_owner_id = tenant_id_factory()
    transaction = personal_transaction_factory(
        owner_id=transaction_owner_id,
        category_ids=set(),
    )
    categories = transaction_category_set_factory(
        owner_id=category_owner_id,
        names=("Taxi",),
    )

    with pytest.raises(EntityInvalidDataError):
        transaction.add_categories(categories)


def test_personal_transaction_rejects_deleted_categories(
    personal_transaction_factory,
    transaction_category_set_factory,
    tenant_id_factory,
) -> None:
    owner_id = tenant_id_factory()
    transaction = personal_transaction_factory(owner_id=owner_id, category_ids=set())
    categories = transaction_category_set_factory(
        owner_id=owner_id,
        names=("Taxi",),
        state=State.DELETED,
    )

    with pytest.raises(EntityInvalidDataError):
        transaction.add_categories(categories)


def test_personal_transaction_adds_only_missing_categories(
    personal_transaction_factory,
    transaction_category_set_factory,
    tenant_id_factory,
) -> None:
    owner_id = tenant_id_factory()
    existing_categories = transaction_category_set_factory(
        owner_id=owner_id,
        names=("Food",),
    )
    existing_category = next(iter(existing_categories))
    transaction = personal_transaction_factory(
        owner_id=owner_id,
        category_ids={existing_category.category_id},
    )
    new_categories = transaction_category_set_factory(
        owner_id=owner_id,
        names=("Taxi",),
    )
    new_category = next(iter(new_categories))

    transaction.add_categories({existing_category, new_category})

    assert transaction.category_ids == {
        existing_category.category_id,
        new_category.category_id,
    }
    assert transaction.version.version == 2


def test_personal_transaction_removes_only_existing_categories(
    personal_transaction_factory,
    transaction_category_set_factory,
    tenant_id_factory,
) -> None:
    owner_id = tenant_id_factory()
    categories = transaction_category_set_factory(
        owner_id=owner_id,
        names=("Food", "Taxi"),
    )
    category_list = list(categories)
    transaction = personal_transaction_factory(
        owner_id=owner_id,
        category_ids={category.category_id for category in categories},
    )
    missing_category = next(
        iter(
            transaction_category_set_factory(
                owner_id=owner_id,
                names=("Office",),
            )
        )
    )

    transaction.remove_categories({category_list[0], missing_category})

    assert transaction.category_ids == {category_list[1].category_id}
    assert transaction.version.version == 2


def test_personal_transaction_rejects_adding_only_existing_categories(
    personal_transaction_factory,
    transaction_category_set_factory,
    tenant_id_factory,
) -> None:
    owner_id = tenant_id_factory()
    categories = transaction_category_set_factory(
        owner_id=owner_id,
        names=("Food", "Taxi"),
    )
    transaction = personal_transaction_factory(
        owner_id=owner_id,
        category_ids={category.category_id for category in categories},
    )

    with pytest.raises(EntityInvalidDataError):
        transaction.add_categories(categories)


def test_personal_transaction_rejects_removing_only_missing_categories(
    personal_transaction_factory,
    transaction_category_set_factory,
    tenant_id_factory,
) -> None:
    owner_id = tenant_id_factory()
    transaction = personal_transaction_factory(owner_id=owner_id, category_ids=set())
    categories = transaction_category_set_factory(
        owner_id=owner_id,
        names=("Food", "Taxi"),
    )

    with pytest.raises(EntityInvalidDataError):
        transaction.remove_categories(categories)
