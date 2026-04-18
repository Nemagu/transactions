from datetime import datetime
from typing import Any

from psycopg.rows import DictRow
from psycopg.sql import SQL, Composed, Identifier

from application.dto import LimitOffsetPaginator
from application.ports.repositories import (
    TransactionCategoryEvent,
    TransactionCategoryVersionRepository,
)
from domain.tenant import Tenant, TenantID
from domain.transaction_category import (
    TransactionCategory,
    TransactionCategoryFactory,
    TransactionCategoryID,
    TransactionCategoryName,
)
from domain.value_objects import State, Version
from infrastructure.db.postgres.base import BasePostgresRepository, handle_domain_errors


class TransactionCategoryVersionPostgresRepository(
    BasePostgresRepository, TransactionCategoryVersionRepository
):
    async def by_id_version(
        self, category_id: TransactionCategoryID, version: Version
    ) -> (
        tuple[TransactionCategory, TransactionCategoryEvent, TenantID | None, datetime]
        | None
    ):
        query = SQL(
            """
            SELECT
                category_id,
                owner_id,
                name,
                description,
                state,
                version,
                event,
                editor_id,
                created_at
            FROM {}
            WHERE category_id = %s AND version = %s
            """
        ).format(Identifier(self._category_tables.version))
        data = await self._fetchone(query, (category_id.category_id, version.version))
        return self._data_to_domain(data) if data is not None else None

    async def filters(
        self,
        owner_id: TenantID,
        paginator: LimitOffsetPaginator,
        category_id: TransactionCategoryID,
        names: list[TransactionCategoryName] | None = None,
        states: list[State] | None = None,
        from_version: Version | None = None,
        to_version: Version | None = None,
    ) -> tuple[
        list[
            tuple[
                TransactionCategory, TransactionCategoryEvent, TenantID | None, datetime
            ]
        ],
        int,
    ]:
        conditions, params = self._init_conditions_with_params(
            owner_id, category_id, names, states, from_version, to_version
        )
        count = await self._count_rows(
            conditions, params, self._category_tables.version
        )
        if count == 0:
            return list(), count
        query, params = self._extend_query_with_limit_offset(
            SQL(
                """
                SELECT
                    category_id,
                    owner_id,
                    name,
                    description,
                    state,
                    version,
                    event,
                    editor_id,
                    created_at
                FROM {}
                """
            ).format(Identifier(self._category_tables.version)),
            conditions,
            params,
            paginator,
        )
        data = await self._fetchall(query, tuple(params))
        return [self._data_to_domain(row) for row in data], count

    async def save(
        self,
        category: TransactionCategory,
        event: TransactionCategoryEvent,
        editor: Tenant | None = None,
    ) -> None:
        await self._create(category, event, editor)

    async def _create(
        self,
        category: TransactionCategory,
        event: TransactionCategoryEvent,
        editor: Tenant | None,
    ) -> None:
        query = SQL(
            """
            INSERT INTO {} (
                category_id,
                owner_id,
                name,
                description,
                state,
                version,
                event,
                editor_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
        ).format(Identifier(self._category_tables.version))
        await self._execute(
            query,
            (
                category.category_id.category_id,
                category.owner_id.tenant_id,
                category.name.name,
                category.description.description,
                category.state.value,
                category.version.version,
                event.value,
                editor.tenant_id.tenant_id if editor is not None else None,
            ),
        )

    @handle_domain_errors
    def _data_to_domain(
        self, data: DictRow
    ) -> tuple[
        TransactionCategory, TransactionCategoryEvent, TenantID | None, datetime
    ]:
        category = TransactionCategoryFactory.restore(
            data["category_id"],
            data["owner_id"],
            data["name"],
            data["description"],
            data["state"],
            data["version"],
        )
        event = TransactionCategoryEvent.from_str(data["event"])
        tenant_id = (
            TenantID(data["editor_id"]) if data["editor_id"] is not None else None
        )
        created_at = data["created_at"]
        return category, event, tenant_id, created_at

    def _init_conditions_with_params(
        self,
        owner_id: TenantID,
        category_id: TransactionCategoryID,
        names: list[TransactionCategoryName] | None,
        states: list[State] | None,
        from_version: Version | None,
        to_version: Version | None,
    ) -> tuple[SQL | Composed, list[Any]]:
        conditions = [SQL("WHERE owner_id = %s AND category_id = %s")]
        params: list[Any] = [owner_id.tenant_id, category_id.category_id]
        if names:
            conditions.append(SQL("name = ANY(%s)"))
            params.append([name.name for name in names])
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
