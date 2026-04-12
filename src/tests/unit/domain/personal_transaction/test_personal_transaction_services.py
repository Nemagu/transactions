import pytest

from src.domain.errors import EntityPolicyError
from src.domain.personal_transaction.services import PersonalTransactionPolicyService


def test_is_owner_allows_owner(tenant_factory, personal_transaction_factory) -> None:
    tenant = tenant_factory()
    transaction = personal_transaction_factory(owner_id=tenant.tenant_id)

    assert PersonalTransactionPolicyService.is_owner(tenant, transaction) is None


def test_is_owner_rejects_non_owner(
    tenant_factory,
    personal_transaction_factory,
) -> None:
    tenant = tenant_factory()
    transaction = personal_transaction_factory()

    with pytest.raises(EntityPolicyError):
        PersonalTransactionPolicyService.is_owner(tenant, transaction)
