from dataclasses import dataclass
from uuid import UUID

from application.dto.personal_transaction import PersonalTransactionVersionSimpleDTO
from application.errors import AppNotFoundError
from application.queries.base import BaseUseCase
from domain.personal_transaction import (
    PersonalTransactionID,
    PersonalTransactionPolicyService,
)
from domain.tenant import TenantID
from domain.value_objects import Version


@dataclass(slots=True, frozen=True)
class GetPersonalTransactionVersionQuery:
    initiator_id: UUID
    transaction_id: UUID
    version: int


class GetPersonalTransactionVersionUseCase(BaseUseCase):
    async def execute(
        self, query: GetPersonalTransactionVersionQuery
    ) -> PersonalTransactionVersionSimpleDTO:
        action = "получение версии транзакции"
        initiator_id = TenantID(query.initiator_id)
        transaction_id = PersonalTransactionID(query.transaction_id)
        version = Version(query.version)
        async with self._uow as uow:
            initiator = await self._initiator(uow, initiator_id, action)
            initiator.raise_access_read()
            transaction_version = (
                await uow.transaction_repositories.version.by_id_version(
                    transaction_id, version
                )
            )
            if transaction_version is None:
                raise AppNotFoundError(
                    msg="транзакции не существует",
                    action=action,
                    data={"transaction": {"transaction_id": query.transaction_id}},
                )
            PersonalTransactionPolicyService().raise_owner(
                initiator, transaction_version.transaction
            )
            return PersonalTransactionVersionSimpleDTO.from_dto(transaction_version)
