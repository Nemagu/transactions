import asyncio
import json
from collections.abc import Callable, Coroutine
from enum import StrEnum
from json import JSONDecodeError
from logging import getLogger
from typing import Any
from uuid import UUID

from nats.aio.msg import Msg
from nats.errors import TimeoutError as NatsTimeoutError
from nats.js.client import JetStreamContext
from pydantic import BaseModel, ValidationError

from application.commands.private.user import (
    UserCreationCommand,
    UserCreationUseCase,
    UserUpdateCommand,
    UserUpdateUseCase,
)
from application.errors import AppError, AppInternalError, AppNotFoundError
from domain.errors import DomainError
from infrastructure.config import MessageBrokerConsumerSettings
from infrastructure.db.postgres import PostgresUnitOfWork
from presentation.background.nats.base import (
    NATS_CONNECTION_ERRORS,
    NatsBaseWorker,
)

logger = getLogger(__name__)

Handler = Callable[[dict], Coroutine[Any, Any, None]]


class MessageResponseType(StrEnum):
    ACK = "ack"
    NAK = "nak"
    TERM = "term"


class _InvalidUserPayloadError(AppInternalError):
    pass


class UserPayload(BaseModel):
    user_id: UUID
    state: str
    version: int


class NatsConsumerWorker(NatsBaseWorker):
    def __init__(self, settings: MessageBrokerConsumerSettings) -> None:
        super().__init__(settings.nats, settings.db)
        self._user_stream = settings.user

    def _create_tasks(self) -> None:
        subjects_handlers = [
            (
                self._user_stream.creation_subject,
                self._handle_creation_user,
                "user_creation",
            ),
            (
                self._user_stream.changed_state_subject,
                self._handle_update_user,
                "user_update",
            ),
        ]
        for subject, handler, name in subjects_handlers:
            self._tasks.append(
                asyncio.create_task(self._consume(subject, handler, name))
            )

    async def _fetch_message(
        self, sub: JetStreamContext.PullSubscription, name: str
    ) -> Msg | None:
        try:
            msgs = await sub.fetch(1, timeout=self._nats_settings.loop_sleep_duration)
            return msgs[0]
        except NatsTimeoutError:
            return None
        except NATS_CONNECTION_ERRORS:
            raise
        except asyncio.CancelledError:
            raise
        except BaseException as e:
            logger.error("[%s] fetch message error: %s", name, e)
            return None

    async def _consume(self, subject: str, handler: Handler, name: str) -> None:
        sub = None
        while not self._shutdown_event.is_set():
            self._update_heartbeat()
            try:
                if sub is None:
                    sub = await self._js.pull_subscribe(subject)  # pyright: ignore[reportOptionalMemberAccess]
                msg = await self._fetch_message(sub, name)
            except NATS_CONNECTION_ERRORS:
                logger.warning("[%s] nats connection lost, reconnecting...", name)
                sub = None
                await self._connect_nats()
                continue
            except asyncio.CancelledError:
                return
            except BaseException as e:
                logger.error("[%s] subscribe error: %s", name, e)
                await asyncio.sleep(self._nats_settings.reconnect_time_wait)
                continue

            if msg is None:
                await asyncio.sleep(self._nats_settings.loop_sleep_duration)
                continue

            processing_error: BaseException | None = None
            try:
                await handler(json.loads(msg.data))
            except asyncio.CancelledError:
                return
            except BaseException as err:
                processing_error = err

            response_type = self._resolve_message_response_type(processing_error)
            self._log_processing_error(name, processing_error)
            try:
                response_sent = await self._handle_message_response(
                    msg=msg,
                    response_type=response_type,
                    name=name,
                )
            except asyncio.CancelledError:
                return

            if not response_sent:
                sub = None
                await self._connect_nats()

            await asyncio.sleep(self._nats_settings.loop_sleep_duration)

    async def _handle_creation_user(self, payload: dict) -> None:
        user_id, state, version = self._extract_user_data_from_payload(payload)
        command = UserCreationCommand(user_id, state, version)
        async with self._db_manager.connection() as db_conn:
            await UserCreationUseCase(PostgresUnitOfWork(db_conn)).execute(command)

    async def _handle_update_user(self, payload: dict) -> None:
        user_id, state, version = self._extract_user_data_from_payload(payload)
        command = UserUpdateCommand(user_id, state, version)
        async with self._db_manager.connection() as db_conn:
            await UserUpdateUseCase(PostgresUnitOfWork(db_conn)).execute(command)

    def _extract_user_data_from_payload(self, payload: dict) -> tuple[UUID, str, int]:
        try:
            data = UserPayload.model_validate(payload)
        except ValidationError as err:
            raise _InvalidUserPayloadError(
                msg="некорректный payload пользователя в сообщении для потребления",
                action="извлечение данных из сообщения о пользователе",
                data={"payload": payload, "errors": err.errors()},
                wrap_error=err,
            )
        return data.user_id, data.state, data.version

    def _resolve_message_response_type(
        self, error: BaseException | None
    ) -> MessageResponseType:
        if error is None:
            return MessageResponseType.ACK
        if isinstance(error, (_InvalidUserPayloadError, JSONDecodeError)):
            return MessageResponseType.TERM
        if isinstance(error, AppNotFoundError):
            return MessageResponseType.NAK
        if isinstance(error, AppInternalError):
            return MessageResponseType.NAK
        if isinstance(error, (DomainError, AppError)):
            return MessageResponseType.TERM
        return MessageResponseType.NAK

    async def _handle_message_response(
        self,
        msg: Msg,
        response_type: MessageResponseType,
        name: str,
    ) -> bool:
        try:
            match response_type:
                case MessageResponseType.ACK:
                    await msg.ack()
                case MessageResponseType.NAK:
                    await msg.nak()
                case MessageResponseType.TERM:
                    await msg.term()
            return True
        except NATS_CONNECTION_ERRORS:
            logger.warning(
                "[%s] nats connection lost on message response (%s), reconnecting...",
                name,
                response_type.value,
            )
            return False
        except asyncio.CancelledError:
            raise
        except BaseException as err:
            logger.error(
                "[%s] message response (%s) failed: %s",
                name,
                response_type.value,
                err,
            )
            return True

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
        if isinstance(error, _InvalidUserPayloadError):
            logger.error(
                "[%s] invalid user payload: %s, action: %s, data=%s",
                name,
                error.msg,
                error.action,
                error.data,
            )
            return
        if isinstance(error, JSONDecodeError):
            logger.error("[%s] invalid json payload: %s", name, error)
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
