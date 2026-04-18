from __future__ import annotations

from decimal import Decimal

import pytest

from application.dto import LimitOffsetPaginator
from application.ports.repositories import PersonalTransactionEvent
from domain.personal_transaction.value_objects import PersonalTransactionType
from domain.value_objects import State, Version


@pytest.mark.asyncio
async def test_save_and_by_id_version(
    transaction_version_repo,
    transaction_read_repo,
    category_read_repo,
    tenant_read_repo,
    tenant_factory,
    category_factory,
    transaction_factory,
) -> None:
    owner = tenant_factory()
    editor = tenant_factory()
    await tenant_read_repo.save(owner)
    await tenant_read_repo.save(editor)

    category = category_factory(owner_id=owner.tenant_id.tenant_id)
    await category_read_repo.save(category)

    transaction = transaction_factory(
        owner_id=owner.tenant_id.tenant_id,
        category_ids={category.category_id.category_id},
    )
    await transaction_read_repo.save(transaction)

    await transaction_version_repo.save(
        transaction=transaction,
        event=PersonalTransactionEvent.CREATED,
        editor=editor,
    )

    stored = await transaction_version_repo.by_id_version(
        transaction.transaction_id,
        Version(1),
    )

    assert stored is not None
    actual_transaction, event, editor_id, _ = stored
    assert actual_transaction.transaction_id == transaction.transaction_id
    assert event == PersonalTransactionEvent.CREATED
    assert editor_id == editor.tenant_id


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "category_keys",
        "transaction_types",
        "from_version",
        "to_version",
        "expected_versions",
    ),
    [
        (
            None,
            [PersonalTransactionType.EXPENSE],
            Version(1),
            Version(2),
            {1, 2},
        ),
        (
            ("two",),
            None,
            None,
            None,
            {2, 3},
        ),
        (
            None,
            [PersonalTransactionType.INCOME],
            Version(3),
            Version(3),
            {3},
        ),
    ],
    ids=["expense-range", "category-two", "income-v3"],
)
async def test_filters_count_distinct_versions(
    transaction_version_repo,
    transaction_read_repo,
    category_read_repo,
    tenant_read_repo,
    tenant_factory,
    category_factory,
    transaction_factory,
    category_keys: tuple[str, ...] | None,
    transaction_types: list[PersonalTransactionType] | None,
    from_version: Version | None,
    to_version: Version | None,
    expected_versions: set[int],
) -> None:
    owner = tenant_factory()
    await tenant_read_repo.save(owner)

    first_category = category_factory(owner_id=owner.tenant_id.tenant_id, name="one")
    second_category = category_factory(owner_id=owner.tenant_id.tenant_id, name="two")
    await category_read_repo.save(first_category)
    await category_read_repo.save(second_category)

    tx_uuid = transaction_factory(
        owner_id=owner.tenant_id.tenant_id,
        category_ids={first_category.category_id.category_id},
    ).transaction_id.transaction_id

    first_version = transaction_factory(
        transaction_id=tx_uuid,
        owner_id=owner.tenant_id.tenant_id,
        category_ids={first_category.category_id.category_id},
        amount=Decimal("100.00"),
        version=1,
    )
    second_version = transaction_factory(
        transaction_id=tx_uuid,
        owner_id=owner.tenant_id.tenant_id,
        category_ids={
            first_category.category_id.category_id,
            second_category.category_id.category_id,
        },
        amount=Decimal("200.00"),
        version=2,
    )
    third_version = transaction_factory(
        transaction_id=tx_uuid,
        owner_id=owner.tenant_id.tenant_id,
        category_ids={second_category.category_id.category_id},
        transaction_type=PersonalTransactionType.INCOME,
        amount=Decimal("300.00"),
        version=3,
    )

    await transaction_read_repo.save(first_version)
    await transaction_version_repo.save(
        first_version,
        PersonalTransactionEvent.CREATED,
        editor=None,
    )
    await transaction_read_repo.save(second_version)
    await transaction_version_repo.save(
        second_version,
        PersonalTransactionEvent.UPDATED,
        editor=None,
    )
    await transaction_read_repo.save(third_version)
    await transaction_version_repo.save(
        third_version,
        PersonalTransactionEvent.UPDATED,
        editor=None,
    )

    categories_map = {
        "one": first_category.category_id,
        "two": second_category.category_id,
    }
    category_ids = (
        [categories_map[item] for item in category_keys]
        if category_keys is not None
        else None
    )

    versions, count = await transaction_version_repo.filters(
        owner_id=owner.tenant_id,
        paginator=LimitOffsetPaginator(limit=10, offset=0),
        transaction_id=first_version.transaction_id,
        category_ids=category_ids,
        transaction_types=transaction_types,
        from_money_amount=None,
        to_money_amount=None,
        from_transaction_time=None,
        to_transaction_time=None,
        states=[State.ACTIVE],
        from_version=from_version,
        to_version=to_version,
    )

    assert count == len(expected_versions)
    assert len(versions) == len(expected_versions)
    assert {item[0].version.version for item in versions} == expected_versions
