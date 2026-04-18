from __future__ import annotations

import pytest

from application.dto import LimitOffsetPaginator
from domain.tenant.value_objects import TenantState, TenantStatus


@pytest.mark.asyncio
async def test_save_and_by_id(tenant_read_repo, tenant_factory, tenant_id_factory) -> None:
    tenant = tenant_factory()

    await tenant_read_repo.save(tenant)

    stored = await tenant_read_repo.by_id(tenant_id_factory(tenant.tenant_id.tenant_id))

    assert stored is not None
    assert stored.tenant_id == tenant.tenant_id
    assert stored.status == tenant.status
    assert stored.state == tenant.state
    assert stored.version == tenant.version


@pytest.mark.asyncio
async def test_batch_save_create_and_update(
    tenant_read_repo,
    tenant_factory,
    tenant_id_factory,
) -> None:
    first = tenant_factory()
    second = tenant_factory()

    await tenant_read_repo.batch_save([first, second])

    first.new_state(TenantState.FROZEN)
    await tenant_read_repo.batch_save([first])

    stored = await tenant_read_repo.by_id(tenant_id_factory(first.tenant_id.tenant_id))

    assert stored is not None
    assert stored.state == TenantState.FROZEN
    assert stored.version.version == 2


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tenant_keys", "statuses", "states", "expected_keys"),
    [
        (
            None,
            [TenantStatus.ADMIN],
            [TenantState.FROZEN],
            {"frozen_admin"},
        ),
        (
            None,
            [TenantStatus.ADMIN],
            None,
            {"active_admin", "frozen_admin"},
        ),
        (
            ("active_tenant", "active_admin"),
            None,
            [TenantState.ACTIVE],
            {"active_tenant", "active_admin"},
        ),
    ],
    ids=["status+state", "status-only", "tenant_ids+state"],
)
async def test_filters_return_filtered_data_and_count(
    tenant_read_repo,
    tenant_factory,
    tenant_keys: tuple[str, ...] | None,
    statuses: list[TenantStatus] | None,
    states: list[TenantState] | None,
    expected_keys: set[str],
) -> None:
    tenants_map = {
        "active_tenant": tenant_factory(state=TenantState.ACTIVE),
        "frozen_admin": tenant_factory(
            status=TenantStatus.ADMIN, state=TenantState.FROZEN
        ),
        "active_admin": tenant_factory(status=TenantStatus.ADMIN, state=TenantState.ACTIVE),
    }
    await tenant_read_repo.batch_save(list(tenants_map.values()))

    tenant_ids = (
        [tenants_map[tenant_key].tenant_id for tenant_key in tenant_keys]
        if tenant_keys is not None
        else None
    )

    tenants, count = await tenant_read_repo.filters(
        paginator=LimitOffsetPaginator(limit=10, offset=0),
        tenant_ids=tenant_ids,
        statuses=statuses,
        states=states,
    )

    expected_ids = {tenants_map[item].tenant_id for item in expected_keys}
    assert count == len(expected_ids)
    assert len(tenants) == len(expected_ids)
    assert {tenant.tenant_id for tenant in tenants} == expected_ids
