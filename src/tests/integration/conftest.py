from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid7

import pytest
import pytest_asyncio
from psycopg import AsyncConnection
from psycopg.rows import DictRow, dict_row

from domain.personal_transaction import (
    Currency,
    PersonalTransaction,
    PersonalTransactionFactory,
    PersonalTransactionID,
    PersonalTransactionTime,
    PersonalTransactionType,
)
from domain.tenant import Tenant, TenantFactory
from domain.tenant.value_objects import TenantID, TenantState, TenantStatus
from domain.transaction_category import (
    TransactionCategory,
    TransactionCategoryFactory,
)
from domain.transaction_category.value_objects import TransactionCategoryID
from domain.user import User, UserFactory
from domain.user.value_objects import UserID, UserState
from infrastructure.db.postgres.personal_transaction import (
    PersonalTransactionReadPostgresRepository,
    PersonalTransactionVersionPostgresRepository,
)
from infrastructure.db.postgres.tenant import (
    TenantReadPostgresRepository,
    TenantSubscriptionPostgresRepository,
    TenantVersionPostgresRepository,
)
from infrastructure.db.postgres.transaction_category import (
    TransactionCategoryReadPostgresRepository,
    TransactionCategoryVersionPostgresRepository,
)
from infrastructure.db.postgres.user import UserReadPostgresRepository

TRUNCATE_ALL_DATA_QUERY = """
TRUNCATE TABLE
    personal_transaction_categories_versions,
    personal_transaction_categories,
    personal_transactions_versions,
    personal_transactions,
    transaction_categories_versions,
    transaction_categories,
    tenants_subscriptions,
    tenants_versions,
    tenants,
    users
RESTART IDENTITY CASCADE
"""


@pytest_asyncio.fixture(autouse=True)
async def clean_db(postgres_settings) -> None:
    conn = await AsyncConnection.connect(
        conninfo=postgres_settings.url,
        row_factory=dict_row,
        autocommit=False,
    )
    try:
        await conn.execute(TRUNCATE_ALL_DATA_QUERY)
        await conn.commit()
    finally:
        await conn.close()


@pytest_asyncio.fixture
async def db_connection(postgres_settings) -> AsyncConnection[DictRow]:
    conn = await AsyncConnection.connect(
        conninfo=postgres_settings.url,
        row_factory=dict_row,
        autocommit=False,
    )
    try:
        yield conn
    finally:
        try:
            await conn.rollback()
        finally:
            await conn.close()


@pytest.fixture
def user_repo(db_connection: AsyncConnection[DictRow]) -> UserReadPostgresRepository:
    return UserReadPostgresRepository(db_connection)


@pytest.fixture
def tenant_read_repo(
    db_connection: AsyncConnection[DictRow],
) -> TenantReadPostgresRepository:
    return TenantReadPostgresRepository(db_connection)


@pytest.fixture
def tenant_version_repo(
    db_connection: AsyncConnection[DictRow],
) -> TenantVersionPostgresRepository:
    return TenantVersionPostgresRepository(db_connection)


@pytest.fixture
def tenant_subscription_repo(
    db_connection: AsyncConnection[DictRow],
) -> TenantSubscriptionPostgresRepository:
    return TenantSubscriptionPostgresRepository(db_connection)


@pytest.fixture
def category_read_repo(
    db_connection: AsyncConnection[DictRow],
) -> TransactionCategoryReadPostgresRepository:
    return TransactionCategoryReadPostgresRepository(db_connection)


@pytest.fixture
def category_version_repo(
    db_connection: AsyncConnection[DictRow],
) -> TransactionCategoryVersionPostgresRepository:
    return TransactionCategoryVersionPostgresRepository(db_connection)


@pytest.fixture
def transaction_read_repo(
    db_connection: AsyncConnection[DictRow],
) -> PersonalTransactionReadPostgresRepository:
    return PersonalTransactionReadPostgresRepository(db_connection)


@pytest.fixture
def transaction_version_repo(
    db_connection: AsyncConnection[DictRow],
) -> PersonalTransactionVersionPostgresRepository:
    return PersonalTransactionVersionPostgresRepository(db_connection)


@pytest.fixture
def user_factory() -> Callable[..., User]:
    def factory(
        *,
        user_id: UUID | None = None,
        state: UserState = UserState.ACTIVE,
        version: int = 1,
    ) -> User:
        return UserFactory.restore(
            user_id=user_id or uuid7(),
            state=state.value,
            version=version,
        )

    return factory


@pytest.fixture
def tenant_factory() -> Callable[..., Tenant]:
    def factory(
        *,
        tenant_id: UUID | None = None,
        status: TenantStatus = TenantStatus.TENANT,
        state: TenantState = TenantState.ACTIVE,
        version: int = 1,
    ) -> Tenant:
        return TenantFactory.restore(
            tenant_id=tenant_id or uuid7(),
            status=status.value,
            state=state.value,
            version=version,
        )

    return factory


@pytest.fixture
def category_factory() -> Callable[..., TransactionCategory]:
    def factory(
        *,
        category_id: UUID | None = None,
        owner_id: UUID | None = None,
        name: str = "category",
        description: str = "category description",
        state: str = "active",
        version: int = 1,
    ) -> TransactionCategory:
        return TransactionCategoryFactory.restore(
            category_id=category_id or uuid7(),
            owner_id=owner_id or uuid7(),
            name=name,
            description=description,
            state=state,
            version=version,
        )

    return factory


@pytest.fixture
def transaction_factory() -> Callable[..., PersonalTransaction]:
    def factory(
        *,
        transaction_id: UUID | None = None,
        owner_id: UUID | None = None,
        category_ids: set[UUID] | None = None,
        name: str = "tx",
        description: str = "tx description",
        transaction_type: PersonalTransactionType = PersonalTransactionType.EXPENSE,
        amount: Decimal = Decimal("100.50"),
        currency: Currency = Currency.RUBLE,
        transaction_time: datetime = datetime(2026, 4, 18, 12, 0, 0),
        state: str = "active",
        version: int = 1,
    ) -> PersonalTransaction:
        raw_category_ids = category_ids or {uuid7()}
        return PersonalTransactionFactory.restore(
            transaction_id=transaction_id or uuid7(),
            owner_id=owner_id or uuid7(),
            name=name,
            description=description,
            category_ids=raw_category_ids,
            transaction_type=transaction_type.value,
            amount=amount,
            currency=currency.value,
            transaction_time=transaction_time,
            state=state,
            version=version,
        )

    return factory


@pytest.fixture
def tenant_id_factory() -> Callable[[UUID | None], TenantID]:
    def factory(value: UUID | None = None) -> TenantID:
        return TenantID(value or uuid7())

    return factory


@pytest.fixture
def user_id_factory() -> Callable[[UUID | None], UserID]:
    def factory(value: UUID | None = None) -> UserID:
        return UserID(value or uuid7())

    return factory


@pytest.fixture
def category_id_factory() -> Callable[[UUID | None], TransactionCategoryID]:
    def factory(value: UUID | None = None) -> TransactionCategoryID:
        return TransactionCategoryID(value or uuid7())

    return factory


@pytest.fixture
def transaction_id_factory() -> Callable[[UUID | None], PersonalTransactionID]:
    def factory(value: UUID | None = None) -> PersonalTransactionID:
        return PersonalTransactionID(value or uuid7())

    return factory


@pytest.fixture
def transaction_time_factory() -> Callable[[datetime | None], PersonalTransactionTime]:
    def factory(value: datetime | None = None) -> PersonalTransactionTime:
        return PersonalTransactionTime(value or datetime(2026, 4, 18, 12, 0, 0))

    return factory
