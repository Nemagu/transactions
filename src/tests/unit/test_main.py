from __future__ import annotations

import importlib

import pytest


def _patch_getenv(monkeypatch, main_module, values: dict[str, str]) -> None:
    def fake_getenv(key: str, default: str | None = None) -> str | None:
        return values.get(key, default)

    monkeypatch.setattr(main_module, "getenv", fake_getenv)


def test_main_runs_api_mode_and_applies_migrations(monkeypatch) -> None:
    main_module = importlib.import_module("main")

    calls = {"migrations": 0, "api_run": 0}

    class FakeAPISettings:
        def __init__(self) -> None:
            self.db = object()

    class FakeAPIWorker:
        def __init__(self, settings) -> None:
            self.settings = settings

        def run(self) -> None:
            calls["api_run"] += 1

    from infrastructure.db import postgres as postgres_module

    def fake_apply_migrations(_db_settings) -> None:
        calls["migrations"] += 1

    monkeypatch.setattr(postgres_module, "apply_migrations", fake_apply_migrations)
    monkeypatch.setattr(main_module, "APIWorkerSettings", FakeAPISettings)
    monkeypatch.setattr(main_module, "APIWorker", FakeAPIWorker)
    _patch_getenv(monkeypatch, main_module, {"MODE": "api", "APPLY_MIGRATIONS": "1"})

    main_module.main()

    assert calls["migrations"] == 1
    assert calls["api_run"] == 1


def test_main_runs_nats_consumer_mode(monkeypatch) -> None:
    main_module = importlib.import_module("main")

    calls = {"worker_run": 0}

    class FakeNatsSettings:
        def __init__(self) -> None:
            self.db = object()

    class FakeNatsWorker:
        def __init__(self, settings) -> None:
            self.settings = settings

        def run(self):
            calls["worker_run"] += 1
            return None

    class FakeRunner:
        def __init__(self, *args, **kwargs) -> None:
            self.args = args
            self.kwargs = kwargs

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> bool:
            return False

        def run(self, awaitable) -> None:
            return None

    monkeypatch.setattr(main_module, "MessageBrokerConsumerSettings", FakeNatsSettings)
    monkeypatch.setattr(main_module, "NatsConsumerWorker", FakeNatsWorker)
    monkeypatch.setattr(main_module, "Runner", FakeRunner)
    _patch_getenv(
        monkeypatch,
        main_module,
        {"MODE": "nats_consumer", "APPLY_MIGRATIONS": "0"},
    )

    main_module.main()

    assert calls["worker_run"] == 1


def test_main_runs_subscription_mode(monkeypatch) -> None:
    main_module = importlib.import_module("main")

    calls = {"worker_run": 0}

    class FakeSubSettings:
        def __init__(self) -> None:
            self.db = object()

    class FakeSubWorker:
        def __init__(self, settings) -> None:
            self.settings = settings

        def run(self):
            calls["worker_run"] += 1
            return None

    class FakeRunner:
        def __init__(self, *args, **kwargs) -> None:
            self.args = args
            self.kwargs = kwargs

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> bool:
            return False

        def run(self, awaitable) -> None:
            return None

    monkeypatch.setattr(main_module, "SubscriptionWorkerSettings", FakeSubSettings)
    monkeypatch.setattr(main_module, "SubscriptionWorker", FakeSubWorker)
    monkeypatch.setattr(main_module, "Runner", FakeRunner)
    _patch_getenv(
        monkeypatch,
        main_module,
        {"MODE": "subscriptions_worker", "APPLY_MIGRATIONS": "0"},
    )

    main_module.main()

    assert calls["worker_run"] == 1


def test_main_raises_for_invalid_mode(monkeypatch) -> None:
    main_module = importlib.import_module("main")
    _patch_getenv(monkeypatch, main_module, {"MODE": "unknown", "APPLY_MIGRATIONS": "0"})

    with pytest.raises(ValueError):
        main_module.main()
