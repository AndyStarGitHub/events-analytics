# 🧱 ADR.md — Architectural Decision Record

## 1️⃣ Мета
Створити асинхронний мікросервіс для збору, збереження та аналітики подій користувачів (**events ingestion & analytics**) із можливістю масштабування, тестування та спостереження.

---

## 2️⃣ Основні рішення

### 2.1. Архітектура
- Використано **FastAPI + PostgreSQL (async SQLAlchemy)**.
- Вибрано **Docker Compose** для ізоляції сервісів (API, Postgres, Adminer).
- Логіка поділена на:
  - `api/` — REST endpoints
  - `services/` — бізнес-логіка (обробка подій, статистика)
  - `db/` — ORM-моделі, міграції (Alembic)
  - `cli/` — імпорт подій із CSV
  - `observability/` — логи, метрики Prometheus
  - `tests/` — pytest-тести

> **Причина вибору:** FastAPI дає продуктивний асинхронний стек, SQLAlchemy 2.0 — контроль над транзакціями, а Docker забезпечує відтворюваність середовища.

---

### 2.2. Збереження подій
- Модель `Event`:
  ```python
  id, event_id (UUID, унікальний), user_id, event_type, occurred_at, properties (JSON)
  ```
- Ідемпотентність забезпечена **унікальним індексом по `event_id`**.
- Додано **індекси продуктивності**:
  - `(event_type)`
  - `(user_id)`
  - `(occurred_at)`
- Імпорт реалізовано через `INSERT ... ON CONFLICT DO NOTHING`.

---

### 2.3. Аналітика
- `/stats/dau` — підрахунок унікальних користувачів за датами (`count(distinct user_id)`).
- `/stats/top-events` — агрегація типів подій.
- `/stats/retention` — когорти користувачів за першою подією.

> Використано SQL-агрегації напряму через SQLAlchemy Core для мінімального overhead.

---

### 2.4. CLI та генератор
- `python tools/gen_csv.py` — створює великі CSV із випадковими подіями.
- `python -m app.cli.import_events /data/events.csv` — імпорт у базу з батчами (і dry-run).
- **Причина:** зручно для тестування на великих даних без додаткових API-викликів.

---

### 2.5. Нагляд
- `/metrics` — метрики **Prometheus** (`http_requests_total`, `http_request_duration_seconds`).
- `/healthz` — стан сервісу та БД.
- JSON-логи формату:
  ```json
  {"level":"info","logger":"access","msg":"access method=GET path=/healthz status=200 request_id=..."}
  ```
- **PrometheusMiddleware** обчислює латентність і лічильники.

---

### 2.6. Тестування
- Використано **pytest + pytest-asyncio + HTTPX**.
- Тести перевіряють:
  - ідемпотентність вставки (`POST /events`);
  - аналітику `/stats/dau`;
  - базову коректність retention-розрахунку.
- Всі тести проходять всередині контейнера через:
  ```bash
  docker compose exec -e TESTING=1 app pytest -q
  ```

---

### 2.7. Міграції
- Використано Alembic.
- Міграції зберігаються в `migrations/versions`.
- Вирішено вручну конфлікт із дубльованим `revision` (`db1fd24928c7` → `a198ede84dff`).

---

### 2.8. Рішення, які були відхилені
- ❌ **Pandas** для агрегацій — занадто важкий у продакшн-сценаріях.
- ❌ **ClickHouse** — надлишковий для тестового обсягу даних.
- ❌ **Synchronous SQLAlchemy** — повільно при великих імпортах.

---

## 3️⃣ Висновок
Обрана архітектура дозволяє:
- ефективно обробляти сотні тисяч подій;
- масштабуватись за рахунок асинхронності;
- легко спостерігати та дебажити через `/metrics` і структуровані логи;
- розширювати аналітику новими endpoint’ами.
