from abc import ABC, abstractmethod

from application.dto import LimitOffsetPaginator
from domain.tenant import Tenant, TenantID, TenantState, TenantStatus
from domain.tenant import TenantReadRepository as DomainTenantReadRepository
from domain.value_objects import Version


class TenantReadRepository(DomainTenantReadRepository):
    @abstractmethod
    async def filters(
        self,
        paginator: LimitOffsetPaginator,
        tenant_ids: list[TenantID] | None,
        statuses: list[TenantStatus] | None,
        states: list[TenantState] | None,
    ) -> tuple[list[Tenant], int]: ...

    @abstractmethod
    async def save(self, tenant: Tenant) -> None: ...

    @abstractmethod
    async def batch_save(self, tenants: list[Tenant]) -> None: ...


class TenantVersionRepository(ABC):
    @abstractmethod
    async def by_id_version(
        self, tenant_id: TenantID, version: Version
    ) -> Tenant | None: ...

    @abstractmethod
    async def filters(
        self,
        paginator: LimitOffsetPaginator,
        tenant_id: TenantID,
        statuses: list[TenantStatus] | None,
        states: list[TenantState] | None,
        from_version: Version | None,
        to_version: Version | None,
    ) -> tuple[list[Tenant], int]: ...

    @abstractmethod
    async def save(self, tenant: Tenant) -> None: ...

    @abstractmethod
    async def batch_save(self, tenants: list[Tenant]) -> None: ...
