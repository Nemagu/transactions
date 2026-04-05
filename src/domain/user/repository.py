from abc import ABC, abstractmethod

from domain.user.entity import User
from domain.user.value_objects import UserID


class UserRepository(ABC):
    """Доменный интерфейс для работы с хранилищем пользователей."""

    @abstractmethod
    def next_id(self) -> UserID: ...

    @abstractmethod
    async def by_id(self, user_id: UserID) -> User | None: ...

    @abstractmethod
    async def save(self, user: User) -> None: ...
