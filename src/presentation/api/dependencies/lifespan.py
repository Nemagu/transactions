from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from infrastructure.config import APISettings
from infrastructure.db.postgres import PostgresConnectionManager


class APILifespan:
    def __init__(self, settings: APISettings) -> None:
        self._settings = settings

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncGenerator:
        connection_manager = PostgresConnectionManager(self._settings.db)
        await connection_manager.init()
        app.state.fastapi_settings = self._settings.fastapi
        app.state.db_connection_manager = connection_manager
        yield
        await connection_manager.close()
