"""Доменная сущность персональной транзакции."""

from src.domain.entities import EntityWithState
from src.domain.errors import EntityIdempotentError, EntityInvalidDataError
from src.domain.personal_transaction.value_objects import (
    MoneyAmount,
    PersonalTransactionDescription,
    PersonalTransactionID,
    PersonalTransactionName,
    PersonalTransactionTime,
    PersonalTransactionType,
)
from src.domain.transaction_category import TransactionCategory, TransactionCategoryID
from src.domain.user import UserID
from src.domain.value_objects import AggregateName, State, Version


class PersonalTransaction(EntityWithState):
    """Сущность персональной транзакции пользователя."""

    def __init__(
        self,
        transaction_id: PersonalTransactionID,
        categories: set[TransactionCategory],
        owner_id: UserID,
        name: PersonalTransactionName,
        description: PersonalTransactionDescription,
        transaction_type: PersonalTransactionType,
        money_amount: MoneyAmount,
        transaction_time: PersonalTransactionTime,
        state: State,
        version: Version,
    ):
        """
        Args:
            transaction_id (PersonalTransactionID): Идентификатор транзакции.
            categories (set[TransactionCategory]): Категории, связанные с \
                транзакцией.
            owner_id (UserID): Идентификатор владельца транзакции.
            name (PersonalTransactionName): Название транзакции.
            description (PersonalTransactionDescription): Описание транзакции.
            transaction_type (PersonalTransactionType): Тип транзакции.
            money_amount (MoneyAmount): Денежная сумма транзакции.
            transaction_time (PersonalTransactionTime): Время транзакции.
            state (State): Состояние транзакции.
            version (Version): Версия агрегата.

        Raises:
            EntityInvalidDataError: Среди категорий есть удаленные.
        """
        super().__init__(
            state,
            version,
            AggregateName("персональная транзакция"),
            [
                "_transaction_id",
                "_category_ids",
                "_owner_id",
                "_name",
                "_description",
                "_transaction_type",
                "_money_amount",
                "_transaction_time",
            ],
        )
        self._transaction_id = transaction_id
        self._owner_id = owner_id
        self._name = name
        self._description = description
        self._transaction_type = transaction_type
        self._money_amount = money_amount
        self._transaction_time = transaction_time
        self._validate_categories(categories)
        self._category_ids = set(category.category_id for category in categories)

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
            set[TransactionCategoryID]: Идентификаторы назначенных категорий.
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
            MoneyAmount: Денежная сумма транзакции.
        """
        return self._money_amount

    @property
    def transaction_time(self) -> PersonalTransactionTime:
        """
        Returns:
            PersonalTransactionTime: Время совершения транзакции.
        """
        return self._transaction_time

    def new_name(self, name: PersonalTransactionName) -> None:
        """
        Args:
            name (PersonalTransactionName): Новое название транзакции.

        Raises:
            EntityIdempotentError: Передано название, совпадающее с текущим.
        """
        self._check_state()
        if self._name == name:
            raise EntityIdempotentError(
                **self._error_data(
                    "название транзакции идентично текущему названию",
                    {
                        "transaction_id": str(self._transaction_id.transaction_id),
                        "name": name.name,
                    },
                )
            )
        self._name = name
        self._update_version()

    def new_description(self, description: PersonalTransactionDescription) -> None:
        """
        Args:
            description (PersonalTransactionDescription): Новое описание \
                транзакции.

        Raises:
            EntityIdempotentError: Передано описание, совпадающее с текущим.
            EntityInvalidDataError: Транзакция удалена.
        """
        self._check_state()
        if self._description == description:
            raise EntityIdempotentError(
                **self._error_data(
                    "описание транзакции идентично текущему описанию",
                    {
                        "transaction_id": str(self._transaction_id.transaction_id),
                        "description": description.description,
                    },
                )
            )
        self._description = description
        self._update_version()

    def new_categories(self, categories: set[TransactionCategory]) -> None:
        """
        Args:
            categories (set[TransactionCategory]): Новый полный набор категорий.

        Raises:
            EntityIdempotentError: Передан тот же набор категорий.
            EntityInvalidDataError: Транзакция удалена или среди категорий есть \
                удаленные.
        """
        self._check_state()
        self._validate_categories(categories)
        if self._category_ids == set(category.category_id for category in categories):
            raise EntityIdempotentError(
                **self._error_data(
                    "категории транзакции идентичны текущим категориям",
                    {
                        "transaction_id": str(self._transaction_id.transaction_id),
                        "categories": [
                            {
                                "category_id": str(category.category_id.category_id),
                                "name": category.name.name,
                            }
                            for category in categories
                        ],
                    },
                )
            )
        self._category_ids = {category.category_id for category in categories}
        self._update_version()

    def add_categories(self, categories: set[TransactionCategory]) -> None:
        """
        Args:
            categories (set[TransactionCategory]): Категории для добавления.

        Raises:
            EntityInvalidDataError: Транзакция удалена, среди категорий есть \
                удаленные или все категории уже назначены.
        """
        self._check_state()
        self._validate_categories(categories)
        existing_categories = set()
        for category in categories:
            if category.category_id in self._category_ids:
                existing_categories.add(category)
        if existing_categories and len(existing_categories) == len(categories):
            raise EntityInvalidDataError(
                **self._error_data(
                    "категории транзакции уже присвоены транзакции",
                    {
                        "transaction_id": str(self._transaction_id.transaction_id),
                        "categories": [
                            {
                                "category_id": str(category.category_id.category_id),
                                "name": category.name.name,
                            }
                            for category in categories
                        ],
                    },
                )
            )
        self._category_ids.update(category.category_id for category in categories)
        self._update_version()

    def remove_categories(self, categories: set[TransactionCategory]) -> None:
        """
        Args:
            categories (set[TransactionCategory]): Категории для удаления.

        Raises:
            EntityInvalidDataError: Транзакция удалена или ни одна из переданных \
                категорий не назначена.
        """
        self._check_state()
        not_existing_categories = set()
        for category in categories:
            if category.category_id not in self._category_ids:
                not_existing_categories.add(category)
        if not_existing_categories and len(not_existing_categories) == len(categories):
            raise EntityInvalidDataError(
                **self._error_data(
                    "категории транзакции не присвоены транзакции",
                    {
                        "transaction_id": str(self._transaction_id.transaction_id),
                        "categories": [
                            {
                                "category_id": str(category.category_id.category_id),
                                "name": category.name.name,
                            }
                            for category in categories
                        ],
                    },
                )
            )
        self._category_ids.difference_update(
            category.category_id for category in categories
        )
        self._update_version()

    def new_transaction_type(
        self,
        transaction_type: PersonalTransactionType,
    ) -> None:
        """
        Args:
            transaction_type (PersonalTransactionType): Новый тип транзакции.

        Raises:
            EntityIdempotentError: Передан тип, совпадающий с текущим.
            EntityInvalidDataError: Транзакция удалена.
        """
        self._check_state()
        if self._transaction_type == transaction_type:
            raise EntityIdempotentError(
                **self._error_data(
                    "тип транзакции идентичен текущему типу",
                    {
                        "transaction_id": str(self._transaction_id.transaction_id),
                        "transaction_type": transaction_type.value,
                    },
                )
            )
        self._transaction_type = transaction_type
        self._update_version()

    def new_money_amount(self, money_amount: MoneyAmount) -> None:
        """
        Args:
            money_amount (MoneyAmount): Новая денежная сумма транзакции.

        Raises:
            EntityIdempotentError: Передана сумма, совпадающая с текущей.
            EntityInvalidDataError: Транзакция удалена.
        """
        self._check_state()
        if self._money_amount == money_amount:
            raise EntityIdempotentError(
                **self._error_data(
                    "количество средств транзакции идентично текущему количеству",
                    {
                        "transaction_id": str(self._transaction_id.transaction_id),
                        "money_amount": {
                            "amount": str(money_amount.amount),
                            "currency": money_amount.currency.value,
                        },
                    },
                )
            )
        self._money_amount = money_amount
        self._update_version()

    def new_transaction_time(
        self,
        transaction_time: PersonalTransactionTime,
    ) -> None:
        """
        Args:
            transaction_time (PersonalTransactionTime): Новое время транзакции.

        Raises:
            EntityIdempotentError: Передано время, совпадающее с текущим.
            EntityInvalidDataError: Транзакция удалена.
        """
        self._check_state()
        if self._transaction_time == transaction_time:
            raise EntityIdempotentError(
                **self._error_data(
                    "время транзакции идентично текущему времени",
                    {
                        "transaction_id": str(self._transaction_id.transaction_id),
                        "transaction_time": str(transaction_time.transaction_time),
                    },
                )
            )
        self._transaction_time = transaction_time
        self._update_version()

    def _check_state(self) -> None:
        """
        Raises:
            EntityInvalidDataError: Транзакция находится в удаленном состоянии.
        """
        return super()._check_state(
            "транзакция была удалена, ее редактирование запрещено",
            {"transaction_id": str(self._transaction_id.transaction_id)},
        )

    def _validate_categories(self, categories: set[TransactionCategory]) -> None:
        """
        Args:
            categories (set[TransactionCategory]): Категории для проверки.

        Raises:
            EntityInvalidDataError: Среди переданных категорий есть удаленные.
        """
        error_data = list()
        struct_name = ""
        for category in categories:
            if category.state.is_deleted():
                error_data.append(
                    {
                        "category_id": str(category.category_id.category_id),
                        "name": category.name.name,
                        "state": category.state.value,
                    }
                )
                if struct_name == "":
                    struct_name = category.aggregate_name.name
        if error_data:
            raise EntityInvalidDataError(
                msg="удаленные категории нельзя назначить транзакции",
                struct_name=struct_name,
                data={"categories": error_data},
            )
