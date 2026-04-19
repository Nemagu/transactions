from __future__ import annotations

from uuid import UUID

import pytest


@pytest.mark.asyncio
async def test_transaction_category_router_supports_mutations_and_versions(
    http_client,
    auth_headers_factory,
    tenant_factory,
    tenant_read_repo,
) -> None:
    tenant = tenant_factory()
    await tenant_read_repo.save(tenant)
    headers = auth_headers_factory(tenant.tenant_id.tenant_id)

    create_response = await http_client.post(
        "/public/v1/transaction-categories",
        headers=headers,
        json={"name": "food", "description": "daily"},
    )
    assert create_response.status_code == 200
    category_id = UUID(create_response.json())

    update_response = await http_client.put(
        f"/public/v1/transaction-categories/{category_id}",
        headers=headers,
        json={"name": "food-updated"},
    )
    assert update_response.status_code == 200

    by_id_response = await http_client.get(
        f"/public/v1/transaction-categories/{category_id}",
        headers=headers,
    )
    assert by_id_response.status_code == 200
    assert by_id_response.json()["name"] == "food-updated"

    versions_response = await http_client.get(
        f"/public/v1/transaction-categories/versions/{category_id}",
        headers=headers,
    )
    assert versions_response.status_code == 200
    assert versions_response.json()["count"] >= 2

    version_response = await http_client.get(
        f"/public/v1/transaction-categories/versions/{category_id}/1",
        headers=headers,
    )
    assert version_response.status_code == 200
    assert version_response.json()["category_id"] == str(category_id)

    delete_response = await http_client.delete(
        f"/public/v1/transaction-categories/{category_id}",
        headers=headers,
    )
    assert delete_response.status_code == 200

    restore_response = await http_client.post(
        f"/public/v1/transaction-categories/{category_id}/restore",
        headers=headers,
    )
    assert restore_response.status_code == 200
