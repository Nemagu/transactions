from abc import ABC, abstractmethod
from typing import Any

from domain.tenant import Tenant
from domain.user import User


class SubscriptionRepository(ABC):
    @abstractmethod
    async def subscribe(self, subscriber: Any, source: Any) -> None: ...

    @abstractmethod
    async def batch_subscribe(
        self, subscriber_and_source: list[tuple[Any, Any]]
    ) -> None: ...

    @abstractmethod
    async def precessed_version(self, subscriber: Any, source: Any) -> None: ...

    @abstractmethod
    async def batch_processed_version(
        self, subscriber_and_source: list[tuple[Any, Any]]
    ) -> None: ...

    @abstractmethod
    async def users_have_no_tenants(self) -> list[User]: ...

    @abstractmethod
    async def new_users_versions_for_tenants(self) -> list[tuple[Tenant, User]]: ...
