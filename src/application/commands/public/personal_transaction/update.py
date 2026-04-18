from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from application.commands.base import BaseUseCase
from application.dto import MoneyAmountDTO, PersonalTransactionSimpleDTO
from application.errors import AppInvalidDataError, AppNotFoundError
from application.ports.repositories import PersonalTransactionEvent
from application.ports.unit_of_work import UnitOfWork
from domain.personal_transaction import (
    Currency,
    MoneyAmount,
    PersonalTransactionDescription,
    PersonalTransactionID,
    PersonalTransactionName,
    PersonalTransactionPolicyService,
    PersonalTransactionTime,
    PersonalTransactionType,
)
from domain.tenant import TenantID
from domain.transaction_category import TransactionCategoryID
from domain.transaction_category.entity import TransactionCategory


@dataclass
class PersonalTransactionUpdateCommand:
    user_id: UUID
    transaction_id: UUID
    category_ids: set[UUID] | None
    add_category_ids: set[UUID] | None
    remove_category_ids: set[UUID] | None
    transaction_type: str | None
    money_amount: MoneyAmountDTO | None
    transaction_time: datetime | None
    name: str | None
    description: str | None

    def __post_init__(self) -> None:
        action = "обновление персональной транзакции"
        if (
            self.category_ids is None
            and self.add_category_ids is None
            and self.remove_category_ids is None
            and self.transaction_type is None
            and self.money_amount is None
            and self.transaction_time is None
            and self.name is None
            and self.description is None
        ):
            raise AppInvalidDataError(
                msg="для обновления транзакции не переданы данные",
                action=action,
                data={
                    "category_ids": None,
                    "add_category_ids": None,
                    "remove_category_ids": None,
                    "transaction_type": None,
                    "money_amount": None,
                    "transaction_time": None,
                    "name": None,
                    "description": None,
                },
            )
        if self.category_ids is not None and (
            self.add_category_ids is not None or self.remove_category_ids is not None
        ):
            raise AppInvalidDataError(
                msg="не корректные данные для обновления категорий транзакции",
                action=action,
                data={
                    "category_ids": self.category_ids,
                    "add_category_ids": self.add_category_ids,
                    "remove_category_ids": self.remove_category_ids,
                },
            )


class PersonalTransactionUpdateUseCase(BaseUseCase):
    async def execute(
        self, command: PersonalTransactionUpdateCommand
    ) -> PersonalTransactionSimpleDTO:
        action = "обновление персональной транзакции"
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
            transaction = await uow.transaction_repositories.read.by_id(
                PersonalTransactionID(command.transaction_id)
            )
            if transaction is None:
                raise AppNotFoundError(
                    msg="транзакции не существует",
                    action=action,
                    data={"transaction": {"transaction_id": command.transaction_id}},
                )
            PersonalTransactionPolicyService().raise_owner(initiator, transaction)
            if command.transaction_type is not None:
                transaction.new_transaction_type(
                    PersonalTransactionType.from_str(command.transaction_type)
                )
            if command.money_amount is not None:
                transaction.new_money_amount(
                    MoneyAmount(
                        command.money_amount.amount,
                        Currency.from_str(command.money_amount.currency),
                    )
                )
            if command.transaction_time is not None:
                transaction.new_transaction_time(
                    PersonalTransactionTime(command.transaction_time)
                )
            if command.name is not None:
                transaction.new_name(PersonalTransactionName(command.name))
            if command.description is not None:
                transaction.new_description(
                    PersonalTransactionDescription(command.description)
                )
            if command.category_ids is not None:
                categories = await self._categories(uow, command.category_ids)
                transaction.new_categories(categories)
            if command.add_category_ids is not None:
                categories = await self._categories(uow, command.add_category_ids)
                transaction.add_categories(categories)
            if command.remove_category_ids is not None:
                categories = await self._categories(uow, command.remove_category_ids)
                transaction.remove_categories(categories)
            await uow.transaction_repositories.read.save(transaction)
            await uow.transaction_repositories.version.save(
                transaction, PersonalTransactionEvent.UPDATED, initiator
            )
            return PersonalTransactionSimpleDTO.from_domain(transaction)

    async def _categories(
        self, uow: UnitOfWork, category_ids: set[UUID]
    ) -> set[TransactionCategory]:
        if len(category_ids) == 0:
            return set()
        categories = await uow.category_repositories.read.by_ids(
            {TransactionCategoryID(category_id) for category_id in category_ids}
        )
        if len(categories) != len(category_ids):
            existing_category_ids = {
                category.category_id.category_id for category in categories
            }
            raise AppInvalidDataError(
                msg="некоторые из переданных категорий не существуют",
                action="обновление персональной транзакции",
                data={
                    "categories": [
                        {"category_id": category_id}
                        for category_id in category_ids - existing_category_ids
                    ]
                },
            )
        return categories
