from dataclasses import dataclass
from uuid import UUID

from application.dto import TransactionCategorySimpleDTO
from application.errors import AppInvalidDataError
from application.queries.base import BaseUseCase
from domain.tenant import TenantID
from domain.transaction_category import (
    TransactionCategoryID,
    TransactionCategoryPolicyService,
)
from domain.value_objects import Version


@dataclass
class TransactionCategoryVersionQuery:
    user_id: UUID
    category_id: UUID
    version: int


class TransactionCategoryVersionUseCase(BaseUseCase):
    async def execute(
        self, query: TransactionCategoryVersionQuery
    ) -> TransactionCategorySimpleDTO:
        action = "получение версии категории транзакций"
        async with self._uow as uow:
            initiator_id = TenantID(query.user_id)
            category_id = TransactionCategoryID(query.category_id)
            version = Version(query.version)
            initiator = await uow.tenant_repositories.read.by_id(initiator_id)
            if initiator is None:
                raise AppInvalidDataError(
                    msg="инициатор не существует",
                    action=action,
                    data={"tenant": {"tenant_id": query.user_id}},
                )
            initiator.raise_access_read()
            category = await uow.category_repositories.version.by_id_version(
                category_id, version
            )
            if category is None:
                raise AppInvalidDataError(
                    msg="категории транзакций не существует",
                    action=action,
                    data={"category": {"category_id": query.category_id}},
                )
            TransactionCategoryPolicyService().raise_owner(initiator, category)
            return TransactionCategorySimpleDTO.from_domain(category)
