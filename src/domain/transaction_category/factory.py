from uuid import UUID

from src.domain.tenant import TenantID
from src.domain.transaction_category.entity import TransactionCategory
from src.domain.transaction_category.value_objects import (
    TransactionCategoryDescription,
    TransactionCategoryID,
    TransactionCategoryName,
)
from src.domain.value_objects import State, Version


class TransactionCategoryFactory:
    @staticmethod
    def new(
        category_id: UUID,
        owner_id: UUID,
        name: str,
        description: str,
    ) -> TransactionCategory:
        return TransactionCategory(
            category_id=TransactionCategoryID(category_id),
            owner_id=TenantID(owner_id),
            name=TransactionCategoryName(name),
            description=TransactionCategoryDescription(description),
            state=State.ACTIVE,
            version=Version(1),
        )

    @staticmethod
    def restore(
        category_id: UUID,
        owner_id: UUID,
        name: str,
        description: str,
        state: str,
        version: int,
    ) -> TransactionCategory:
        return TransactionCategory(
            category_id=TransactionCategoryID(category_id),
            owner_id=TenantID(owner_id),
            name=TransactionCategoryName(name),
            description=TransactionCategoryDescription(description),
            state=State.from_str(state),
            version=Version(version),
        )
