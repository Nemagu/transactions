import pytest


@pytest.mark.asyncio
async def test_get_my_tenant_returns_current_tenant(
    http_client,
    auth_headers_factory,
    tenant_factory,
    tenant_read_repo,
) -> None:
    tenant = tenant_factory()
    await tenant_read_repo.save(tenant)

    response = await http_client.get(
        "/public/v1/tenants/me",
        headers=auth_headers_factory(tenant.tenant_id.tenant_id),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["tenant_id"] == str(tenant.tenant_id.tenant_id)
    assert data["status"] == tenant.status.value
    assert data["state"] == tenant.state.value
    assert data["version"] == tenant.version.version
