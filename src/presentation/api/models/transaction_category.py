from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel

from application.commands.public.transaction_category import (
    TransactionCategoryCreationCommand,
    TransactionCategoryUpdateCommand,
)
from application.dto import (
    TransactionCategorySimpleDTO,
    TransactionCategoryVersionSimpleDTO,
)

__all__ = [
    "TransactionCategoryCreationRequest",
    "TransactionCategorySimpleResponse",
    "TransactionCategoryUpdateRequest",
    "TransactionCategoryVersionSimpleResponse",
]


class TransactionCategoryCreationRequest(BaseModel):
    name: str
    description: str = ""

    def to_command(self, user_id: UUID) -> TransactionCategoryCreationCommand:
        return TransactionCategoryCreationCommand(
            user_id=user_id,
            name=self.name,
            description=self.description,
        )


class TransactionCategoryUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None

    def to_command(
        self, user_id: UUID, category_id: UUID
    ) -> TransactionCategoryUpdateCommand:
        return TransactionCategoryUpdateCommand(
            user_id=user_id,
            category_id=category_id,
            name=self.name,
            description=self.description,
        )


class TransactionCategorySimpleResponse(BaseModel):
    category_id: UUID
    owner_id: UUID
    name: str
    description: str
    state: str
    version: int

    @classmethod
    def from_dto(cls, dto: TransactionCategorySimpleDTO) -> Self:
        return cls(
            category_id=dto.category_id,
            owner_id=dto.owner_id,
            name=dto.name,
            description=dto.description,
            state=dto.state,
            version=dto.version,
        )


class TransactionCategoryVersionSimpleResponse(BaseModel):
    category_id: UUID
    owner_id: UUID
    name: str
    description: str
    state: str
    version: int
    event: str
    editor_id: UUID | None
    created_at: datetime

    @classmethod
    def from_dto(cls, dto: TransactionCategoryVersionSimpleDTO) -> Self:
        return cls(
            category_id=dto.category_id,
            owner_id=dto.owner_id,
            name=dto.name,
            description=dto.description,
            state=dto.state,
            version=dto.version,
            event=dto.event,
            editor_id=dto.editor_id,
            created_at=dto.created_at,
        )
