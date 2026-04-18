from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel

from application.dto import (
    TenantSimpleDTO,
    TenantVersionDetailDTO,
    TenantVersionSimpleDTO,
)

__all__ = [
    "TenantSimpleResponse",
    "TenantVersionDetailResponse",
    "TenantVersionSimpleResponse",
]


class TenantSimpleResponse(BaseModel):
    tenant_id: UUID
    status: str
    state: str
    version: int

    @classmethod
    def from_dto(cls, dto: TenantSimpleDTO) -> Self:
        return cls(
            tenant_id=dto.tenant_id,
            status=dto.status,
            state=dto.state,
            version=dto.version,
        )


class TenantVersionSimpleResponse(BaseModel):
    tenant_id: UUID
    status: str
    state: str
    version: int
    event: str
    editor_id: UUID | None
    created_at: datetime

    @classmethod
    def from_dto(cls, dto: TenantVersionSimpleDTO) -> Self:
        return cls(
            tenant_id=dto.tenant_id,
            status=dto.status,
            state=dto.state,
            version=dto.version,
            event=dto.event,
            editor_id=dto.editor_id,
            created_at=dto.created_at,
        )


class TenantVersionDetailResponse(BaseModel):
    tenant_id: UUID
    status: str
    state: str
    version: int
    event: str
    editor: TenantSimpleResponse | None
    created_at: datetime

    @classmethod
    def from_dto(cls, dto: TenantVersionDetailDTO) -> Self:
        return cls(
            tenant_id=dto.tenant_id,
            status=dto.status,
            state=dto.state,
            version=dto.version,
            event=dto.event,
            editor=TenantSimpleResponse.from_dto(dto.editor)
            if dto.editor is not None
            else None,
            created_at=dto.created_at,
        )
