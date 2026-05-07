from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

from pydantic import BaseModel

from application.commands.public.personal_transaction import (
    CreatePersonalTransactionCommand,
    UpdatePersonalTransactionCommand,
)
from application.dto.personal_transaction import (
    MoneyAmountDTO,
    PersonalTransactionDetailDTO,
    PersonalTransactionSimpleDTO,
    PersonalTransactionVersionDetailDTO,
    PersonalTransactionVersionSimpleDTO,
)
from presentation.api.models.transaction_category import (
    TransactionCategorySimpleResponse,
)

__all__ = [
    "MoneyAmountRequest",
    "MoneyAmountResponse",
    "PersonalTransactionCreationRequest",
    "PersonalTransactionDetailResponse",
    "PersonalTransactionSimpleResponse",
    "PersonalTransactionUpdateRequest",
    "PersonalTransactionVersionDetailResponse",
    "PersonalTransactionVersionSimpleResponse",
]


class MoneyAmountRequest(BaseModel):
    amount: Decimal
    currency: str

    def to_command(self) -> MoneyAmountDTO:
        return MoneyAmountDTO(
            amount=self.amount,
            currency=self.currency,
        )


class PersonalTransactionCreationRequest(BaseModel):
    category_ids: set[UUID]
    transaction_type: str
    money_amount: MoneyAmountRequest
    transaction_time: datetime
    name: str = ""
    description: str = ""

    def to_command(self, user_id: UUID) -> CreatePersonalTransactionCommand:
        return CreatePersonalTransactionCommand(
            user_id=user_id,
            category_ids=list(self.category_ids),
            transaction_type=self.transaction_type,
            money_amount=self.money_amount.to_command(),
            transaction_time=self.transaction_time,
            name=self.name,
            description=self.description,
        )


class PersonalTransactionUpdateRequest(BaseModel):
    category_ids: set[UUID] | None = None
    add_category_ids: set[UUID] | None = None
    remove_category_ids: set[UUID] | None = None
    transaction_type: str | None = None
    money_amount: MoneyAmountRequest | None = None
    transaction_time: datetime | None = None
    name: str | None = None
    description: str | None = None

    def to_command(
        self, user_id: UUID, transaction_id: UUID
    ) -> UpdatePersonalTransactionCommand:
        return UpdatePersonalTransactionCommand(
            user_id=user_id,
            transaction_id=transaction_id,
            category_ids=list(self.category_ids)
            if self.category_ids is not None
            else None,
            add_category_ids=list(self.add_category_ids)
            if self.add_category_ids is not None
            else None,
            remove_category_ids=list(self.remove_category_ids)
            if self.remove_category_ids is not None
            else None,
            transaction_type=self.transaction_type,
            money_amount=self.money_amount.to_command()
            if self.money_amount is not None
            else None,
            transaction_time=self.transaction_time,
            name=self.name,
            description=self.description,
        )


class MoneyAmountResponse(BaseModel):
    amount: Decimal
    currency: str

    @classmethod
    def from_dto(cls, dto: MoneyAmountDTO) -> Self:
        return cls(
            amount=dto.amount,
            currency=dto.currency,
        )


class PersonalTransactionSimpleResponse(BaseModel):
    transaction_id: UUID
    category_ids: list[UUID]
    owner_id: UUID
    name: str
    description: str
    transaction_type: str
    money_amount: MoneyAmountResponse
    transaction_time: datetime
    state: str
    version: int

    @classmethod
    def from_dto(cls, dto: PersonalTransactionSimpleDTO) -> Self:
        return cls(
            transaction_id=dto.transaction_id,
            category_ids=dto.category_ids,
            owner_id=dto.owner_id,
            name=dto.name,
            description=dto.description,
            transaction_type=dto.transaction_type,
            money_amount=MoneyAmountResponse.from_dto(dto.money_amount),
            transaction_time=dto.transaction_time,
            state=dto.state,
            version=dto.version,
        )


class PersonalTransactionDetailResponse(BaseModel):
    transaction_id: UUID
    categories: list[TransactionCategorySimpleResponse]
    owner_id: UUID
    name: str
    description: str
    transaction_type: str
    money_amount: MoneyAmountResponse
    transaction_time: datetime
    state: str
    version: int

    @classmethod
    def from_dto(cls, dto: PersonalTransactionDetailDTO) -> Self:
        return cls(
            transaction_id=dto.transaction_id,
            categories=[TransactionCategorySimpleResponse.from_dto(d) for d in dto.categories],
            owner_id=dto.owner_id,
            name=dto.name,
            description=dto.description,
            transaction_type=dto.transaction_type,
            money_amount=MoneyAmountResponse.from_dto(dto.money_amount),
            transaction_time=dto.transaction_time,
            state=dto.state,
            version=dto.version,
        )


class PersonalTransactionVersionSimpleResponse(BaseModel):
    transaction_id: UUID
    category_ids: list[UUID]
    owner_id: UUID
    name: str
    description: str
    transaction_type: str
    money_amount: MoneyAmountResponse
    transaction_time: datetime
    state: str
    version: int
    event: str
    editor_id: UUID | None
    created_at: datetime

    @classmethod
    def from_dto(cls, dto: PersonalTransactionVersionSimpleDTO) -> Self:
        return cls(
            transaction_id=dto.transaction_id,
            category_ids=dto.category_ids,
            owner_id=dto.owner_id,
            name=dto.name,
            description=dto.description,
            transaction_type=dto.transaction_type,
            money_amount=MoneyAmountResponse.from_dto(dto.money_amount),
            transaction_time=dto.transaction_time,
            state=dto.state,
            version=dto.version,
            event=dto.event,
            editor_id=dto.editor_id,
            created_at=dto.created_at,
        )


class PersonalTransactionVersionDetailResponse(BaseModel):
    transaction_id: UUID
    categories: list[TransactionCategorySimpleResponse]
    owner_id: UUID
    name: str
    description: str
    transaction_type: str
    money_amount: MoneyAmountResponse
    transaction_time: datetime
    state: str
    version: int
    event: str
    editor_id: UUID | None
    created_at: datetime

    @classmethod
    def from_dto(cls, dto: PersonalTransactionVersionDetailDTO) -> Self:
        return cls(
            transaction_id=dto.transaction_id,
            categories=[TransactionCategorySimpleResponse.from_dto(d) for d in dto.categories],
            owner_id=dto.owner_id,
            name=dto.name,
            description=dto.description,
            transaction_type=dto.transaction_type,
            money_amount=MoneyAmountResponse.from_dto(dto.money_amount),
            transaction_time=dto.transaction_time,
            state=dto.state,
            version=dto.version,
            event=dto.event,
            editor_id=dto.editor_id,
            created_at=dto.created_at,
        )
