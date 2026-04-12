from dataclasses import dataclass
from uuid import UUID

from application.commands.base import BaseUseCase
from application.dto import TransactionCategorySimpleDTO
from application.errors import AppInvalidDataError
from domain.tenant import TenantID
from domain.transaction_category import (
    TransactionCategoryFactory,
    TransactionCategoryName,
    TransactionCategoryUniquenessService,
)


@dataclass
class TransactionCategoryCreationCommand:
    user_id: UUID
    name: str
    description: str = ""


class TransactionCategoryCreationUseCase(BaseUseCase):
    async def execute(
        self, command: TransactionCategoryCreationCommand
    ) -> TransactionCategorySimpleDTO:
        action = "создание категории транзакции"
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
            await uow.category_repositories.version.save(category)
            return TransactionCategorySimpleDTO.from_domain(category)
