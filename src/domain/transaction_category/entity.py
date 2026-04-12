from src.domain.entities import EntityWithState
from src.domain.errors import EntityIdempotentError
from src.domain.tenant import TenantID
from src.domain.transaction_category.value_objects import (
    TransactionCategoryDescription,
    TransactionCategoryID,
    TransactionCategoryName,
)
from src.domain.value_objects import AggregateName, State, Version


class TransactionCategory(EntityWithState):
    def __init__(
        self,
        category_id: TransactionCategoryID,
        owner_id: TenantID,
        name: TransactionCategoryName,
        description: TransactionCategoryDescription,
        state: State,
        version: Version,
    ):
        super().__init__(
            state,
            version,
            AggregateName("категория транзакций"),
            "_category_id",
            "category",
            ["_category_id", "_owner_id", "_name", "_description"],
        )
        self._category_id = category_id
        self._owner_id = owner_id
        self._name = name
        self._description = description

    @property
    def category_id(self) -> TransactionCategoryID:
        return self._category_id

    @property
    def owner_id(self) -> TenantID:
        return self._owner_id

    @property
    def name(self) -> TransactionCategoryName:
        return self._name

    @property
    def description(self) -> TransactionCategoryDescription:
        return self._description

    def new_name(self, name: TransactionCategoryName) -> None:
        self._check_state()
        if self._name == name:
            raise EntityIdempotentError(
                **self._error_data(
                    "название категории транзакции идентично текущему названию",
                    {"name": name.name},
                )
            )
        self._name = name
        self._update_version()

    def new_description(self, description: TransactionCategoryDescription) -> None:
        self._check_state()
        if self._description == description:
            raise EntityIdempotentError(
                **self._error_data(
                    "описание категории транзакции идентично текущему описанию",
                    {"description": description.description},
                )
            )
        self._description = description
        self._update_version()

    def _check_state(self) -> None:
        return super()._check_state(
            "категория транзакции была удалена, ее редактирование запрещено",
        )
