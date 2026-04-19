# transactions

Сервис для учета персональных транзакций с разделением на слои `domain`, `application`, `infrastructure`, `presentation`.

## Технологии

- Python 3.14+
- FastAPI
- PostgreSQL
- NATS JetStream
- pydantic + pydantic-settings (чтение YAML-конфига)
- pytest / pytest-asyncio / pytest-cov

## Режимы запуска

Приложение запускается через `src/main.py` и поддерживает 3 режима:

1. `api`
2. `nats_consumer`
3. `subscriptions_worker`

Выбор режима задается переменной окружения `MODE`.

## Конфиг

Конфиг читается из YAML-файла, путь передается через переменную окружения `CONFIG_FILE`.

Переменные окружения:

- `CONFIG_FILE` — путь до YAML-конфига.
- `MODE` — режим запуска (`api`, `nats_consumer`, `subscriptions_worker`).
- `APPLY_MIGRATIONS` — применять миграции при старте (`1` или `0`, по умолчанию `1`).

Готовые примеры:

- `config/examples/api.yaml`
- `config/examples/nats_consumer.yaml`
- `config/examples/subscriptions_worker.yaml`

Важно: поле `db.password_file` должно указывать на существующий файл с паролем PostgreSQL.

## Примеры конфигов

### API (`config/examples/api.yaml`)

```yaml
fastapi:
  user_id_header_name: X-User-Id

uvicorn:
  host: 0.0.0.0
  port: 8000
  workers: 1
  reload: false
  loop: uvloop

db:
  host: localhost
  port: 5432
  user: transactions_user
  password_file: /run/secrets/transactions_db_password
  database: transactions
  pool:
    min_size: 10
    max_size: 20
    max_inactive_connection_lifetime: 300
    max_connection_lifetime: 3600
    timeout: 20
```

### NATS Consumer Worker (`config/examples/nats_consumer.yaml`)

```yaml
nats:
  host: localhost
  port: 4222
  healthcheck_file: /tmp/nats_worker_healthbeat
  loop_sleep_duration: 2
  connect_name: transactions-consumer
  reconnect_time_wait: 5
  connect_timeout: 5
  ping_interval: 120
  max_outstanding_pings: 3

user:
  stream_name: users
  main_subject_name: user
  creation_subject_name: created
  changed_state_subject_name: changed_state

db:
  host: localhost
  port: 5432
  user: transactions_user
  password_file: /run/secrets/transactions_db_password
  database: transactions
  pool:
    min_size: 10
    max_size: 20
    max_inactive_connection_lifetime: 300
    max_connection_lifetime: 3600
    timeout: 20
```

### Subscriptions Worker (`config/examples/subscriptions_worker.yaml`)

```yaml
subscription:
  healthcheck_file: /tmp/subscription_worker_healthbeat
  loop_sleep_duration: 10

db:
  host: localhost
  port: 5432
  user: transactions_user
  password_file: /run/secrets/transactions_db_password
  database: transactions
  pool:
    min_size: 10
    max_size: 20
    max_inactive_connection_lifetime: 300
    max_connection_lifetime: 3600
    timeout: 20
```

## Запуск

### 1) API

```bash
CONFIG_FILE=config/examples/api.yaml \
MODE=api \
APPLY_MIGRATIONS=1 \
uv run python src/main.py
```

### 2) NATS Consumer Worker

```bash
CONFIG_FILE=config/examples/nats_consumer.yaml \
MODE=nats_consumer \
APPLY_MIGRATIONS=1 \
uv run python src/main.py
```

### 3) Subscriptions Worker

```bash
CONFIG_FILE=config/examples/subscriptions_worker.yaml \
MODE=subscriptions_worker \
APPLY_MIGRATIONS=1 \
uv run python src/main.py
```

## Тесты

Запуск всех тестов:

```bash
uv run pytest
```

Проверка покрытия:

```bash
uv run pytest --cov=src --cov-report=term-missing
```

Линтер:

```bash
uv run ruff check
```
