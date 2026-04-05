from domain.transaction_category.errors import (
    TransactionCategoryInvalidDataError,
    TransactionCategoryPolicyError,
)
from domain.transaction_category.repository import TransactionCategoryRepository
from domain.transaction_category.value_objects import TransactionCategoryName
from domain.user.value_objects import UserID


class TransactionCategoryPolicyService:
    """Сервис проверки прав доступа для работы с категориями транзакции."""

    @staticmethod
    def is_owner(user_id: UserID, owner_id: UserID) -> None:
        """Является ли пользователь владельцем категории транзакции.

        Args:
            user_id (UserID): Идентификатор пользователя.
            owner_id (UserID): Идентификатор владельца категории.

        Raises:
            TransactionCategoryPolicyError: Пользователь не является владельцем.
        """
        if user_id != owner_id:
            raise TransactionCategoryPolicyError(
                msg="только владелец может работать с категорией транзакции",
                data={"user_id": user_id.user_id, "owner_id": owner_id.user_id},
            )


class TransactionCategoryNameUniquenessService:
    """Сервис проверки уникальности названия категории транзакции."""

    def __init__(self, repository: TransactionCategoryRepository) -> None:
        """
        Args:
            repository (TransactionCategoryRepository): Репозиторий категорий \
                транзакции.
        """
        self._repo = repository

    async def ensure_unique(
        self,
        owner_id: UserID,
        name: TransactionCategoryName,
    ) -> None:
        """Проверка уникальности названия категории транзакции.

        Args:
            owner_id (UserID): Идентификатор владельца категории.
            name (TransactionCategoryName): Проверяемое название категории.

        Raises:
            TransactionCategoryInvalidDataError: Название категории уже занято \
                не удаленной категорией.
        """
        categories = await self._repo.by_owner_id_and_name(owner_id, name)
        if any(not category.state.is_deleted() for category in categories):
            raise TransactionCategoryInvalidDataError(
                msg="название категории транзакции уже используется",
                data={"name": name.name},
            )
