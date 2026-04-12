from abc import ABC, abstractmethod
from typing import Any


class SubscriptionRepository(ABC):
    @abstractmethod
    async def subscribe(self, subscriber: Any, source: Any) -> None: ...
