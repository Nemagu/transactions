import pytest

from domain.tenant.repository import TenantReadRepository


def test_tenant_repository_requires_by_id_implementation() -> None:
    with pytest.raises(TypeError):
        TenantReadRepository()


def test_tenant_repository_can_be_instantiated_with_by_id() -> None:
    class StubTenantRepository(TenantReadRepository):
        async def by_id(self, tenant_id):
            return None

    repository = StubTenantRepository()

    assert isinstance(repository, TenantReadRepository)
