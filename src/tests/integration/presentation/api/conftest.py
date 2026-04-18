from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from uuid import UUID

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from psycopg import AsyncConnection
from psycopg.rows import DictRow

from infrastructure.config import APISettings
from presentation.api.server import APIWorker


class _TestConnectionManager:
    def __init__(self, connection: AsyncConnection[DictRow]) -> None:
        self._connection = connection

    @asynccontextmanager
    async def connection(self) -> AsyncIterator[AsyncConnection[DictRow]]:
        yield self._connection


@pytest.fixture
def api_settings(postgres_settings) -> APISettings:
    return APISettings()


@pytest.fixture
def api_app(
    api_settings: APISettings,
    db_connection: AsyncConnection[DictRow],
) -> FastAPI:
    worker = APIWorker(api_settings)
    app = worker.app
    app.state.fastapi_settings = api_settings.fastapi
    app.state.db_connection_manager = _TestConnectionManager(db_connection)
    return app


@pytest_asyncio.fixture
async def http_client(api_app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=api_app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        yield client


@pytest.fixture
def auth_headers_factory(api_app: FastAPI) -> Callable[[UUID], dict[str, str]]:
    header_name: str = api_app.state.fastapi_settings.user_id_header_name

    def factory(user_id: UUID) -> dict[str, str]:
        return {header_name: str(user_id)}

    return factory
