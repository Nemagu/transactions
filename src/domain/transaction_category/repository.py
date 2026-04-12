from abc import ABC, abstractmethod

from domain.tenant import TenantID
from domain.transaction_category.entity import TransactionCategory
from domain.transaction_category.value_objects import TransactionCategoryName


class TransactionCategoryReadRepository(ABC):
    @abstractmethod
    async def by_owner_id_name(
        self,
        owner_id: TenantID,
        name: TransactionCategoryName,
    ) -> TransactionCategory | None: ...
