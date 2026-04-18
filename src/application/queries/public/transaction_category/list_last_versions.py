from dataclasses import dataclass
from typing import Any
from uuid import UUID

from application.dto import LimitOffsetPaginator, TransactionCategorySimpleDTO
from application.errors import AppInvalidDataError
from application.queries.base import BaseUseCase
from domain.tenant import TenantID
from domain.transaction_category import (
    TransactionCategoryID,
    TransactionCategoryName,
    TransactionCategoryPolicyService,
)
from domain.value_objects import State


@dataclass
class TransactionCategoryLastVersionsQuery:
    initiator_id: UUID
    paginator: LimitOffsetPaginator
    category_ids: list[UUID] | None
    names: list[str] | None
    states: list[str] | None


class TransactionCategoryLastVersionsUseCase(BaseUseCase):
    async def execute(
        self, query: TransactionCategoryLastVersionsQuery
    ) -> tuple[list[TransactionCategorySimpleDTO], int]:
        action = "получение последних версий категорий транзакций"
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
            categories, count = await uow.category_repositories.read.filters(
                **filtering_data
            )
            service = TransactionCategoryPolicyService()
            for category in categories:
                service.raise_owner(initiator, category)
            return [
                TransactionCategorySimpleDTO.from_domain(category)
                for category in categories
            ], count

    def _cast_data_from_query(
        self, query: TransactionCategoryLastVersionsQuery
    ) -> dict[str, Any]:
        data = {"paginator": query.paginator, "owner_id": TenantID(query.initiator_id)}
        if query.category_ids is not None:
            data["category_ids"] = [
                TransactionCategoryID(category_id) for category_id in query.category_ids
            ]
        if query.names is not None:
            data["names"] = [TransactionCategoryName(name) for name in query.names]
        if query.states is not None:
            data["states"] = [State(state) for state in query.states]
        return data
