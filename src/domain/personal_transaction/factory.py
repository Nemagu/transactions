from datetime import datetime
from decimal import Decimal
from uuid import UUID

from domain.personal_transaction.entity import PersonalTransaction
from domain.personal_transaction.value_objects import (
    Currency,
    MoneyAmount,
    PersonalTransactionDescription,
    PersonalTransactionID,
    PersonalTransactionName,
    PersonalTransactionTime,
    PersonalTransactionType,
)
from domain.tenant import TenantID
from domain.transaction_category import TransactionCategoryID
from domain.value_objects import State, Version


class PersonalTransactionFactory:
    @staticmethod
    def new(
        transaction_id: UUID,
        category_ids: set[UUID],
        owner_id: UUID,
        name: str,
        description: str,
        transaction_type: str,
        amount: Decimal,
        currency: str,
        transaction_time: datetime,
    ) -> PersonalTransaction:
        return PersonalTransaction(
            transaction_id=PersonalTransactionID(transaction_id),
            category_ids={
                TransactionCategoryID(category_id) for category_id in category_ids
            },
            owner_id=TenantID(owner_id),
            name=PersonalTransactionName(name),
            description=PersonalTransactionDescription(description),
            transaction_type=PersonalTransactionType.from_str(transaction_type),
            money_amount=MoneyAmount(
                amount=amount, currency=Currency.from_str(currency)
            ),
            transaction_time=PersonalTransactionTime(transaction_time),
            state=State.ACTIVE,
            version=Version(1),
        )

    @staticmethod
    def restore(
        transaction_id: UUID,
        owner_id: UUID,
        name: str,
        description: str,
        category_ids: set[UUID],
        transaction_type: str,
        amount: Decimal,
        currency: str,
        transaction_time: datetime,
        state: str,
        version: int,
    ) -> PersonalTransaction:
        return PersonalTransaction(
            transaction_id=PersonalTransactionID(transaction_id),
            category_ids={
                TransactionCategoryID(category_id) for category_id in category_ids
            },
            owner_id=TenantID(owner_id),
            name=PersonalTransactionName(name),
            description=PersonalTransactionDescription(description),
            transaction_type=PersonalTransactionType.from_str(transaction_type),
            money_amount=MoneyAmount(
                amount=amount, currency=Currency.from_str(currency)
            ),
            transaction_time=PersonalTransactionTime(transaction_time),
            state=State.from_str(state),
            version=Version(version),
        )
