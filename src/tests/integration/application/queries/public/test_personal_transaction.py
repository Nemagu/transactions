from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import pytest

from application.dto import LimitOffsetPaginator, MoneyAmountDTO
from application.ports.repositories import PersonalTransactionEvent
from application.queries.public.personal_transaction import (
    PersonalTransactionLastVersionQuery,
    PersonalTransactionLastVersionsQuery,
    PersonalTransactionLastVersionsUseCase,
    PersonalTransactionLastVersionUseCase,
    PersonalTransactionVersionQuery,
    PersonalTransactionVersionsQuery,
    PersonalTransactionVersionsUseCase,
    PersonalTransactionVersionUseCase,
)
from domain.personal_transaction import PersonalTransactionType
from domain.tenant import TenantState, TenantStatus
from domain.value_objects import State


@pytest.mark.asyncio
async def test_personal_transaction_queries_use_cases(
    uow_factory,
    tenant_factory,
    category_factory,
    transaction_factory,
    tenant_read_repo,
    category_read_repo,
    transaction_read_repo,
    transaction_version_repo,
) -> None:
    initiator = tenant_factory(status=TenantStatus.TENANT, state=TenantState.ACTIVE)
    await tenant_read_repo.save(initiator)

    first_category = category_factory(
        owner_id=initiator.tenant_id.tenant_id, name="food"
    )
    second_category = category_factory(
        owner_id=initiator.tenant_id.tenant_id,
        name="travel",
    )
    await category_read_repo.save(first_category)
    await category_read_repo.save(second_category)

    transaction_id = transaction_factory().transaction_id.transaction_id
    transaction_v1 = transaction_factory(
        transaction_id=transaction_id,
        owner_id=initiator.tenant_id.tenant_id,
        category_ids={first_category.category_id.category_id},
        transaction_type=PersonalTransactionType.EXPENSE,
        amount=Decimal("100.00"),
        transaction_time=datetime(2026, 4, 18, 12, 0, 0),
        version=1,
    )
    transaction_v2 = transaction_factory(
        transaction_id=transaction_id,
        owner_id=initiator.tenant_id.tenant_id,
        category_ids={
            first_category.category_id.category_id,
            second_category.category_id.category_id,
        },
        transaction_type=PersonalTransactionType.INCOME,
        amount=Decimal("200.00"),
        transaction_time=datetime(2026, 4, 18, 13, 0, 0),
        version=2,
    )
    await transaction_read_repo.save(transaction_v1)
    await transaction_version_repo.save(
        transaction_v1, PersonalTransactionEvent.CREATED, None
    )
    await transaction_read_repo.save(transaction_v2)
    await transaction_version_repo.save(
        transaction_v2, PersonalTransactionEvent.UPDATED, None
    )

    last_versions, last_count = await PersonalTransactionLastVersionsUseCase(
        uow_factory()
    ).execute(
        PersonalTransactionLastVersionsQuery(
            initiator_id=initiator.tenant_id.tenant_id,
            paginator=LimitOffsetPaginator(limit=10, offset=0),
            transaction_ids=[],
            category_ids=[],
            transaction_types=[PersonalTransactionType.INCOME.value],
            from_money_amount=MoneyAmountDTO(amount=Decimal("0.00"), currency="ruble"),
            to_money_amount=MoneyAmountDTO(amount=Decimal("300.00"), currency="ruble"),
            from_transaction_time=datetime(2026, 4, 18, 11, 0, 0),
            to_transaction_time=datetime(2026, 4, 18, 14, 0, 0),
            states=[State.ACTIVE.value],
        )
    )
    last_version = await PersonalTransactionLastVersionUseCase(uow_factory()).execute(
        PersonalTransactionLastVersionQuery(
            initiator_id=initiator.tenant_id.tenant_id,
            transaction_id=transaction_id,
        )
    )
    versions, versions_count = await PersonalTransactionVersionsUseCase(
        uow_factory()
    ).execute(
        PersonalTransactionVersionsQuery(
            initiator_id=initiator.tenant_id.tenant_id,
            paginator=LimitOffsetPaginator(limit=10, offset=0),
            transaction_id=transaction_id,
            category_ids=[],
            transaction_types=[],
            from_money_amount=MoneyAmountDTO(
                amount=Decimal("100.00"), currency="ruble"
            ),
            to_money_amount=MoneyAmountDTO(amount=Decimal("300.00"), currency="ruble"),
            from_transaction_time=datetime(2026, 4, 18, 11, 0, 0),
            to_transaction_time=datetime(2026, 4, 18, 14, 0, 0),
            states=[State.ACTIVE.value],
            from_version=1,
            to_version=2,
        )
    )
    version = await PersonalTransactionVersionUseCase(uow_factory()).execute(
        PersonalTransactionVersionQuery(
            initiator_id=initiator.tenant_id.tenant_id,
            transaction_id=transaction_id,
            version=1,
        )
    )

    assert last_count == 1
    assert len(last_versions) == 1
    assert last_versions[0].transaction_id == transaction_id
    assert last_versions[0].version == 2
    assert last_version.version == 2
    assert last_version.transaction_type == PersonalTransactionType.INCOME.value

    assert versions_count == 2
    assert len(versions) == 2
    assert {item.version for item in versions} == {1, 2}
    assert version.version == 1
    assert version.event == PersonalTransactionEvent.CREATED.value
