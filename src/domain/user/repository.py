from abc import ABC, abstractmethod

from src.domain.user.projection import User
from src.domain.user.value_objects import UserID


class UserReadRepository(ABC):
    @abstractmethod
    async def by_id(self, user_id: UserID) -> User | None: ...
