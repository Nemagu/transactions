from abc import ABC, abstractmethod
from datetime import datetime
from enum import StrEnum
from typing import Self

from application.dto.paginators import LimitOffsetPaginator
from application.errors import AppInternalError
from domain.personal_transaction import (
    MoneyAmount,
    PersonalTransaction,
    PersonalTransactionID,
    PersonalTransactionTime,
    PersonalTransactionType,
)
from domain.tenant import Tenant, TenantID
from domain.transaction_category import TransactionCategoryID
from domain.value_objects import State, Version


class PersonalTransactionEvent(StrEnum):
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
            msg="не удалось найти событие персональной транзакции по предоставленной строке",
            action="получение события персональной транзакции",
            data={"event": value},
        )


class PersonalTransactionReadRepository(ABC):
    @abstractmethod
    async def next_id(self) -> PersonalTransactionID: ...

    @abstractmethod
    async def by_id(
        self, transaction_id: PersonalTransactionID
    ) -> PersonalTransaction | None: ...

    @abstractmethod
    async def filters(
        self,
        owner_id: TenantID,
        paginator: LimitOffsetPaginator,
        transaction_ids: list[PersonalTransactionID] | None = None,
        category_ids: list[TransactionCategoryID] | None = None,
        transaction_types: list[PersonalTransactionType] | None = None,
        from_money_amount: MoneyAmount | None = None,
        to_money_amount: MoneyAmount | None = None,
        from_transaction_time: PersonalTransactionTime | None = None,
        to_transaction_time: PersonalTransactionTime | None = None,
        states: list[State] | None = None,
    ) -> tuple[list[PersonalTransaction], int]: ...

    @abstractmethod
    async def save(self, transaction: PersonalTransaction) -> None: ...


class PersonalTransactionVersionRepository(ABC):
    @abstractmethod
    async def by_id_version(
        self, transaction_id: PersonalTransactionID, version: Version
    ) -> (
        tuple[PersonalTransaction, PersonalTransactionEvent, TenantID | None, datetime]
        | None
    ): ...

    @abstractmethod
    async def filters(
        self,
        owner_id: TenantID,
        paginator: LimitOffsetPaginator,
        transaction_id: PersonalTransactionID,
        category_ids: list[TransactionCategoryID] | None = None,
        transaction_types: list[PersonalTransactionType] | None = None,
        from_money_amount: MoneyAmount | None = None,
        to_money_amount: MoneyAmount | None = None,
        from_transaction_time: PersonalTransactionTime | None = None,
        to_transaction_time: PersonalTransactionTime | None = None,
        states: list[State] | None = None,
        from_version: Version | None = None,
        to_version: Version | None = None,
    ) -> tuple[
        list[
            tuple[
                PersonalTransaction, PersonalTransactionEvent, TenantID | None, datetime
            ]
        ],
        int,
    ]: ...

    @abstractmethod
    async def save(
        self,
        transaction: PersonalTransaction,
        event: PersonalTransactionEvent,
        editor: Tenant | None,
    ) -> None: ...
