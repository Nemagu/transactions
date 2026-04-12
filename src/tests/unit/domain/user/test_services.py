import pytest

from domain.errors import EntityAlreadyExistsError
from domain.user.repository import UserReadRepository
from domain.user.services import UserUniquenessService


class InMemoryUserRepository(UserReadRepository):
    def __init__(self, user) -> None:
        self._user = user

    async def by_id(self, user_id):
        if self._user and self._user.user_id == user_id:
            return self._user
        return None


@pytest.mark.asyncio
async def test_user_uniqueness_allows_free_user_id(user_id_factory) -> None:
    service = UserUniquenessService(InMemoryUserRepository(None))

    assert await service.validate_user_id(user_id_factory()) is None


@pytest.mark.asyncio
async def test_user_uniqueness_rejects_existing_user(
    user_factory,
) -> None:
    existing_user = user_factory()
    service = UserUniquenessService(InMemoryUserRepository(existing_user))

    with pytest.raises(EntityAlreadyExistsError):
        await service.validate_user_id(existing_user.user_id)
