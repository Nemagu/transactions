from __future__ import annotations

from collections.abc import Callable

import pytest
from psycopg import AsyncConnection
from psycopg.rows import DictRow

from infrastructure.db.postgres.unit_of_work import PostgresUnitOfWork


@pytest.fixture
def uow_factory(
    db_connection: AsyncConnection[DictRow],
) -> Callable[[], PostgresUnitOfWork]:
    def factory() -> PostgresUnitOfWork:
        return PostgresUnitOfWork(db_connection)

    return factory

