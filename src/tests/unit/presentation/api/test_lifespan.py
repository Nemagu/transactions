from __future__ import annotations

import pytest
from fastapi import FastAPI

from infrastructure.config import APIWorkerSettings
from presentation.api.dependencies.lifespan import APILifespan


@pytest.mark.asyncio
async def test_lifespan_sets_app_state_and_closes_connection_manager(monkeypatch) -> None:
    created_managers: list[object] = []

    class _FakeConnectionManager:
        def __init__(self, db_settings) -> None:
            self.db_settings = db_settings
            self.inited = False
            self.closed = False
            created_managers.append(self)

        async def init(self) -> None:
            self.inited = True

        async def close(self) -> None:
            self.closed = True

    monkeypatch.setattr(
        "presentation.api.dependencies.lifespan.PostgresConnectionManager",
        _FakeConnectionManager,
    )

    settings = APIWorkerSettings()
    app = FastAPI()
    lifespan = APILifespan(settings)

    async with lifespan.lifespan(app):
        assert len(created_managers) == 1
        manager = created_managers[0]
        assert manager.inited is True
        assert app.state.fastapi_settings == settings.fastapi
        assert app.state.db_connection_manager is manager

    manager = created_managers[0]
    assert manager.closed is True
