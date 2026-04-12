from dataclasses import dataclass
from uuid import UUID

from application.commands.base import BaseUseCase
from application.dto import TransactionCategorySimpleDTO
from application.errors import AppInvalidDataError
from domain.tenant import TenantID
from domain.transaction_category import (
    TransactionCategoryID,
    TransactionCategoryPolicyService,
)


@dataclass
class TransactionCategoryRestorationCommand:
    user_id: UUID
    category_id: UUID


class TransactionCategoryRestorationUseCase(BaseUseCase):
    async def execute(
        self, command: TransactionCategoryRestorationCommand
    ) -> TransactionCategorySimpleDTO:
        action = "восстановление категории транзакции"
        async with self._uow as uow:
            initiator = await uow.tenant_repositories.read.by_id(
                TenantID(command.user_id)
            )
            if initiator is None:
                raise AppInvalidDataError(
                    msg="инициатор не существует",
                    action=action,
                    data={"tenant": {"tenant_id": command.user_id}},
                )
            initiator.raise_access_edit()
            category = await uow.category_repositories.read.by_id(
                TransactionCategoryID(command.category_id)
            )
            if category is None:
                raise AppInvalidDataError(
                    msg="категории не существует",
                    action=action,
                    data={"category": {"category_id": command.category_id}},
                )
            TransactionCategoryPolicyService().raise_owner(initiator, category)
            category.activate()
            await uow.category_repositories.read.save(category)
            await uow.category_repositories.version.save(category)
            return TransactionCategorySimpleDTO.from_domain(category)
