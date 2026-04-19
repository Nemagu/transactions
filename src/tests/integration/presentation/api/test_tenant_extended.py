from __future__ import annotations

import pytest

from application.ports.repositories import TenantEvent
from domain.tenant import TenantStatus


@pytest.mark.asyncio
async def test_tenant_router_supports_list_versions_and_appointments(
    http_client,
    auth_headers_factory,
    tenant_factory,
    tenant_read_repo,
    tenant_version_repo,
) -> None:
    initiator = tenant_factory(status=TenantStatus.ADMIN)
    target = tenant_factory(status=TenantStatus.TENANT)
    await tenant_read_repo.save(initiator)
    await tenant_read_repo.save(target)
    await tenant_version_repo.save(target, TenantEvent.CREATED, None)

    headers = auth_headers_factory(initiator.tenant_id.tenant_id)

    list_response = await http_client.get(
        "/public/v1/tenants",
        headers=headers,
        params=[("tenant_id", str(target.tenant_id.tenant_id))],
    )
    assert list_response.status_code == 200
    assert list_response.json()["count"] >= 1

    by_id_response = await http_client.get(
        f"/public/v1/tenants/{target.tenant_id.tenant_id}",
        headers=headers,
    )
    assert by_id_response.status_code == 200
    assert by_id_response.json()["tenant_id"] == str(target.tenant_id.tenant_id)

    appoint_admin_response = await http_client.put(
        f"/public/v1/tenants/{target.tenant_id.tenant_id}/appoint-admin",
        headers=headers,
    )
    assert appoint_admin_response.status_code == 200

    appoint_tenant_response = await http_client.put(
        f"/public/v1/tenants/{target.tenant_id.tenant_id}/appoint-tenant",
        headers=headers,
    )
    assert appoint_tenant_response.status_code == 200

    versions_response = await http_client.get(
        f"/public/v1/tenants/versions/{target.tenant_id.tenant_id}",
        headers=headers,
    )
    assert versions_response.status_code == 200
    assert versions_response.json()["count"] >= 3

    version_response = await http_client.get(
        f"/public/v1/tenants/versions/{target.tenant_id.tenant_id}/1",
        headers=headers,
    )
    assert version_response.status_code == 200
    assert version_response.json()["tenant_id"] == str(target.tenant_id.tenant_id)
