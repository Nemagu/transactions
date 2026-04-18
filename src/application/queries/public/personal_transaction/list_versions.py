from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from application.dto import (
    LimitOffsetPaginator,
    MoneyAmountDTO,
    PersonalTransactionVersionSimpleDTO,
)
from application.errors import AppInvalidDataError
from application.queries.base import BaseUseCase
from domain.personal_transaction import (
    Currency,
    MoneyAmount,
    PersonalTransactionID,
    PersonalTransactionPolicyService,
    PersonalTransactionTime,
    PersonalTransactionType,
)
from domain.tenant import TenantID
from domain.transaction_category import (
    TransactionCategoryID,
)
from domain.value_objects import State, Version


@dataclass
class PersonalTransactionVersionsQuery:
    initiator_id: UUID
    paginator: LimitOffsetPaginator
    transaction_id: UUID
    category_ids: list[UUID] | None
    transaction_types: list[str] | None
    from_money_amount: MoneyAmountDTO | None
    to_money_amount: MoneyAmountDTO | None
    from_transaction_time: datetime | None
    to_transaction_time: datetime | None
    states: list[str] | None
    from_version: int | None
    to_version: int | None


class PersonalTransactionVersionsUseCase(BaseUseCase):
    async def execute(
        self, query: PersonalTransactionVersionsQuery
    ) -> tuple[list[PersonalTransactionVersionSimpleDTO], int]:
        action = "получение версий транзакции"
        async with self._uow as uow:
            initiator_id = TenantID(query.initiator_id)
            filtering_data = self._cast_data_from_query(query)
            initiator = await uow.tenant_repositories.read.by_id(initiator_id)
            if initiator is None:
                raise AppInvalidDataError(
                    msg="инициатор не существует",
                    action=action,
                    data={"tenant": {"tenant_id": query.initiator_id}},
                )
            initiator.raise_access_read()
            transactions, count = await uow.transaction_repositories.version.filters(
                **filtering_data
            )
            if count == 0:
                return list(), count
            service = PersonalTransactionPolicyService()
            for transaction, _, _, _ in transactions:
                service.raise_owner(initiator, transaction)
            return [
                PersonalTransactionVersionSimpleDTO.from_domain(
                    transaction, event, editor_id, created_at
                )
                for transaction, event, editor_id, created_at in transactions
            ], count

    def _cast_data_from_query(
        self, query: PersonalTransactionVersionsQuery
    ) -> dict[str, Any]:
        data = {
            "paginator": query.paginator,
            "owner_id": TenantID(query.initiator_id),
            "transaction_id": PersonalTransactionID(query.transaction_id),
        }
        if query.category_ids is not None:
            data["category_ids"] = [
                TransactionCategoryID(category_id) for category_id in query.category_ids
            ]
        if query.transaction_types is not None:
            data["transaction_types"] = [
                PersonalTransactionType.from_str(transaction_type)
                for transaction_type in query.transaction_types
            ]
        if query.from_money_amount is not None:
            data["from_money_amount"] = MoneyAmount(
                query.from_money_amount.amount,
                Currency.from_str(query.from_money_amount.currency),
            )
        if query.to_money_amount is not None:
            data["to_money_amount"] = MoneyAmount(
                query.to_money_amount.amount,
                Currency.from_str(query.to_money_amount.currency),
            )
        if query.from_transaction_time is not None:
            data["from_transaction_time"] = PersonalTransactionTime(
                query.from_transaction_time
            )
        if query.to_transaction_time is not None:
            data["to_transaction_time"] = PersonalTransactionTime(
                query.to_transaction_time
            )
        if query.states is not None:
            data["states"] = [State(state) for state in query.states]
        if query.from_version is not None:
            data["from_version"] = Version(query.from_version)
        if query.to_version is not None:
            data["to_version"] = Version(query.to_version)
        return data
