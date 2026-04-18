from dataclasses import dataclass
from uuid import UUID

from application.dto import TenantVersionSimpleDTO
from application.errors import AppInvalidDataError
from application.queries.base import BaseUseCase
from domain.tenant import TenantID
from domain.value_objects import Version


@dataclass
class TenantVersionQuery:
    initiator_id: UUID
    tenant_id: UUID
    version: int


class TenantVersionUseCase(BaseUseCase):
    async def execute(self, query: TenantVersionQuery) -> TenantVersionSimpleDTO:
        action = "получение одной из версий арендатора"
        async with self._uow as uow:
            initiator_id = TenantID(query.initiator_id)
            tenant_id = TenantID(query.tenant_id)
            version = Version(query.version)
            initiator = await uow.tenant_repositories.read.by_id(initiator_id)
            if initiator is None:
                raise AppInvalidDataError(
                    msg="инициатор не существует",
                    action=action,
                    data={"tenant": {"tenant_id": query.initiator_id}},
                )
            if query.initiator_id == query.tenant_id:
                initiator.raise_access_read()
            else:
                initiator.raise_staff()
            tenant = await uow.tenant_repositories.version.by_id_version(
                tenant_id, version
            )
            if tenant is None:
                raise AppInvalidDataError(
                    msg="арендатор такой версии не существует",
                    action=action,
                    data={
                        "tenant": {
                            "tenant_id": query.tenant_id,
                            "version": query.version,
                        }
                    },
                )
            tenant, event, editor_id, created_at = tenant
            return TenantVersionSimpleDTO.from_domain(
                tenant, event, editor_id, created_at
            )
