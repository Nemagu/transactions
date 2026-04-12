import pytest

from domain.errors import EntityAlreadyExistsError
from domain.tenant.repository import TenantReadRepository
from domain.tenant.services import TenantCreationService
from domain.tenant.value_objects import TenantID


class InMemoryTenantRepository(TenantReadRepository):
    def __init__(self, tenant) -> None:
        self._tenant = tenant

    async def by_id(self, tenant_id):
        if self._tenant and self._tenant.tenant_id == tenant_id:
            return self._tenant
        return None


@pytest.mark.asyncio
async def test_tenant_creation_service_creates_tenant_from_user(user_factory) -> None:
    user = user_factory()
    service = TenantCreationService(InMemoryTenantRepository(None))

    tenant = await service.create(user)

    assert tenant.tenant_id.tenant_id == user.user_id.user_id
    assert tenant.state.value == user.state.value


@pytest.mark.asyncio
async def test_tenant_creation_service_rejects_existing_tenant(
    user_factory,
    tenant_factory,
) -> None:
    user = user_factory()
    tenant = tenant_factory(tenant_id=TenantID(user.user_id.user_id))
    service = TenantCreationService(InMemoryTenantRepository(tenant))

    with pytest.raises(EntityAlreadyExistsError):
        await service.create(user)
