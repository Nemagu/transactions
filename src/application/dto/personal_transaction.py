from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Self
from uuid import UUID

from application.dto.transaction_category import (
    TransactionCategorySimpleDTO,
)
from domain.personal_transaction import PersonalTransaction
from domain.tenant import TenantID
from domain.transaction_category import TransactionCategory

if TYPE_CHECKING:
    from application.ports.repositories.personal_transaction import (
        PersonalTransactionEvent,
    )


@dataclass(slots=True)
class MoneyAmountDTO:
    amount: Decimal
    currency: str


@dataclass(slots=True)
class PersonalTransactionSimpleDTO:
    transaction_id: UUID
    category_ids: list[UUID]
    owner_id: UUID
    name: str
    description: str
    transaction_type: str
    money_amount: MoneyAmountDTO
    transaction_time: datetime
    state: str
    version: int

    @classmethod
    def from_domain(cls, transaction: PersonalTransaction) -> Self:
        money_amount = MoneyAmountDTO(
            transaction.money_amount.amount, transaction.money_amount.currency.value
        )
        return cls(
            transaction.transaction_id.transaction_id,
            [category_id.category_id for category_id in transaction.category_ids],
            transaction.owner_id.tenant_id,
            transaction.name.name,
            transaction.description.description,
            transaction.transaction_type.value,
            money_amount,
            transaction.transaction_time.transaction_time,
            transaction.state.value,
            transaction.version.version,
        )


@dataclass(slots=True)
class PersonalTransactionDetailDTO:
    transaction_id: UUID
    categories: list[TransactionCategorySimpleDTO]
    owner_id: UUID
    name: str
    description: str
    transaction_type: str
    money_amount: MoneyAmountDTO
    transaction_time: datetime
    state: str
    version: int

    @classmethod
    def from_domain(
        cls, transaction: PersonalTransaction, categories: list[TransactionCategory]
    ) -> Self:
        money_amount = MoneyAmountDTO(
            transaction.money_amount.amount, transaction.money_amount.currency.value
        )
        return cls(
            transaction.transaction_id.transaction_id,
            [
                TransactionCategorySimpleDTO.from_domain(category)
                for category in categories
            ],
            transaction.owner_id.tenant_id,
            transaction.name.name,
            transaction.description.description,
            transaction.transaction_type.value,
            money_amount,
            transaction.transaction_time.transaction_time,
            transaction.state.value,
            transaction.version.version,
        )


@dataclass(slots=True)
class PersonalTransactionVersionSimpleDTO:
    transaction_id: UUID
    category_ids: list[UUID]
    owner_id: UUID
    name: str
    description: str
    transaction_type: str
    money_amount: MoneyAmountDTO
    transaction_time: datetime
    state: str
    version: int
    event: str
    editor_id: UUID | None
    created_at: datetime

    @classmethod
    def from_domain(
        cls,
        transaction: PersonalTransaction,
        event: "PersonalTransactionEvent",
        editor_id: TenantID | None,
        created_at: datetime,
    ) -> Self:
        money_amount = MoneyAmountDTO(
            transaction.money_amount.amount, transaction.money_amount.currency.value
        )
        return cls(
            transaction.transaction_id.transaction_id,
            [category_id.category_id for category_id in transaction.category_ids],
            transaction.owner_id.tenant_id,
            transaction.name.name,
            transaction.description.description,
            transaction.transaction_type.value,
            money_amount,
            transaction.transaction_time.transaction_time,
            transaction.state.value,
            transaction.version.version,
            event.value,
            editor_id.tenant_id if editor_id is not None else None,
            created_at,
        )


@dataclass(slots=True)
class PersonalTransactionVersionDetailDTO:
    transaction_id: UUID
    categories: list[TransactionCategorySimpleDTO]
    owner_id: UUID
    name: str
    description: str
    transaction_type: str
    money_amount: MoneyAmountDTO
    transaction_time: datetime
    state: str
    version: int
    event: str
    editor_id: UUID | None
    created_at: datetime

    @classmethod
    def from_domain(
        cls,
        transaction: PersonalTransaction,
        categories: list[TransactionCategory],
        event: "PersonalTransactionEvent",
        editor_id: TenantID | None,
        created_at: datetime,
    ) -> Self:
        money_amount = MoneyAmountDTO(
            transaction.money_amount.amount, transaction.money_amount.currency.value
        )
        return cls(
            transaction.transaction_id.transaction_id,
            [
                TransactionCategorySimpleDTO.from_domain(category)
                for category in categories
            ],
            transaction.owner_id.tenant_id,
            transaction.name.name,
            transaction.description.description,
            transaction.transaction_type.value,
            money_amount,
            transaction.transaction_time.transaction_time,
            transaction.state.value,
            transaction.version.version,
            event.value,
            editor_id.tenant_id if editor_id is not None else None,
            created_at,
        )
