from pydantic import BaseModel


class SubscriptionSettings(BaseModel):
    healthcheck_file: str = "/tmp/subscription_worker_healthbeat"
    loop_sleep_duration: int = 10
