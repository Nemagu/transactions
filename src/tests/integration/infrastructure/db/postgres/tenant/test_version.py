from __future__ import annotations

import pytest

from application.dto import LimitOffsetPaginator
from application.ports.repositories import TenantEvent
from domain.tenant.value_objects import TenantState, TenantStatus
from domain.value_objects import Version


@pytest.mark.asyncio
async def test_save_and_by_id_version(
    tenant_version_repo,
    tenant_read_repo,
    tenant_factory,
    tenant_id_factory,
) -> None:
    tenant = tenant_factory()
    editor = tenant_factory(status=TenantStatus.ADMIN)
    await tenant_read_repo.save(tenant)
    await tenant_read_repo.save(editor)

    await tenant_version_repo.save(tenant, TenantEvent.CREATED, editor)

    stored = await tenant_version_repo.by_id_version(
        tenant_id_factory(tenant.tenant_id.tenant_id),
        Version(1),
    )

    assert stored is not None
    actual_tenant, event, editor_id, _ = stored
    assert actual_tenant.tenant_id == tenant.tenant_id
    assert event == TenantEvent.CREATED
    assert editor_id == editor.tenant_id


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("statuses", "states", "from_version", "to_version", "expected_versions", "expected_events"),
    [
        (
            [TenantStatus.ADMIN],
            None,
            None,
            None,
            {2, 3},
            {TenantEvent.UPDATED, TenantEvent.FROZEN},
        ),
        (
            [TenantStatus.ADMIN],
            [TenantState.FROZEN],
            Version(3),
            Version(3),
            {3},
            {TenantEvent.FROZEN},
        ),
        (
            [TenantStatus.TENANT],
            [TenantState.ACTIVE],
            Version(1),
            Version(1),
            {1},
            {TenantEvent.CREATED},
        ),
    ],
    ids=["status-admin", "status+state+version-range", "initial-version"],
)
async def test_filters_by_version_and_state(
    tenant_version_repo,
    tenant_read_repo,
    tenant_factory,
    statuses: list[TenantStatus] | None,
    states: list[TenantState] | None,
    from_version: Version | None,
    to_version: Version | None,
    expected_versions: set[int],
    expected_events: set[TenantEvent],
) -> None:
    tenant_id = tenant_factory().tenant_id.tenant_id
    version_1 = tenant_factory(
        tenant_id=tenant_id,
        status=TenantStatus.TENANT,
        state=TenantState.ACTIVE,
        version=1,
    )
    version_2 = tenant_factory(
        tenant_id=tenant_id,
        status=TenantStatus.ADMIN,
        state=TenantState.ACTIVE,
        version=2,
    )
    version_3 = tenant_factory(
        tenant_id=tenant_id,
        status=TenantStatus.ADMIN,
        state=TenantState.FROZEN,
        version=3,
    )

    await tenant_read_repo.save(version_1)
    await tenant_version_repo.save(version_1, TenantEvent.CREATED, None)
    await tenant_read_repo.save(version_2)
    await tenant_version_repo.save(version_2, TenantEvent.UPDATED, None)
    await tenant_read_repo.save(version_3)
    await tenant_version_repo.save(version_3, TenantEvent.FROZEN, None)

    versions, count = await tenant_version_repo.filters(
        paginator=LimitOffsetPaginator(limit=10, offset=0),
        tenant_id=version_1.tenant_id,
        statuses=statuses,
        states=states,
        from_version=from_version,
        to_version=to_version,
    )

    assert count == len(expected_versions)
    assert len(versions) == len(expected_versions)
    assert {item[0].version.version for item in versions} == expected_versions
    assert {item[1] for item in versions} == expected_events


@pytest.mark.asyncio
async def test_batch_save_creates_many_versions(
    tenant_version_repo,
    tenant_read_repo,
    tenant_factory,
) -> None:
    first = tenant_factory()
    second = tenant_factory()
    await tenant_read_repo.batch_save([first, second])

    await tenant_version_repo.batch_save(
        [
            (first, TenantEvent.CREATED, None),
            (second, TenantEvent.CREATED, None),
        ]
    )

    first_saved = await tenant_version_repo.by_id_version(first.tenant_id, Version(1))
    second_saved = await tenant_version_repo.by_id_version(second.tenant_id, Version(1))

    assert first_saved is not None
    assert second_saved is not None
