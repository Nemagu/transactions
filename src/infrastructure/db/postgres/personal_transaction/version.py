from datetime import datetime

from application.dto import (
    LimitOffsetPaginator,
    PersonalTransactionVersionDetailDTO,
    PersonalTransactionVersionSimpleDTO,
)
from application.ports.repositories import (
    PersonalTransactionEvent,
    PersonalTransactionVersionRepository,
)
from domain.personal_transaction import (
    MoneyAmount,
    PersonalTransaction,
    PersonalTransactionID,
    PersonalTransactionTime,
)
from domain.tenant import Tenant, TenantID
from domain.transaction_category import TransactionCategoryID
from domain.value_objects import State, Version
from infrastructure.db.postgres.base import BasePostgresRepository


class PersonalTransactionVersionPostgresRepository(
    BasePostgresRepository, PersonalTransactionVersionRepository
):
    async def by_id_version(
        self, transaction_id: PersonalTransactionID, version: Version
    ) -> (
        tuple[PersonalTransaction, PersonalTransactionEvent, Tenant | None, datetime]
        | None
    ): ...

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
        from_version: Version | None,
        to_version: Version | None,
    ) -> tuple[
        list[
            tuple[
                PersonalTransaction, PersonalTransactionEvent, Tenant | None, datetime
            ]
        ],
        int,
    ]: ...

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
        from_version: Version | None,
        to_version: Version | None,
    ) -> tuple[
        list[PersonalTransactionVersionSimpleDTO],
        int,
    ]: ...

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
        from_version: Version | None,
        to_version: Version | None,
    ) -> tuple[
        list[PersonalTransactionVersionDetailDTO],
        int,
    ]: ...

    async def save(
        self, transaction: PersonalTransaction, event: PersonalTransactionEvent
    ) -> None: ...
