from dataclasses import dataclass
from typing import Any
from uuid import UUID

from application.dto import (
    LimitOffsetPaginator,
    TransactionCategoryVersionSimpleDTO,
)
from application.errors import AppInvalidDataError
from application.queries.base import BaseUseCase
from domain.tenant import TenantID
from domain.transaction_category import (
    TransactionCategoryID,
    TransactionCategoryName,
    TransactionCategoryPolicyService,
)
from domain.value_objects import State, Version


@dataclass
class TransactionCategoryVersionsQuery:
    initiator_id: UUID
    paginator: LimitOffsetPaginator
    category_id: UUID
    names: list[str] | None
    states: list[str] | None
    from_version: int | None
    to_version: int | None


class TransactionCategoryVersionsUseCase(BaseUseCase):
    async def execute(
        self, query: TransactionCategoryVersionsQuery
    ) -> tuple[list[TransactionCategoryVersionSimpleDTO], int]:
        action = "получение версий категории транзакции"
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
            categories, count = await uow.category_repositories.version.filters(
                **filtering_data
            )
            if count == 0:
                return list(), count
            service = TransactionCategoryPolicyService()
            for category, _, _, _ in categories:
                service.raise_owner(initiator, category)
            return [
                TransactionCategoryVersionSimpleDTO.from_domain(
                    category, event, editor_id, created_at
                )
                for category, event, editor_id, created_at in categories
            ], count

    def _cast_data_from_query(
        self, query: TransactionCategoryVersionsQuery
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
