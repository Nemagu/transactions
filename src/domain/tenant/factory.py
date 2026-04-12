from uuid import UUID

from domain.tenant.entity import Tenant
from domain.tenant.value_objects import TenantID, TenantState, TenantStatus
from domain.value_objects import Version


class TenantFactory:
    @staticmethod
    def new(tenant_id: UUID, state: str) -> Tenant:
        return Tenant(
            tenant_id=TenantID(tenant_id),
            status=TenantStatus.TENANT,
            state=TenantState.from_str(state),
            version=Version(1),
        )

    @staticmethod
    def restore(tenant_id: UUID, status: str, state: str, version: int) -> Tenant:
        return Tenant(
            tenant_id=TenantID(tenant_id),
            status=TenantStatus.from_str(status),
            state=TenantState.from_str(state),
            version=Version(version),
        )
