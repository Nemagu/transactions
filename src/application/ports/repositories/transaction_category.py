from abc import ABC, abstractmethod
from datetime import datetime
from enum import StrEnum
from typing import Self

from application.dto import LimitOffsetPaginator
from application.errors import AppInternalError
from domain.tenant import Tenant, TenantID
from domain.transaction_category import (
    TransactionCategory,
    TransactionCategoryID,
    TransactionCategoryName,
)
from domain.transaction_category import (
    TransactionCategoryReadRepository as DomainTransactionCategoryReadRepository,
)
from domain.value_objects import State, Version


class TransactionCategoryEvent(StrEnum):
    CREATED = "created"
    UPDATED = "updated"
    RESTORED = "restored"
    DELETED = "deleted"

    @classmethod
    def from_str(cls, value: str) -> Self:
        lower_value = value.lower()
        if lower_value in cls._value2member_map_:
            return cls(lower_value)
        raise AppInternalError(
            msg="не удалось найти событие категории транзакций по предоставленной строке",
            action="получение события категории транзакций",
            data={"event": value},
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
    ) -> (
        tuple[TransactionCategory, TransactionCategoryEvent, TenantID | None, datetime]
        | None
    ): ...

    @abstractmethod
    async def filters(
        self,
        owner_id: TenantID,
        paginator: LimitOffsetPaginator,
        names: list[TransactionCategoryName] | None,
        states: list[State] | None,
        from_version: Version | None,
        to_version: Version | None,
    ) -> tuple[
        list[
            tuple[
                TransactionCategory, TransactionCategoryEvent, TenantID | None, datetime
            ]
        ],
        int,
    ]: ...

    @abstractmethod
    async def save(
        self,
        category: TransactionCategory,
        event: TransactionCategoryEvent,
        editor: Tenant | None,
    ) -> None: ...
