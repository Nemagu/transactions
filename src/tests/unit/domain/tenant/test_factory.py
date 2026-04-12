from uuid import uuid4

import pytest

from domain.errors import ValueObjectInvalidDataError
from domain.tenant.factory import TenantFactory
from domain.tenant.value_objects import TenantState, TenantStatus


def test_tenant_factory_new_creates_default_tenant() -> None:
    tenant_id = uuid4()

    tenant = TenantFactory.new(tenant_id=tenant_id, state="active")

    assert tenant.tenant_id.tenant_id == tenant_id
    assert tenant.status == TenantStatus.TENANT
    assert tenant.state == TenantState.ACTIVE
    assert tenant.version.version == 1


def test_tenant_factory_restore_recreates_tenant() -> None:
    tenant_id = uuid4()

    tenant = TenantFactory.restore(
        tenant_id=tenant_id,
        status="ADMIN",
        state="FROZEN",
        version=3,
    )

    assert tenant.tenant_id.tenant_id == tenant_id
    assert tenant.status == TenantStatus.ADMIN
    assert tenant.state == TenantState.FROZEN
    assert tenant.version.version == 3


def test_tenant_factory_restore_rejects_invalid_status() -> None:
    with pytest.raises(ValueObjectInvalidDataError):
        TenantFactory.restore(
            tenant_id=uuid4(),
            status="manager",
            state="active",
            version=1,
        )
