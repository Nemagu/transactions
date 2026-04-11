"""Доменные сервисы, связанные с категориями транзакций."""

from src.domain.errors import EntityInvalidDataError, EntityPolicyError
from src.domain.transaction_category.entity import TransactionCategory
from src.domain.transaction_category.repository import TransactionCategoryRepository
from src.domain.transaction_category.value_objects import TransactionCategoryName
from src.domain.user.entity import User


class TransactionCategoryPolicyService:
    """Сервис проверки политик доступа к категориям транзакций."""

    @staticmethod
    def is_owner(user: User, category: TransactionCategory) -> None:
        """
        Args:
            user (User): Пользователь, выполняющий действие.
            category (TransactionCategory): Целевая категория транзакции.

        Raises:
            EntityPolicyError: Пользователь не является владельцем категории.
        """
        if user.user_id != category.owner_id:
            raise EntityPolicyError(
                msg="только владелец может работать с категорией транзакции",
                struct_name=user.aggregate_name.name,
                data={
                    "user_id": str(user.user_id.user_id),
                    "category_id": str(
                        category.category_id.category_id,
                    ),
                },
            )


class TransactionCategoryUniquenessService:
    """Сервис проверки уникальности названия категории транзакций."""

    def __init__(self, repository: TransactionCategoryRepository) -> None:
        """
        Args:
            repository (TransactionCategoryRepository): Репозиторий для поиска \
                существующих категорий.
        """
        self._repo = repository

    async def ensure_unique(
        self,
        user: User,
        name: TransactionCategoryName,
    ) -> None:
        """
        Args:
            user (User): Владелец категории.
            name (TransactionCategoryName): Проверяемое название категории.

        Raises:
            EntityInvalidDataError: Название уже занято существующей или удаленной \
                категорией.
        """
        category = await self._repo.by_owner_id_name(user.user_id, name)
        if category is not None:
            if category.state.is_deleted():
                raise EntityInvalidDataError(
                    msg="название категории транзакции уже используется, но она была ранее удалена",
                    struct_name=category.aggregate_name.name,
                    data={
                        "category_id": str(category.category_id.category_id),
                        "name": name.name,
                    },
                )
            raise EntityInvalidDataError(
                msg="название категории транзакции уже используется",
                struct_name=category.aggregate_name.name,
                data={
                    "category_id": str(category.category_id.category_id),
                    "name": name.name,
                },
            )
