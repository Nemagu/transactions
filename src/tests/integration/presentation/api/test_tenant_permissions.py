from uuid import uuid7

import pytest

from domain.tenant import TenantState, TenantStatus


@pytest.mark.asyncio
async def test_appoint_admin_returns_404_when_target_tenant_not_exists(
    http_client,
    auth_headers_factory,
    tenant_factory,
    tenant_read_repo,
) -> None:
    initiator = tenant_factory(status=TenantStatus.ADMIN)
    await tenant_read_repo.save(initiator)

    missing_tenant_id = uuid7()
    response = await http_client.put(
        f"/public/v1/tenants/{missing_tenant_id}/appoint-admin",
        headers=auth_headers_factory(initiator.tenant_id.tenant_id),
    )

    assert response.status_code == 404
    payload = response.json()
    assert "арендатор" in payload["detail"]
    assert payload["data"]["tenant"]["tenant_id"] == str(missing_tenant_id)


@pytest.mark.asyncio
async def test_appoint_admin_returns_403_when_initiator_has_not_enough_rights(
    http_client,
    auth_headers_factory,
    tenant_factory,
    tenant_read_repo,
) -> None:
    initiator = tenant_factory(status=TenantStatus.TENANT, state=TenantState.ACTIVE)
    target_tenant = tenant_factory()
    await tenant_read_repo.save(initiator)
    await tenant_read_repo.save(target_tenant)

    response = await http_client.put(
        f"/public/v1/tenants/{target_tenant.tenant_id.tenant_id}/appoint-admin",
        headers=auth_headers_factory(initiator.tenant_id.tenant_id),
    )

    assert response.status_code == 403
    payload = response.json()
    assert payload["detail"] == "вы не являетесь администратором"
