from dataclasses import dataclass
from uuid import UUID

from application.commands.base import BaseUseCase
from application.dto.personal_transaction import PersonalTransactionSimpleDTO
from application.errors import AppNotFoundError
from application.ports.repositories import PersonalTransactionEvent
from domain.personal_transaction import (
    PersonalTransactionID,
    PersonalTransactionPolicyService,
)
from domain.tenant import TenantID


@dataclass(slots=True, frozen=True)
class DeletePersonalTransactionCommand:
    user_id: UUID
    transaction_id: UUID


class DeletePersonalTransactionUseCase(BaseUseCase):
    async def execute(
        self, command: DeletePersonalTransactionCommand
    ) -> PersonalTransactionSimpleDTO:
        action = "удаление персональной транзакции"
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
            transaction.delete()
            await uow.transaction_repositories.read.save(transaction)
            await uow.transaction_repositories.version.save(
                transaction, PersonalTransactionEvent.DELETED, initiator.tenant_id
            )
            return PersonalTransactionSimpleDTO.from_domain(transaction)
