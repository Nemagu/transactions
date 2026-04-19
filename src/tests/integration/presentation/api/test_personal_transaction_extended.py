from __future__ import annotations

from datetime import datetime
from uuid import UUID

import pytest


@pytest.mark.asyncio
async def test_personal_transaction_router_supports_mutations_and_versions(
    http_client,
    auth_headers_factory,
    tenant_factory,
    tenant_read_repo,
    category_factory,
    category_read_repo,
) -> None:
    tenant = tenant_factory()
    await tenant_read_repo.save(tenant)

    category = category_factory(owner_id=tenant.tenant_id.tenant_id, name="food")
    await category_read_repo.save(category)

    headers = auth_headers_factory(tenant.tenant_id.tenant_id)

    create_response = await http_client.post(
        "/public/v1/personal-transactions",
        headers=headers,
        json={
            "category_ids": [str(category.category_id.category_id)],
            "transaction_type": "expense",
            "money_amount": {"amount": "150.00", "currency": "ruble"},
            "transaction_time": datetime(2026, 4, 18, 12, 0, 0).isoformat(),
            "name": "coffee",
            "description": "daily",
        },
    )
    assert create_response.status_code == 200
    transaction_id = UUID(create_response.json())

    update_response = await http_client.put(
        f"/public/v1/personal-transactions/{transaction_id}",
        headers=headers,
        json={"name": "coffee-updated"},
    )
    assert update_response.status_code == 200

    versions_response = await http_client.get(
        f"/public/v1/personal-transactions/versions/{transaction_id}",
        headers=headers,
    )
    assert versions_response.status_code == 200
    assert versions_response.json()["count"] >= 2

    version_response = await http_client.get(
        f"/public/v1/personal-transactions/versions/{transaction_id}/1",
        headers=headers,
    )
    assert version_response.status_code == 200
    assert version_response.json()["transaction_id"] == str(transaction_id)

    delete_response = await http_client.delete(
        f"/public/v1/personal-transactions/{transaction_id}",
        headers=headers,
    )
    assert delete_response.status_code == 200

    restore_response = await http_client.post(
        f"/public/v1/personal-transactions/{transaction_id}/restore",
        headers=headers,
    )
    assert restore_response.status_code == 200
