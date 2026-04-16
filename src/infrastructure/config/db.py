from os import path
from typing import Self

from pydantic import BaseModel, Field, SecretStr, model_validator


class PostgresPoolSettings(BaseModel):
    min_size: int = 10
    max_size: int = 20
    max_inactive_connection_lifetime: int = 300
    max_connection_lifetime: int = 3600
    timeout: int = 20


class PostgresSettings(BaseModel):
    host: str = "localhost"
    port: int = 5432
    user: str = "companies_service"
    password_file: str = "path/to/db/password"
    database: str = "companies_service"

    pool: PostgresPoolSettings = Field(default_factory=PostgresPoolSettings)

    @model_validator(mode="after")
    def _load_password_from_file(self) -> Self:
        if not path.isfile(self.password_file):
            raise ValueError(f"Password file not found: {self.password_file}")
        return self

    @property
    def password(self) -> SecretStr:
        if not hasattr(self, "_password"):
            with open(self.password_file, "r") as f:
                self._password = SecretStr(f.read().strip())
        return self._password

    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.database}"

    @property
    def url_with_psycopg(self) -> str:
        return f"postgresql+psycopg://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.database}"
