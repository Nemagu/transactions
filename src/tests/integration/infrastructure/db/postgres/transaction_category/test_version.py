from __future__ import annotations

import pytest

from application.dto import LimitOffsetPaginator
from application.ports.repositories import TransactionCategoryEvent
from domain.transaction_category.value_objects import TransactionCategoryName
from domain.value_objects import State, Version


@pytest.mark.asyncio
async def test_save_and_by_id_version(
    category_version_repo,
    category_read_repo,
    tenant_read_repo,
    category_factory,
    tenant_factory,
) -> None:
    owner_tenant = tenant_factory()
    editor = tenant_factory()
    await tenant_read_repo.save(owner_tenant)
    await tenant_read_repo.save(editor)

    category = category_factory(owner_id=owner_tenant.tenant_id.tenant_id)
    await category_read_repo.save(category)
    await category_version_repo.save(category, TransactionCategoryEvent.CREATED, editor)

    stored = await category_version_repo.by_id_version(category.category_id, Version(1))

    assert stored is not None
    actual_category, event, editor_id, _ = stored
    assert actual_category.category_id == category.category_id
    assert event == TransactionCategoryEvent.CREATED
    assert editor_id == editor.tenant_id


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("names", "states", "from_version", "to_version", "expected_versions", "expected_events"),
    [
        (
            [TransactionCategoryName("updated")],
            [State.ACTIVE],
            Version(2),
            Version(2),
            {2},
            {TransactionCategoryEvent.UPDATED},
        ),
        (
            None,
            [State.DELETED],
            None,
            None,
            {3},
            {TransactionCategoryEvent.DELETED},
        ),
        (
            [TransactionCategoryName("base")],
            None,
            Version(1),
            Version(1),
            {1},
            {TransactionCategoryEvent.CREATED},
        ),
    ],
    ids=["updated-only", "deleted-only", "first-version"],
)
async def test_filters_by_version_name_and_state(
    category_version_repo,
    category_read_repo,
    tenant_read_repo,
    category_factory,
    tenant_factory,
    names: list[TransactionCategoryName] | None,
    states: list[State] | None,
    from_version: Version | None,
    to_version: Version | None,
    expected_versions: set[int],
    expected_events: set[TransactionCategoryEvent],
) -> None:
    owner_tenant = tenant_factory()
    await tenant_read_repo.save(owner_tenant)

    category_id = category_factory().category_id.category_id
    version_1 = category_factory(
        category_id=category_id,
        owner_id=owner_tenant.tenant_id.tenant_id,
        name="base",
        state=State.ACTIVE.value,
        version=1,
    )
    version_2 = category_factory(
        category_id=category_id,
        owner_id=owner_tenant.tenant_id.tenant_id,
        name="updated",
        state=State.ACTIVE.value,
        version=2,
    )
    version_3 = category_factory(
        category_id=category_id,
        owner_id=owner_tenant.tenant_id.tenant_id,
        name="updated",
        state=State.DELETED.value,
        version=3,
    )

    await category_read_repo.save(version_1)
    await category_version_repo.save(version_1, TransactionCategoryEvent.CREATED, None)
    await category_read_repo.save(version_2)
    await category_version_repo.save(version_2, TransactionCategoryEvent.UPDATED, None)
    await category_read_repo.save(version_3)
    await category_version_repo.save(version_3, TransactionCategoryEvent.DELETED, None)

    data, count = await category_version_repo.filters(
        owner_id=version_1.owner_id,
        paginator=LimitOffsetPaginator(limit=10, offset=0),
        category_id=version_1.category_id,
        names=names,
        states=states,
        from_version=from_version,
        to_version=to_version,
    )

    assert count == len(expected_versions)
    assert len(data) == len(expected_versions)
    assert {item[0].version.version for item in data} == expected_versions
    assert {item[1] for item in data} == expected_events
