import pytest


@pytest.mark.asyncio
async def test_tenant_me_requires_user_id_header(http_client) -> None:
    response = await http_client.get("/public/v1/tenants/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "id пользователя не передан"


@pytest.mark.asyncio
async def test_tenant_me_rejects_invalid_user_id_header(http_client, api_app) -> None:
    header_name = api_app.state.fastapi_settings.user_id_header_name

    response = await http_client.get(
        "/public/v1/tenants/me",
        headers={header_name: "invalid-uuid"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "некорректный id пользователя"
