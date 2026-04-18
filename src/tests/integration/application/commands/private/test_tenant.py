from __future__ import annotations

import pytest

from application.commands.private.tenant import (
    TenantCreationUseCase,
    TenantUpdateUseCase,
)
from application.commands.private.user import UserUpdateCommand, UserUpdateUseCase
from application.ports.repositories import TenantEvent
from domain.tenant import TenantID, TenantState, TenantStatus
from domain.user import UserState
from domain.value_objects import Version


@pytest.mark.asyncio
async def test_tenant_creation_use_case_creates_tenants_versions_and_subscriptions(
    uow_factory,
    user_repo,
    user_factory,
    tenant_read_repo,
    tenant_version_repo,
) -> None:
    first_user = user_factory(state=UserState.ACTIVE, version=1)
    second_user = user_factory(state=UserState.FROZEN, version=1)
    await user_repo.save(first_user)
    await user_repo.save(second_user)

    await TenantCreationUseCase(uow_factory()).execute()

    first_tenant = await tenant_read_repo.by_id(TenantID(first_user.user_id.user_id))
    second_tenant = await tenant_read_repo.by_id(TenantID(second_user.user_id.user_id))
    assert first_tenant is not None
    assert second_tenant is not None
    assert first_tenant.status == TenantStatus.TENANT
    assert second_tenant.status == TenantStatus.TENANT
    assert first_tenant.state == TenantState.ACTIVE
    assert second_tenant.state == TenantState.FROZEN

    first_version = await tenant_version_repo.by_id_version(
        first_tenant.tenant_id,
        Version(1),
    )
    second_version = await tenant_version_repo.by_id_version(
        second_tenant.tenant_id,
        Version(1),
    )
    assert first_version is not None
    assert second_version is not None
    assert first_version[1] == TenantEvent.CREATED
    assert second_version[1] == TenantEvent.CREATED


@pytest.mark.asyncio
async def test_tenant_update_use_case_syncs_state_from_user_versions(
    uow_factory,
    user_repo,
    user_factory,
    tenant_read_repo,
    tenant_version_repo,
) -> None:
    user = user_factory(state=UserState.ACTIVE, version=1)
    await user_repo.save(user)

    await TenantCreationUseCase(uow_factory()).execute()
    await UserUpdateUseCase(uow_factory()).execute(
        UserUpdateCommand(
            user_id=user.user_id.user_id,
            state=UserState.FROZEN.value,
            version=2,
        )
    )
    await TenantUpdateUseCase(uow_factory()).execute()

    tenant = await tenant_read_repo.by_id(TenantID(user.user_id.user_id))
    assert tenant is not None
    assert tenant.state == TenantState.FROZEN
    assert tenant.version.version == 2

    second_version = await tenant_version_repo.by_id_version(
        tenant.tenant_id,
        Version(2),
    )
    assert second_version is not None
    assert second_version[1] == TenantEvent.FROZEN

