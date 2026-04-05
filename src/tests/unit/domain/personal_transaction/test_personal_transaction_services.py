import pytest

from domain.personal_transaction.errors import PersonalTransactionPolicyError
from domain.personal_transaction.services import PersonalTransactionPolicyService
from domain.personal_transaction.value_objects import PersonalTransactionState


def test_is_owner_allows_owner(user_id_factory) -> None:
    user_id = user_id_factory()

    assert PersonalTransactionPolicyService.is_owner(user_id, user_id) is None


def test_is_owner_rejects_non_owner(user_id_factory) -> None:
    with pytest.raises(PersonalTransactionPolicyError):
        PersonalTransactionPolicyService.is_owner(
            user_id_factory(),
            user_id_factory(),
        )


def test_can_edit_allows_active_transaction(personal_transaction_factory) -> None:
    transaction = personal_transaction_factory()

    assert PersonalTransactionPolicyService.can_edit(transaction) is None


def test_can_edit_rejects_deleted_transaction(personal_transaction_factory) -> None:
    transaction = personal_transaction_factory(state=PersonalTransactionState.DELETED)

    with pytest.raises(PersonalTransactionPolicyError):
        PersonalTransactionPolicyService.can_edit(transaction)
