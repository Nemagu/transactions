from uuid import UUID

from domain.transaction_category.entity import TransactionCategory
from domain.transaction_category.value_objects import (
    TransactionCategoryDescription,
    TransactionCategoryID,
    TransactionCategoryName,
    TransactionCategoryState,
)
from domain.user.value_objects import UserID
from domain.value_objects import Version


class TransactionCategoryFactory:
    """Фабрика создания и восстановления категории транзакции."""

    @staticmethod
    def new(
        category_id: UUID,
        owner_id: UUID,
        name: str,
        description: str = "",
    ) -> TransactionCategory:
        """Создание новой категории транзакции.

        Args:
            category_id (UUID): Идентификатор для новой категории.
            owner_id (UUID): Идентификатор владельца категории.
            name (str): Название новой категории.
            description (str, optional): Описание новой категории. По умолчанию \
                пустая строка.

        Raises:
            TransactionCategoryError: Ошибки при создании объектов значений из \
                переданных данных.

        Returns:
            TransactionCategory: Новая категория транзакции.
        """
        return TransactionCategory(
            category_id=TransactionCategoryID(category_id),
            owner_id=UserID(owner_id),
            name=TransactionCategoryName(name),
            description=TransactionCategoryDescription(description),
            state=TransactionCategoryState.ACTIVE,
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
        """Восстановление категории транзакции.

        Args:
            category_id (UUID): Идентификатор категории.
            owner_id (UUID): Идентификатор владельца категории.
            name (str): Название категории.
            description (str): Описание категории.
            state (str): Состояние категории.
            version (int): Версия категории.

        Raises:
            TransactionCategoryError: Ошибки при создании объектов значений из \
                переданных данных.

        Returns:
            TransactionCategory: Восстановленная категория транзакции.
        """
        return TransactionCategory(
            category_id=TransactionCategoryID(category_id),
            owner_id=UserID(owner_id),
            name=TransactionCategoryName(name),
            description=TransactionCategoryDescription(description),
            state=TransactionCategoryState.from_str(state),
            version=Version(version),
        )
