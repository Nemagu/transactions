from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from src.domain.errors import ValueObjectInvalidDataError
from src.domain.personal_transaction.factory import PersonalTransactionFactory
from src.domain.personal_transaction.value_objects import (
    Currency,
    PersonalTransactionType,
)
from src.domain.value_objects import State


def test_personal_transaction_factory_new_creates_default_transaction() -> None:
    transaction_id = uuid4()
    owner_id = uuid4()
    category_id = uuid4()
    transaction_time = datetime(2026, 4, 5, 12, 0, 0)

    transaction = PersonalTransactionFactory.new(
        transaction_id=transaction_id,
        category_ids={category_id},
        owner_id=owner_id,
        name=" Coffee ",
        description="",
        transaction_type="expense",
        amount=Decimal("100"),
        currency="ruble",
        transaction_time=transaction_time,
    )

    assert transaction.transaction_id.transaction_id == transaction_id
    assert transaction.owner_id.tenant_id == owner_id
    assert {item.category_id for item in transaction.category_ids} == {category_id}
    assert transaction.name.name == "Coffee"
    assert transaction.description.description == ""
    assert transaction.transaction_type == PersonalTransactionType.EXPENSE
    assert transaction.money_amount.amount == Decimal("100")
    assert transaction.money_amount.currency == Currency.RUBLE
    assert transaction.transaction_time.transaction_time == transaction_time
    assert transaction.state == State.ACTIVE
    assert transaction.version.version == 1
    assert transaction.original_version.version == 1


def test_personal_transaction_factory_restore_recreates_transaction() -> None:
    transaction_id = uuid4()
    owner_id = uuid4()
    category_id = uuid4()
    transaction_time = datetime(2026, 4, 5, 12, 0, 0)

    transaction = PersonalTransactionFactory.restore(
        transaction_id=transaction_id,
        owner_id=owner_id,
        name="Salary",
        description="April salary",
        category_ids={category_id},
        transaction_type="income",
        amount=Decimal("2500"),
        currency="dollar",
        transaction_time=transaction_time,
        state="DELETED",
        version=3,
    )

    assert transaction.transaction_id.transaction_id == transaction_id
    assert transaction.owner_id.tenant_id == owner_id
    assert {item.category_id for item in transaction.category_ids} == {category_id}
    assert transaction.name.name == "Salary"
    assert transaction.description.description == "April salary"
    assert transaction.transaction_type == PersonalTransactionType.INCOME
    assert transaction.money_amount.amount == Decimal("2500")
    assert transaction.money_amount.currency == Currency.DOLLAR
    assert transaction.transaction_time.transaction_time == transaction_time
    assert transaction.state == State.DELETED
    assert transaction.version.version == 3
    assert transaction.original_version.version == 3


def test_personal_transaction_factory_restore_raises_error_for_invalid_type() -> None:
    with pytest.raises(ValueObjectInvalidDataError):
        PersonalTransactionFactory.restore(
            transaction_id=uuid4(),
            owner_id=uuid4(),
            name="Salary",
            description="April salary",
            category_ids={uuid4()},
            transaction_type="transfer",
            amount=Decimal("2500"),
            currency="dollar",
            transaction_time=datetime(2026, 4, 5, 12, 0, 0),
            state="active",
            version=1,
        )
