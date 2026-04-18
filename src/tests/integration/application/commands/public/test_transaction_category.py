from __future__ import annotations

import pytest

from application.commands.public.transaction_category import (
    TransactionCategoryCreationCommand,
    TransactionCategoryCreationUseCase,
    TransactionCategoryDeletionCommand,
    TransactionCategoryDeletionUseCase,
    TransactionCategoryRestorationCommand,
    TransactionCategoryRestorationUseCase,
    TransactionCategoryUpdateCommand,
    TransactionCategoryUpdateUseCase,
)
from application.ports.repositories import TransactionCategoryEvent
from domain.tenant import TenantState, TenantStatus
from domain.transaction_category import TransactionCategoryID
from domain.value_objects import State, Version


@pytest.mark.asyncio
async def test_transaction_category_public_commands_flow(
    uow_factory,
    tenant_factory,
    tenant_read_repo,
    category_read_repo,
    category_version_repo,
) -> None:
    initiator = tenant_factory(status=TenantStatus.TENANT, state=TenantState.ACTIVE)
    await tenant_read_repo.save(initiator)

    created = await TransactionCategoryCreationUseCase(uow_factory()).execute(
        TransactionCategoryCreationCommand(
            user_id=initiator.tenant_id.tenant_id,
            name="food",
            description="base",
        )
    )
    updated = await TransactionCategoryUpdateUseCase(uow_factory()).execute(
        TransactionCategoryUpdateCommand(
            user_id=initiator.tenant_id.tenant_id,
            category_id=created.category_id,
            name="travel",
            description="updated",
        )
    )
    deleted = await TransactionCategoryDeletionUseCase(uow_factory()).execute(
        TransactionCategoryDeletionCommand(
            user_id=initiator.tenant_id.tenant_id,
            category_id=created.category_id,
        )
    )
    restored = await TransactionCategoryRestorationUseCase(uow_factory()).execute(
        TransactionCategoryRestorationCommand(
            user_id=initiator.tenant_id.tenant_id,
            category_id=created.category_id,
        )
    )

    assert created.version == 1
    assert updated.version == 2
    assert deleted.version == 3
    assert deleted.state == State.DELETED.value
    assert restored.version == 4
    assert restored.state == State.ACTIVE.value

    latest = await category_read_repo.by_id(
        category_id=TransactionCategoryID(created.category_id)
    )
    assert latest is not None
    assert latest.version.version == 4
    assert latest.state == State.ACTIVE

    events = {
        1: TransactionCategoryEvent.CREATED,
        2: TransactionCategoryEvent.UPDATED,
        3: TransactionCategoryEvent.DELETED,
        4: TransactionCategoryEvent.RESTORED,
    }
    for version, event in events.items():
        stored = await category_version_repo.by_id_version(
            latest.category_id,
            Version(version),
        )
        assert stored is not None
        assert stored[1] == event
