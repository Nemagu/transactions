"""Доменная сущность категории транзакций."""

from src.domain.entities import EntityWithState
from src.domain.errors import EntityIdempotentError
from src.domain.transaction_category.value_objects import (
    TransactionCategoryDescription,
    TransactionCategoryID,
    TransactionCategoryName,
)
from src.domain.user import UserID
from src.domain.value_objects import AggregateName, State, Version


class TransactionCategory(EntityWithState):
    """Сущность пользовательской категории транзакций."""

    def __init__(
        self,
        category_id: TransactionCategoryID,
        owner_id: UserID,
        name: TransactionCategoryName,
        description: TransactionCategoryDescription,
        state: State,
        version: Version,
    ):
        """
        Args:
            category_id (TransactionCategoryID): Идентификатор категории.
            owner_id (UserID): Идентификатор владельца категории.
            name (TransactionCategoryName): Название категории.
            description (TransactionCategoryDescription): Описание категории.
            state (State): Состояние категории.
            version (Version): Версия агрегата.
        """
        super().__init__(
            state,
            version,
            AggregateName("категория транзакций"),
            ["_category_id", "_owner_id", "_name", "_description"],
        )
        self._category_id = category_id
        self._owner_id = owner_id
        self._name = name
        self._description = description

    @property
    def category_id(self) -> TransactionCategoryID:
        """
        Returns:
            TransactionCategoryID: Идентификатор категории.
        """
        return self._category_id

    @property
    def owner_id(self) -> UserID:
        """
        Returns:
            UserID: Идентификатор владельца категории.
        """
        return self._owner_id

    @property
    def name(self) -> TransactionCategoryName:
        """
        Returns:
            TransactionCategoryName: Название категории.
        """
        return self._name

    @property
    def description(self) -> TransactionCategoryDescription:
        """
        Returns:
            TransactionCategoryDescription: Описание категории.
        """
        return self._description

    def new_name(self, name: TransactionCategoryName) -> None:
        """
        Args:
            name (TransactionCategoryName): Новое название категории.

        Raises:
            EntityIdempotentError: Передано название, совпадающее с текущим.
        """
        self._check_state()
        if self._name == name:
            raise EntityIdempotentError(
                **self._error_data(
                    "название категории транзакции идентично текущему названию",
                    {
                        "category_id": str(self._category_id.category_id),
                        "name": name.name,
                    },
                )
            )
        self._name = name
        self._update_version()

    def new_description(self, description: TransactionCategoryDescription) -> None:
        """
        Args:
            description (TransactionCategoryDescription): Новое описание \
                категории.

        Raises:
            EntityIdempotentError: Передано описание, совпадающее с текущим.
        """
        self._check_state()
        if self._description == description:
            raise EntityIdempotentError(
                **self._error_data(
                    "описание категории транзакции идентично текущему описанию",
                    {
                        "category_id": str(self._category_id.category_id),
                        "description": description.description,
                    },
                )
            )
        self._description = description
        self._update_version()

    def _check_state(self) -> None:
        """
        Raises:
            EntityInvalidDataError: Категория находится в удаленном состоянии.
        """
        return super()._check_state(
            "категория транзакции была удалена, ее редактирование запрещено",
            {"category_id": str(self._category_id.category_id)},
        )
