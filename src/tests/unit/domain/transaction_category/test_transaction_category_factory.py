from uuid import uuid4

import pytest

from src.domain.errors import ValueObjectInvalidDataError
from src.domain.transaction_category.factory import TransactionCategoryFactory
from src.domain.value_objects import State


def test_transaction_category_factory_new_creates_default_category() -> None:
    category_id = uuid4()
    owner_id = uuid4()

    category = TransactionCategoryFactory.new(
        category_id=category_id,
        owner_id=owner_id,
        name=" Food ",
        description="",
    )

    assert category.category_id.category_id == category_id
    assert category.owner_id.tenant_id == owner_id
    assert category.name.name == "Food"
    assert category.description.description == ""
    assert category.state == State.ACTIVE
    assert category.version.version == 1
    assert category.original_version.version == 1


def test_transaction_category_factory_restore_recreates_category() -> None:
    category_id = uuid4()
    owner_id = uuid4()

    category = TransactionCategoryFactory.restore(
        category_id=category_id,
        owner_id=owner_id,
        name="Food",
        description="Daily expenses",
        state="DELETED",
        version=3,
    )

    assert category.category_id.category_id == category_id
    assert category.owner_id.tenant_id == owner_id
    assert category.name.name == "Food"
    assert category.description.description == "Daily expenses"
    assert category.state == State.DELETED
    assert category.version.version == 3
    assert category.original_version.version == 3


def test_transaction_category_factory_restore_raises_error_for_invalid_state() -> None:
    with pytest.raises(ValueObjectInvalidDataError):
        TransactionCategoryFactory.restore(
            category_id=uuid4(),
            owner_id=uuid4(),
            name="Food",
            description="Daily expenses",
            state="archived",
            version=1,
        )
