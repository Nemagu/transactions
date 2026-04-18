from enum import StrEnum
from uuid import UUID

from psycopg.rows import DictRow
from psycopg.sql import SQL, Identifier

from application.errors import AppInternalError
from application.ports.repositories import TenantSubscriptionRepository
from domain.tenant import Tenant, TenantFactory
from domain.user import User, UserFactory
from infrastructure.db.postgres.base import BasePostgresRepository, handle_domain_errors


class SubscriptionStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"


class TenantSubscriptionPostgresRepository(
    BasePostgresRepository, TenantSubscriptionRepository
):
    async def subscribe(self, subscriber: Tenant, source: User) -> None:
        await self.batch_subscribe([(subscriber, source)])

    async def batch_subscribe(
        self, subscriber_and_source: list[tuple[Tenant, User]]
    ) -> None:
        if not subscriber_and_source:
            return
        user_table_id = await self._user_table_id()
        query = SQL(
            """
            INSERT INTO {} (
                tenant_id,
                table_id,
                source_id,
                status,
                start_version,
                last_processed_version
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """
        ).format(Identifier(self._tenant_tables.subscription))
        await self._executemany(
            query,
            [
                (
                    tenant.tenant_id.tenant_id,
                    user_table_id,
                    user.user_id.user_id,
                    SubscriptionStatus.ACTIVE.value,
                    user.version.version,
                    user.version.version,
                )
                for tenant, user in subscriber_and_source
            ],
        )

    async def processed_version(self, subscriber: Tenant, source: User) -> None:
        await self.batch_processed_version([(subscriber, source)])

    async def batch_processed_version(
        self, subscriber_and_source: list[tuple[Tenant, User]]
    ) -> None:
        if not subscriber_and_source:
            return
        user_table_id = await self._user_table_id()
        query = SQL(
            """
            UPDATE {}
            SET last_processed_version = %s
            WHERE tenant_id = %s AND table_id = %s AND source_id = %s
            """
        ).format(Identifier(self._tenant_tables.subscription))
        await self._executemany(
            query,
            [
                (
                    user.version.version,
                    tenant.tenant_id.tenant_id,
                    user_table_id,
                    user.user_id.user_id,
                )
                for tenant, user in subscriber_and_source
            ],
        )

    async def users_have_no_tenants(self) -> list[User]:
        query = SQL(
            """
            SELECT
                u.user_id,
                u.state AS user_state,
                u.version AS user_version
            FROM {} u
            WHERE NOT EXISTS (SELECT 1 FROM {} t WHERE t.tenant_id = user_id)
            """
        ).format(
            Identifier(self._user_tables.read), Identifier(self._tenant_tables.read)
        )
        data = await self._fetchall(query)
        return [self._data_to_user(row) for row in data]

    async def new_users_versions(self) -> list[tuple[Tenant, User]]:
        query = SQL(
            """
            SELECT
                s.source_id AS user_id,
                u.state AS user_state,
                u.version AS user_version,
                s.tenant_id,
                t.status AS tenant_status,
                t.state AS tenant_state,
                t.version AS tenant_version
            FROM {} s
            JOIN {} t ON t.tenant_id = s.tenant_id
            JOIN {} u ON u.user_id = s.source_id
            WHERE u.version > s.last_processed_version
            """
        ).format(
            Identifier(self._tenant_tables.subscription),
            Identifier(self._tenant_tables.read),
            Identifier(self._user_tables.read),
        )
        data = await self._fetchall(query)
        return [(self._data_to_tenant(row), self._data_to_user(row)) for row in data]

    async def _user_table_id(self) -> UUID:
        query = SQL(
            """
            SELECT table_id
            FROM {}
            WHERE name = %s
            """
        ).format(Identifier(self._table_with_tables))
        data = await self._fetchone(query, (self._user_tables.read,))
        if data is None:
            raise AppInternalError(
                msg="не удалось получить id таблицы пользователей",
                action="попытка получить id таблицы пользователей",
                data={"name": self._user_tables.read},
            )
        return data["table_id"]

    @handle_domain_errors
    def _data_to_user(self, data: DictRow) -> User:
        return UserFactory.restore(
            data["user_id"], data["user_state"], data["user_version"]
        )

    @handle_domain_errors
    def _data_to_tenant(self, data: DictRow) -> Tenant:
        return TenantFactory.restore(
            data["tenant_id"],
            data["tenant_status"],
            data["tenant_state"],
            data["tenant_version"],
        )
