from abc import ABC, abstractmethod

from src.domain.tenant.entity import Tenant
from src.domain.tenant.value_objects import TenantID


class TenantReadRepository(ABC):
    @abstractmethod
    async def by_id(self, tenant_id: TenantID) -> Tenant | None: ...
