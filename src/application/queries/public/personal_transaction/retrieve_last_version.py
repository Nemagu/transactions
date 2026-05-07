from dataclasses import dataclass
from uuid import UUID

from application.dto.personal_transaction import PersonalTransactionSimpleDTO
from application.errors import AppNotFoundError
from application.queries.base import BaseUseCase
from domain.personal_transaction import (
    PersonalTransactionID,
    PersonalTransactionPolicyService,
)
from domain.tenant import TenantID


@dataclass(slots=True, frozen=True)
class GetPersonalTransactionLastVersionQuery:
    initiator_id: UUID
    transaction_id: UUID


class GetPersonalTransactionLastVersionUseCase(BaseUseCase):
    async def execute(
        self, query: GetPersonalTransactionLastVersionQuery
    ) -> PersonalTransactionSimpleDTO:
        action = "получение последней версии транзакции"
        initiator_id = TenantID(query.initiator_id)
        transaction_id = PersonalTransactionID(query.transaction_id)
        async with self._uow as uow:
            initiator = await self._initiator(uow, initiator_id, action)
            initiator.raise_access_read()
            transaction = await uow.transaction_repositories.read.by_id(transaction_id)
            if transaction is None:
                raise AppNotFoundError(
                    msg="транзакции не существует",
                    action=action,
                    data={"transaction": {"transaction_id": query.transaction_id}},
                )
            PersonalTransactionPolicyService().raise_owner(initiator, transaction)
            return PersonalTransactionSimpleDTO.from_domain(transaction)
