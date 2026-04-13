from abc import ABC, abstractmethod

from application.dto import LimitOffsetPaginator
from domain.personal_transaction import (
    MoneyAmount,
    PersonalTransaction,
    PersonalTransactionID,
    PersonalTransactionTime,
)
from domain.tenant import TenantID
from domain.transaction_category import TransactionCategoryID
from domain.value_objects import State, Version


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
        transaction_ids: list[PersonalTransactionID] | None,
        category_ids: list[TransactionCategoryID] | None,
        transaction_types: list[str] | None,
        from_money_amount: MoneyAmount | None,
        to_money_amount: MoneyAmount | None,
        from_transaction_time: PersonalTransactionTime | None,
        to_transaction_time: PersonalTransactionTime | None,
        states: list[State] | None,
    ) -> tuple[list[PersonalTransaction], int]: ...

    @abstractmethod
    async def save(self, transaction: PersonalTransaction) -> None: ...


class PersonalTransactionVersionRepository(ABC):
    @abstractmethod
    async def by_id_version(
        self, transaction_id: PersonalTransactionID, version: Version
    ) -> PersonalTransaction | None: ...

    @abstractmethod
    async def filters(
        self,
        owner_id: TenantID,
        paginator: LimitOffsetPaginator,
        transaction_ids: list[PersonalTransactionID] | None,
        category_ids: list[TransactionCategoryID] | None,
        transaction_types: list[str] | None,
        from_money_amount: MoneyAmount | None,
        to_money_amount: MoneyAmount | None,
        from_transaction_time: PersonalTransactionTime | None,
        to_transaction_time: PersonalTransactionTime | None,
        states: list[State] | None,
        from_version: Version | None,
        to_version: Version | None,
    ) -> tuple[list[PersonalTransaction], int]: ...

    @abstractmethod
    async def save(self, transaction: PersonalTransaction) -> None: ...
