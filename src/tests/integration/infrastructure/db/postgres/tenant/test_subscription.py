from __future__ import annotations

import pytest

from domain.user.value_objects import UserState
from domain.value_objects import Version


@pytest.mark.asyncio
async def test_users_have_no_tenants_returns_unassigned_users(
    tenant_subscription_repo,
    user_repo,
    tenant_read_repo,
    user_factory,
    tenant_factory,
) -> None:
    assigned_user = user_factory()
    free_user = user_factory()

    await user_repo.save(assigned_user)
    await user_repo.save(free_user)
    await tenant_read_repo.save(
        tenant_factory(tenant_id=assigned_user.user_id.user_id)
    )

    users = await tenant_subscription_repo.users_have_no_tenants()

    assert len(users) == 1
    assert users[0].user_id == free_user.user_id


@pytest.mark.asyncio
async def test_subscribe_new_versions_and_processed_version_flow(
    tenant_subscription_repo,
    user_repo,
    tenant_read_repo,
    user_factory,
    tenant_factory,
) -> None:
    user = user_factory()
    tenant = tenant_factory(tenant_id=user.user_id.user_id)

    await user_repo.save(user)
    await tenant_read_repo.save(tenant)
    await tenant_subscription_repo.subscribe(tenant, user)

    empty = await tenant_subscription_repo.new_users_versions()
    assert empty == []

    user.new_state(UserState.FROZEN)
    user.new_version(Version(2))
    await user_repo.save(user)

    updates = await tenant_subscription_repo.new_users_versions()
    assert len(updates) == 1
    updated_tenant, updated_user = updates[0]
    assert updated_tenant.tenant_id == tenant.tenant_id
    assert updated_user.user_id == user.user_id
    assert updated_user.version.version == 2

    await tenant_subscription_repo.processed_version(tenant, user)
    assert await tenant_subscription_repo.new_users_versions() == []


@pytest.mark.asyncio
async def test_batch_subscribe_and_batch_processed_version(
    tenant_subscription_repo,
    user_repo,
    tenant_read_repo,
    user_factory,
    tenant_factory,
) -> None:
    first_user = user_factory()
    second_user = user_factory()
    first_tenant = tenant_factory(tenant_id=first_user.user_id.user_id)
    second_tenant = tenant_factory(tenant_id=second_user.user_id.user_id)

    await user_repo.save(first_user)
    await user_repo.save(second_user)
    await tenant_read_repo.batch_save([first_tenant, second_tenant])

    await tenant_subscription_repo.batch_subscribe(
        [(first_tenant, first_user), (second_tenant, second_user)]
    )

    first_user.new_version(Version(2))
    second_user.new_version(Version(2))
    await user_repo.save(first_user)
    await user_repo.save(second_user)

    changes = await tenant_subscription_repo.new_users_versions()
    assert len(changes) == 2

    await tenant_subscription_repo.batch_processed_version(
        [(first_tenant, first_user), (second_tenant, second_user)]
    )

    assert await tenant_subscription_repo.new_users_versions() == []
