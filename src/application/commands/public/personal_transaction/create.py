from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from application.commands.base import BaseUseCase
from application.dto import MoneyAmountDTO, PersonalTransactionSimpleDTO
from application.errors import AppInvalidDataError
from application.ports.repositories import PersonalTransactionEvent
from domain.personal_transaction import PersonalTransactionFactory
from domain.tenant import TenantID
from domain.transaction_category import TransactionCategoryID


@dataclass
class PersonalTransactionCreationCommand:
    user_id: UUID
    category_ids: set[UUID]
    transaction_type: str
    money_amount: MoneyAmountDTO
    transaction_time: datetime
    name: str = ""
    description: str = ""


class PersonalTransactionCreationUseCase(BaseUseCase):
    async def execute(
        self, command: PersonalTransactionCreationCommand
    ) -> PersonalTransactionSimpleDTO:
        action = "создание персональной транзакции"
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
            transaction_id = await uow.transaction_repositories.read.next_id()
            transaction = PersonalTransactionFactory.new(
                transaction_id.transaction_id,
                command.category_ids,
                command.user_id,
                command.name,
                command.description,
                command.transaction_type,
                command.money_amount.amount,
                command.money_amount.currency,
                command.transaction_time,
            )
            categories = await uow.category_repositories.read.by_ids(
                {
                    TransactionCategoryID(category_id)
                    for category_id in command.category_ids
                }
            )
            if len(categories) != len(command.category_ids):
                existing_category_ids = {
                    category.category_id.category_id for category in categories
                }
                raise AppInvalidDataError(
                    msg="некоторые из переданных категорий не существуют",
                    action=action,
                    data={
                        "categories": [
                            {"category_id": category_id}
                            for category_id in command.category_ids
                            - existing_category_ids
                        ]
                    },
                )
            transaction.validate_categories((categories))
            await uow.transaction_repositories.read.save(transaction)
            await uow.transaction_repositories.version.save(
                transaction, PersonalTransactionEvent.CREATED, initiator
            )
            return PersonalTransactionSimpleDTO.from_domain(transaction)
