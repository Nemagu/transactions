"""Контракты доступа к категориям транзакций."""

from abc import ABC, abstractmethod

from src.domain.transaction_category.entity import TransactionCategory
from src.domain.transaction_category.value_objects import TransactionCategoryName
from src.domain.user.value_objects import UserID


class TransactionCategoryRepository(ABC):
    """Абстракция хранилища категорий транзакций."""

    @abstractmethod
    async def by_owner_id_name(
        self,
        owner_id: UserID,
        name: TransactionCategoryName,
    ) -> TransactionCategory | None:
        """
        Args:
            owner_id (UserID): Идентификатор владельца категории.
            name (TransactionCategoryName): Название категории.

        Returns:
            TransactionCategory | None: Найденная категория или `None`, если \
                запись отсутствует.
        """
        ...
