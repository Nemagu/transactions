from dataclasses import dataclass
from typing import Self
from uuid import UUID

from domain.transaction_category import TransactionCategory


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
