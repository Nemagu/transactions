from src.domain.errors import EntityAlreadyExistsError
from src.domain.tenant import Tenant
from src.domain.tenant.factory import TenantFactory
from src.domain.tenant.repository import TenantReadRepository
from src.domain.tenant.value_objects import TenantID
from src.domain.user import User


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
                    "tenant": {"tenant_id": str(existing_tenant.tenant_id.tenant_id)},
                    "user": {"user_id": str(user.user_id.user_id)},
                },
            )
        tenant = TenantFactory.new(user.user_id.user_id, user.state.value)
        return tenant
