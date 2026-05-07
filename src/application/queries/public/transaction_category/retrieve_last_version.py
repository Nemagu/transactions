from dataclasses import dataclass
from uuid import UUID

from application.dto.transaction_category import TransactionCategorySimpleDTO
from application.errors import AppNotFoundError
from application.queries.base import BaseUseCase
from domain.tenant import TenantID
from domain.transaction_category import (
    TransactionCategoryID,
    TransactionCategoryPolicyService,
)


@dataclass(slots=True, frozen=True)
class GetTransactionCategoryLastVersionQuery:
    initiator_id: UUID
    category_id: UUID


class GetTransactionCategoryLastVersionUseCase(BaseUseCase):
    async def execute(
        self, query: GetTransactionCategoryLastVersionQuery
    ) -> TransactionCategorySimpleDTO:
        action = "получение последней версии категории транзакций"
        initiator_id = TenantID(query.initiator_id)
        category_id = TransactionCategoryID(query.category_id)
        async with self._uow as uow:
            initiator = await self._initiator(uow, initiator_id, action)
            initiator.raise_access_read()
            category = await uow.category_repositories.read.by_id(category_id)
            if category is None:
                raise AppNotFoundError(
                    msg="категории транзакций не существует",
                    action=action,
                    data={"category": {"category_id": query.category_id}},
                )
            TransactionCategoryPolicyService().raise_owner(initiator, category)
            return TransactionCategorySimpleDTO.from_domain(category)
