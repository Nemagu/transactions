from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from application.commands.base import BaseUseCase
from application.dto.personal_transaction import (
    MoneyAmountDTO,
    PersonalTransactionSimpleDTO,
)
from application.errors import AppInvalidDataError
from application.ports.repositories import PersonalTransactionEvent
from domain.personal_transaction import PersonalTransactionFactory
from domain.tenant import TenantID
from domain.transaction_category import TransactionCategoryID


@dataclass(slots=True, frozen=True)
class CreatePersonalTransactionCommand:
    user_id: UUID
    category_ids: list[UUID]
    transaction_type: str
    money_amount: MoneyAmountDTO
    transaction_time: datetime
    name: str = ""
    description: str = ""


class CreatePersonalTransactionUseCase(BaseUseCase):
    async def execute(
        self, command: CreatePersonalTransactionCommand
    ) -> PersonalTransactionSimpleDTO:
        action = "создание персональной транзакции"
        initiator_id = TenantID(command.user_id)
        async with self._uow as uow:
            initiator = await self._initiator(uow, initiator_id, action)
            initiator.raise_access_edit()
            transaction_id = await uow.transaction_repositories.read.next_id()
            category_ids = set(command.category_ids)
            transaction = PersonalTransactionFactory.new(
                transaction_id.transaction_id,
                category_ids,
                command.user_id,
                command.name,
                command.description,
                command.transaction_type,
                command.money_amount.amount,
                command.money_amount.currency,
                command.transaction_time,
            )
            categories = await uow.category_repositories.read.by_ids(
                {TransactionCategoryID(category_id) for category_id in category_ids}
            )
            if len(categories) != len(category_ids):
                existing_category_ids = {
                    category.category_id.category_id for category in categories
                }
                raise AppInvalidDataError(
                    msg="некоторые из переданных категорий не существуют",
                    action=action,
                    data={
                        "categories": [
                            {"category_id": category_id}
                            for category_id in category_ids - existing_category_ids
                        ]
                    },
                )
            transaction.validate_categories((categories))
            await uow.transaction_repositories.read.save(transaction)
            await uow.transaction_repositories.version.save(
                transaction, PersonalTransactionEvent.CREATED, initiator.tenant_id
            )
            return PersonalTransactionSimpleDTO.from_domain(transaction)
