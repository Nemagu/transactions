import pytest

from src.domain.transaction_category.repository import TransactionCategoryRepository


def test_transaction_category_repository_requires_name_lookup_implementation() -> None:
    with pytest.raises(TypeError):
        TransactionCategoryRepository()


def test_transaction_category_repository_can_be_instantiated_with_name_lookup() -> None:
    class StubTransactionCategoryRepository(TransactionCategoryRepository):
        async def by_owner_id_name(self, owner_id, name):
            return None

    repository = StubTransactionCategoryRepository()

    assert isinstance(repository, TransactionCategoryRepository)
