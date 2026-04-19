from __future__ import annotations

from json import JSONDecodeError

import pytest
from nats.errors import TimeoutError as NatsTimeoutError

from application.errors import AppInternalError, AppInvalidDataError, AppNotFoundError
from domain.errors import EntityPolicyError
from infrastructure.config import MessageBrokerConsumerSettings
from presentation.background.nats.base import NATS_CONNECTION_ERRORS
from presentation.background.nats.consumer import (
    MessageResponseType,
    NatsConsumerWorker,
)


class _FakeMsg:
    def __init__(self, *, fail_on: str | None = None, fail_exception: BaseException | None = None) -> None:
        self.calls: list[str] = []
        self._fail_on = fail_on
        self._fail_exception = fail_exception

    async def ack(self) -> None:
        self.calls.append("ack")
        if self._fail_on == "ack" and self._fail_exception is not None:
            raise self._fail_exception

    async def nak(self) -> None:
        self.calls.append("nak")
        if self._fail_on == "nak" and self._fail_exception is not None:
            raise self._fail_exception

    async def term(self) -> None:
        self.calls.append("term")
        if self._fail_on == "term" and self._fail_exception is not None:
            raise self._fail_exception


class _FakePullSubscription:
    def __init__(self, fetch_result=None, fetch_exception: BaseException | None = None) -> None:
        self._fetch_result = fetch_result or []
        self._fetch_exception = fetch_exception

    async def fetch(self, *_args, **_kwargs):
        if self._fetch_exception is not None:
            raise self._fetch_exception
        return self._fetch_result


def _build_worker() -> NatsConsumerWorker:
    settings = MessageBrokerConsumerSettings()
    return NatsConsumerWorker(settings)


def test_resolve_message_response_type_maps_errors_to_response_type() -> None:
    worker = _build_worker()

    assert worker._resolve_message_response_type(None) == MessageResponseType.ACK
    assert (
        worker._resolve_message_response_type(
            JSONDecodeError("invalid", "{", 0),
        )
        == MessageResponseType.TERM
    )
    assert (
        worker._resolve_message_response_type(
            AppNotFoundError(msg="missing", action="update user"),
        )
        == MessageResponseType.NAK
    )
    assert (
        worker._resolve_message_response_type(
            AppInternalError(msg="boom", action="process"),
        )
        == MessageResponseType.NAK
    )
    assert (
        worker._resolve_message_response_type(
            EntityPolicyError(msg="denied", struct_name="tenant"),
        )
        == MessageResponseType.TERM
    )
    assert (
        worker._resolve_message_response_type(
            AppInvalidDataError(msg="invalid", action="process"),
        )
        == MessageResponseType.TERM
    )
    assert (
        worker._resolve_message_response_type(RuntimeError("unexpected"))
        == MessageResponseType.NAK
    )


@pytest.mark.asyncio
async def test_handle_message_response_calls_expected_msg_method() -> None:
    worker = _build_worker()

    msg = _FakeMsg()
    sent = await worker._handle_message_response(msg, MessageResponseType.ACK, "test")
    assert sent is True
    assert msg.calls == ["ack"]

    msg = _FakeMsg()
    sent = await worker._handle_message_response(msg, MessageResponseType.NAK, "test")
    assert sent is True
    assert msg.calls == ["nak"]

    msg = _FakeMsg()
    sent = await worker._handle_message_response(msg, MessageResponseType.TERM, "test")
    assert sent is True
    assert msg.calls == ["term"]


@pytest.mark.asyncio
async def test_handle_message_response_returns_false_on_nats_connection_error() -> None:
    worker = _build_worker()
    nats_error_cls = NATS_CONNECTION_ERRORS[0]
    msg = _FakeMsg(
        fail_on="ack",
        fail_exception=nats_error_cls(),
    )

    sent = await worker._handle_message_response(msg, MessageResponseType.ACK, "test")

    assert sent is False
    assert msg.calls == ["ack"]


def test_extract_user_data_from_payload_validates_and_casts_uuid() -> None:
    worker = _build_worker()

    user_id, state, version = worker._extract_user_data_from_payload(
        {"user_id": "00000000-0000-0000-0000-000000000123", "state": "active", "version": 3}
    )

    assert str(user_id) == "00000000-0000-0000-0000-000000000123"
    assert state == "active"
    assert version == 3


def test_extract_user_data_from_payload_raises_for_invalid_payload() -> None:
    worker = _build_worker()

    with pytest.raises(AppInternalError):
        worker._extract_user_data_from_payload(
            {"user_id": "not-a-uuid", "state": "active", "version": "v1"}
        )


@pytest.mark.asyncio
async def test_fetch_message_returns_none_on_timeout() -> None:
    worker = _build_worker()
    sub = _FakePullSubscription(fetch_exception=NatsTimeoutError())

    result = await worker._fetch_message(sub, "test")

    assert result is None


@pytest.mark.asyncio
async def test_fetch_message_reraises_nats_connection_error() -> None:
    worker = _build_worker()
    nats_error_cls = NATS_CONNECTION_ERRORS[0]
    sub = _FakePullSubscription(fetch_exception=nats_error_cls())

    with pytest.raises(nats_error_cls):
        await worker._fetch_message(sub, "test")


@pytest.mark.asyncio
async def test_fetch_message_returns_none_on_unexpected_error() -> None:
    worker = _build_worker()
    sub = _FakePullSubscription(fetch_exception=RuntimeError("fetch failed"))

    result = await worker._fetch_message(sub, "test")

    assert result is None
