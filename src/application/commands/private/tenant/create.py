from application.commands.base import BaseUseCase
from domain.tenant import Tenant, TenantCreationService
from domain.user import User


class TenantCreationUseCase(BaseUseCase):
    async def execute(self) -> None:
        async with self._uow as uow:
            users = await uow.subscription_repositories.common.users_have_no_tenants()
            if len(users) == 0:
                return
            service = TenantCreationService(uow.tenant_repositories.read)
            tenants = list()
            tenant_and_user_list: list[tuple[Tenant, User]] = list()
            for user in users:
                tenant = await service.create(user)
                tenants.append(tenant)
                tenant_and_user_list.append((tenant, user))
            await uow.tenant_repositories.read.batch_save(tenants)
            await uow.tenant_repositories.version.batch_save(tenants)
            await uow.subscription_repositories.common.batch_subscribe(
                tenant_and_user_list
            )
