from dataclasses import dataclass
from typing import Any
from uuid import UUID

from application.dto.paginators import LimitOffsetPaginator
from application.dto.transaction_category import TransactionCategoryVersionSimpleDTO
from application.queries.base import BaseUseCase
from domain.tenant import TenantID
from domain.transaction_category import (
    TransactionCategoryID,
    TransactionCategoryName,
    TransactionCategoryPolicyService,
)
from domain.value_objects import State, Version


@dataclass(slots=True, frozen=True)
class ListTransactionCategoryVersionsQuery:
    initiator_id: UUID
    paginator: LimitOffsetPaginator
    category_id: UUID
    names: list[str] | None
    states: list[str] | None
    from_version: int | None
    to_version: int | None


class ListTransactionCategoryVersionsUseCase(BaseUseCase):
    async def execute(
        self, query: ListTransactionCategoryVersionsQuery
    ) -> tuple[list[TransactionCategoryVersionSimpleDTO], int]:
        action = "получение версий категории транзакции"
        initiator_id = TenantID(query.initiator_id)
        filtering_data = self._filtering_data(query)
        async with self._uow as uow:
            initiator = await self._initiator(uow, initiator_id, action)
            initiator.raise_access_read()
            versions, count = await uow.category_repositories.version.filters(
                **filtering_data
            )
            if count == 0:
                return list(), count
            service = TransactionCategoryPolicyService()
            for version in versions:
                service.raise_owner(initiator, version.category)
            return [
                TransactionCategoryVersionSimpleDTO.from_dto(version)
                for version in versions
            ], count

    def _filtering_data(
        self, query: ListTransactionCategoryVersionsQuery
    ) -> dict[str, Any]:
        data = {
            "paginator": query.paginator,
            "owner_id": TenantID(query.initiator_id),
            "category_id": TransactionCategoryID(query.category_id),
        }
        if query.names is not None:
            data["names"] = [TransactionCategoryName(name) for name in query.names]
        if query.states is not None:
            data["states"] = [State(state) for state in query.states]
        if query.from_version is not None:
            data["from_version"] = Version(query.from_version)
        if query.to_version is not None:
            data["to_version"] = Version(query.to_version)
        return data
