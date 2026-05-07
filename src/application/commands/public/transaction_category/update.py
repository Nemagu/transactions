from dataclasses import dataclass
from uuid import UUID

from application.commands.base import BaseUseCase
from application.dto.transaction_category import TransactionCategorySimpleDTO
from application.errors import AppInvalidDataError, AppNotFoundError
from application.ports.repositories import TransactionCategoryEvent
from domain.tenant import TenantID
from domain.transaction_category import (
    TransactionCategoryDescription,
    TransactionCategoryID,
    TransactionCategoryName,
    TransactionCategoryPolicyService,
    TransactionCategoryUniquenessService,
)


@dataclass(slots=True, frozen=True)
class UpdateTransactionCategoryCommand:
    user_id: UUID
    category_id: UUID
    name: str | None
    description: str | None


class UpdateTransactionCategoryUseCase(BaseUseCase):
    async def execute(
        self, command: UpdateTransactionCategoryCommand
    ) -> TransactionCategorySimpleDTO:
        action = "обновление категории транзакции"
        if command.name is None and command.description is None:
            raise AppInvalidDataError(
                msg="данные для обновления категории не переданы",
                action=action,
                data={"category": {"category_id": command.category_id}},
            )
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
            if command.description is not None:
                category.new_description(
                    TransactionCategoryDescription(command.description)
                )
            if command.name is not None:
                service = TransactionCategoryUniquenessService(
                    uow.category_repositories.read
                )
                await service.validate_name(
                    initiator, TransactionCategoryName(command.name)
                )
                category.new_name(TransactionCategoryName(command.name))
            await uow.category_repositories.read.save(category)
            await uow.category_repositories.version.save(
                category, TransactionCategoryEvent.UPDATED, initiator.tenant_id
            )
            return TransactionCategorySimpleDTO.from_domain(category)
