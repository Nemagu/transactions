from os import path

from msgspec import Struct, field


class PostgresPoolSettings(Struct):
    min_size: int = 10
    max_size: int = 20
    max_inactive_connection_lifetime: int = 300
    max_connection_lifetime: int = 3600
    timeout: int = 20


class PostgresSettings(Struct):
    host: str = "localhost"
    port: int = 5432
    user: str = "companies_service"
    password_file: str = "/tmp/transactions/db_password"
    database: str = "companies_service"

    pool: PostgresPoolSettings = field(default_factory=PostgresPoolSettings)

    def __post_init__(self) -> None:
        if not path.isfile(self.password_file):
            raise ValueError(f"Password file not found: {self.password_file}")

    @property
    def password(self) -> str:
        with open(self.password_file, "r", encoding="utf-8") as file:
            return file.read().strip()

    @property
    def url(self) -> str:
        return (
            f"postgresql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )

    @property
    def url_with_psycopg(self) -> str:
        return (
            f"postgresql+psycopg://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )
