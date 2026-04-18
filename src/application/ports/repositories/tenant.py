from abc import ABC, abstractmethod
from datetime import datetime
from enum import StrEnum
from typing import Self

from application.dto import LimitOffsetPaginator
from application.errors import AppInternalError
from domain.tenant import Tenant, TenantID, TenantState, TenantStatus
from domain.tenant import TenantReadRepository as DomainTenantReadRepository
from domain.user import User
from domain.value_objects import Version


class TenantEvent(StrEnum):
    CREATED = "created"
    UPDATED = "updated"
    RESTORED = "restored"
    FROZEN = "frozen"
    DELETED = "deleted"

    @classmethod
    def from_str(cls, value: str) -> Self:
        lower_value = value.lower()
        if lower_value in cls._value2member_map_:
            return cls(lower_value)
        raise AppInternalError(
            msg="не удалось найти событие арендатора по предоставленной строке",
            action="получение события арендатора",
            data={"event": value},
        )


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
    ) -> tuple[Tenant, TenantEvent, TenantID | None, datetime] | None: ...

    @abstractmethod
    async def filters(
        self,
        paginator: LimitOffsetPaginator,
        tenant_id: TenantID,
        statuses: list[TenantStatus] | None,
        states: list[TenantState] | None,
        from_version: Version | None,
        to_version: Version | None,
    ) -> tuple[list[tuple[Tenant, TenantEvent, TenantID | None, datetime]], int]: ...

    @abstractmethod
    async def save(
        self, tenant: Tenant, event: TenantEvent, editor: Tenant | None = None
    ) -> None: ...

    @abstractmethod
    async def batch_save(
        self, tenants_events_editors: list[tuple[Tenant, TenantEvent, Tenant | None]]
    ) -> None: ...


class TenantSubscriptionRepository(ABC):
    @abstractmethod
    async def subscribe(self, subscriber: Tenant, source: User) -> None: ...

    @abstractmethod
    async def batch_subscribe(
        self, subscriber_and_source: list[tuple[Tenant, User]]
    ) -> None: ...

    @abstractmethod
    async def processed_version(self, subscriber: Tenant, source: User) -> None: ...

    @abstractmethod
    async def batch_processed_version(
        self, subscriber_and_source: list[tuple[Tenant, User]]
    ) -> None: ...

    @abstractmethod
    async def users_have_no_tenants(self) -> list[User]: ...

    @abstractmethod
    async def new_users_versions(self) -> list[tuple[Tenant, User]]: ...
