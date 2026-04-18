from __future__ import annotations

import pytest

from application.dto import LimitOffsetPaginator
from application.ports.repositories import TransactionCategoryEvent
from application.queries.public.transaction_category import (
    TransactionCategoryLastVersionQuery,
    TransactionCategoryLastVersionsQuery,
    TransactionCategoryLastVersionsUseCase,
    TransactionCategoryLastVersionUseCase,
    TransactionCategoryVersionQuery,
    TransactionCategoryVersionsQuery,
    TransactionCategoryVersionsUseCase,
    TransactionCategoryVersionUseCase,
)
from domain.tenant import TenantState, TenantStatus
from domain.value_objects import State


@pytest.mark.asyncio
async def test_transaction_category_queries_use_cases(
    uow_factory,
    tenant_factory,
    category_factory,
    tenant_read_repo,
    category_read_repo,
    category_version_repo,
) -> None:
    initiator = tenant_factory(status=TenantStatus.TENANT, state=TenantState.ACTIVE)
    await tenant_read_repo.save(initiator)

    category_v1 = category_factory(
        category_id=category_factory().category_id.category_id,
        owner_id=initiator.tenant_id.tenant_id,
        name="food",
        state=State.ACTIVE.value,
        version=1,
    )
    category_v2 = category_factory(
        category_id=category_v1.category_id.category_id,
        owner_id=initiator.tenant_id.tenant_id,
        name="travel",
        state=State.ACTIVE.value,
        version=2,
    )
    await category_read_repo.save(category_v1)
    await category_version_repo.save(
        category_v1, TransactionCategoryEvent.CREATED, None
    )
    await category_read_repo.save(category_v2)
    await category_version_repo.save(
        category_v2, TransactionCategoryEvent.UPDATED, None
    )

    last_versions, last_count = await TransactionCategoryLastVersionsUseCase(
        uow_factory()
    ).execute(
        TransactionCategoryLastVersionsQuery(
            initiator_id=initiator.tenant_id.tenant_id,
            paginator=LimitOffsetPaginator(limit=10, offset=0),
            category_ids=None,
            names=["travel"],
            states=[State.ACTIVE.value],
        )
    )
    last_version = await TransactionCategoryLastVersionUseCase(uow_factory()).execute(
        TransactionCategoryLastVersionQuery(
            initiator_id=initiator.tenant_id.tenant_id,
            category_id=category_v1.category_id.category_id,
        )
    )
    versions, versions_count = await TransactionCategoryVersionsUseCase(
        uow_factory()
    ).execute(
        TransactionCategoryVersionsQuery(
            initiator_id=initiator.tenant_id.tenant_id,
            paginator=LimitOffsetPaginator(limit=10, offset=0),
            category_id=category_v1.category_id.category_id,
            names=[],
            states=[],
            from_version=1,
            to_version=2,
        )
    )
    version = await TransactionCategoryVersionUseCase(uow_factory()).execute(
        TransactionCategoryVersionQuery(
            initiator_id=initiator.tenant_id.tenant_id,
            category_id=category_v1.category_id.category_id,
            version=1,
        )
    )

    assert last_count == 1
    assert len(last_versions) == 1
    assert last_versions[0].category_id == category_v1.category_id.category_id
    assert last_version.version == 2
    assert last_version.name == "travel"

    assert versions_count == 2
    assert len(versions) == 2
    assert {item.version for item in versions} == {1, 2}
    assert version.version == 1
    assert version.event == TransactionCategoryEvent.CREATED.value
