from datetime import datetime
from typing import Any

from psycopg.rows import DictRow
from psycopg.sql import SQL, Composed, Identifier

from application.dto import LimitOffsetPaginator
from application.ports.repositories import TenantEvent, TenantVersionRepository
from domain.tenant import Tenant, TenantFactory, TenantID, TenantState, TenantStatus
from domain.value_objects import Version
from infrastructure.db.postgres.base import BasePostgresRepository, handle_domain_errors


class TenantVersionPostgresRepository(BasePostgresRepository, TenantVersionRepository):
    async def by_id_version(
        self, tenant_id: TenantID, version: Version
    ) -> tuple[Tenant, TenantEvent, TenantID | None, datetime] | None:
        query = SQL(
            """
            SELECT
                tenant_id,
                status,
                state,
                version,
                event,
                editor_id,
                created_at
            FROM {}
            WHERE tenant_id = %s AND version = %s
            """
        ).format(Identifier(self._tenant_tables.version))
        data = await self._fetchone(query, (tenant_id.tenant_id, version.version))
        return self._data_to_domain(data) if data is not None else None

    async def filters(
        self,
        paginator: LimitOffsetPaginator,
        tenant_id: TenantID,
        statuses: list[TenantStatus] | None = None,
        states: list[TenantState] | None = None,
        from_version: Version | None = None,
        to_version: Version | None = None,
    ) -> tuple[list[tuple[Tenant, TenantEvent, TenantID | None, datetime]], int]:
        conditions, params = self._init_conditions_with_params(
            tenant_id, statuses, states, from_version, to_version
        )
        count = await self._count_rows(conditions, params, self._tenant_tables.version)
        if count == 0:
            return list(), 0

        query, params = self._extend_query_with_limit_offset(
            SQL(
                """
                SELECT
                    tenant_id,
                    status,
                    state,
                    version,
                    event,
                    editor_id,
                    created_at
                FROM {}
                """
            ).format(Identifier(self._tenant_tables.version)),
            conditions,
            params,
            paginator,
        )
        data = await self._fetchall(query, tuple(params))
        return [self._data_to_domain(row) for row in data], count

    async def save(
        self, tenant: Tenant, event: TenantEvent, editor: Tenant | None = None
    ) -> None:
        await self._create(tenant, event, editor)

    async def batch_save(
        self, tenants_events_editors: list[tuple[Tenant, TenantEvent, Tenant | None]]
    ) -> None:
        await self._batch_create(tenants_events_editors)

    async def _create(
        self, tenant: Tenant, event: TenantEvent, editor: Tenant | None = None
    ) -> None:
        query = SQL(
            """
            INSERT INTO {} (
                tenant_id,
                status,
                state,
                version,
                event,
                editor_id
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """
        ).format(Identifier(self._tenant_tables.version))
        await self._execute(
            query,
            (
                tenant.tenant_id.tenant_id,
                tenant.status.value,
                tenant.state.value,
                tenant.version.version,
                event.value,
                editor.tenant_id.tenant_id if editor is not None else None,
            ),
        )

    async def _batch_create(
        self, tenants_events_editors: list[tuple[Tenant, TenantEvent, Tenant | None]]
    ) -> None:
        if len(tenants_events_editors) == 0:
            return
        query = SQL(
            """
            INSERT INTO {} (
                tenant_id,
                status,
                state,
                version,
                event,
                editor_id
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """
        ).format(Identifier(self._tenant_tables.version))
        await self._executemany(
            query,
            [
                (
                    tenant.tenant_id.tenant_id,
                    tenant.status.value,
                    tenant.state.value,
                    tenant.version.version,
                    event.value,
                    editor.tenant_id.tenant_id if editor is not None else None,
                )
                for tenant, event, editor in tenants_events_editors
            ],
        )

    @handle_domain_errors
    def _data_to_domain(
        self, data: DictRow
    ) -> tuple[Tenant, TenantEvent, TenantID | None, datetime]:
        tenant = TenantFactory.restore(
            data["tenant_id"], data["status"], data["state"], data["version"]
        )
        event = TenantEvent.from_str(data["event"])
        editor_id = (
            TenantID(data["editor_id"]) if data["editor_id"] is not None else None
        )
        return tenant, event, editor_id, data["created_at"]

    def _init_conditions_with_params(
        self,
        tenant_id: TenantID,
        statuses: list[TenantStatus] | None,
        states: list[TenantState] | None,
        from_version: Version | None,
        to_version: Version | None,
    ) -> tuple[SQL | Composed, list[Any]]:
        conditions = [SQL("WHERE tenant_id = %s")]
        params: list[Any] = [tenant_id.tenant_id]
        if statuses:
            conditions.append(SQL("status = ANY(%s)"))
            params.append([status.value for status in statuses])
        if states:
            conditions.append(SQL("state = ANY(%s)"))
            params.append([state.value for state in states])
        if from_version:
            conditions.append(SQL("version >= %s"))
            params.append(from_version.version)
        if to_version:
            conditions.append(SQL("version <= %s"))
            params.append(to_version.version)
        if len(conditions) == 1:
            conditions = conditions[0]
        else:
            conditions = SQL(" AND ").join(conditions)
        return conditions, params
