"""Фабрика создания и восстановления персональных транзакций."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.domain.personal_transaction.entity import PersonalTransaction
from src.domain.personal_transaction.value_objects import (
    Currency,
    MoneyAmount,
    PersonalTransactionDescription,
    PersonalTransactionID,
    PersonalTransactionName,
    PersonalTransactionTime,
    PersonalTransactionType,
)
from src.domain.transaction_category import TransactionCategory
from src.domain.user import UserID
from src.domain.value_objects import State, Version


class PersonalTransactionFactory:
    """Фабрика для работы с агрегатом персональной транзакции."""

    @staticmethod
    def new(
        transaction_id: UUID,
        categories: set[TransactionCategory],
        owner_id: UUID,
        name: str,
        description: str,
        transaction_type: str,
        amount: Decimal,
        currency: str,
        transaction_time: datetime,
    ) -> PersonalTransaction:
        """
        Args:
            transaction_id (UUID): Идентификатор транзакции.
            categories (set[TransactionCategory]): Категории транзакции.
            owner_id (UUID): Идентификатор владельца транзакции.
            name (str): Название транзакции.
            description (str): Описание транзакции.
            transaction_type (str): Тип транзакции в строковом виде.
            amount (Decimal): Денежная сумма транзакции.
            currency (str): Валюта транзакции в строковом виде.
            transaction_time (datetime): Время совершения транзакции.

        Returns:
            PersonalTransaction: Новая активная персональная транзакция.
        """
        return PersonalTransaction(
            transaction_id=PersonalTransactionID(transaction_id),
            categories=categories,
            owner_id=UserID(owner_id),
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
        categories: set[TransactionCategory],
        transaction_type: str,
        amount: Decimal,
        currency: str,
        transaction_time: datetime,
        state: str,
        version: int,
    ) -> PersonalTransaction:
        """
        Args:
            transaction_id (UUID): Идентификатор транзакции.
            owner_id (UUID): Идентификатор владельца транзакции.
            name (str): Название транзакции.
            description (str): Описание транзакции.
            categories (set[TransactionCategory]): Категории транзакции.
            transaction_type (str): Тип транзакции в строковом виде.
            amount (Decimal): Денежная сумма транзакции.
            currency (str): Валюта транзакции в строковом виде.
            transaction_time (datetime): Время совершения транзакции.
            state (str): Состояние транзакции в строковом виде.
            version (int): Версия агрегата.

        Returns:
            PersonalTransaction: Восстановленная персональная транзакция.
        """
        return PersonalTransaction(
            transaction_id=PersonalTransactionID(transaction_id),
            categories=categories,
            owner_id=UserID(owner_id),
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
