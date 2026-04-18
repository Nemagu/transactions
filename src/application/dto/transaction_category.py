from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Self
from uuid import UUID

from domain.tenant import TenantID
from domain.transaction_category import TransactionCategory

if TYPE_CHECKING:
    from application.ports.repositories.transaction_category import (
        TransactionCategoryEvent,
    )


@dataclass(slots=True)
class TransactionCategorySimpleDTO:
    category_id: UUID
    owner_id: UUID
    name: str
    description: str
    state: str
    version: int

    @classmethod
    def from_domain(cls, category: TransactionCategory) -> Self:
        return cls(
            category.category_id.category_id,
            category.owner_id.tenant_id,
            category.name.name,
            category.description.description,
            category.state.value,
            category.version.version,
        )


@dataclass(slots=True)
class TransactionCategoryVersionSimpleDTO:
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
    def from_domain(
        cls,
        category: TransactionCategory,
        event: "TransactionCategoryEvent",
        editor_id: TenantID | None,
        created_at: datetime,
    ) -> Self:
        return cls(
            category.category_id.category_id,
            category.owner_id.tenant_id,
            category.name.name,
            category.description.description,
            category.state.value,
            category.version.version,
            event.value,
            editor_id.tenant_id if editor_id is not None else None,
            created_at,
        )
