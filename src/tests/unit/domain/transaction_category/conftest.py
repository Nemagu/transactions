from collections.abc import Callable

import pytest

from domain.transaction_category.entity import TransactionCategory
from domain.transaction_category.value_objects import (
    TransactionCategoryDescription,
    TransactionCategoryID,
    TransactionCategoryName,
    TransactionCategoryState,
)
from domain.user.value_objects import UserID
from domain.value_objects import Version


@pytest.fixture
def transaction_category_factory(
    user_id_factory: Callable[..., UserID],
) -> Callable[..., TransactionCategory]:
    def factory(
        *,
        category_id: TransactionCategoryID | None = None,
        owner_id: UserID | None = None,
        name: str = "Food",
        description: str = "Daily expenses",
        state: TransactionCategoryState = TransactionCategoryState.ACTIVE,
        version: int = 1,
    ) -> TransactionCategory:
        return TransactionCategory(
            category_id=category_id or TransactionCategoryID(user_id_factory().user_id),
            owner_id=owner_id or user_id_factory(),
            name=TransactionCategoryName(name),
            description=TransactionCategoryDescription(description),
            state=state,
            version=Version(version),
        )

    return factory
