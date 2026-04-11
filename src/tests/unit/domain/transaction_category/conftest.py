from collections.abc import Callable
from uuid import uuid4

import pytest

from src.domain.transaction_category.entity import TransactionCategory
from src.domain.transaction_category.value_objects import (
    TransactionCategoryDescription,
    TransactionCategoryID,
    TransactionCategoryName,
)
from src.domain.user.value_objects import UserID
from src.domain.value_objects import State, Version


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
        state: State = State.ACTIVE,
        version: int = 1,
    ) -> TransactionCategory:
        return TransactionCategory(
            category_id=category_id or TransactionCategoryID(uuid4()),
            owner_id=owner_id or user_id_factory(),
            name=TransactionCategoryName(name),
            description=TransactionCategoryDescription(description),
            state=state,
            version=Version(version),
        )

    return factory
