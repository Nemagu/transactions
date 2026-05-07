from dataclasses import dataclass
from uuid import UUID

from application.commands.base import BaseUseCase
from application.dto.transaction_category import TransactionCategorySimpleDTO
from application.errors import AppNotFoundError
from application.ports.repositories import TransactionCategoryEvent
from domain.tenant import TenantID
from domain.transaction_category import (
    TransactionCategoryID,
    TransactionCategoryPolicyService,
)


@dataclass(slots=True, frozen=True)
class RestoreTransactionCategoryCommand:
    user_id: UUID
    category_id: UUID


class RestoreTransactionCategoryUseCase(BaseUseCase):
    async def execute(
        self, command: RestoreTransactionCategoryCommand
    ) -> TransactionCategorySimpleDTO:
        action = "восстановление категории транзакции"
        initiator_id = TenantID(command.user_id)
        async with self._uow as uow:
            initiator = await self._initiator(uow, initiator_id, action)
            initiator.raise_access_edit()
            category = await uow.category_repositories.read.by_id(
                TransactionCategoryID(command.category_id)
            )
            if category is None:
                raise AppNotFoundError(
                    msg="категории не существует",
                    action=action,
                    data={"category": {"category_id": command.category_id}},
                )
            TransactionCategoryPolicyService().raise_owner(initiator, category)
            category.activate()
            await uow.category_repositories.read.save(category)
            await uow.category_repositories.version.save(
                category, TransactionCategoryEvent.RESTORED, initiator.tenant_id
            )
            return TransactionCategorySimpleDTO.from_domain(category)
