from domain.errors import EntityAlreadyExistsError
from domain.tenant import Tenant
from domain.tenant.factory import TenantFactory
from domain.tenant.repository import TenantReadRepository
from domain.tenant.value_objects import TenantID
from domain.user import User


class TenantCreationService:
    def __init__(self, read_repository: TenantReadRepository) -> None:
        self._read_repo = read_repository

    async def create(self, user: User) -> Tenant:
        existing_tenant = await self._read_repo.by_id(TenantID(user.user_id.user_id))
        if existing_tenant:
            raise EntityAlreadyExistsError(
                msg="арендатор для пользователя уже существует",
                struct_name=existing_tenant.aggregate_name.name,
                data={
                    "tenant": {"tenant_id": existing_tenant.tenant_id.tenant_id},
                    "user": {"user_id": user.user_id.user_id},
                },
            )
        tenant = TenantFactory.new(user.user_id.user_id, user.state.value)
        return tenant
