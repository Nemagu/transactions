from abc import ABC, abstractmethod

from domain.transaction_category import TransactionCategory, TransactionCategoryID
from domain.transaction_category import (
    TransactionCategoryReadRepository as DomainTransactionCategoryReadRepository,
)


class TransactionCategoryReadRepository(DomainTransactionCategoryReadRepository):
    @abstractmethod
    async def next_id(self) -> TransactionCategoryID: ...

    @abstractmethod
    async def by_id(
        self, category_id: TransactionCategoryID
    ) -> TransactionCategory | None: ...

    @abstractmethod
    async def by_ids(
        self, category_ids: set[TransactionCategoryID]
    ) -> set[TransactionCategory]: ...

    @abstractmethod
    async def save(self, category: TransactionCategory) -> None: ...


class TransactionCategoryVersionRepository(ABC):
    @abstractmethod
    async def save(self, category: TransactionCategory) -> None: ...
