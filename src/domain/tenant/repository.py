from abc import ABC, abstractmethod

from domain.tenant.entity import Tenant
from domain.tenant.value_objects import TenantID


class TenantReadRepository(ABC):
    @abstractmethod
    async def by_id(self, tenant_id: TenantID) -> Tenant | None: ...
