from collections.abc import Callable
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from domain.personal_transaction.entity import PersonalTransaction
from domain.personal_transaction.value_objects import (
    Currency,
    MoneyAmount,
    PersonalTransactionDescription,
    PersonalTransactionID,
    PersonalTransactionName,
    PersonalTransactionTime,
    PersonalTransactionType,
)
from domain.tenant.value_objects import TenantID
from domain.transaction_category.entity import TransactionCategory
from domain.transaction_category.value_objects import (
    TransactionCategoryDescription,
    TransactionCategoryID,
    TransactionCategoryName,
)
from domain.value_objects import State, Version


@pytest.fixture
def transaction_category_set_factory() -> Callable[..., set[TransactionCategory]]:
    def factory(
        *,
        owner_id: TenantID,
        names: tuple[str, ...] = ("Food",),
        state: State = State.ACTIVE,
    ) -> set[TransactionCategory]:
        return {
            TransactionCategory(
                category_id=TransactionCategoryID(uuid4()),
                owner_id=owner_id,
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
    tenant_id_factory: Callable[..., TenantID],
    transaction_category_set_factory: Callable[..., set[TransactionCategory]],
) -> Callable[..., PersonalTransaction]:
    def factory(
        *,
        transaction_id: PersonalTransactionID | None = None,
        category_ids: set[TransactionCategoryID] | None = None,
        owner_id: TenantID | None = None,
        name: str = "Coffee",
        description: str = "Morning coffee",
        transaction_type: PersonalTransactionType = PersonalTransactionType.EXPENSE,
        money_amount: MoneyAmount | None = None,
        transaction_time: PersonalTransactionTime | None = None,
        state: State = State.ACTIVE,
        version: int = 1,
    ) -> PersonalTransaction:
        transaction_owner_id = owner_id or tenant_id_factory()
        ids = category_ids
        if ids is None:
            categories = transaction_category_set_factory(owner_id=transaction_owner_id)
            ids = {category.category_id for category in categories}
        return PersonalTransaction(
            transaction_id=transaction_id or PersonalTransactionID(uuid4()),
            category_ids=ids,
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
