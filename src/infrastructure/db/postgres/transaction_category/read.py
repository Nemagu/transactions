from typing import Any
from uuid import uuid7

from psycopg.rows import DictRow
from psycopg.sql import SQL, Identifier

from application.dto import LimitOffsetPaginator
from application.ports.repositories import TransactionCategoryReadRepository
from domain.tenant import TenantID
from domain.transaction_category import (
    TransactionCategory,
    TransactionCategoryFactory,
    TransactionCategoryID,
    TransactionCategoryName,
)
from domain.value_objects import State
from infrastructure.db.postgres.base import BasePostgresRepository


class TransactionCategoryReadPostgresRepository(
    BasePostgresRepository, TransactionCategoryReadRepository
):
    async def next_id(self) -> TransactionCategoryID:
        return TransactionCategoryID(uuid7())

    async def by_id(
        self, category_id: TransactionCategoryID
    ) -> TransactionCategory | None:
        query = SQL(
            """
            SELECT
                category_id,
                owner_id,
                name,
                description,
                state,
                version
            FROM {}
            WHERE category_id = %s
            """
        ).format(Identifier(self._category_tables.read))
        data = await self._fetchone(query, (category_id.category_id,))
        return self._data_to_domain(data) if data is not None else None

    async def by_ids(
        self, category_ids: set[TransactionCategoryID]
    ) -> set[TransactionCategory]:
        query = SQL(
            """
            SELECT
                category_id,
                owner_id,
                name,
                description,
                state,
                version
            FROM {}
            WHERE category_id = ANY(%s)
            """
        ).format(Identifier(self._category_tables.read))
        data = await self._fetchall(
            query, ([category_id.category_id for category_id in category_ids],)
        )
        return set(self._data_to_domain(row) for row in data)

    async def by_owner_id_name(
        self,
        owner_id: TenantID,
        name: TransactionCategoryName,
    ) -> TransactionCategory | None:
        query = SQL(
            """
            SELECT
                category_id,
                owner_id,
                name,
                description,
                state,
                version
            FROM {}
            WHERE owner_id = %s AND name = %s
            """
        ).format(Identifier(self._category_tables.read))
        data = await self._fetchone(query, (owner_id.tenant_id, name.name))
        return self._data_to_domain(data) if data is not None else None

    async def filters(
        self,
        owner_id: TenantID,
        paginator: LimitOffsetPaginator,
        names: list[TransactionCategoryName] | None,
        states: list[State] | None,
    ) -> tuple[list[TransactionCategory], int]:
        conditions = [SQL("WHERE owner_id = %s")]
        params: list[Any] = [owner_id.tenant_id]
        if names:
            conditions.append(SQL("name = ANY(%s)"))
            params.append([name.name for name in names])
        if states:
            conditions.append(SQL("state = ANY(%s)"))
            params.append([state.value for state in states])
        conditions = SQL(" AND ").join(conditions)

        count = await self._count_rows(conditions, params, self._category_tables.read)
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
                    version
                FROM {}
                """
            ).format(Identifier(self._category_tables.read)),
            conditions,
            params,
            paginator,
        )
        data = await self._fetchall(query, tuple(params))
        return [self._data_to_domain(row) for row in data], count

    async def save(self, category: TransactionCategory) -> None:
        if category.version.version == 1:
            await self._create(category)
        else:
            await self._update(category)

    async def _create(self, category: TransactionCategory) -> None:
        query = SQL(
            """
            INSERT INTO {} (
                category_id,
                owner_id,
                name,
                description,
                state,
                version
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """
        ).format(Identifier(self._category_tables.read))
        await self._execute(
            query,
            (
                category.category_id.category_id,
                category.owner_id.tenant_id,
                category.name.name,
                category.description.description,
                category.state.value,
                category.version.version,
            ),
        )

    async def _update(self, category: TransactionCategory) -> None:
        query = SQL(
            """
            UPDATE {}
            SET name = %s, description = %s, state = %s, version = %s
            WHERE category_id = %s
            """
        ).format(Identifier(self._category_tables.read))
        await self._execute(
            query,
            (
                category.name.name,
                category.description.description,
                category.state.value,
                category.version.version,
                category.category_id.category_id,
            ),
        )

    def _data_to_domain(self, data: DictRow) -> TransactionCategory:
        return TransactionCategoryFactory.restore(
            data["category_id"],
            data["owner_id"],
            data["name"],
            data["description"],
            data["state"],
            data["version"],
        )
