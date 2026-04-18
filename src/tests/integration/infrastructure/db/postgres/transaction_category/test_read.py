from __future__ import annotations

import pytest

from application.dto import LimitOffsetPaginator
from domain.transaction_category.value_objects import TransactionCategoryName
from domain.value_objects import State


@pytest.mark.asyncio
async def test_save_by_id_and_by_owner_name(
    category_read_repo,
    tenant_read_repo,
    category_factory,
    tenant_factory,
    category_id_factory,
) -> None:
    category = category_factory(name="food")
    await tenant_read_repo.save(tenant_factory(tenant_id=category.owner_id.tenant_id))

    await category_read_repo.save(category)

    by_id = await category_read_repo.by_id(
        category_id_factory(category.category_id.category_id)
    )
    by_owner_name = await category_read_repo.by_owner_id_name(
        owner_id=category.owner_id,
        name=TransactionCategoryName("food"),
    )

    assert by_id is not None
    assert by_owner_name is not None
    assert by_id.category_id == category.category_id
    assert by_owner_name.category_id == category.category_id


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("category_keys", "names", "states", "expected_names"),
    [
        (
            None,
            [TransactionCategoryName("travel")],
            [State.ACTIVE],
            {"travel"},
        ),
        (
            None,
            None,
            [State.DELETED],
            {"archive"},
        ),
        (
            ("food", "travel"),
            [TransactionCategoryName("food"), TransactionCategoryName("travel")],
            None,
            {"food", "travel"},
        ),
    ],
    ids=["name+active", "deleted-only", "category-ids+names"],
)
async def test_filters_and_update(
    category_read_repo,
    tenant_read_repo,
    category_factory,
    tenant_factory,
    category_keys: tuple[str, ...] | None,
    names: list[TransactionCategoryName] | None,
    states: list[State] | None,
    expected_names: set[str],
) -> None:
    owner_tenant = tenant_factory()
    await tenant_read_repo.save(owner_tenant)

    owner_uuid = owner_tenant.tenant_id.tenant_id
    food = category_factory(owner_id=owner_uuid, name="food")
    travel = category_factory(owner_id=owner_uuid, name="travel")
    archive = category_factory(owner_id=owner_uuid, name="archive")

    await category_read_repo.save(food)
    await category_read_repo.save(travel)
    await category_read_repo.save(archive)

    travel.new_description(type(travel.description)("updated"))
    await category_read_repo.save(travel)
    archive.delete()
    await category_read_repo.save(archive)

    categories_map = {
        "food": food.category_id,
        "travel": travel.category_id,
        "archive": archive.category_id,
    }
    category_ids = (
        [categories_map[item] for item in category_keys]
        if category_keys is not None
        else None
    )

    data, count = await category_read_repo.filters(
        owner_id=food.owner_id,
        paginator=LimitOffsetPaginator(limit=10, offset=0),
        category_ids=category_ids,
        names=names,
        states=states,
    )

    assert count == len(expected_names)
    assert len(data) == len(expected_names)
    assert {item.name.name for item in data} == expected_names
    if "travel" in expected_names:
        travel_item = next(item for item in data if item.name.name == "travel")
        assert travel_item.description.description == "updated"


@pytest.mark.asyncio
async def test_next_id_and_by_ids(
    category_read_repo,
    tenant_read_repo,
    category_factory,
    tenant_factory,
) -> None:
    owner = tenant_factory()
    await tenant_read_repo.save(owner)

    first = category_factory(owner_id=owner.tenant_id.tenant_id, name="first")
    second = category_factory(owner_id=owner.tenant_id.tenant_id, name="second")
    await category_read_repo.save(first)
    await category_read_repo.save(second)

    generated_id = await category_read_repo.next_id()
    assert generated_id.category_id is not None

    categories = await category_read_repo.by_ids({first.category_id, second.category_id})
    assert {item.category_id for item in categories} == {first.category_id, second.category_id}
