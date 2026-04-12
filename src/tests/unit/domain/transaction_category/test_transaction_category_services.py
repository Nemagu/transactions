import pytest

from domain.errors import EntityAlreadyExistsError, EntityPolicyError
from domain.transaction_category.repository import TransactionCategoryReadRepository
from domain.transaction_category.services import (
    TransactionCategoryPolicyService,
    TransactionCategoryUniquenessService,
)
from domain.transaction_category.value_objects import TransactionCategoryName
from domain.value_objects import State


def test_is_owner_allows_owner(tenant_factory, transaction_category_factory) -> None:
    tenant = tenant_factory()
    category = transaction_category_factory(owner_id=tenant.tenant_id)

    assert TransactionCategoryPolicyService.is_owner(tenant, category) is None


def test_is_owner_rejects_non_owner(
    tenant_factory, transaction_category_factory
) -> None:
    tenant = tenant_factory()
    category = transaction_category_factory()

    with pytest.raises(EntityPolicyError) as error:
        TransactionCategoryPolicyService.is_owner(tenant, category)

    assert error.value.data["tenant"]["tenant_id"] == tenant.tenant_id.tenant_id
    assert error.value.data["category"]["category_id"] == category.category_id.category_id
    assert error.value.data["category"]["owner_id"] == category.owner_id.tenant_id


class InMemoryTransactionCategoryRepository(TransactionCategoryReadRepository):
    def __init__(self, categories) -> None:
        self._categories = categories

    async def by_owner_id_name(self, owner_id, name):
        for category in self._categories:
            if category.owner_id == owner_id and category.name == name:
                return category
        return None


@pytest.mark.asyncio
async def test_name_uniqueness_allows_when_name_is_free(
    tenant_factory,
) -> None:
    service = TransactionCategoryUniquenessService(
        InMemoryTransactionCategoryRepository([]),
    )
    tenant = tenant_factory()

    assert await service.ensure_unique(tenant, TransactionCategoryName("Food")) is None


@pytest.mark.asyncio
async def test_name_uniqueness_rejects_when_only_deleted_categories_exist(
    tenant_factory,
    transaction_category_factory,
) -> None:
    tenant = tenant_factory()
    service = TransactionCategoryUniquenessService(
        InMemoryTransactionCategoryRepository(
            [
                transaction_category_factory(
                    owner_id=tenant.tenant_id,
                    name="Food",
                    state=State.DELETED,
                ),
            ],
        ),
    )

    with pytest.raises(EntityAlreadyExistsError):
        await service.ensure_unique(tenant, TransactionCategoryName("Food"))


@pytest.mark.asyncio
async def test_name_uniqueness_rejects_when_active_category_exists(
    tenant_factory,
    transaction_category_factory,
) -> None:
    tenant = tenant_factory()
    service = TransactionCategoryUniquenessService(
        InMemoryTransactionCategoryRepository(
            [
                transaction_category_factory(
                    owner_id=tenant.tenant_id,
                    name="Food",
                ),
            ],
        ),
    )

    with pytest.raises(EntityAlreadyExistsError):
        await service.ensure_unique(tenant, TransactionCategoryName("Food"))
