from dataclasses import asdict, dataclass
from uuid import UUID

from application.commands.base import BaseUseCase
from application.dto import TransactionCategorySimpleDTO
from application.errors import AppInvalidDataError
from application.ports.repositories import TransactionCategoryEvent
from domain.tenant import TenantID
from domain.transaction_category import (
    TransactionCategoryDescription,
    TransactionCategoryID,
    TransactionCategoryName,
    TransactionCategoryPolicyService,
    TransactionCategoryUniquenessService,
)


@dataclass
class TransactionCategoryUpdateCommand:
    user_id: UUID
    category_id: UUID
    name: str | None
    description: str | None

    def __post_init__(self) -> None:
        if self.name is None and self.description is None:
            raise AppInvalidDataError(
                msg="данные для обновления категории не переданы",
                action="обновление категории транзакции",
                data=asdict(self),
            )


class TransactionCategoryUpdateUseCase(BaseUseCase):
    async def execute(
        self, command: TransactionCategoryUpdateCommand
    ) -> TransactionCategorySimpleDTO:
        action = "обновление категории транзакции"
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
                category, TransactionCategoryEvent.UPDATED, initiator
            )
            return TransactionCategorySimpleDTO.from_domain(category)
