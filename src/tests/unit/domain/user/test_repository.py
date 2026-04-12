import pytest

from src.domain.user.repository import UserReadRepository


def test_user_repository_requires_by_id_implementation() -> None:
    with pytest.raises(TypeError):
        UserReadRepository()


def test_user_repository_can_be_instantiated_with_by_id() -> None:
    class StubUserRepository(UserReadRepository):
        async def by_id(self, user_id):
            return None

    repository = StubUserRepository()

    assert isinstance(repository, UserReadRepository)
