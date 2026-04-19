from os import getenv

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from infrastructure.config.db import PostgresPoolSettings, PostgresSettings
from infrastructure.config.fastapi import FastAPISettings, UvicornSettings
from infrastructure.config.nats import NatsSettings, UserNatsConsumerStreamSettings
from infrastructure.config.subscriptions import SubscriptionSettings

__all__ = [
    "APIWorkerSettings",
    "FastAPISettings",
    "NatsSettings",
    "PostgresPoolSettings",
    "PostgresSettings",
    "SubscriptionSettings",
    "UserNatsConsumerStreamSettings",
    "UvicornSettings",
]


class AppBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        yaml_file=getenv("CONFIG_FILE"),
        yaml_file_encoding="utf-8",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            YamlConfigSettingsSource(
                settings_cls=settings_cls,
                yaml_file=getenv("CONFIG_FILE"),
                yaml_file_encoding="utf-8",
            ),
        )


class APIWorkerSettings(AppBaseSettings):
    fastapi: FastAPISettings = Field(default_factory=FastAPISettings)
    uvicorn: UvicornSettings = Field(default_factory=UvicornSettings)
    db: PostgresSettings = Field(default_factory=PostgresSettings)


class MessageBrokerConsumerSettings(AppBaseSettings):
    nats: NatsSettings = Field(default_factory=NatsSettings)
    user: UserNatsConsumerStreamSettings = Field(
        default_factory=UserNatsConsumerStreamSettings
    )
    db: PostgresSettings = Field(default_factory=PostgresSettings)


class SubscriptionWorkerSettings(AppBaseSettings):
    subscription: SubscriptionSettings = Field(default_factory=SubscriptionSettings)
    db: PostgresSettings = Field(default_factory=PostgresSettings)
