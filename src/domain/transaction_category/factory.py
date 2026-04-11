"""Фабрика создания и восстановления категорий транзакций."""

from uuid import UUID

from src.domain.transaction_category.entity import TransactionCategory
from src.domain.transaction_category.value_objects import (
    TransactionCategoryDescription,
    TransactionCategoryID,
    TransactionCategoryName,
)
from src.domain.user.value_objects import UserID
from src.domain.value_objects import State, Version


class TransactionCategoryFactory:
    """Фабрика для работы с агрегатом категории транзакций."""

    @staticmethod
    def new(
        category_id: UUID,
        owner_id: UUID,
        name: str,
        description: str,
    ) -> TransactionCategory:
        """
        Args:
            category_id (UUID): Идентификатор категории.
            owner_id (UUID): Идентификатор владельца категории.
            name (str): Название категории.
            description (str): Описание категории.

        Returns:
            TransactionCategory: Новая активная категория транзакций.
        """
        return TransactionCategory(
            category_id=TransactionCategoryID(category_id),
            owner_id=UserID(owner_id),
            name=TransactionCategoryName(name),
            description=TransactionCategoryDescription(description),
            state=State.ACTIVE,
            version=Version(1),
        )

    @staticmethod
    def restore(
        category_id: UUID,
        owner_id: UUID,
        name: str,
        description: str,
        state: str,
        version: int,
    ) -> TransactionCategory:
        """
        Args:
            category_id (UUID): Идентификатор категории.
            owner_id (UUID): Идентификатор владельца категории.
            name (str): Название категории.
            description (str): Описание категории.
            state (str): Состояние категории в строковом виде.
            version (int): Версия агрегата.

        Returns:
            TransactionCategory: Восстановленная категория транзакций.
        """
        return TransactionCategory(
            category_id=TransactionCategoryID(category_id),
            owner_id=UserID(owner_id),
            name=TransactionCategoryName(name),
            description=TransactionCategoryDescription(description),
            state=State.from_str(state),
            version=Version(version),
        )
