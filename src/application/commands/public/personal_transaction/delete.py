from dataclasses import dataclass
from uuid import UUID

from application.commands.base import BaseUseCase
from application.dto import PersonalTransactionSimpleDTO
from application.errors import AppInvalidDataError, AppNotFoundError
from domain.personal_transaction import (
    PersonalTransactionID,
    PersonalTransactionPolicyService,
)
from domain.tenant import TenantID


@dataclass
class PersonalTransactionDeletionCommand:
    user_id: UUID
    transaction_id: UUID


class PersonalTransactionDeletionUseCase(BaseUseCase):
    async def execute(
        self, command: PersonalTransactionDeletionCommand
    ) -> PersonalTransactionSimpleDTO:
        action = "удаление персональной транзакции"
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
            transaction.delete()
            await uow.transaction_repositories.read.save(transaction)
            await uow.transaction_repositories.version.save(transaction)
            return PersonalTransactionSimpleDTO.from_domain(transaction)
