from uuid import UUID

import pytest


@pytest.mark.asyncio
async def test_create_and_list_transaction_categories(
    http_client,
    auth_headers_factory,
    tenant_factory,
    tenant_read_repo,
) -> None:
    tenant = tenant_factory()
    await tenant_read_repo.save(tenant)

    creation_response = await http_client.post(
        "/public/v1/transaction-categories",
        headers=auth_headers_factory(tenant.tenant_id.tenant_id),
        json={"name": "food", "description": "daily"},
    )

    assert creation_response.status_code == 200
    category_id = UUID(creation_response.json())

    list_response = await http_client.get(
        "/public/v1/transaction-categories",
        headers=auth_headers_factory(tenant.tenant_id.tenant_id),
        params=[("name", "food")],
    )

    assert list_response.status_code == 200
    payload = list_response.json()
    assert payload["count"] == 1
    assert len(payload["results"]) == 1
    assert payload["results"][0]["category_id"] == str(category_id)
    assert payload["results"][0]["name"] == "food"
