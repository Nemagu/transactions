from types import TracebackType
from typing import Self

from psycopg import AsyncConnection
from psycopg.rows import DictRow

from application.errors import AppInternalError
from application.ports.repositories import (
    PersonalTransactionRepositories,
    TenantRepositories,
    TransactionCategoryRepositories,
    UserRepositories,
)
from application.ports.unit_of_work import UnitOfWork
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


class PostgresUnitOfWork(UnitOfWork):
    def __init__(self, connection: AsyncConnection[DictRow]) -> None:
        self._conn = connection
        self._committed = False
        self._rolled_back = False
        self._closed = False
        self._user_repositories = None
        self._tenant_repositories = None
        self._category_repositories = None
        self._transaction_repositories = None

    @property
    def user_repositories(self) -> UserRepositories:
        if self._user_repositories is None:
            self._user_repositories = UserRepositories(
                UserReadPostgresRepository(self._conn)
            )
        return self._user_repositories

    @property
    def tenant_repositories(self) -> TenantRepositories:
        if self._tenant_repositories is None:
            self._tenant_repositories = TenantRepositories(
                TenantReadPostgresRepository(self._conn),
                TenantVersionPostgresRepository(self._conn),
                TenantSubscriptionPostgresRepository(self._conn),
            )
        return self._tenant_repositories

    @property
    def category_repositories(self) -> TransactionCategoryRepositories:
        if self._category_repositories is None:
            self._category_repositories = TransactionCategoryRepositories(
                TransactionCategoryReadPostgresRepository(self._conn),
                TransactionCategoryVersionPostgresRepository(self._conn),
            )
        return self._category_repositories

    @property
    def transaction_repositories(self) -> PersonalTransactionRepositories:
        if self._transaction_repositories is None:
            self._transaction_repositories = PersonalTransactionRepositories(
                PersonalTransactionReadPostgresRepository(self._conn),
                PersonalTransactionVersionPostgresRepository(self._conn),
            )
        return self._transaction_repositories

    async def __aenter__(self) -> Self:
        await self._conn.execute("BEGIN")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is None and not self._committed and not self._rolled_back:
            await self._commit()
        if exc_type is not None and not self._rolled_back:
            await self._rollback()

    def _ensure_active(self) -> None:
        if self._committed:
            raise AppInternalError(
                msg="UoW уже закоммичен",
                action="повторная попытка коммита в базу данных",
            )
        if self._rolled_back:
            raise AppInternalError(
                msg="UoW уже откачен", action="повторная попытка отката транзакции"
            )
        if self._closed:
            raise AppInternalError(
                msg="UoW уже закрыт", action="повторная попытка закрытия соединения"
            )

    async def _commit(self) -> None:
        self._ensure_active()
        try:
            await self._conn.execute("COMMIT")
            self._committed = True
        except BaseException as err:
            await self._rollback()
            raise AppInternalError(
                msg=f"ошибка при коммите: {err}",
                action="коммит в базу данных",
                wrap_error=err,
            )

    async def _rollback(self) -> None:
        self._ensure_active()
        try:
            await self._conn.execute("ROLLBACK")
            self._rolled_back = True
        except BaseException as err:
            raise AppInternalError(
                msg=f"ошибка при роллбэке: {err}",
                action="откат изменений транзакции",
                wrap_error=err,
            )

    async def _close(self) -> None:
        await self._conn.close()
