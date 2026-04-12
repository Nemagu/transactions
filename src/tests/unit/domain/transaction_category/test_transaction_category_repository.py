import pytest

from domain.transaction_category.repository import TransactionCategoryReadRepository


def test_transaction_category_repository_requires_name_lookup_implementation() -> None:
    with pytest.raises(TypeError):
        TransactionCategoryReadRepository()


def test_transaction_category_repository_can_be_instantiated_with_name_lookup() -> None:
    class StubTransactionCategoryRepository(TransactionCategoryReadRepository):
        async def by_owner_id_name(self, owner_id, name):
            return None

    repository = StubTransactionCategoryRepository()

    assert isinstance(repository, TransactionCategoryReadRepository)
