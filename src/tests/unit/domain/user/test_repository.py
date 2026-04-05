import pytest

from domain.user.repository import UserRepository


def test_user_repository_requires_next_id_implementation() -> None:
    class StubUserRepository(UserRepository):
        async def by_id(self, user_id):
            return None

        async def save(self, user) -> None:
            return None

    with pytest.raises(TypeError):
        StubUserRepository()
