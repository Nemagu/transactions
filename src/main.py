from asyncio import Runner
from logging import CRITICAL, getLogger
from os import getenv

from uvloop import new_event_loop

from infrastructure.config import (
    APIWorkerSettings,
    MessageBrokerConsumerSettings,
    PostgresSettings,
    SubscriptionWorkerSettings,
)
from presentation.api.server import APIWorker
from presentation.background.nats import NatsConsumerWorker
from presentation.background.subscriptions import SubscriptionWorker

logger = getLogger(__name__)


def main():
    def apply_db_migrations(db_settings: PostgresSettings) -> None:
        if getenv("APPLY_MIGRATIONS", "1") == "1":
            from infrastructure.db.postgres import apply_migrations

            logger.info("applying migrations")
            apply_migrations(db_settings)
            logger.info("migrations applied")

    mode = getenv("MODE", "api")
    logger.info(f"starting app in mode: {mode}")

    match mode:
        case "api":
            logger.info("init api settings")
            api_settings = APIWorkerSettings()
            apply_db_migrations(api_settings.db)
            logger.info("init api worker")
            app = APIWorker(api_settings)
            logger.info("run api worker")
            app.run()
        case "nats_consumer":
            getLogger("nats").setLevel(CRITICAL)
            logger.info("init nats worker settings")
            nats_settings = MessageBrokerConsumerSettings()
            apply_db_migrations(nats_settings.db)
            logger.info("init nats worker")
            worker = NatsConsumerWorker(nats_settings)
            logger.info("run nats worker")
            with Runner(loop_factory=new_event_loop) as runner:
                runner.run(worker.run())
        case "subscriptions_worker":
            logger.info("init subscriptions worker settings")
            subscriptions_settings = SubscriptionWorkerSettings()
            apply_db_migrations(subscriptions_settings.db)
            logger.info("init subscriptions worker")
            worker = SubscriptionWorker(subscriptions_settings)
            logger.info("run subscriptions worker")
            with Runner(loop_factory=new_event_loop) as runner:
                runner.run(worker.run())
        case _:
            raise ValueError(f"Invalid mode: {mode}")


if __name__ == "__main__":
    main()
