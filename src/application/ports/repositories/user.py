from abc import abstractmethod

from domain.user import User
from domain.user import UserReadRepository as DomainUserReadRepository


class UserReadRepository(DomainUserReadRepository):
    @abstractmethod
    async def save(self, user: User) -> None: ...
