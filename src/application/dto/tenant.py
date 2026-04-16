from dataclasses import dataclass
from datetime import datetime
from typing import Self
from uuid import UUID

from domain.tenant import Tenant


@dataclass(slots=True)
class TenantSimpleDTO:
    tenant_id: UUID
    status: str
    state: str
    version: int

    @classmethod
    def from_domain(cls, tenant: Tenant) -> Self:
        return cls(
            tenant.tenant_id.tenant_id,
            tenant.status.value,
            tenant.state.value,
            tenant.version.version,
        )


@dataclass(slots=True)
class TenantVersionSimpleDTO:
    tenant_id: UUID
    status: str
    state: str
    version: int
    editor_id: UUID | None
    event: str
    created_at: datetime


@dataclass(slots=True)
class TenantVersionDetailDTO:
    tenant_id: UUID
    status: str
    state: str
    version: int
    editor: TenantSimpleDTO | None
    event: str
    created_at: datetime
