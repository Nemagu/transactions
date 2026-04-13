from dataclasses import dataclass
from typing import Any
from uuid import UUID

from application.dto import LimitOffsetPaginator, TransactionCategorySimpleDTO
from application.errors import AppInvalidDataError
from application.queries.base import BaseUseCase
from domain.tenant import TenantID
from domain.transaction_category import (
    TransactionCategoryName,
    TransactionCategoryPolicyService,
)
from domain.value_objects import State


@dataclass
class TransactionCategoryLastVersionsQuery:
    user_id: UUID
    paginator: LimitOffsetPaginator
    names: list[str] | None
    states: list[str] | None


class TransactionCategoryLastVersionsUseCase(BaseUseCase):
    async def execute(
        self, query: TransactionCategoryLastVersionsQuery
    ) -> tuple[list[TransactionCategorySimpleDTO], int]:
        action = "получение последних версий категорий транзакций"
        async with self._uow as uow:
            initiator_id = TenantID(query.user_id)
            filtering_data = self._cast_data_from_query(query)
            initiator = await uow.tenant_repositories.read.by_id(initiator_id)
            if initiator is None:
                raise AppInvalidDataError(
                    msg="инициатор не существует",
                    action=action,
                    data={"tenant": {"tenant_id": query.user_id}},
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
        data = {"paginator": query.paginator, "owner_id": TenantID(query.user_id)}
        if query.names is not None:
            data["names"] = [TransactionCategoryName(name) for name in query.names]
        if query.states is not None:
            data["states"] = [State(state) for state in query.states]
        return data
