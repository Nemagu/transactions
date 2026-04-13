from abc import ABC, abstractmethod

from application.dto import LimitOffsetPaginator
from domain.tenant import TenantID
from domain.transaction_category import (
    TransactionCategory,
    TransactionCategoryID,
    TransactionCategoryName,
)
from domain.transaction_category import (
    TransactionCategoryReadRepository as DomainTransactionCategoryReadRepository,
)
from domain.value_objects import State, Version


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
    async def filters(
        self,
        owner_id: TenantID,
        paginator: LimitOffsetPaginator,
        names: list[TransactionCategoryName] | None,
        states: list[State] | None,
    ) -> tuple[list[TransactionCategory], int]: ...

    @abstractmethod
    async def save(self, category: TransactionCategory) -> None: ...


class TransactionCategoryVersionRepository(ABC):
    @abstractmethod
    async def by_id_version(
        self, category_id: TransactionCategoryID, version: Version
    ) -> TransactionCategory | None: ...

    @abstractmethod
    async def filters(
        self,
        owner_id: TenantID,
        paginator: LimitOffsetPaginator,
        names: list[TransactionCategoryName] | None,
        states: list[State] | None,
        from_version: Version | None,
        to_version: Version | None,
    ) -> tuple[list[TransactionCategory], int]: ...

    @abstractmethod
    async def save(self, category: TransactionCategory) -> None: ...
