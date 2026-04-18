from uuid import UUID

import pytest


@pytest.mark.asyncio
async def test_create_and_read_personal_transaction(
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

    creation_response = await http_client.post(
        "/public/v1/personal-transactions",
        headers=auth_headers_factory(tenant.tenant_id.tenant_id),
        json={
            "category_ids": [str(category.category_id.category_id)],
            "transaction_type": "expense",
            "money_amount": {"amount": "100.50", "currency": "ruble"},
            "transaction_time": "2026-04-18T12:00:00",
            "name": "coffee",
            "description": "morning",
        },
    )

    assert creation_response.status_code == 200
    transaction_id = UUID(creation_response.json())

    by_id_response = await http_client.get(
        f"/public/v1/personal-transactions/{transaction_id}",
        headers=auth_headers_factory(tenant.tenant_id.tenant_id),
    )

    assert by_id_response.status_code == 200
    by_id_data = by_id_response.json()
    assert by_id_data["transaction_id"] == str(transaction_id)
    assert by_id_data["name"] == "coffee"
    assert by_id_data["money_amount"]["amount"] == "100.50"

    list_response = await http_client.get(
        "/public/v1/personal-transactions",
        headers=auth_headers_factory(tenant.tenant_id.tenant_id),
        params=[("transaction_id", str(transaction_id))],
    )

    assert list_response.status_code == 200
    payload = list_response.json()
    assert payload["count"] == 1
    assert len(payload["results"]) == 1
    assert payload["results"][0]["transaction_id"] == str(transaction_id)
    assert payload["results"][0]["category_ids"] == [
        str(category.category_id.category_id)
    ]
