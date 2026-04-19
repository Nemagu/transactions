from __future__ import annotations

import os
import secrets
import shutil
import socket
import subprocess
import time
from collections.abc import Generator
from pathlib import Path
from uuid import uuid7

import psycopg
import pytest

from infrastructure.config import APIWorkerSettings, PostgresSettings
from infrastructure.db.postgres.apply_migrations import apply_migrations

TEST_DB_DIR = Path("/tmp/transactions/test-db")
DOCKER_COMPOSE_FILE: Path | None = None
POSTGRES_CONFIG_FILE: Path | None = None
POSTGRES_PASSWORD_FILE: Path | None = None

POSTGRES_USER = "transactions_test"
POSTGRES_DATABASE = "transactions_test"
POSTGRES_PORT = None
POSTGRES_PASSWORD = secrets.token_urlsafe(24)
NATS_PORT = None

DOCKER_COMPOSE_TEMPLATE = """services:
  postgres:
    image: postgres:18-alpine
    environment:
      POSTGRES_USER: {postgres_user}
      POSTGRES_DB: {postgres_db}
      POSTGRES_PASSWORD: {postgres_password}
    ports:
      - \"{postgres_port}:5432\"
    healthcheck:
      test: [\"CMD-SHELL\", \"pg_isready -U {postgres_user} -d {postgres_db}\"]
      interval: 2s
      timeout: 3s
      retries: 30
      start_period: 2s
  nats:
    image: nats:2.12-alpine
    command: [\"-js\", \"-m\", \"8222\", \"-sd\", \"/data\"]
    ports:
      - \"{nats_port}:4222\"
"""

POSTGRES_CONFIG_TEMPLATE = """db:
  port: {postgres_port}
  user: {postgres_user}
  database: {postgres_db}
  password_file: {password_file}
  pool:
    min_size: 1
    max_size: 5
    max_inactive_connection_lifetime: 60
    max_connection_lifetime: 300
    timeout: 10
nats:
  host: localhost
  port: {nats_port}
  connect_name: transactions-tests
  connect_timeout: 2
  reconnect_time_wait: 1
  loop_sleep_duration: 1
user:
  stream_name: users
  main_subject_name: user
  creation_subject_name: created
  changed_state_subject_name: changed_state
subscription:
  healthcheck_file: /tmp/subscription_worker_healthbeat
  loop_sleep_duration: 1
"""


def _choose_free_port() -> int:
    min_port = 2000
    max_port = 65000
    for _ in range(2000):
        port = secrets.randbelow(max_port - min_port + 1) + min_port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    raise RuntimeError("Не удалось подобрать свободный порт")


def _run_compose(*args: str) -> None:
    if DOCKER_COMPOSE_FILE is None:
        raise RuntimeError("Файл docker compose не подготовлен")
    command = ["docker", "compose", "-f", str(DOCKER_COMPOSE_FILE), *args]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            "Команда docker compose завершилась с ошибкой:\n"
            f"cmd: {' '.join(command)}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )


def _write_runtime_files(postgres_port: int, nats_port: int) -> None:
    if POSTGRES_PASSWORD_FILE is None:
        raise RuntimeError("Файл пароля не подготовлен")
    if DOCKER_COMPOSE_FILE is None:
        raise RuntimeError("Файл docker compose не подготовлен")
    if POSTGRES_CONFIG_FILE is None:
        raise RuntimeError("Файл конфига не подготовлен")

    TEST_DB_DIR.mkdir(parents=True, exist_ok=True)
    POSTGRES_PASSWORD_FILE.write_text(POSTGRES_PASSWORD, encoding="utf-8")

    compose_content = DOCKER_COMPOSE_TEMPLATE.format(
        postgres_user=POSTGRES_USER,
        postgres_db=POSTGRES_DATABASE,
        postgres_password=POSTGRES_PASSWORD,
        postgres_port=postgres_port,
        nats_port=nats_port,
    )
    DOCKER_COMPOSE_FILE.write_text(compose_content, encoding="utf-8")

    config_content = POSTGRES_CONFIG_TEMPLATE.format(
        postgres_user=POSTGRES_USER,
        postgres_db=POSTGRES_DATABASE,
        postgres_port=postgres_port,
        nats_port=nats_port,
        password_file=str(POSTGRES_PASSWORD_FILE),
    )
    POSTGRES_CONFIG_FILE.write_text(config_content, encoding="utf-8")


