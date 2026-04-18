from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import pytest

from application.commands.public.personal_transaction import (
    PersonalTransactionCreationCommand,
    PersonalTransactionCreationUseCase,
    PersonalTransactionDeletionCommand,
    PersonalTransactionDeletionUseCase,
    PersonalTransactionRestorationCommand,
    PersonalTransactionRestorationUseCase,
    PersonalTransactionUpdateCommand,
    PersonalTransactionUpdateUseCase,
)
from application.dto import MoneyAmountDTO
from application.ports.repositories import PersonalTransactionEvent
from domain.personal_transaction import PersonalTransactionID, PersonalTransactionType
from domain.tenant import TenantState, TenantStatus
from domain.value_objects import State, Version


@pytest.mark.asyncio
async def test_personal_transaction_public_commands_flow(
    uow_factory,
    tenant_factory,
    category_factory,
    tenant_read_repo,
    category_read_repo,
    transaction_read_repo,
    transaction_version_repo,
) -> None:
    initiator = tenant_factory(status=TenantStatus.TENANT, state=TenantState.ACTIVE)
    await tenant_read_repo.save(initiator)

    first_category = category_factory(owner_id=initiator.tenant_id.tenant_id, name="food")
    second_category = category_factory(
        owner_id=initiator.tenant_id.tenant_id,
        name="travel",
    )
    await category_read_repo.save(first_category)
    await category_read_repo.save(second_category)

    created = await PersonalTransactionCreationUseCase(uow_factory()).execute(
        PersonalTransactionCreationCommand(
            user_id=initiator.tenant_id.tenant_id,
            category_ids={first_category.category_id.category_id},
            transaction_type=PersonalTransactionType.EXPENSE.value,
            money_amount=MoneyAmountDTO(amount=Decimal("100.00"), currency="ruble"),
            transaction_time=datetime(2026, 4, 18, 12, 0, 0),
            name="purchase",
            description="base",
        )
    )
    updated = await PersonalTransactionUpdateUseCase(uow_factory()).execute(
        PersonalTransactionUpdateCommand(
            user_id=initiator.tenant_id.tenant_id,
            transaction_id=created.transaction_id,
            category_ids=None,
            add_category_ids={second_category.category_id.category_id},
            remove_category_ids=None,
            transaction_type=None,
            money_amount=MoneyAmountDTO(amount=Decimal("120.00"), currency="ruble"),
            transaction_time=None,
            name="purchase-updated",
            description=None,
        )
    )
    deleted = await PersonalTransactionDeletionUseCase(uow_factory()).execute(
        PersonalTransactionDeletionCommand(
            user_id=initiator.tenant_id.tenant_id,
            transaction_id=created.transaction_id,
        )
    )
    restored = await PersonalTransactionRestorationUseCase(uow_factory()).execute(
        PersonalTransactionRestorationCommand(
            user_id=initiator.tenant_id.tenant_id,
            transaction_id=created.transaction_id,
        )
    )

    assert created.version == 1
    assert updated.version == 2
    assert deleted.version == 3
    assert deleted.state == State.DELETED.value
    assert restored.version == 4
    assert restored.state == State.ACTIVE.value
    assert set(updated.category_ids) == {
        first_category.category_id.category_id,
        second_category.category_id.category_id,
    }

    latest = await transaction_read_repo.by_id(PersonalTransactionID(created.transaction_id))
    assert latest is not None
    assert latest.version.version == 4
    assert latest.state == State.ACTIVE

    events = {
        1: PersonalTransactionEvent.CREATED,
        2: PersonalTransactionEvent.UPDATED,
        3: PersonalTransactionEvent.DELETED,
        4: PersonalTransactionEvent.RESTORED,
    }
    for version, event in events.items():
        stored = await transaction_version_repo.by_id_version(
            latest.transaction_id,
            Version(version),
        )
        assert stored is not None
        assert stored[1] == event

