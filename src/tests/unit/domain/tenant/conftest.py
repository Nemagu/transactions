from collections.abc import Callable
from uuid import uuid4

import pytest

from domain.tenant.entity import Tenant
from domain.tenant.value_objects import TenantID, TenantState, TenantStatus
from domain.value_objects import Version


@pytest.fixture
def local_tenant_factory() -> Callable[..., Tenant]:
    def factory(
        *,
        tenant_id: TenantID | None = None,
        status: TenantStatus = TenantStatus.TENANT,
        state: TenantState = TenantState.ACTIVE,
        version: int = 1,
    ) -> Tenant:
        return Tenant(
            tenant_id=tenant_id or TenantID(uuid4()),
            status=status,
            state=state,
            version=Version(version),
        )

    return factory
