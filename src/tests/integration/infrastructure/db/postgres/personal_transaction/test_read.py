from __future__ import annotations

from decimal import Decimal

import pytest

from application.dto import LimitOffsetPaginator
from domain.personal_transaction import Currency, MoneyAmount
from domain.personal_transaction.value_objects import PersonalTransactionType
from domain.value_objects import State


@pytest.mark.asyncio
async def test_save_and_by_id(
    transaction_read_repo,
    category_read_repo,
    tenant_read_repo,
    tenant_factory,
    category_factory,
    transaction_factory,
    transaction_id_factory,
) -> None:
    owner = tenant_factory()
    await tenant_read_repo.save(owner)

    category = category_factory(owner_id=owner.tenant_id.tenant_id)
    await category_read_repo.save(category)

    transaction = transaction_factory(
        owner_id=owner.tenant_id.tenant_id,
        category_ids={category.category_id.category_id},
    )
    await transaction_read_repo.save(transaction)

    stored = await transaction_read_repo.by_id(
        transaction_id_factory(transaction.transaction_id.transaction_id)
    )

    assert stored is not None
    assert stored.transaction_id == transaction.transaction_id
    assert stored.owner_id == transaction.owner_id
    assert stored.category_ids == transaction.category_ids


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "transaction_keys",
        "category_keys",
        "transaction_types",
        "from_amount",
        "to_amount",
        "expected_keys",
    ),
    [
        (
            None,
            None,
            [PersonalTransactionType.EXPENSE],
            None,
            None,
            {"expense"},
        ),
        (
            None,
            ("second",),
            None,
            None,
            None,
            {"income"},
        ),
        (
            None,
            None,
            None,
            Decimal("600.00"),
            Decimal("800.00"),
            {"expense"},
        ),
    ],
    ids=["type-expense", "category-second", "amount-range"],
)
async def test_filters_count_distinct_and_update_categories(
    transaction_read_repo,
    category_read_repo,
    tenant_read_repo,
    tenant_factory,
    category_factory,
    transaction_factory,
    transaction_keys: tuple[str, ...] | None,
    category_keys: tuple[str, ...] | None,
    transaction_types: list[PersonalTransactionType] | None,
    from_amount: Decimal | None,
    to_amount: Decimal | None,
    expected_keys: set[str],
) -> None:
    owner = tenant_factory()
    await tenant_read_repo.save(owner)

    first_category = category_factory(owner_id=owner.tenant_id.tenant_id, name="first")
    second_category = category_factory(owner_id=owner.tenant_id.tenant_id, name="second")
    await category_read_repo.save(first_category)
    await category_read_repo.save(second_category)

    expense_tx_id = transaction_factory(
        owner_id=owner.tenant_id.tenant_id,
        category_ids={
            first_category.category_id.category_id,
            second_category.category_id.category_id,
        },
    ).transaction_id.transaction_id

    expense_tx = transaction_factory(
        transaction_id=expense_tx_id,
        owner_id=owner.tenant_id.tenant_id,
        category_ids={
            first_category.category_id.category_id,
            second_category.category_id.category_id,
        },
        amount=Decimal("500.00"),
    )
    await transaction_read_repo.save(expense_tx)

    expense_tx_updated = transaction_factory(
        transaction_id=expense_tx_id,
        owner_id=owner.tenant_id.tenant_id,
        category_ids={first_category.category_id.category_id},
        amount=Decimal("700.00"),
        version=2,
    )
    await transaction_read_repo.save(expense_tx_updated)

    income_tx = transaction_factory(
        owner_id=owner.tenant_id.tenant_id,
        category_ids={second_category.category_id.category_id},
        transaction_type=PersonalTransactionType.INCOME,
        amount=Decimal("1500.00"),
    )
    await transaction_read_repo.save(income_tx)

    transactions_map = {
        "expense": expense_tx_updated.transaction_id,
        "income": income_tx.transaction_id,
    }
    categories_map = {
        "first": first_category.category_id,
        "second": second_category.category_id,
    }
    transaction_ids = (
        [transactions_map[item] for item in transaction_keys]
        if transaction_keys is not None
        else None
    )
    category_ids = (
        [categories_map[item] for item in category_keys]
        if category_keys is not None
        else None
    )
    from_money_amount = (
        MoneyAmount(amount=from_amount, currency=Currency.RUBLE)
        if from_amount is not None
        else None
    )
    to_money_amount = (
        MoneyAmount(amount=to_amount, currency=Currency.RUBLE)
        if to_amount is not None
        else None
    )

    items, count = await transaction_read_repo.filters(
        owner_id=owner.tenant_id,
        paginator=LimitOffsetPaginator(limit=10, offset=0),
        transaction_ids=transaction_ids,
        category_ids=category_ids,
        transaction_types=transaction_types,
        from_money_amount=from_money_amount,
        to_money_amount=to_money_amount,
        from_transaction_time=None,
        to_transaction_time=None,
        states=[State.ACTIVE],
    )

    expected_ids = {transactions_map[item] for item in expected_keys}
    assert count == len(expected_ids)
    assert len(items) == len(expected_ids)
    assert {item.transaction_id for item in items} == expected_ids
    if expected_keys == {"expense"}:
        assert items[0].category_ids == expense_tx_updated.category_ids


@pytest.mark.asyncio
async def test_next_id_returns_uuid(transaction_read_repo) -> None:
    transaction_id = await transaction_read_repo.next_id()
    assert transaction_id.transaction_id is not None
