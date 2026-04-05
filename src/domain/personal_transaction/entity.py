from domain.entities import Entity
from domain.personal_transaction.errors import PersonalTransactionIdempotentError
from domain.personal_transaction.value_objects import (
    MoneyAmount,
    PersonalTransactionDescription,
    PersonalTransactionID,
    PersonalTransactionName,
    PersonalTransactionState,
    PersonalTransactionTime,
    PersonalTransactionType,
)
from domain.transaction_category.value_objects import TransactionCategoryID
from domain.user import UserID
from domain.value_objects import Version


class PersonalTransaction(Entity):
    """Агрегат персональной транзакции."""

    def __init__(
        self,
        transaction_id: PersonalTransactionID,
        owner_id: UserID,
        name: PersonalTransactionName,
        description: PersonalTransactionDescription,
        category_ids: set[TransactionCategoryID],
        transaction_type: PersonalTransactionType,
        money_amount: MoneyAmount,
        transaction_time: PersonalTransactionTime,
        state: PersonalTransactionState,
        version: Version,
    ):
        """
        Args:
            transaction_id (PersonalTransactionID): Идентификатор транзакции.
            owner_id (UserID): Идентификатор владельца транзакции.
            name (PersonalTransactionName): Название транзакции.
            description (PersonalTransactionDescription): Описание транзакции.
            category_ids (set[TransactionCategoryID]): Идентификаторы категорий \
                транзакции.
            transaction_type (PersonalTransactionType): Тип транзакции.
            money_amount (MoneyAmount): Количество средств транзакции.
            transaction_time (PersonalTransactionTime): Время транзакции.
            state (PersonalTransactionState): Состояние транзакции.
            version (Version): Версия транзакции.
        """
        super().__init__(version)
        self._transaction_id = transaction_id
        self._owner_id = owner_id
        self._name = name
        self._description = description
        self._category_ids = category_ids
        self._transaction_type = transaction_type
        self._money_amount = money_amount
        self._transaction_time = transaction_time
        self._state = state

    @property
    def transaction_id(self) -> PersonalTransactionID:
        """
        Returns:
            PersonalTransactionID: Идентификатор транзакции.
        """
        return self._transaction_id

    @property
    def owner_id(self) -> UserID:
        """
        Returns:
            UserID: Идентификатор владельца транзакции.
        """
        return self._owner_id

    @property
    def name(self) -> PersonalTransactionName:
        """
        Returns:
            PersonalTransactionName: Название транзакции.
        """
        return self._name

    @property
    def description(self) -> PersonalTransactionDescription:
        """
        Returns:
            PersonalTransactionDescription: Описание транзакции.
        """
        return self._description

    @property
    def category_ids(self) -> set[TransactionCategoryID]:
        """
        Returns:
            set[TransactionCategoryID]: Идентификаторы категорий транзакции.
        """
        return self._category_ids

    @property
    def transaction_type(self) -> PersonalTransactionType:
        """
        Returns:
            PersonalTransactionType: Тип транзакции.
        """
        return self._transaction_type

    @property
    def money_amount(self) -> MoneyAmount:
        """
        Returns:
            MoneyAmount: Количество средств транзакции.
        """
        return self._money_amount

    @property
    def transaction_time(self) -> PersonalTransactionTime:
        """
        Returns:
            PersonalTransactionTime: Время транзакции.
        """
        return self._transaction_time

    @property
    def state(self) -> PersonalTransactionState:
        """
        Returns:
            PersonalTransactionState: Состояние транзакции.
        """
        return self._state

    def new_name(self, name: PersonalTransactionName) -> None:
        """Смена названия персональной транзакции.

        Args:
            name (PersonalTransactionName): Новое название транзакции.

        Raises:
            PersonalTransactionIdempotentError: Новое название транзакции не может \
                совпадать с предыдущим.
        """
        if self._name == name:
            raise PersonalTransactionIdempotentError(
                msg="название транзакции идентично текущему названию",
                data={"name": name.name},
            )
        self._name = name
        self._update_version()

    def new_description(self, description: PersonalTransactionDescription) -> None:
        """Смена описания персональной транзакции.

        Args:
            description (PersonalTransactionDescription): Новое описание транзакции.

        Raises:
            PersonalTransactionIdempotentError: Новое описание транзакции не может \
                совпадать с предыдущим.
        """
        if self._description == description:
            raise PersonalTransactionIdempotentError(
                msg="описание транзакции идентично текущему описанию",
                data={"description": description.description},
            )
        self._description = description
        self._update_version()

    def new_category_ids(self, category_ids: set[TransactionCategoryID]) -> None:
        """Смена категорий персональной транзакции.

        Args:
            category_ids (set[TransactionCategoryID]): Новый набор идентификаторов \
                категорий транзакции.

        Raises:
            PersonalTransactionIdempotentError: Новый набор категорий не может \
                совпадать с предыдущим.
        """
        if self._category_ids == category_ids:
            raise PersonalTransactionIdempotentError(
                msg="категории транзакции идентичны текущим категориям",
                data={"category_ids": [category.category_id for category in category_ids]},
            )
        self._category_ids = category_ids
        self._update_version()

    def new_transaction_type(
        self,
        transaction_type: PersonalTransactionType,
    ) -> None:
        """Смена типа персональной транзакции.

        Args:
            transaction_type (PersonalTransactionType): Новый тип транзакции.

        Raises:
            PersonalTransactionIdempotentError: Новый тип транзакции не может \
                совпадать с предыдущим.
        """
        if self._transaction_type == transaction_type:
            raise PersonalTransactionIdempotentError(
                msg="тип транзакции идентичен текущему типу",
                data={"transaction_type": transaction_type.value},
            )
        self._transaction_type = transaction_type
        self._update_version()

    def new_money_amount(self, money_amount: MoneyAmount) -> None:
        """Смена количества средств персональной транзакции.

        Args:
            money_amount (MoneyAmount): Новое количество средств транзакции.

        Raises:
            PersonalTransactionIdempotentError: Новое количество средств не может \
                совпадать с предыдущим.
        """
        if self._money_amount == money_amount:
            raise PersonalTransactionIdempotentError(
                msg="количество средств транзакции идентично текущему количеству",
                data={
                    "money_amount": {
                        "amount": str(money_amount.amount),
                        "currency": money_amount.currency.value,
                    }
                },
            )
        self._money_amount = money_amount
        self._update_version()

    def new_transaction_time(
        self,
        transaction_time: PersonalTransactionTime,
    ) -> None:
        """Смена времени персональной транзакции.

        Args:
            transaction_time (PersonalTransactionTime): Новое время транзакции.

        Raises:
            PersonalTransactionIdempotentError: Новое время транзакции не может \
                совпадать с предыдущим.
        """
        if self._transaction_time == transaction_time:
            raise PersonalTransactionIdempotentError(
                msg="время транзакции идентично текущему времени",
                data={"transaction_time": str(transaction_time.transaction_time)},
            )
        self._transaction_time = transaction_time
        self._update_version()

    def activate(self) -> None:
        """Активировать персональную транзакцию.

        Raises:
            PersonalTransactionIdempotentError: Активную транзакцию нельзя повторно \
                активировать.
        """
        if self._state.is_active():
            raise PersonalTransactionIdempotentError(
                msg="транзакция уже является активной",
                data={"state": self._state.value},
            )
        self._state = PersonalTransactionState.ACTIVE
        self._update_version()

    def delete(self) -> None:
        """Удалить персональную транзакцию.

        Raises:
            PersonalTransactionIdempotentError: Удаленную транзакцию нельзя повторно \
                удалить.
        """
        if self._state.is_deleted():
            raise PersonalTransactionIdempotentError(
                msg="транзакция уже является удаленной",
                data={"state": self._state.value},
            )
        self._state = PersonalTransactionState.DELETED
        self._update_version()
