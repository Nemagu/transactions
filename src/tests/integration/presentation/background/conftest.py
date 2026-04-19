from __future__ import annotations

import pytest
import pytest_asyncio
from nats import connect
from nats.js.client import JetStreamContext
from nats.js.errors import NotFoundError

from infrastructure.config import (
    MessageBrokerConsumerSettings,
    SubscriptionWorkerSettings,
)


@pytest.fixture
def message_broker_consumer_settings() -> MessageBrokerConsumerSettings:
    settings = MessageBrokerConsumerSettings()
    settings.nats.loop_sleep_duration = 0.2
    settings.nats.reconnect_time_wait = 0.2
    return settings


@pytest.fixture
def subscription_worker_settings() -> SubscriptionWorkerSettings:
    settings = SubscriptionWorkerSettings()
    settings.subscription.loop_sleep_duration = 0.2
    return settings


@pytest_asyncio.fixture
async def nats_jetstream(
    message_broker_consumer_settings: MessageBrokerConsumerSettings,
) -> JetStreamContext:
    settings = message_broker_consumer_settings
    nc = await connect(settings.nats.url, name="transactions-integration-tests")
    js = nc.jetstream()
    stream_name = settings.user.stream_name
    stream_subject = f"{stream_name}.{settings.user.main_subject_name}.>"

    try:
        await js.delete_stream(stream_name)
    except NotFoundError:
        pass

    await js.add_stream(name=stream_name, subjects=[stream_subject])

    try:
        yield js
    finally:
        try:
            await js.delete_stream(stream_name)
        except NotFoundError:
            pass
        await nc.close()
