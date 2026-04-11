import pytest

from src.domain.errors import EntityInvalidDataError, EntityPolicyError
from src.domain.transaction_category.repository import TransactionCategoryRepository
from src.domain.transaction_category.services import (
    TransactionCategoryPolicyService,
    TransactionCategoryUniquenessService,
)
from src.domain.transaction_category.value_objects import TransactionCategoryName
from src.domain.value_objects import State


def test_is_owner_allows_owner(user_factory, transaction_category_factory) -> None:
    user = user_factory()
    category = transaction_category_factory(owner_id=user.user_id)

    assert TransactionCategoryPolicyService.is_owner(user, category) is None


def test_is_owner_rejects_non_owner(user_factory, transaction_category_factory) -> None:
    user = user_factory()
    category = transaction_category_factory()

    with pytest.raises(EntityPolicyError):
        TransactionCategoryPolicyService.is_owner(
            user,
            category,
        )


class InMemoryTransactionCategoryRepository(TransactionCategoryRepository):
    def __init__(self, categories) -> None:
        self._categories = categories

    async def by_owner_id_name(self, owner_id, name):
        for category in self._categories:
            if category.owner_id == owner_id and category.name == name:
                return category
        return None


async def test_name_uniqueness_allows_when_name_is_free(
    user_factory,
) -> None:
    service = TransactionCategoryUniquenessService(
        InMemoryTransactionCategoryRepository([]),
    )
    user = user_factory()

    assert (
        await service.ensure_unique(
            user,
            TransactionCategoryName("Food"),
        )
        is None
    )


async def test_name_uniqueness_rejects_when_only_deleted_categories_exist(
    user_factory,
    transaction_category_factory,
) -> None:
    user = user_factory()
    service = TransactionCategoryUniquenessService(
        InMemoryTransactionCategoryRepository(
            [
                transaction_category_factory(
                    owner_id=user.user_id,
                    name="Food",
                    state=State.DELETED,
                ),
            ],
        ),
    )

    with pytest.raises(EntityInvalidDataError):
        await service.ensure_unique(
            user,
            TransactionCategoryName("Food"),
        )


async def test_name_uniqueness_rejects_when_active_category_exists(
    user_factory,
    transaction_category_factory,
) -> None:
    user = user_factory()
    service = TransactionCategoryUniquenessService(
        InMemoryTransactionCategoryRepository(
            [
                transaction_category_factory(
                    owner_id=user.user_id,
                    name="Food",
                ),
            ],
        ),
    )

    with pytest.raises(EntityInvalidDataError):
        await service.ensure_unique(
            user,
            TransactionCategoryName("Food"),
        )
