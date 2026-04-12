from abc import ABC, abstractmethod

from src.domain.tenant import TenantID
from src.domain.transaction_category.entity import TransactionCategory
from src.domain.transaction_category.value_objects import TransactionCategoryName


class TransactionCategoryRepository(ABC):
    @abstractmethod
    async def by_owner_id_name(
        self,
        owner_id: TenantID,
        name: TransactionCategoryName,
    ) -> TransactionCategory | None: ...
