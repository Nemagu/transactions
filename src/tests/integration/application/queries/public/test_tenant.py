from __future__ import annotations

import pytest

from application.dto import LimitOffsetPaginator
from application.ports.repositories import TenantEvent
from application.queries.public.tenant import (
    TenantLastVersionQuery,
    TenantLastVersionsQuery,
    TenantLastVersionsUseCase,
    TenantLastVersionUseCase,
    TenantVersionQuery,
    TenantVersionsQuery,
    TenantVersionsUseCase,
    TenantVersionUseCase,
)
from domain.tenant import TenantState, TenantStatus


@pytest.mark.asyncio
async def test_tenant_queries_use_cases(
    uow_factory,
    tenant_factory,
    tenant_read_repo,
    tenant_version_repo,
) -> None:
    initiator = tenant_factory(status=TenantStatus.ADMIN, state=TenantState.ACTIVE)
    target_v1 = tenant_factory(
        tenant_id=tenant_factory().tenant_id.tenant_id,
        status=TenantStatus.TENANT,
        state=TenantState.ACTIVE,
        version=1,
    )
    target_v2 = tenant_factory(
        tenant_id=target_v1.tenant_id.tenant_id,
        status=TenantStatus.ADMIN,
        state=TenantState.ACTIVE,
        version=2,
    )
    await tenant_read_repo.save(initiator)
    await tenant_read_repo.save(target_v1)
    await tenant_version_repo.save(target_v1, TenantEvent.CREATED, initiator)
    await tenant_read_repo.save(target_v2)
    await tenant_version_repo.save(target_v2, TenantEvent.UPDATED, initiator)

    last_versions, last_count = await TenantLastVersionsUseCase(uow_factory()).execute(
        TenantLastVersionsQuery(
            user_id=initiator.tenant_id.tenant_id,
            paginator=LimitOffsetPaginator(limit=10, offset=0),
            tenant_ids=[target_v2.tenant_id.tenant_id],
            statuses=[TenantStatus.ADMIN.value],
            states=[TenantState.ACTIVE.value],
        )
    )
    last_version = await TenantLastVersionUseCase(uow_factory()).execute(
        TenantLastVersionQuery(
            user_id=initiator.tenant_id.tenant_id,
            tenant_id=target_v2.tenant_id.tenant_id,
        )
    )
    versions, version_count = await TenantVersionsUseCase(uow_factory()).execute(
        TenantVersionsQuery(
            user_id=initiator.tenant_id.tenant_id,
            tenant_id=target_v2.tenant_id.tenant_id,
            paginator=LimitOffsetPaginator(limit=10, offset=0),
            statuses=[],
            states=[],
            from_version=1,
            to_version=2,
        )
    )
    version = await TenantVersionUseCase(uow_factory()).execute(
        TenantVersionQuery(
            user_id=initiator.tenant_id.tenant_id,
            tenant_id=target_v2.tenant_id.tenant_id,
            version=1,
        )
    )

    assert last_count == 1
    assert len(last_versions) == 1
    assert last_versions[0].tenant_id == target_v2.tenant_id.tenant_id
    assert last_version.tenant_id == target_v2.tenant_id.tenant_id
    assert last_version.version == 2

    assert version_count == 2
    assert len(versions) == 2
    assert {item.version for item in versions} == {1, 2}
    assert version.version == 1
    assert version.event == TenantEvent.CREATED.value
