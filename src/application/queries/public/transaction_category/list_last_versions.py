from dataclasses import dataclass
from typing import Any
from uuid import UUID

from application.dto.paginators import LimitOffsetPaginator
from application.dto.transaction_category import TransactionCategorySimpleDTO
from application.queries.base import BaseUseCase
from domain.tenant import TenantID
from domain.transaction_category import (
    TransactionCategoryID,
    TransactionCategoryName,
    TransactionCategoryPolicyService,
)
from domain.value_objects import State


@dataclass(slots=True, frozen=True)
class ListTransactionCategoryLastVersionsQuery:
    initiator_id: UUID
    paginator: LimitOffsetPaginator
    category_ids: list[UUID] | None
    names: list[str] | None
    states: list[str] | None


class ListTransactionCategoryLastVersionsUseCase(BaseUseCase):
    async def execute(
        self, query: ListTransactionCategoryLastVersionsQuery
    ) -> tuple[list[TransactionCategorySimpleDTO], int]:
        action = "получение последних версий категорий транзакций"
        initiator_id = TenantID(query.initiator_id)
        filtering_data = self._filtering_data(query)
        async with self._uow as uow:
            initiator = await self._initiator(uow, initiator_id, action)
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

    def _filtering_data(
        self, query: ListTransactionCategoryLastVersionsQuery
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
