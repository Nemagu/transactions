from dataclasses import dataclass
from uuid import UUID

from application.dto.tenant import TenantVersionSimpleDTO
from application.errors import AppNotFoundError
from application.queries.base import BaseUseCase
from domain.tenant import TenantID
from domain.value_objects import Version


@dataclass(slots=True, frozen=True)
class GetTenantVersionQuery:
    initiator_id: UUID
    tenant_id: UUID
    version: int


class GetTenantVersionUseCase(BaseUseCase):
    async def execute(self, query: GetTenantVersionQuery) -> TenantVersionSimpleDTO:
        action = "получение одной из версий арендатора"
        initiator_id = TenantID(query.initiator_id)
        tenant_id = TenantID(query.tenant_id)
        version = Version(query.version)
        async with self._uow as uow:
            initiator = await self._initiator(uow, initiator_id, action)
            if query.initiator_id == query.tenant_id:
                initiator.raise_access_read()
            else:
                initiator.raise_staff()
            tenant_version = await uow.tenant_repositories.version.by_id_version(
                tenant_id, version
            )
            if tenant_version is None:
                raise AppNotFoundError(
                    msg="арендатор такой версии не существует",
                    action=action,
                    data={
                        "tenant": {
                            "tenant_id": query.tenant_id,
                            "version": query.version,
                        }
                    },
                )
            return TenantVersionSimpleDTO.from_dto(tenant_version)
