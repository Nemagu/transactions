from pydantic import BaseModel


class UserNatsConsumerStreamSettings(BaseModel):
    stream_name: str = "users"
    main_subject_name: str = "user"
    creation_subject_name: str = "created"
    changed_state_subject_name: str = "changed_state"

    @property
    def creation_subject(self) -> str:
        return (
            f"{self.stream_name}.{self.main_subject_name}.{self.creation_subject_name}"
        )

    @property
    def changed_state_subject(self) -> str:
        return f"{self.stream_name}.{self.main_subject_name}.{self.changed_state_subject_name}"


class NatsSettings(BaseModel):
    host: str = "localhost"
    port: int = 4222
    healthcheck_file: str = "/tmp/nats_worker_healthbeat"

    loop_sleep_duration: int = 2

    connect_name: str = "transactions"
    reconnect_time_wait: int = 5
    connect_timeout: int = 5
    ping_interval: int = 120
    max_outstanding_pings: int = 3

    @property
    def url(self) -> str:
        return f"nats://{self.host}:{self.port}"
