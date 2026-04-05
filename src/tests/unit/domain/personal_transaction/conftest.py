from collections.abc import Callable
from datetime import datetime
from decimal import Decimal

import pytest

from domain.personal_transaction.entity import PersonalTransaction
from domain.personal_transaction.value_objects import (
    Currency,
    MoneyAmount,
    PersonalTransactionDescription,
    PersonalTransactionID,
    PersonalTransactionName,
    PersonalTransactionState,
    PersonalTransactionTime,
    PersonalTransactionType,
)
from domain.transaction_category.value_objects import TransactionCategoryID
from domain.user.value_objects import UserID
from domain.value_objects import Version


@pytest.fixture
def personal_transaction_factory(
    user_id_factory: Callable[..., UserID],
) -> Callable[..., PersonalTransaction]:
    def factory(
        *,
        transaction_id: PersonalTransactionID | None = None,
        owner_id: UserID | None = None,
        name: str = "Coffee",
        description: str = "Morning coffee",
        category_ids: set[TransactionCategoryID] | None = None,
        transaction_type: PersonalTransactionType = PersonalTransactionType.EXPENSE,
        money_amount: MoneyAmount | None = None,
        transaction_time: PersonalTransactionTime | None = None,
        state: PersonalTransactionState = PersonalTransactionState.ACTIVE,
        version: int = 1,
    ) -> PersonalTransaction:
        return PersonalTransaction(
            transaction_id=transaction_id or PersonalTransactionID(user_id_factory().user_id),
            owner_id=owner_id or user_id_factory(),
            name=PersonalTransactionName(name),
            description=PersonalTransactionDescription(description),
            category_ids=category_ids or {TransactionCategoryID(user_id_factory().user_id)},
            transaction_type=transaction_type,
            money_amount=money_amount
            or MoneyAmount(amount=Decimal("100"), currency=Currency.RUBLE),
            transaction_time=transaction_time
            or PersonalTransactionTime(datetime(2026, 4, 5, 12, 0, 0)),
            state=state,
            version=Version(version),
        )

    return factory
