import logging
from uuid import uuid7

import pytest

from domain.tenant import TenantStatus

LOGGER_NAME = "presentation.api.middlewares.logging"


def _extract_last_context(caplog) -> dict:
    records = [record for record in caplog.records if record.name == LOGGER_NAME]
    assert records
    last_record_args = records[-1].args
    if isinstance(last_record_args, dict):
        context = last_record_args
    else:
        context = last_record_args[0]
    assert isinstance(context, dict)
    return context


@pytest.mark.asyncio
async def test_logging_includes_action_for_application_error(
    http_client,
    auth_headers_factory,
    caplog,
) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)

    response = await http_client.post(
        "/public/v1/transaction-categories",
        headers=auth_headers_factory(uuid7()),
        json={"name": "food", "description": "daily"},
    )

    assert response.status_code == 400
    context = _extract_last_context(caplog)
    assert context["action"] == "создание категории транзакции"
    assert context["struct_name"] is None


@pytest.mark.asyncio
async def test_logging_includes_struct_name_for_domain_error(
    http_client,
    auth_headers_factory,
    tenant_factory,
    tenant_read_repo,
    caplog,
) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)

    initiator = tenant_factory(status=TenantStatus.TENANT)
    target_tenant = tenant_factory()
    await tenant_read_repo.save(initiator)
    await tenant_read_repo.save(target_tenant)

    response = await http_client.put(
        f"/public/v1/tenants/{target_tenant.tenant_id.tenant_id}/appoint-admin",
        headers=auth_headers_factory(initiator.tenant_id.tenant_id),
    )

    assert response.status_code == 403
    context = _extract_last_context(caplog)
    assert context["action"] is None
    assert context["struct_name"] == "арендатор"
