from datetime import datetime
from typing import Any
from uuid import UUID

from psycopg.rows import DictRow
from psycopg.sql import SQL, Composed, Identifier

from application.dto import (
    LimitOffsetPaginator,
)
from application.errors import AppInternalError
from application.ports.repositories import (
    PersonalTransactionEvent,
    PersonalTransactionVersionRepository,
)
from domain.personal_transaction import (
    MoneyAmount,
    PersonalTransaction,
    PersonalTransactionFactory,
    PersonalTransactionID,
    PersonalTransactionTime,
    PersonalTransactionType,
)
from domain.tenant import Tenant, TenantID
from domain.transaction_category import TransactionCategoryID
from domain.value_objects import State, Version
from infrastructure.db.postgres.base import BasePostgresRepository, handle_domain_errors


class PersonalTransactionVersionPostgresRepository(
    BasePostgresRepository, PersonalTransactionVersionRepository
):
    async def by_id_version(
        self, transaction_id: PersonalTransactionID, version: Version
    ) -> (
        tuple[PersonalTransaction, PersonalTransactionEvent, TenantID | None, datetime]
        | None
    ):
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
                t.event,
                t.editor_id,
                t.created_at,
                COALESCE(
                    ARRAY_AGG(tc.category_id ORDER BY tc.category_id)
                    FILTER (WHERE tc.category_id IS NOT NULL),
                    ARRAY[]::uuid[]
                ) AS category_ids
            FROM {} t
            JOIN {} tc ON t.transaction_version_id = tc.transaction_version_id
            WHERE t.transaction_id = %s AND t.version = %s
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
                t.version,
                t.event,
                t.editor_id,
                t.created_at
            ORDER BY t.transaction_time DESC
            """
        ).format(
            Identifier(self._transaction_tables.version),
            Identifier(self._transaction_tables.categories.version),
        )
        data = await self._fetchone(
            query, (transaction_id.transaction_id, version.version)
        )
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
        from_version: Version | None,
        to_version: Version | None,
    ) -> tuple[
        list[
            tuple[
                PersonalTransaction, PersonalTransactionEvent, TenantID | None, datetime
            ]
        ],
        int,
    ]:
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
            from_version,
            to_version,
        )
        count_query = SQL(
            """
            SELECT COUNT(DISTINCT t.transaction_version_id) AS count_rows
            FROM {} t
            LEFT JOIN {} tc ON t.transaction_version_id = tc.transaction_version_id
            {}
            """
        ).format(
            Identifier(self._transaction_tables.version),
            Identifier(self._transaction_tables.categories.version),
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
                t.event,
                t.editor_id,
                t.created_at,
                COALESCE(
                    ARRAY_AGG(tc.category_id ORDER BY tc.category_id)
                    FILTER (WHERE tc.category_id IS NOT NULL),
                    ARRAY[]::uuid[]
                ) AS category_ids
            FROM {} t
            LEFT JOIN {} tc ON t.transaction_version_id = tc.transaction_version_id
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
                t.version,
                t.event,
                t.editor_id,
                t.created_at
            ORDER BY t.transaction_time DESC
            LIMIT %s OFFSET %s
            """
        ).format(
            Identifier(self._transaction_tables.version),
            Identifier(self._transaction_tables.categories.version),
            conditions,
        )
        params.extend([paginator.limit, paginator.offset])
        data = await self._fetchall(query, tuple(params))
        return [self._data_to_domain(row) for row in data], count

    async def save(
        self,
        transaction: PersonalTransaction,
        event: PersonalTransactionEvent,
        editor: Tenant | None,
    ) -> None:
        await self._create(transaction, event, editor)

    async def _create(
        self,
        transaction: PersonalTransaction,
        event: PersonalTransactionEvent,
        editor: Tenant | None,
    ) -> None:
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
                version,
                event,
                editor_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING transaction_version_id
            """
        ).format(Identifier(self._transaction_tables.version))
        data = await self._fetchone(
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
                event.value,
                editor.tenant_id.tenant_id if editor is not None else None,
            ),
        )
        if data is None:
            raise AppInternalError(
                msg="не вернулось id созданной записи версии персональной транзакции",
                action="создание записи новой версии персональной транзакции",
                data={
                    "transaction": {
                        "transaction_id": transaction.transaction_id.transaction_id
                    }
                },
            )
        await self._set_categories(transaction, data["transaction_version_id"])

    async def _set_categories(
        self, transaction: PersonalTransaction, version_id: UUID
    ) -> None:
        category_ids = transaction.category_ids
        if len(category_ids) == 0:
            return
        query = SQL(
            """
            INSERT INTO {} (
                transaction_version_id,
                category_id
            )
            VALUES (%s, %s)
            """
        ).format(Identifier(self._transaction_tables.categories.version))
        await self._executemany(
            query,
            [(version_id, category_id.category_id) for category_id in category_ids],
        )

    @handle_domain_errors
    def _data_to_domain(
        self, data: DictRow
    ) -> tuple[
        PersonalTransaction, PersonalTransactionEvent, TenantID | None, datetime
    ]:
        return (
            PersonalTransactionFactory.restore(
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
            ),
            PersonalTransactionEvent.from_str(data["event"]),
            TenantID(data["editor_id"]) if data["editor_id"] is not None else None,
            data["created_at"],
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
        from_version: Version | None,
        to_version: Version | None,
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
        if from_version:
            conditions.append(SQL("t.version >= %s"))
            params.append(from_version.version)
        if to_version:
            conditions.append(SQL("t.version <= %s"))
            params.append(to_version.version)
        if len(conditions) == 1:
            conditions = conditions[0]
        else:
            conditions = SQL(" AND ").join(conditions)
        return conditions, params