def _load_settings() -> PostgresSettings:
    if POSTGRES_CONFIG_FILE is None:
        raise RuntimeError("Файл конфига не подготовлен")
    settings = APIWorkerSettings()
    return settings.db


def _wait_postgres_ready(settings: PostgresSettings) -> None:
    timeout_sec = 60
    start = time.monotonic()
    while time.monotonic() - start < timeout_sec:
        try:
            with psycopg.connect(settings.url, connect_timeout=1) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
            return
        except Exception:
            time.sleep(1)
    raise TimeoutError("PostgreSQL не стал доступен за отведенное время")


def _wait_nats_ready(nats_port: int) -> None:
    timeout_sec = 60
    start = time.monotonic()
    while time.monotonic() - start < timeout_sec:
        try:
            with socket.create_connection(("127.0.0.1", nats_port), timeout=1) as sock:
                sock.settimeout(1)
                data = sock.recv(1024)
                if b"INFO" in data:
                    return
        except Exception:
            time.sleep(1)
    raise TimeoutError("NATS не стал доступен за отведенное время")


def _apply_migrations(settings: PostgresSettings) -> None:
    apply_migrations(settings)


@pytest.fixture(scope="session", autouse=True)
def postgres_service() -> Generator[None, None, None]:
    global \
        DOCKER_COMPOSE_FILE, \
        POSTGRES_CONFIG_FILE, \
        POSTGRES_PASSWORD_FILE, \
        POSTGRES_PORT, \
        NATS_PORT

    previous_config_file = os.environ.get("CONFIG_FILE")
    runtime_file_id = uuid7()
    DOCKER_COMPOSE_FILE = TEST_DB_DIR / f"docker-compose-{runtime_file_id}.yml"
    POSTGRES_CONFIG_FILE = TEST_DB_DIR / f"postgres-config-{runtime_file_id}.yaml"
    POSTGRES_PASSWORD_FILE = TEST_DB_DIR / f"db-password-{runtime_file_id}.txt"
    POSTGRES_PORT = _choose_free_port()
    NATS_PORT = _choose_free_port()
    _write_runtime_files(POSTGRES_PORT, NATS_PORT)
    os.environ["CONFIG_FILE"] = str(POSTGRES_CONFIG_FILE)
    settings = _load_settings()

    _run_compose("up", "-d")
    try:
        _wait_postgres_ready(settings)
        if NATS_PORT is None:
            raise RuntimeError("Порт NATS не подготовлен")
        _wait_nats_ready(NATS_PORT)
        _apply_migrations(settings)
        yield
    finally:
        try:
            _run_compose("down", "-v", "--remove-orphans")
        finally:
            for path in (
                DOCKER_COMPOSE_FILE,
                POSTGRES_CONFIG_FILE,
                POSTGRES_PASSWORD_FILE,
            ):
                if path is not None:
                    path.unlink(missing_ok=True)
            if TEST_DB_DIR.exists() and len(list(TEST_DB_DIR.iterdir())) == 0:
                shutil.rmtree(TEST_DB_DIR, ignore_errors=True)
            if previous_config_file is None:
                os.environ.pop("CONFIG_FILE", None)
            else:
                os.environ["CONFIG_FILE"] = previous_config_file


@pytest.fixture(scope="session")
def postgres_settings(postgres_service: None) -> PostgresSettings:
    return _load_settings()
