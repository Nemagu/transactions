from typing import Any
from uuid import uuid7

from psycopg.rows import DictRow
from psycopg.sql import SQL, Composed, Identifier

from application.dto import (
    LimitOffsetPaginator,
)
from application.ports.repositories import PersonalTransactionReadRepository
from domain.personal_transaction import (
    MoneyAmount,
    PersonalTransaction,
    PersonalTransactionFactory,
    PersonalTransactionID,
    PersonalTransactionTime,
    PersonalTransactionType,
)
from domain.tenant import TenantID
from domain.transaction_category import TransactionCategoryID
from domain.value_objects import State
from infrastructure.db.postgres.base import BasePostgresRepository, handle_domain_errors


class PersonalTransactionReadPostgresRepository(
    BasePostgresRepository, PersonalTransactionReadRepository
):
    async def next_id(self) -> PersonalTransactionID:
        return PersonalTransactionID(uuid7())

    async def by_id(
        self, transaction_id: PersonalTransactionID
    ) -> PersonalTransaction | None:
        query = SQL(
            """
            SELECT
                t.transaction_id,
                t.owner_id,
                t.name,
                t.description,
                t.transaction_type,
                t.amount,
                t.currency,
                t.transaction_time,
                t.state,
                t.version,
                COALESCE(
                    ARRAY_AGG(tc.category_id ORDER BY tc.category_id)
                    FILTER (WHERE tc.category_id IS NOT NULL),
                    ARRAY[]::uuid[]
                ) AS category_ids
            FROM {} t
            LEFT JOIN {} tc ON t.transaction_id = tc.transaction_id
            WHERE t.transaction_id = %s
            GROUP BY
                t.transaction_id,
                t.owner_id,
                t.name,
                t.description,
                t.transaction_type,
                t.amount,
                t.currency,
                t.transaction_time,
                t.state,
                t.version
            ORDER BY t.transaction_time DESC
            """
        ).format(
            Identifier(self._transaction_tables.read),
            Identifier(self._transaction_tables.categories.read),
        )
        data = await self._fetchone(query, (transaction_id.transaction_id,))
        return self._data_to_domain(data) if data is not None else None

    async def filters(
        self,
        owner_id: TenantID,
        paginator: LimitOffsetPaginator,
        transaction_ids: list[PersonalTransactionID] | None,
        category_ids: list[TransactionCategoryID] | None,
        transaction_types: list[PersonalTransactionType] | None,
        from_money_amount: MoneyAmount | None,
        to_money_amount: MoneyAmount | None,
        from_transaction_time: PersonalTransactionTime | None,
        to_transaction_time: PersonalTransactionTime | None,
        states: list[State] | None,
    ) -> tuple[list[PersonalTransaction], int]:
        conditions, params = self._init_conditions_with_params(
            owner_id,
            transaction_ids,
            category_ids,
            transaction_types,
            from_money_amount,
            to_money_amount,
            from_transaction_time,
            to_transaction_time,
            states,
        )
        count_query = SQL(
            """
            SELECT COUNT(DISTINCT t.transaction_id) AS count_rows
            FROM {} t
            LEFT JOIN {} tc ON t.transaction_id = tc.transaction_id
            {}
            """
        ).format(
            Identifier(self._transaction_tables.read),
            Identifier(self._transaction_tables.categories.read),
            conditions,
        )
        count_data = await self._fetchone(count_query, tuple(params))
        if count_data is None:
            return list(), 0
        count: int = count_data["count_rows"]
        if count == 0:
            return list(), count

        query = SQL(
            """
            SELECT
                t.transaction_id,
                t.owner_id,
                t.name,
                t.description,
                t.transaction_type,
                t.amount,
                t.currency,
                t.transaction_time,
                t.state,
                t.version,
                COALESCE(
                    ARRAY_AGG(tc.category_id ORDER BY tc.category_id)
                    FILTER (WHERE tc.category_id IS NOT NULL),
                    ARRAY[]::uuid[]
                ) AS category_ids
            FROM {} t
            LEFT JOIN {} tc ON t.transaction_id = tc.transaction_id
            {}
            GROUP BY
                t.transaction_id,
                t.owner_id,
                t.name,
                t.description,
                t.transaction_type,
                t.amount,
                t.currency,
                t.transaction_time,
                t.state,
                t.version
            ORDER BY t.transaction_time DESC
            LIMIT %s OFFSET %s
            """
        ).format(
            Identifier(self._transaction_tables.read),
            Identifier(self._transaction_tables.categories.read),
            conditions,
        )
        params.extend([paginator.limit, paginator.offset])
        data = await self._fetchall(query, tuple(params))
        return [self._data_to_domain(row) for row in data], count

    async def save(self, transaction: PersonalTransaction) -> None:
        if transaction.version.version == 1:
            await self._create(transaction)
        else:
            await self._update(transaction)

    async def _create(self, transaction: PersonalTransaction) -> None:
        query = SQL(
            """
            INSERT INTO {} (
                transaction_id,
                owner_id,
                name,
                description,
                transaction_type,
                amount,
                currency,
                transaction_time,
                state,
                version
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
        ).format(Identifier(self._transaction_tables.read))
        await self._execute(
            query,
            (
                transaction.transaction_id.transaction_id,
                transaction.owner_id.tenant_id,
                transaction.name.name,
                transaction.description.description,
                transaction.transaction_type.value,
                transaction.money_amount.amount,
                transaction.money_amount.currency.value,
                transaction.transaction_time.transaction_time,
                transaction.state.value,
                transaction.version.version,
            ),
        )
        await self._set_categories(transaction)

    async def _update(self, transaction: PersonalTransaction) -> None:
        query = SQL(
            """
            UPDATE {}
            SET
                name = %s,
                description = %s,
                transaction_type = %s, 
                amount = %s,
                currency = %s,
                transaction_time = %s,
                state = %s,
                version = %s
            WHERE transaction_id = %s
            """
        ).format(Identifier(self._transaction_tables.read))
        await self._execute(
            query,
            (
                transaction.name.name,
                transaction.description.description,
                transaction.transaction_type.value,
                transaction.money_amount.amount,
                transaction.money_amount.currency.value,
                transaction.transaction_time.transaction_time,
                transaction.state.value,
                transaction.version.version,
                transaction.transaction_id.transaction_id,
            ),
        )
        await self._set_categories(transaction)

    async def _set_categories(self, transaction: PersonalTransaction) -> None:
        category_ids = transaction.category_ids
        deletion_query = SQL(
            """
            DELETE FROM {}
            WHERE transaction_id = %s
            """
        ).format(Identifier(self._transaction_tables.categories.read))
        await self._execute(
            deletion_query, (transaction.transaction_id.transaction_id,)
        )
        if len(category_ids) == 0:
            return
        creation_query = SQL(
            """
            INSERT INTO {} (
                transaction_id,
                category_id
            )
            VALUES (%s, %s)
            """
        ).format(Identifier(self._transaction_tables.categories.read))
        await self._executemany(
            creation_query,
            [
                (transaction.transaction_id.transaction_id, category_id.category_id)
                for category_id in category_ids
            ],
        )

    @handle_domain_errors
    def _data_to_domain(self, data: DictRow) -> PersonalTransaction:
        return PersonalTransactionFactory.restore(
            data["transaction_id"],
            data["owner_id"],
            data["name"],
            data["description"],
            set(data["category_ids"]),
            data["transaction_type"],
            data["amount"],
            data["currency"],
            data["transaction_time"],
            data["state"],
            data["version"],
        )

    def _init_conditions_with_params(
        self,
        owner_id: TenantID,
        transaction_ids: list[PersonalTransactionID] | None,
        category_ids: list[TransactionCategoryID] | None,
        transaction_types: list[PersonalTransactionType] | None,
        from_money_amount: MoneyAmount | None,
        to_money_amount: MoneyAmount | None,
        from_transaction_time: PersonalTransactionTime | None,
        to_transaction_time: PersonalTransactionTime | None,
        states: list[State] | None,
    ) -> tuple[SQL | Composed, list[Any]]:
        conditions = [SQL("WHERE t.owner_id = %s")]
        params: list[Any] = [owner_id.tenant_id]
        if transaction_ids:
            conditions.append(SQL("t.transaction_id = ANY(%s)"))
            params.append(
                [transaction_id.transaction_id for transaction_id in transaction_ids]
            )
        if category_ids:
            conditions.append(SQL("tc.category_id = ANY(%s)"))
            params.append([category_id.category_id for category_id in category_ids])
        if transaction_types:
            conditions.append(SQL("t.transaction_type = ANY(%s)"))
            params.append(
                [transaction_type.value for transaction_type in transaction_types]
            )
        if from_money_amount:
            conditions.append(SQL("t.amount >= %s"))
            params.append(from_money_amount.amount)
        if to_money_amount:
            conditions.append(SQL("t.amount <= %s"))
            params.append(to_money_amount.amount)
        if from_transaction_time:
            conditions.append(SQL("t.transaction_time >= %s"))
            params.append(from_transaction_time.transaction_time)
        if to_transaction_time:
            conditions.append(SQL("t.transaction_time <= %s"))
            params.append(to_transaction_time.transaction_time)
        if states:
            conditions.append(SQL("t.state = ANY(%s)"))
            params.append([state.value for state in states])
        if len(conditions) == 1:
            conditions = conditions[0]
        else:
            conditions = SQL(" AND ").join(conditions)
        return conditions, params
