from __future__ import annotations

import pytest

from application.commands.public.tenant import (
    TenantAppointmentAdminCommand,
    TenantAppointmentAdminUseCase,
    TenantAppointmentTenantCommand,
    TenantAppointmentTenantUseCase,
)
from application.ports.repositories import TenantEvent
from domain.tenant import TenantState, TenantStatus
from domain.value_objects import Version


@pytest.mark.asyncio
async def test_tenant_public_commands_change_status_and_create_versions(
    uow_factory,
    tenant_factory,
    tenant_read_repo,
    tenant_version_repo,
) -> None:
    initiator = tenant_factory(status=TenantStatus.ADMIN, state=TenantState.ACTIVE)
    tenant = tenant_factory(status=TenantStatus.TENANT, state=TenantState.ACTIVE)
    await tenant_read_repo.save(initiator)
    await tenant_read_repo.save(tenant)

    to_admin = await TenantAppointmentAdminUseCase(uow_factory()).execute(
        TenantAppointmentAdminCommand(
            initiator_id=initiator.tenant_id.tenant_id,
            tenant_id=tenant.tenant_id.tenant_id,
        )
    )
    to_tenant = await TenantAppointmentTenantUseCase(uow_factory()).execute(
        TenantAppointmentTenantCommand(
            initiator_id=initiator.tenant_id.tenant_id,
            tenant_id=tenant.tenant_id.tenant_id,
        )
    )

    assert to_admin.status == TenantStatus.ADMIN.value
    assert to_admin.version == 2
    assert to_tenant.status == TenantStatus.TENANT.value
    assert to_tenant.version == 3

    admin_version = await tenant_version_repo.by_id_version(
        tenant.tenant_id,
        Version(2),
    )
    tenant_version = await tenant_version_repo.by_id_version(
        tenant.tenant_id,
        Version(3),
    )
    assert admin_version is not None
    assert tenant_version is not None
    assert admin_version[1] == TenantEvent.UPDATED
    assert tenant_version[1] == TenantEvent.UPDATED
    assert admin_version[2] == initiator.tenant_id
    assert tenant_version[2] == initiator.tenant_id

