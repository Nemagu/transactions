from __future__ import annotations

import asyncio
import json
import time
from uuid import UUID, uuid7

import pytest
from nats.js.client import JetStreamContext

from domain.user import UserID, UserState
from infrastructure.config import MessageBrokerConsumerSettings
from presentation.background.nats import NatsConsumerWorker


async def _wait_user_state(
    user_repo,
    user_id: UUID,
    state: UserState,
    version: int,
    timeout_sec: int = 20,
) -> None:
    started_at = time.monotonic()
    while time.monotonic() - started_at < timeout_sec:
        user = await user_repo.by_id(UserID(user_id))
        if (
            user is not None
            and user.state == state
            and user.version.version == version
        ):
            return
        await asyncio.sleep(0.2)
    raise TimeoutError("Пользователь не был обработан воркером в отведенное время")


@pytest.mark.asyncio
async def test_nats_consumer_worker_creates_and_updates_user(
    nats_jetstream: JetStreamContext,
    message_broker_consumer_settings: MessageBrokerConsumerSettings,
    user_repo,
) -> None:
    worker = NatsConsumerWorker(message_broker_consumer_settings)
    worker_task = asyncio.create_task(worker.run())
    user_id = uuid7()

    try:
        await asyncio.sleep(1)

        await nats_jetstream.publish(
            subject=message_broker_consumer_settings.user.creation_subject,
            payload=json.dumps(
                {
                    "user_id": str(user_id),
                    "state": UserState.ACTIVE.value,
                    "version": 1,
                }
            ).encode(),
        )
        await _wait_user_state(user_repo, user_id, UserState.ACTIVE, 1)

        await nats_jetstream.publish(
            subject=message_broker_consumer_settings.user.changed_state_subject,
            payload=json.dumps(
                {
                    "user_id": str(user_id),
                    "state": UserState.FROZEN.value,
                    "version": 2,
                }
            ).encode(),
        )
        await _wait_user_state(user_repo, user_id, UserState.FROZEN, 2)
    finally:
        worker._shutdown_event.set()
        await asyncio.wait_for(worker_task, timeout=10)
