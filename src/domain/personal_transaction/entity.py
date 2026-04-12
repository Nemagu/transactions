from domain.entities import EntityWithState
from domain.errors import EntityIdempotentError, EntityInvalidDataError
from domain.personal_transaction.value_objects import (
    MoneyAmount,
    PersonalTransactionDescription,
    PersonalTransactionID,
    PersonalTransactionName,
    PersonalTransactionTime,
    PersonalTransactionType,
)
from domain.tenant import TenantID
from domain.transaction_category import TransactionCategory, TransactionCategoryID
from domain.value_objects import AggregateName, State, Version


class PersonalTransaction(EntityWithState):
    def __init__(
        self,
        transaction_id: PersonalTransactionID,
        category_ids: set[TransactionCategoryID],
        owner_id: TenantID,
        name: PersonalTransactionName,
        description: PersonalTransactionDescription,
        transaction_type: PersonalTransactionType,
        money_amount: MoneyAmount,
        transaction_time: PersonalTransactionTime,
        state: State,
        version: Version,
    ):
        super().__init__(
            state,
            version,
            AggregateName("персональная транзакция"),
            "_transaction_id",
            "transaction",
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
        self._category_ids = category_ids

    @property
    def transaction_id(self) -> PersonalTransactionID:
        return self._transaction_id

    @property
    def owner_id(self) -> TenantID:
        return self._owner_id

    @property
    def name(self) -> PersonalTransactionName:
        return self._name

    @property
    def description(self) -> PersonalTransactionDescription:
        return self._description

    @property
    def category_ids(self) -> set[TransactionCategoryID]:
        return self._category_ids

    @property
    def transaction_type(self) -> PersonalTransactionType:
        return self._transaction_type

    @property
    def money_amount(self) -> MoneyAmount:
        return self._money_amount

    @property
    def transaction_time(self) -> PersonalTransactionTime:
        return self._transaction_time

    def new_name(self, name: PersonalTransactionName) -> None:
        self._check_state()
        if self._name == name:
            raise EntityIdempotentError(
                **self._error_data(
                    "название транзакции идентично текущему названию",
                    {"name": name.name},
                )
            )
        self._name = name
        self._update_version()

    def new_description(self, description: PersonalTransactionDescription) -> None:
        self._check_state()
        if self._description == description:
            raise EntityIdempotentError(
                **self._error_data(
                    "описание транзакции идентично текущему описанию",
                    {"description": description.description},
                )
            )
        self._description = description
        self._update_version()

    def new_categories(self, categories: set[TransactionCategory]) -> None:
        self._check_state()
        self.validate_categories(categories)
        if self._category_ids == set(category.category_id for category in categories):
            raise EntityInvalidDataError(
                msg="категории транзакции идентичны текущим категориям",
                struct_name=self._aggregate_name.name,
                data={
                    "transaction": {
                        "transaction_id": str(self._transaction_id.transaction_id)
                    },
                    "categories": [
                        {
                            "category_id": str(category.category_id.category_id),
                            "name": category.name.name,
                        }
                        for category in categories
                    ],
                },
            )
        self._category_ids = {category.category_id for category in categories}
        self._update_version()

    def add_categories(self, categories: set[TransactionCategory]) -> None:
        self._check_state()
        if len(categories) == 0:
            raise EntityInvalidDataError(
                **self._error_data("не переданы категории для добавления транзакции")
            )
        self.validate_categories(categories)
        existing_categories = set()
        for category in categories:
            if category.category_id in self._category_ids:
                existing_categories.add(category)
        if existing_categories and len(existing_categories) == len(categories):
            raise EntityInvalidDataError(
                msg="категории транзакции уже присвоены транзакции",
                struct_name=self._aggregate_name.name,
                data={
                    "transaction": {
                        "transaction_id": str(self._transaction_id.transaction_id)
                    },
                    "categories": [
                        {
                            "category_id": str(category.category_id.category_id),
                            "name": category.name.name,
                        }
                        for category in categories
                    ],
                },
            )
        self._category_ids.update(category.category_id for category in categories)
        self._update_version()

    def remove_categories(self, categories: set[TransactionCategory]) -> None:
        self._check_state()
        if len(categories) == 0:
            raise EntityInvalidDataError(
                **self._error_data("не переданы категории для удаления из транзакции")
            )
        not_existing_categories = set()
        for category in categories:
            if category.category_id not in self._category_ids:
                not_existing_categories.add(category)
        if not_existing_categories and len(not_existing_categories) == len(categories):
            raise EntityInvalidDataError(
                msg="категории транзакции не присвоены транзакции",
                struct_name=self._aggregate_name.name,
                data={
                    "transaction": {
                        "transaction_id": str(self._transaction_id.transaction_id)
                    },
                    "categories": [
                        {
                            "category_id": str(category.category_id.category_id),
                            "name": category.name.name,
                        }
                        for category in categories
                    ],
                },
            )
        self._category_ids.difference_update(
            category.category_id for category in categories
        )
        self._update_version()

    def new_transaction_type(
        self,
        transaction_type: PersonalTransactionType,
    ) -> None:
        self._check_state()
        if self._transaction_type == transaction_type:
            raise EntityIdempotentError(
                **self._error_data(
                    "тип транзакции идентичен текущему типу",
                    {
                        "transaction_type": transaction_type.value,
                    },
                )
            )
        self._transaction_type = transaction_type
        self._update_version()

    def new_money_amount(self, money_amount: MoneyAmount) -> None:
        self._check_state()
        if self._money_amount == money_amount:
            raise EntityIdempotentError(
                **self._error_data(
                    "количество средств транзакции идентично текущему количеству",
                    {
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
        self._check_state()
        if self._transaction_time == transaction_time:
            raise EntityIdempotentError(
                **self._error_data(
                    "время транзакции идентично текущему времени",
                    {
                        "transaction_time": str(transaction_time.transaction_time),
                    },
                )
            )
        self._transaction_time = transaction_time
        self._update_version()

    def _check_state(self) -> None:
        return super()._check_state(
            "транзакция была удалена, ее редактирование запрещено"
        )

    def validate_categories(self, categories: set[TransactionCategory]) -> None:
        self._validate_category_owners(categories)
        self._validate_deleted_categories(categories)

    def _validate_category_owners(self, categories: set[TransactionCategory]) -> None:
        error_data = list()
        struct_name = ""
        for category in categories:
            if self._owner_id != category.owner_id:
                error_data.append(
                    {
                        "category_id": str(category.category_id.category_id),
                    }
                )
                if struct_name == "":
                    struct_name = category.aggregate_name.name
        if error_data:
            raise EntityInvalidDataError(
                msg="чужие категории нельзя назначить транзакции",
                struct_name=struct_name,
                data={"categories": error_data},
            )

    def _validate_deleted_categories(
        self, categories: set[TransactionCategory]
    ) -> None:
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
