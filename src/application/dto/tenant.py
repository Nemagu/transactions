from dataclasses import dataclass
from datetime import datetime
from typing import Self
from uuid import UUID

from application.ports.repositories.tenant import TenantEvent
from domain.tenant import Tenant, TenantID


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
    event: str
    editor_id: UUID | None
    created_at: datetime

    @classmethod
    def from_domain(
        cls,
        tenant: Tenant,
        event: TenantEvent,
        editor_id: TenantID | None,
        created_at: datetime,
    ) -> Self:
        return cls(
            tenant.tenant_id.tenant_id,
            tenant.status.value,
            tenant.state.value,
            tenant.version.version,
            event.value,
            editor_id.tenant_id if editor_id is not None else None,
            created_at,
        )


@dataclass(slots=True)
class TenantVersionDetailDTO:
    tenant_id: UUID
    status: str
    state: str
    version: int
    event: str
    editor: TenantSimpleDTO | None
    created_at: datetime

    @classmethod
    def from_domain(
        cls,
        tenant: Tenant,
        event: TenantEvent,
        editor: Tenant | None,
        created_at: datetime,
    ) -> Self:
        return cls(
            tenant.tenant_id.tenant_id,
            tenant.status.value,
            tenant.state.value,
            tenant.version.version,
            event.value,
            TenantSimpleDTO.from_domain(editor) if editor is not None else None,
            created_at,
        )
