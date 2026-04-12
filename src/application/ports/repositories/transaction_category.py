from abc import ABC, abstractmethod

from domain.transaction_category import TransactionCategory
from domain.transaction_category import (
    TransactionCategoryReadRepository as DomainTransactionCategoryReadRepository,
)


class TransactionCategoryReadRepository(DomainTransactionCategoryReadRepository):
    @abstractmethod
    async def save(self, category: TransactionCategory) -> None: ...


class TransactionCategoryVersionRepository(ABC):
    @abstractmethod
    async def save(self, category: TransactionCategory) -> None: ...
