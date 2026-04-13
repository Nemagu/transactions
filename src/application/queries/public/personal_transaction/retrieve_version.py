from dataclasses import dataclass
from uuid import UUID

from application.dto import PersonalTransactionSimpleDTO
from application.errors import AppInvalidDataError
from application.queries.base import BaseUseCase
from domain.personal_transaction import (
    PersonalTransactionID,
    PersonalTransactionPolicyService,
)
from domain.tenant import TenantID
from domain.value_objects import Version


@dataclass
class PersonalTransactionVersionQuery:
    user_id: UUID
    transaction_id: UUID
    version: int


class PersonalTransactionVersionUseCase(BaseUseCase):
    async def execute(
        self, query: PersonalTransactionVersionQuery
    ) -> PersonalTransactionSimpleDTO:
        action = "получение версии транзакции"
        async with self._uow as uow:
            initiator_id = TenantID(query.user_id)
            transaction_id = PersonalTransactionID(query.transaction_id)
            version = Version(query.version)
            initiator = await uow.tenant_repositories.read.by_id(initiator_id)
            if initiator is None:
                raise AppInvalidDataError(
                    msg="инициатор не существует",
                    action=action,
                    data={"tenant": {"tenant_id": query.user_id}},
                )
            initiator.raise_access_read()
            transaction = await uow.transaction_repositories.version.by_id_version(
                transaction_id, version
            )
            if transaction is None:
                raise AppInvalidDataError(
                    msg="транзакции не существует",
                    action=action,
                    data={"transaction": {"transaction_id": query.transaction_id}},
                )
            PersonalTransactionPolicyService().raise_owner(initiator, transaction)
            return PersonalTransactionSimpleDTO.from_domain(transaction)
