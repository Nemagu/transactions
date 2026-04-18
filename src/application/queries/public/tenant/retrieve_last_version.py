from dataclasses import dataclass
from uuid import UUID

from application.dto import TenantSimpleDTO
from application.errors import AppInvalidDataError
from application.queries.base import BaseUseCase
from domain.tenant import TenantID


@dataclass
class TenantLastVersionQuery:
    initiator_id: UUID
    tenant_id: UUID


class TenantLastVersionUseCase(BaseUseCase):
    async def execute(self, query: TenantLastVersionQuery) -> TenantSimpleDTO:
        action = "получение последней версии арендатора"
        async with self._uow as uow:
            initiator_id = TenantID(query.initiator_id)
            tenant_id = TenantID(query.tenant_id)
            initiator = await uow.tenant_repositories.read.by_id(initiator_id)
            if initiator is None:
                raise AppInvalidDataError(
                    msg="инициатор не существует",
                    action=action,
                    data={"tenant": {"tenant_id": query.initiator_id}},
                )
            if query.initiator_id == query.tenant_id:
                initiator.raise_access_read()
                return TenantSimpleDTO.from_domain(initiator)
            initiator.raise_staff()
            tenant = await uow.tenant_repositories.read.by_id(tenant_id)
            if tenant is None:
                raise AppInvalidDataError(
                    msg="арендатор не существует",
                    action=action,
                    data={"tenant": {"tenant_id": query.tenant_id}},
                )
            return TenantSimpleDTO.from_domain(tenant)
