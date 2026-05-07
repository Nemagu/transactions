from abc import ABC

from application.errors import AppInvalidDataError
from application.ports.unit_of_work import UnitOfWork
from domain.tenant import Tenant, TenantID


class BaseUseCase(ABC):
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def _initiator(
        self, uow: UnitOfWork, initiator_id: TenantID, action: str
    ) -> Tenant:
        initiator = await uow.tenant_repositories.read.by_id(initiator_id)
        if initiator is None:
            raise AppInvalidDataError(
                msg="инициатор не существует",
                action=action,
                data={"tenant": {"tenant_id": initiator_id.tenant_id}},
            )
        return initiator
