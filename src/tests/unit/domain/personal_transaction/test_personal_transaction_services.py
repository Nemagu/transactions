import pytest

from src.domain.errors import EntityPolicyError
from src.domain.personal_transaction.services import PersonalTransactionPolicyService


def test_is_owner_allows_owner(user_factory, personal_transaction_factory) -> None:
    user = user_factory()
    transaction = personal_transaction_factory(owner_id=user.user_id)

    assert PersonalTransactionPolicyService.is_owner(user, transaction) is None


def test_is_owner_rejects_non_owner(user_factory, personal_transaction_factory) -> None:
    user = user_factory()
    transaction = personal_transaction_factory()

    with pytest.raises(EntityPolicyError):
        PersonalTransactionPolicyService.is_owner(
            user,
            transaction,
        )
