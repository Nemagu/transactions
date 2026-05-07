from dataclasses import dataclass
from uuid import UUID

from application.commands.base import BaseUseCase
from application.dto.transaction_category import TransactionCategorySimpleDTO
from application.ports.repositories import TransactionCategoryEvent
from domain.tenant import TenantID
from domain.transaction_category import (
    TransactionCategoryFactory,
    TransactionCategoryName,
    TransactionCategoryUniquenessService,
)


@dataclass(slots=True, frozen=True)
class CreateTransactionCategoryCommand:
    user_id: UUID
    name: str
    description: str = ""


class CreateTransactionCategoryUseCase(BaseUseCase):
    async def execute(
        self, command: CreateTransactionCategoryCommand
    ) -> TransactionCategorySimpleDTO:
        action = "создание категории транзакции"
        initiator_id = TenantID(command.user_id)
        async with self._uow as uow:
            initiator = await self._initiator(uow, initiator_id, action)
            initiator.raise_access_edit()
            service = TransactionCategoryUniquenessService(
                uow.category_repositories.read
            )
            await service.validate_name(
                initiator, TransactionCategoryName(command.name)
            )
            category_id = await uow.category_repositories.read.next_id()
            category = TransactionCategoryFactory.new(
                category_id.category_id,
                initiator.tenant_id.tenant_id,
                command.name,
                command.description,
            )
            await uow.category_repositories.read.save(category)
            await uow.category_repositories.version.save(
                category, TransactionCategoryEvent.CREATED, initiator.tenant_id
            )
            return TransactionCategorySimpleDTO.from_domain(category)
