# Stina

Backend-сервис для записи на встречи. Пользователь создаёт бронь через REST API, система ставит задачу в очередь, воркер асинхронно подтверждает запись и логирует mock-уведомление.

> ⚠️ MVP. Проект реализован в рамках тестового задания.

## Стек

- **Python 3.14**, **FastAPI**, **SQLAlchemy 2 (async)**
- **PostgreSQL 18**, **Redis 7**
- **TaskIQ** + **taskiq-redis** (очередь и result backend)
- **Alembic** (миграции), **pytest** (тесты), **uv** (зависимости)

Документация после запуска: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Запуск сервиса

### Требования

- Docker и Docker Compose
- (опционально) [uv](https://docs.astral.sh/uv/) для локальной разработки и тестов

### 1. Клонирование и окружение

```bash
git clone https://github.com/sibeardev/stina.git
cd stina
cp .env.example .env
```

Переменные в `.env` (имена сервисов — из `docker-compose.yml`):

```env
POSTGRES_DB=db
POSTGRES_USER=user
POSTGRES_PASSWORD=password
REDIS_URL=redis://redis:6379/0
```

`POSTGRES_HOST` по умолчанию `db` — задаётся в [`app/core/config.py`](app/core/config.py) для контейнеров

### 2. Запуск

```bash
docker compose up --build
```

Поднимаются сервисы:

- **api** — FastAPI на порту `8000`
- **worker** — TaskIQ-воркер
- **db** — PostgreSQL
- **redis** — брокер и result backend

### 3. Миграции

При старте API автоматически выполняется `alembic upgrade head` (с повторными попытками, пока Postgres не готов).

Ручной запуск при необходимости:

```bash
docker compose exec api uv run alembic upgrade head
```

### 4. Пример запроса

```bash
curl -X POST http://localhost:8000/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Иван",
    "datetime": "2026-12-01T15:00:00+03:00",
    "service_type": "consultation"
  }'
```

### 5. Остановка

```bash
docker compose down
```

Данные Postgres сохраняются в volume `postgres_data`. Полное удаление: `docker compose down -v`.

---

## Тесты

Тесты **не требуют Docker**: используется SQLite in-memory и мок постановки задачи в очередь.

```bash
uv sync --group dev
uv run pytest
```

С подробным выводом:

```bash
uv run pytest -v
```

Покрытие:

- API: создание, список, статус, отмена, валидация и пагинация
- воркер: подтверждение, имитация сбоя внешнего сервиса, идемпотентность

---

## Технические решения

### FastAPI + async SQLAlchemy

API полностью асинхронный (`asyncpg`). Согласуется с TaskIQ worker (тот же `BookingService` и та же async-сессия, без отдельного sync-слоя).

### TaskIQ вместо Celery

В задании Celery указан как базовый вариант. **TaskIQ** выбран как плюс за async-first подход:

Постановка задачи — в роуте **после** `commit` в `service.create()`, чтобы воркер в отдельном процессе уже видел запись в БД

### Идемпотентность

Повторный запуск `confirm_booking_task` с тем же `booking_id` безопасен:

1. Бронь читается с **`SELECT … FOR UPDATE`** — защита от гонок между воркерами.
2. Если записи нет или `status != pending` — **выход без изменений** (уже `confirmed` / `failed` / `cancelled`).
3. Повторное уведомление не отправляется.

Так задача переживает повторную доставку из Redis без дублей и без «отката» финального статуса.

### Домен и отмена

- Статусы вынесены в [`app/domain/enums.py`](app/domain/enums.py) — общий тип для API, ORM и воркера.
- `DELETE /bookings/{id}` —  запись остаётся в истории со статусом `cancelled`.

### Миграции

**Alembic** + async-драйвер `asyncpg` для CLI
