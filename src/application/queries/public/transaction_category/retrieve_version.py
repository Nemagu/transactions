from dataclasses import dataclass
from uuid import UUID

from application.dto.transaction_category import TransactionCategoryVersionSimpleDTO
from application.errors import AppNotFoundError
from application.queries.base import BaseUseCase
from domain.tenant import TenantID
from domain.transaction_category import (
    TransactionCategoryID,
    TransactionCategoryPolicyService,
)
from domain.value_objects import Version


@dataclass(slots=True, frozen=True)
class GetTransactionCategoryVersionQuery:
    initiator_id: UUID
    category_id: UUID
    version: int


class GetTransactionCategoryVersionUseCase(BaseUseCase):
    async def execute(
        self, query: GetTransactionCategoryVersionQuery
    ) -> TransactionCategoryVersionSimpleDTO:
        action = "получение версии категории транзакций"
        initiator_id = TenantID(query.initiator_id)
        category_id = TransactionCategoryID(query.category_id)
        version = Version(query.version)
        async with self._uow as uow:
            initiator = await self._initiator(uow, initiator_id, action)
            initiator.raise_access_read()
            category_version = await uow.category_repositories.version.by_id_version(
                category_id, version
            )
            if category_version is None:
                raise AppNotFoundError(
                    msg="категории транзакций не существует",
                    action=action,
                    data={"category": {"category_id": query.category_id}},
                )
            TransactionCategoryPolicyService().raise_owner(
                initiator, category_version.category
            )
            return TransactionCategoryVersionSimpleDTO.from_dto(category_version)
