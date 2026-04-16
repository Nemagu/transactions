from application.dto import (
    LimitOffsetPaginator,
    PersonalTransactionDetailDTO,
    PersonalTransactionSimpleDTO,
)
from application.ports.repositories import PersonalTransactionReadRepository
from domain.personal_transaction import (
    MoneyAmount,
    PersonalTransaction,
    PersonalTransactionID,
    PersonalTransactionTime,
)
from domain.tenant import TenantID
from domain.transaction_category import TransactionCategoryID
from domain.value_objects import State
from infrastructure.db.postgres.base import BasePostgresRepository


class PersonalTransactionReadPostgresRepository(
    BasePostgresRepository, PersonalTransactionReadRepository
):
    async def next_id(self) -> PersonalTransactionID: ...

    async def by_id(
        self, transaction_id: PersonalTransactionID
    ) -> PersonalTransaction | None: ...

    async def filters(
        self,
        owner_id: TenantID,
        paginator: LimitOffsetPaginator,
        transaction_ids: list[PersonalTransactionID] | None,
        category_ids: list[TransactionCategoryID] | None,
        transaction_types: list[str] | None,
        from_money_amount: MoneyAmount | None,
        to_money_amount: MoneyAmount | None,
        from_transaction_time: PersonalTransactionTime | None,
        to_transaction_time: PersonalTransactionTime | None,
        states: list[State] | None,
    ) -> tuple[list[PersonalTransaction], int]: ...

    async def filters_to_simple_dto(
        self,
        owner_id: TenantID,
        paginator: LimitOffsetPaginator,
        transaction_ids: list[PersonalTransactionID] | None,
        category_ids: list[TransactionCategoryID] | None,
        transaction_types: list[str] | None,
        from_money_amount: MoneyAmount | None,
        to_money_amount: MoneyAmount | None,
        from_transaction_time: PersonalTransactionTime | None,
        to_transaction_time: PersonalTransactionTime | None,
        states: list[State] | None,
    ) -> tuple[list[PersonalTransactionSimpleDTO], int]: ...

    async def filters_to_detail_dto(
        self,
        owner_id: TenantID,
        paginator: LimitOffsetPaginator,
        transaction_ids: list[PersonalTransactionID] | None,
        category_ids: list[TransactionCategoryID] | None,
        transaction_types: list[str] | None,
        from_money_amount: MoneyAmount | None,
        to_money_amount: MoneyAmount | None,
        from_transaction_time: PersonalTransactionTime | None,
        to_transaction_time: PersonalTransactionTime | None,
        states: list[State] | None,
    ) -> tuple[list[PersonalTransactionDetailDTO], int]: ...

    async def save(self, transaction: PersonalTransaction) -> None: ...
