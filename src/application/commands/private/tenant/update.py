from application.commands.base import BaseUseCase
from application.ports.repositories import TenantEvent
from domain.errors import EntityIdempotentError
from domain.tenant import Tenant, TenantState


class TenantUpdateUseCase(BaseUseCase):
    async def execute(self) -> None:
        async with self._uow as uow:
            tenant_match_user = (
                await uow.tenant_repositories.subscription.new_users_versions()
            )
            if len(tenant_match_user) == 0:
                return
            edited_tenants_and_events: list[
                tuple[Tenant, TenantEvent, Tenant | None]
            ] = list()
            for tenant, user in tenant_match_user:
                try:
                    state = TenantState.from_str(user.state.value)
                    tenant.new_state(state)
                    match state:
                        case TenantState.ACTIVE:
                            event = TenantEvent.RESTORED
                        case TenantState.FROZEN:
                            event = TenantEvent.FROZEN
                        case TenantState.DELETED:
                            event = TenantEvent.DELETED
                    edited_tenants_and_events.append((tenant, event, None))
                except EntityIdempotentError:
                    pass
            if edited_tenants_and_events:
                await uow.tenant_repositories.read.batch_save(
                    [matching[0] for matching in edited_tenants_and_events]
                )
                await uow.tenant_repositories.version.batch_save(
                    edited_tenants_and_events
                )
            await uow.tenant_repositories.subscription.batch_processed_version(
                tenant_match_user
            )
