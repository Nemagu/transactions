from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

from application.dto.transaction_category import (
    TransactionCategorySimpleDTO,
)
from domain.personal_transaction import PersonalTransaction


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
    category: list[TransactionCategorySimpleDTO]
    owner_id: UUID
    name: str
    description: str
    transaction_type: str
    money_amount: MoneyAmountDTO
    transaction_time: datetime
    state: str
    version: int


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


@dataclass(slots=True)
class PersonalTransactionVersionDetailDTO:
    transaction_id: UUID
    category: list[TransactionCategorySimpleDTO]
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
