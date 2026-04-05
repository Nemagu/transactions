from abc import ABC, abstractmethod

from domain.transaction_category.entity import TransactionCategory
from domain.transaction_category.value_objects import TransactionCategoryName
from domain.user.value_objects import UserID


class TransactionCategoryRepository(ABC):
    """Доменный интерфейс для работы с хранилищем категорий транзакции."""

    @abstractmethod
    async def by_owner_id_and_name(
        self,
        owner_id: UserID,
        name: TransactionCategoryName,
    ) -> list[TransactionCategory]: ...
