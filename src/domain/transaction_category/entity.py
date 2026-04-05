from domain.entities import Entity
from domain.transaction_category.errors import TransactionCategoryIdempotentError
from domain.transaction_category.value_objects import (
    TransactionCategoryDescription,
    TransactionCategoryID,
    TransactionCategoryName,
    TransactionCategoryState,
)
from domain.user import UserID
from domain.value_objects import Version


class TransactionCategory(Entity):
    """Агрегат категории транзакции."""

    def __init__(
        self,
        category_id: TransactionCategoryID,
        owner_id: UserID,
        name: TransactionCategoryName,
        description: TransactionCategoryDescription,
        state: TransactionCategoryState,
        version: Version,
    ):
        """
        Args:
            category_id (TransactionCategoryID): Идентификатор категории.
            owner_id (UserID): Идентификатор владельца категории.
            name (TransactionCategoryName): Название категории.
            description (TransactionCategoryDescription): Описание категории.
            state (TransactionCategoryState): Состояние категории.
            version (Version): Версия категории.
        """
        super().__init__(version)
        self._category_id = category_id
        self._owner_id = owner_id
        self._name = name
        self._description = description
        self._state = state

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

    @property
    def state(self) -> TransactionCategoryState:
        """
        Returns:
            TransactionCategoryState: Состояние категории.
        """
        return self._state

    def new_name(self, name: TransactionCategoryName) -> None:
        """Смена названия категории транзакции.

        Args:
            name (TransactionCategoryName): Новое название категории.

        Raises:
            TransactionCategoryIdempotentError: Новое название категории не может \
                совпадать с предыдущим.
        """
        if self._name == name:
            raise TransactionCategoryIdempotentError(
                msg="название категории транзакции идентично текущему названию",
                data={"name": name.name},
            )
        self._name = name
        self._update_version()

    def new_description(self, description: TransactionCategoryDescription) -> None:
        """Смена описания категории транзакции.

        Args:
            description (TransactionCategoryDescription): Новое описание категории.

        Raises:
            TransactionCategoryIdempotentError: Новое описание категории не может \
                совпадать с предыдущим.
        """
        if self._description == description:
            raise TransactionCategoryIdempotentError(
                msg="описание категории транзакции идентично текущему описанию",
                data={"description": description.description},
            )
        self._description = description
        self._update_version()

    def activate(self) -> None:
        """Активировать категорию транзакции.

        Raises:
            TransactionCategoryIdempotentError: Активную категорию нельзя повторно \
                активировать.
        """
        if self._state.is_active():
            raise TransactionCategoryIdempotentError(
                msg="категория транзакции уже является активной",
                data={"state": self._state.value},
            )
        self._state = TransactionCategoryState.ACTIVE
        self._update_version()

    def delete(self) -> None:
        """Удалить категорию транзакции.

        Raises:
            TransactionCategoryIdempotentError: Удаленную категорию нельзя повторно \
                удалить.
        """
        if self._state.is_deleted():
            raise TransactionCategoryIdempotentError(
                msg="категория транзакции уже является удаленной",
                data={"state": self._state.value},
            )
        self._state = TransactionCategoryState.DELETED
        self._update_version()
