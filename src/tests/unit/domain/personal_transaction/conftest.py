from collections.abc import Callable
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from src.domain.personal_transaction.entity import PersonalTransaction
from src.domain.personal_transaction.value_objects import (
    Currency,
    MoneyAmount,
    PersonalTransactionDescription,
    PersonalTransactionID,
    PersonalTransactionName,
    PersonalTransactionTime,
    PersonalTransactionType,
)
from src.domain.transaction_category.entity import TransactionCategory
from src.domain.transaction_category.value_objects import (
    TransactionCategoryDescription,
    TransactionCategoryID,
    TransactionCategoryName,
)
from src.domain.user.value_objects import UserID
from src.domain.value_objects import State, Version


@pytest.fixture
def transaction_category_set_factory(
    user_id_factory: Callable[..., UserID],
) -> Callable[..., set[TransactionCategory]]:
    def factory(
        *,
        owner_id: UserID | None = None,
        names: tuple[str, ...] = ("Food",),
        state: State = State.ACTIVE,
    ) -> set[TransactionCategory]:
        category_owner_id = owner_id or user_id_factory()
        return {
            TransactionCategory(
                category_id=TransactionCategoryID(uuid4()),
                owner_id=category_owner_id,
                name=TransactionCategoryName(name),
                description=TransactionCategoryDescription(f"{name} description"),
                state=state,
                version=Version(1),
            )
            for name in names
        }

    return factory


@pytest.fixture
def personal_transaction_factory(
    user_id_factory: Callable[..., UserID],
    transaction_category_set_factory: Callable[..., set[TransactionCategory]],
) -> Callable[..., PersonalTransaction]:
    def factory(
        *,
        transaction_id: PersonalTransactionID | None = None,
        categories: set[TransactionCategory] | None = None,
        owner_id: UserID | None = None,
        name: str = "Coffee",
        description: str = "Morning coffee",
        transaction_type: PersonalTransactionType = PersonalTransactionType.EXPENSE,
        money_amount: MoneyAmount | None = None,
        transaction_time: PersonalTransactionTime | None = None,
        state: State = State.ACTIVE,
        version: int = 1,
    ) -> PersonalTransaction:
        transaction_owner_id = owner_id or user_id_factory()
        return PersonalTransaction(
            transaction_id=transaction_id or PersonalTransactionID(uuid4()),
            categories=categories
            or transaction_category_set_factory(owner_id=transaction_owner_id),
            owner_id=transaction_owner_id,
            name=PersonalTransactionName(name),
            description=PersonalTransactionDescription(description),
            transaction_type=transaction_type,
            money_amount=money_amount
            or MoneyAmount(amount=Decimal("100"), currency=Currency.RUBLE),
            transaction_time=transaction_time
            or PersonalTransactionTime(datetime(2026, 4, 5, 12, 0, 0)),
            state=state,
            version=Version(version),
        )

    return factory
