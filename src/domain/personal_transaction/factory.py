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
    PersonalTransactionState,
    PersonalTransactionTime,
    PersonalTransactionType,
)
from domain.transaction_category.value_objects import TransactionCategoryID
from domain.user.value_objects import UserID
from domain.value_objects import Version


class PersonalTransactionFactory:
    """Фабрика создания и восстановления персональной транзакции."""

    @staticmethod
    def new(
        transaction_id: UUID,
        owner_id: UUID,
        name: str,
        category_ids: set[UUID],
        transaction_type: str,
        amount: Decimal,
        currency: str,
        transaction_time: datetime,
        description: str = "",
    ) -> PersonalTransaction:
        """Создание новой персональной транзакции.

        Args:
            transaction_id (UUID): Идентификатор для новой транзакции.
            owner_id (UUID): Идентификатор владельца транзакции.
            name (str): Название новой транзакции.
            category_ids (set[UUID]): Идентификаторы категорий транзакции.
            transaction_type (str): Тип новой транзакции.
            amount (Decimal): Количество средств новой транзакции.
            currency (str): Валюта новой транзакции.
            transaction_time (datetime): Время новой транзакции.
            description (str, optional): Описание новой транзакции. По умолчанию \
                пустая строка.

        Raises:
            PersonalTransactionError: Ошибки при создании объектов значений из \
                переданных данных.

        Returns:
            PersonalTransaction: Новая персональная транзакция.
        """
        return PersonalTransaction(
            transaction_id=PersonalTransactionID(transaction_id),
            owner_id=UserID(owner_id),
            name=PersonalTransactionName(name),
            description=PersonalTransactionDescription(description),
            category_ids={
                TransactionCategoryID(category_id) for category_id in category_ids
            },
            transaction_type=PersonalTransactionType.from_str(transaction_type),
            money_amount=MoneyAmount(amount=amount, currency=Currency.from_str(currency)),
            transaction_time=PersonalTransactionTime(transaction_time),
            state=PersonalTransactionState.ACTIVE,
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
        """Восстановление персональной транзакции.

        Args:
            transaction_id (UUID): Идентификатор транзакции.
            owner_id (UUID): Идентификатор владельца транзакции.
            name (str): Название транзакции.
            description (str): Описание транзакции.
            category_ids (set[UUID]): Идентификаторы категорий транзакции.
            transaction_type (str): Тип транзакции.
            amount (Decimal): Количество средств транзакции.
            currency (str): Валюта транзакции.
            transaction_time (datetime): Время транзакции.
            state (str): Состояние транзакции.
            version (int): Версия транзакции.

        Raises:
            PersonalTransactionError: Ошибки при создании объектов значений из \
                переданных данных.

        Returns:
            PersonalTransaction: Восстановленная персональная транзакция.
        """
        return PersonalTransaction(
            transaction_id=PersonalTransactionID(transaction_id),
            owner_id=UserID(owner_id),
            name=PersonalTransactionName(name),
            description=PersonalTransactionDescription(description),
            category_ids={
                TransactionCategoryID(category_id) for category_id in category_ids
            },
            transaction_type=PersonalTransactionType.from_str(transaction_type),
            money_amount=MoneyAmount(amount=amount, currency=Currency.from_str(currency)),
            transaction_time=PersonalTransactionTime(transaction_time),
            state=PersonalTransactionState.from_str(state),
            version=Version(version),
        )
