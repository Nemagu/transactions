from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from application.commands.base import BaseUseCase
from application.dto.personal_transaction import (
    MoneyAmountDTO,
    PersonalTransactionSimpleDTO,
)
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


@dataclass(slots=True, frozen=True)
class UpdatePersonalTransactionCommand:
    user_id: UUID
    transaction_id: UUID
    category_ids: list[UUID] | None
    add_category_ids: list[UUID] | None
    remove_category_ids: list[UUID] | None
    transaction_type: str | None
    money_amount: MoneyAmountDTO | None
    transaction_time: datetime | None
    name: str | None
    description: str | None


class UpdatePersonalTransactionUseCase(BaseUseCase):
    async def execute(
        self, command: UpdatePersonalTransactionCommand
    ) -> PersonalTransactionSimpleDTO:
        action = "обновление персональной транзакции"
        self._validate_command(command, action)
        initiator_id = TenantID(command.user_id)
        async with self._uow as uow:
            initiator = await self._initiator(uow, initiator_id, action)
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
                categories = await self._categories(uow, set(command.category_ids))
                transaction.new_categories(categories)
            if command.add_category_ids is not None:
                categories = await self._categories(
                    uow, set(command.add_category_ids)
                )
                transaction.add_categories(categories)
            if command.remove_category_ids is not None:
                categories = await self._categories(
                    uow, set(command.remove_category_ids)
                )
                transaction.remove_categories(categories)
            await uow.transaction_repositories.read.save(transaction)
            await uow.transaction_repositories.version.save(
                transaction, PersonalTransactionEvent.UPDATED, initiator.tenant_id
            )
            return PersonalTransactionSimpleDTO.from_domain(transaction)

    @staticmethod
    def _validate_command(
        command: UpdatePersonalTransactionCommand, action: str
    ) -> None:
        if (
            command.category_ids is None
            and command.add_category_ids is None
            and command.remove_category_ids is None
            and command.transaction_type is None
            and command.money_amount is None
            and command.transaction_time is None
            and command.name is None
            and command.description is None
        ):
            raise AppInvalidDataError(
                msg="для обновления транзакции не переданы данные",
                action=action,
                data={"transaction": {"transaction_id": command.transaction_id}},
            )
        if command.category_ids is not None and (
            command.add_category_ids is not None
            or command.remove_category_ids is not None
        ):
            raise AppInvalidDataError(
                msg="не корректные данные для обновления категорий транзакции",
                action=action,
                data={
                    "transaction": {"transaction_id": command.transaction_id},
                },
            )

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
