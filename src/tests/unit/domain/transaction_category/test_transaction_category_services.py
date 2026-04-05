import pytest

from domain.transaction_category.errors import (
    TransactionCategoryInvalidDataError,
    TransactionCategoryPolicyError,
)
from domain.transaction_category.repository import TransactionCategoryRepository
from domain.transaction_category.services import (
    TransactionCategoryNameUniquenessService,
    TransactionCategoryPolicyService,
)
from domain.transaction_category.value_objects import (
    TransactionCategoryName,
    TransactionCategoryState,
)


def test_is_owner_allows_owner(user_id_factory) -> None:
    user_id = user_id_factory()

    assert TransactionCategoryPolicyService.is_owner(user_id, user_id) is None


def test_is_owner_rejects_non_owner(user_id_factory) -> None:
    with pytest.raises(TransactionCategoryPolicyError):
        TransactionCategoryPolicyService.is_owner(
            user_id_factory(),
            user_id_factory(),
        )


def test_can_edit_allows_active_category(transaction_category_factory) -> None:
    category = transaction_category_factory()

    assert TransactionCategoryPolicyService.can_edit(category) is None


def test_can_edit_rejects_deleted_category(transaction_category_factory) -> None:
    category = transaction_category_factory(state=TransactionCategoryState.DELETED)

    with pytest.raises(TransactionCategoryPolicyError):
        TransactionCategoryPolicyService.can_edit(category)


class InMemoryTransactionCategoryRepository(TransactionCategoryRepository):
    def __init__(self, categories) -> None:
        self._categories = categories

    async def by_owner_id_and_name(self, owner_id, name):
        return [
            category
            for category in self._categories
            if category.owner_id == owner_id and category.name == name
        ]


async def test_name_uniqueness_allows_when_name_is_free(
    user_id_factory,
) -> None:
    service = TransactionCategoryNameUniquenessService(
        InMemoryTransactionCategoryRepository([]),
    )

    assert await service.ensure_unique(
        user_id_factory(),
        TransactionCategoryName("Food"),
    ) is None


async def test_name_uniqueness_allows_when_only_deleted_categories_exist(
    user_id_factory,
    transaction_category_factory,
) -> None:
    owner_id = user_id_factory()
    service = TransactionCategoryNameUniquenessService(
        InMemoryTransactionCategoryRepository(
                [
                    transaction_category_factory(
                        owner_id=owner_id,
                        name="Food",
                        state=TransactionCategoryState.DELETED,
                    ),
                ],
            ),
        )

    assert await service.ensure_unique(
        owner_id,
        TransactionCategoryName("Food"),
    ) is None


async def test_name_uniqueness_rejects_when_active_category_exists(
    user_id_factory,
    transaction_category_factory,
) -> None:
    owner_id = user_id_factory()
    service = TransactionCategoryNameUniquenessService(
        InMemoryTransactionCategoryRepository(
            [
                transaction_category_factory(
                    owner_id=owner_id,
                    name="Food",
                ),
            ],
        ),
    )

    with pytest.raises(TransactionCategoryInvalidDataError):
        await service.ensure_unique(
            owner_id,
            TransactionCategoryName("Food"),
        )
