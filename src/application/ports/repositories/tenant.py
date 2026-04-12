from abc import ABC, abstractmethod

from domain.tenant import Tenant
from domain.tenant import TenantReadRepository as DomainTenantReadRepository


class TenantReadRepository(DomainTenantReadRepository):
    @abstractmethod
    async def save(self, tenant: Tenant) -> None: ...


class TenantVersionRepository(ABC):
    @abstractmethod
    async def save(self, tenant: Tenant) -> None: ...
