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

__all__ = [
    "APISettings",
    "FastAPISettings",
    "PostgresPoolSettings",
    "PostgresSettings",
    "UvicornSettings",
]


class APISettings(BaseSettings):
    model_config = SettingsConfigDict(
        yaml_file=getenv("CONFIG_FILE"),
        yaml_file_encoding="utf-8",
        extra="ignore",
    )

    fastapi: FastAPISettings = Field(default_factory=FastAPISettings)
    uvicorn: UvicornSettings = Field(default_factory=UvicornSettings)
    db: PostgresSettings = Field(default_factory=PostgresSettings)

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
