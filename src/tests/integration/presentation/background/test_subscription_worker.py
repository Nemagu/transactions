from __future__ import annotations

import asyncio
import time

import pytest

from domain.tenant import TenantID, TenantState, TenantStatus
from domain.user import UserState
from infrastructure.config import SubscriptionWorkerSettings
from presentation.background.subscriptions import SubscriptionWorker


async def _wait_tenant_state(
    tenant_read_repo,
    tenant_id: TenantID,
    state: TenantState,
    version: int,
    timeout_sec: int = 20,
) -> None:
    started_at = time.monotonic()
    while time.monotonic() - started_at < timeout_sec:
        tenant = await tenant_read_repo.by_id(tenant_id)
        if (
            tenant is not None
            and tenant.state == state
            and tenant.version.version == version
        ):
            return
        await asyncio.sleep(0.2)
    raise TimeoutError("Арендатор не был обработан воркером в отведенное время")


@pytest.mark.asyncio
async def test_subscription_worker_creates_tenant_for_new_user(
    subscription_worker_settings: SubscriptionWorkerSettings,
    user_factory,
    user_repo,
    tenant_read_repo,
    db_connection,
) -> None:
    user = user_factory(state=UserState.ACTIVE, version=1)
    await user_repo.save(user)
    await db_connection.commit()

    worker = SubscriptionWorker(subscription_worker_settings)
    worker_task = asyncio.create_task(worker.run())

    try:
        await _wait_tenant_state(
            tenant_read_repo,
            TenantID(user.user_id.user_id),
            TenantState.ACTIVE,
            1,
        )

        tenant = await tenant_read_repo.by_id(TenantID(user.user_id.user_id))
        assert tenant is not None
        assert tenant.status == TenantStatus.TENANT
    finally:
        worker._shutdown_event.set()
        await asyncio.wait_for(worker_task, timeout=10)


@pytest.mark.asyncio
async def test_subscription_worker_updates_tenant_state_from_user_state(
    subscription_worker_settings: SubscriptionWorkerSettings,
    user_factory,
    tenant_factory,
    user_repo,
    tenant_read_repo,
    tenant_subscription_repo,
    db_connection,
) -> None:
    user_v1 = user_factory(state=UserState.ACTIVE, version=1)
    tenant = tenant_factory(
        tenant_id=user_v1.user_id.user_id,
        status=TenantStatus.TENANT,
        state=TenantState.ACTIVE,
        version=1,
    )
    await user_repo.save(user_v1)
    await tenant_read_repo.save(tenant)
    await tenant_subscription_repo.subscribe(tenant, user_v1)

    user_v2 = user_factory(
        user_id=user_v1.user_id.user_id,
        state=UserState.FROZEN,
        version=2,
    )
    await user_repo.save(user_v2)
    await db_connection.commit()

    worker = SubscriptionWorker(subscription_worker_settings)
    worker_task = asyncio.create_task(worker.run())

    try:
        tenant_id = TenantID(user_v1.user_id.user_id)
        await _wait_tenant_state(
            tenant_read_repo,
            tenant_id,
            TenantState.FROZEN,
            2,
        )

        tenant_versions = await tenant_subscription_repo.new_users_versions()
        assert len(tenant_versions) == 0
    finally:
        worker._shutdown_event.set()
        await asyncio.wait_for(worker_task, timeout=10)
