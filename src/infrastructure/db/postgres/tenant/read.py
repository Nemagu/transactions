from uuid import UUID

from psycopg.sql import SQL, Identifier

from application.dto import LimitOffsetPaginator
from application.ports.repositories import TenantReadRepository
from domain.tenant import Tenant, TenantFactory, TenantID, TenantState, TenantStatus
from infrastructure.db.postgres.base import BasePostgresRepository, handle_domain_errors


class TenantReadPostgresRepository(BasePostgresRepository, TenantReadRepository):
    async def by_id(self, tenant_id: TenantID) -> Tenant | None:
        query = SQL(
            """
            SELECT
                tenant_id,
                status,
                state,
                version
            FROM {}
            WHERE tenant_id = %s
            """
        ).format(Identifier(self._tenant_tables.read))
        data = await self._fetchone(query, (tenant_id.tenant_id,))
        return self._data_to_domain(data) if data is not None else None

    async def filters(
        self,
        paginator: LimitOffsetPaginator,
        tenant_ids: list[TenantID] | None,
        statuses: list[TenantStatus] | None,
        stages: list[TenantState] | None,
    ) -> tuple[list[Tenant], int]:
        params = list()
        conditions = [SQL("WHERE 1 = 1")]
        if tenant_ids:
            conditions.append(SQL("tenant_id = ANY(%s)"))
            params.append([tenant_id.tenant_id for tenant_id in tenant_ids])
        if statuses:
            conditions.append(SQL("status = ANY(%s)"))
            params.append([status.value for status in statuses])
        if stages:
            conditions.append(SQL("stage = ANY(%s)"))
            params.append([stage.value for stage in stages])
        if len(conditions) == 1:
            conditions = conditions[0]
        else:
            conditions = SQL(" AND ").join(conditions)

        count = await self._count_rows(conditions, params, self._tenant_tables.read)
        if count == 0:
            return list(), 0

        query, params = self._extend_query_with_limit_offset(
            SQL(
                """
            SELECT
                id,
                company_id,
                external_user_id,
                status,
                version
            FROM {}
            """
            ).format(Identifier(self._tenant_tables.read)),
            conditions,
            params,
            paginator,
        )
        data = await self._fetchall(query, tuple(params))
        return [self._data_to_domain(row) for row in data], count

    async def save(self, tenant: Tenant) -> None:
        if tenant.version.version == 1:
            await self._create(tenant)
        else:
            await self._update(tenant)

    async def batch_save(self, tenants: list[Tenant]) -> None:
        creation_tenants = list()
        update_tenants = list()
        for tenant in tenants:
            if tenant.version.version == 1:
                creation_tenants.append(tenant)
            else:
                update_tenants.append(tenant)
        if creation_tenants:
            await self._batch_create(creation_tenants)
        if update_tenants:
            await self._batch_update(update_tenants)

    async def _create(self, tenant: Tenant) -> None:
        query = SQL(
            """
            INSERT INTO {} (
                tenant_id,
                status,
                state,
                version
            )
            VALUES (%s, %s, %s, %s)
            """
        ).format(Identifier(self._tenant_tables.read))
        await self._execute(
            query,
            (
                tenant.tenant_id.tenant_id,
                tenant.status.value,
                tenant.state.value,
                tenant.version.version,
            ),
        )

    async def _update(self, tenant: Tenant) -> None:
        query = SQL(
            """
            UPDATE {}
            SET status = %s, state = %s, version = %s
            WHERE tenant_id = %s
            """
        ).format(Identifier(self._tenant_tables.read))
        await self._execute(
            query,
            (
                tenant.status.value,
                tenant.state.value,
                tenant.version.version,
                tenant.tenant_id.tenant_id,
            ),
        )

    async def _batch_create(self, tenants: list[Tenant]) -> None:
        if len(tenants) == 0:
            return
        values = list()
        for tenant in tenants:
            values.append(tenant.tenant_id.tenant_id)
            values.append(tenant.status.value)
            values.append(tenant.state.value)
            values.append(tenant.version.version)
        sql_values = SQL("; ").join(
            SQL("(%s, %s, %s, %s)") for _ in range(len(tenants))
        )
        query = SQL(
            """
            INSERT INTO {} (
                tenant_id,
                status,
                state,
                version
            )
            VALUES ({})
            """
        ).format(Identifier(self._tenant_tables.read), sql_values)
        await self._execute(query, tuple(values))

    async def _batch_update(self, tenants: list[Tenant]) -> None:
        if len(tenants) == 0:
            return
        query_template = SQL(
            """
            UPDATE {}
            SET status = %s, state = %s, version = %s
            WHERE tenant_id = %s
            """
        ).format(Identifier(self._tenant_tables.read))
        query = SQL("; ").join(query_template for _ in range(len(tenants)))
        values = list()
        for tenant in tenants:
            values.append(tenant.status.value)
            values.append(tenant.state.value)
            values.append(tenant.version.version)
            values.append(tenant.tenant_id.tenant_id)
        await self._execute(query, tuple(values))

    @handle_domain_errors
    def _data_to_domain(self, data: tuple[UUID, str, str, int]) -> Tenant:
        return TenantFactory.restore(*data)
