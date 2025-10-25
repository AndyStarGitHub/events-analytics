📊 Events Analytics Service

Events Analytics — це мікросервіс на FastAPI + PostgreSQL, який приймає події з інших 
систем, зберігає їх у базі даних і надає аналітичні показники в реальному часі 
(DAU, топ подій, retention). Сервіс створений із фокусом на продуктивність, 
ідемпотентність, тестування та спостережуваність (observability).

🚀 Основні можливості

✅ Ідемпотентний імпорт подій через /events

📈 Аналітика користувачів

```
GET /stats/dau — щоденні активні користувачі (DAU)
GET /stats/top-events — найпопулярніші типи подій
GET /stats/retention — утримання користувачів по днях
```

🧾 CLI-інструмент для масового імпорту CSV

🧠 Тести для перевірки коректності обробки подій

🔍 JSON-логи доступу

📊 Prometheus метрики — /metrics

🩺 Healthcheck — /healthz

🧱 Міграції Alembic + Dockerized PostgreSQL

🧩 Технологічний стек
Компонент	Опис
FastAPI	REST API
SQLAlchemy 2.0 (async)	ORM
Alembic	Міграції бази даних
PostgreSQL 16	Сховище подій
Docker Compose	Контейнеризація
Pytest + HTTPX	Тестування
Prometheus Client	Метрики /metrics
Logging (JSON)	Структуровані логи
Adminer	UI для перевірки бази даних
🧰 Запуск проєкту
1️⃣ Створити .env файл:
```
POSTGRES_USER=events
POSTGRES_PASSWORD=change_me
POSTGRES_DB=events
DATABASE_URL=postgresql+asyncpg://events:change_me@postgres:5432/events
```

2️⃣ Запуск Docker-контейнерів:
```bash
docker compose up -d
```

3️⃣ Ініціалізація міграцій:
```bash
docker compose exec app bash -lc "alembic upgrade head"
```

4️⃣ Перевірка сервісу:
```
Swagger UI: http://localhost:8000/docs
Healthcheck: http://localhost:8000/healthz
Prometheus метрики: http://localhost:8000/metrics
Adminer: http://localhost:8080
```

🛠️ Папка tools/

Каталог tools/ містить допоміжні утиліти для генерації тестових даних і 
перевірки продуктивності сервісу.

📄 tools/gen_csv.py

Це скрипт для створення CSV-файлу з випадковими подіями, який потім можна 
імпортувати в базу через CLI-інструмент.

🔧 Параметри
Параметр	Опис	Приклад
path	шлях до файлу, куди буде записано CSV	data/events.csv
--rows	кількість рядків (подій) для генерації	--rows 50000
▶️ Приклади запуску

Згенерувати 5 рядків для швидкої перевірки:
```bash
python tools/gen_csv.py data/events.csv --rows 5
```

Згенерувати 50 000 рядків для масового тесту:
```bash
python tools/gen_csv.py data/events.csv --rows 50000
```

Результат:
```
Wrote 50000 rows to data/events.csv
```

🧩 Формат згенерованих подій
```
event_id,occurred_at,user_id,event_type,properties_json
6d1d4fae-7dec-11d0-a765-00a0c91e6bf6,2025-10-19T10:00:00Z,u1,login,{"device":"mobile"}
d81d4fae-7dec-11d0-a765-00a0c91e6bf6,2025-10-20T12:30:00Z,u2,view,{"page":"home"}
```

💡 Для чого потрібен цей скрипт

- Перевірити швидкість імпорту (app.cli.import_events) при різному обсязі даних.
- Реалістично наповнити базу подіями для тестування аналітики (/stats/*).
- Провести локальні бенчмарки перед розгортанням.

🧾 Імпорт CSV через CLI

Сервіс має зручний CLI-модуль для імпорту подій у базу — app.cli.import_events.

🧩 Формат виклику
```bash
docker compose run --rm app python -m app.cli.import_events /data/events.csv [--batch-size 5000] [--dry-run]
```

📍 Параметри
Параметр	Опис
--batch-size	Розмір партії вставки в базу (за замовчуванням 1000)
--dry-run	Якщо вказано — тільки перевірка CSV без запису в базу
▶️ Приклади

✅ Сухий прогін (без запису в базу):
```bash
docker compose run --rm app python -m app.cli.import_events /data/events.csv --dry-run
```

✅ Повний імпорт із великим файлом:
```bash
docker compose run --rm app python -m app.cli.import_events /data/events.csv --batch-size 5000
```

🧾 Приклад логу імпорту:
2025-10-24 16:30:34 [info] import_start batch_size=5000 path=/data/events.csv
2025-10-24 16:30:35 [info] import_batch_done accepted=5000 read=5000 skipped=0 total_accepted=5000 total_read=5000 total_skipped=0
2025-10-24 16:30:47 [info] import_complete total_accepted=50000 total_read=50000 total_skipped=0


📊 після завершення можна перевірити в Adminer або через SQL:

SELECT COUNT(*) FROM events;
SELECT MIN(occurred_at), MAX(occurred_at) FROM events;

📊 Приклади результатів аналітики
🔹 Щоденні активні користувачі (DAU)
GET /stats/dau?from=2025-10-19&to=2025-10-25

[
  {"date": "2025-10-19", "unique_users": 3},
  {"date": "2025-10-20", "unique_users": 5}
]

🔹 Топ подій
GET /stats/top-events?from=2025-10-19&to=2025-10-25

[
  {"event_type": "purchase", "count": 376},
  {"event_type": "login", "count": 376}
]

🔹 Retention-аналітика
GET /stats/retention?start_date=2025-10-19&windows=7

{
  "cohort_size": 3,
  "windows": [
    {"day": 0, "count": 3, "rate": 1},
    {"day": 1, "count": 3, "rate": 1}
  ]
}

🧪 Тести
```bash
docker compose exec -e TESTING=1 app pytest -q
```

✅ Очікувано (приклад):

3 passed, 1 warning in 1.53s

🔍 Логування

Сервіс використовує структуровані JSON-логи з автоматичним request_id:
```
{"level":"info","logger":"access","msg":"access method=GET path=/healthz status=200 request_id=3de6d467-1d2b-49fd-b276-dacd3e41b33d"}
```

Перегляд логів:

docker compose logs -f --tail=100 app | findstr /i access

📈 Метрики Prometheus

Всі технічні метрики доступні за /metrics:
```
http_requests_total{method="GET",path="/healthz",status="200"} 5
http_request_duration_seconds_bucket{le="0.1"} 15
events_ingest_accepted_total 50000
```

⚙️ Оптимізація та індекси
CREATE INDEX IF NOT EXISTS ix_events_event_type   ON events (event_type);
CREATE INDEX IF NOT EXISTS ix_events_user_id      ON events (user_id);
CREATE INDEX IF NOT EXISTS ix_events_occurred_at  ON events (occurred_at);

🧩 Архітектура
FastAPI ──► SQLAlchemy (async)
    │
    ├── /events          → ідемпотентне приймання подій
    ├── /stats/dau       → щоденні користувачі
    ├── /stats/top-events→ топ подій
    ├── /stats/retention → утримання
    ├── /metrics         → метрики Prometheus
    └── /healthz         → стан сервісу
