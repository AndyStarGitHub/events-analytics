# 📊 Events Analytics Service

## 🔍 Огляд
Сервіс для збору та аналітики подій користувачів (event ingestion & analytics).  
Реалізовано на **FastAPI + PostgreSQL + SQLAlchemy (async)**.  
Підтримує: ідемпотентний імпорт подій, щоденну аналітику, retention-кохорти, Prometheus метрики.

---

## ⚙️ Функціональність
- `POST /events` — прийом подій;
- `GET /stats/dau` — щоденна активність користувачів;
- `GET /stats/top-events` — топ подій;
- `GET /stats/retention` — когорти користувачів;
- `/metrics` — метрики Prometheus;
- `/healthz` — перевірка стану сервісу та бази.

---

## 🧰 Запуск проєкту

```bash
docker compose up -d
```

Swagger: http://localhost:8000/docs  
Adminer: http://localhost:8080

---

## 🧮 Імпорт даних

### Генерація CSV
```bash
python tools/gen_csv.py data/events.csv --rows 10000
```

### Імпорт у базу
```bash
docker compose run --rm app python -m app.cli.import_events /data/events.csv --batch-size 5000
```

Для тестового запуску без збереження:
```bash
docker compose run --rm app python -m app.cli.import_events /data/events.csv --dry-run
```

---

## 🧠 Структура
```
app/
 ├── api/              # REST endpoints + middleware
 ├── services/         # бізнес-логіка (аналітика)
 ├── db/               # SQLAlchemy ORM
 ├── cli/              # імпорт подій
 ├── observability/    # логи та метрики Prometheus
 └── tests/            # pytest тести
tools/
 └── gen_csv.py        # генерація тестових CSV
```

---

## 🧰 CLI та tools
Папка `tools/` містить допоміжні утиліти для створення тестових CSV-файлів.  
Після генерації CSV ви можете імпортувати дані у базу через CLI-команду:

```bash
docker compose run --rm app python -m app.cli.import_events /data/events.csv --batch-size 5000
```

CLI підтримує прапорець `--dry-run` для тестування без фактичного запису.

---

## 🐍 Локальний запуск (venv)

```bash
python -m venv .venv
source .venv/bin/activate   # або .\.venv\Scripts\Activate.ps1 у Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.api.main:app --reload --port 8000
```

---

## 🧪 Тести

```bash
docker compose exec -e TESTING=1 app pytest -q
```

---

## 📈 Observability

- `/metrics` — метрики Prometheus (latency, http_requests_total)
- `/healthz` — стан сервісу
- JSON-логи у форматі:
  ```json
  {"level":"info","logger":"access","msg":"access method=GET path=/healthz status=200 request_id=..."}
  ```

---
