import asyncio
from collections.abc import Callable, Coroutine
from logging import getLogger
from typing import Any

from application.commands.private.tenant import (
    TenantCreationUseCase,
    TenantUpdateUseCase,
)
from application.errors import AppError, AppInternalError
from domain.errors import DomainError
from infrastructure.config import SubscriptionWorkerSettings
from infrastructure.db.postgres import PostgresConnectionManager, PostgresUnitOfWork
from presentation.background.base import BackgroundBaseWorker

logger = getLogger(__name__)

Handler = Callable[[], Coroutine[Any, Any, None]]


class SubscriptionWorker(BackgroundBaseWorker):
    def __init__(self, settings: SubscriptionWorkerSettings) -> None:
        super().__init__(settings.subscription.healthcheck_file)
        self._subscription_settings = settings.subscription
        self._db_manager = PostgresConnectionManager(settings.db)

    async def setup(self) -> None:
        await self._db_manager.init()

    async def complete(self) -> None:
        await self._db_manager.close()

    def _create_tasks(self) -> None:
        subjects_handlers = [
            (self._handle_creation_tenant, "tenant_creation"),
            (self._handle_update_tenant, "tenant_update"),
        ]
        for handler, name in subjects_handlers:
            self._tasks.append(asyncio.create_task(self._subscribe(handler, name)))

    async def _subscribe(self, handler: Handler, name: str) -> None:
        while not self._shutdown_event.is_set():
            self._update_heartbeat()
            processing_error: BaseException | None = None
            try:
                await handler()
            except asyncio.CancelledError:
                return
            except BaseException as err:
                processing_error = err
            self._log_processing_error(name, processing_error)
            await asyncio.sleep(self._subscription_settings.loop_sleep_duration)

    async def _handle_creation_tenant(self) -> None:
        async with self._db_manager.connection() as conn:
            await TenantCreationUseCase(PostgresUnitOfWork(conn)).execute()

    async def _handle_update_tenant(self) -> None:
        async with self._db_manager.connection() as conn:
            await TenantUpdateUseCase(PostgresUnitOfWork(conn)).execute()

    def _log_processing_error(self, name: str, error: BaseException | None) -> None:
        if error is None:
            return
        if isinstance(error, DomainError):
            logger.warning(
                "[%s] domain error: %s, struct_name: %s, data=%s",
                name,
                error.msg,
                error.struct_name,
                error.data,
            )
            return
        if isinstance(error, AppInternalError):
            logger.error(
                "[%s] app internal error: %s, action: %s, data=%s",
                name,
                error.msg,
                error.action,
                error.data,
            )
            return
        if isinstance(error, AppError):
            logger.warning(
                "[%s] app error: %s, action: %s, data=%s",
                name,
                error.msg,
                error.action,
                error.data,
            )
            return
        logger.error("[%s] handler error: %s", name, error)
