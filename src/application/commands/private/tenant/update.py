from application.commands.base import BaseUseCase
from domain.errors import EntityIdempotentError
from domain.tenant import TenantState


class TenantUpdateUseCase(BaseUseCase):
    async def execute(self) -> None:
        async with self._uow as uow:
            tenant_match_user = await uow.subscription_repositories.common.new_users_versions_for_tenants()
            if len(tenant_match_user) == 0:
                return
            for tenant, user in tenant_match_user:
                try:
                    tenant.new_state(TenantState.from_str(user.state.value))
                except EntityIdempotentError:
                    pass
            await uow.tenant_repositories.read.batch_save(
                [matching[0] for matching in tenant_match_user]
            )
            await uow.tenant_repositories.version.batch_save(
                [matching[0] for matching in tenant_match_user]
            )
            await uow.subscription_repositories.common.batch_processed_version(
                tenant_match_user
            )
