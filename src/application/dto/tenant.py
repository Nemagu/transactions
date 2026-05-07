from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Self
from uuid import UUID

from domain.tenant import Tenant

if TYPE_CHECKING:
    from application.ports.repositories.tenant import TenantEvent, TenantVersionDTO


@dataclass(slots=True, frozen=True)
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


@dataclass(slots=True, frozen=True)
class TenantVersionSimpleDTO:
    tenant_id: UUID
    status: str
    state: str
    version: int
    event: str
    editor_id: UUID | None
    created_at: datetime

    @classmethod
    def from_dto(cls, dto: "TenantVersionDTO") -> Self:
        return cls(
            dto.tenant.tenant_id.tenant_id,
            dto.tenant.status.value,
            dto.tenant.state.value,
            dto.tenant.version.version,
            dto.event.value,
            dto.editor_id.tenant_id if dto.editor_id is not None else None,
            dto.created_at,
        )


@dataclass(slots=True, frozen=True)
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
        event: "TenantEvent",
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
