# 📊 Events Analytics Service

## 🔍 Огляд
Сервіс для збору та аналітики подій користувачів (event ingestion & analytics).  
Реалізовано на **FastAPI + PostgreSQL + SQLAlchemy (async)**.  
Підтримує: ідемпотентний імпорт подій, щоденну аналітику, retention-когорти, Prometheus метрики.

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

### Ґенерація CSV
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

## 📈 Спостереження
"Вручну" в базу даних було завантажено понад 150000 записів зґенерованих за 
допомогою tool. Також додано 5000 записів, які були надані з технічним заданням.
Відповідні csv файли додано до репозиторію (папка data).

- `/metrics` — метрики Prometheus (latency, http_requests_total)
- `/healthz` — стан сервісу
- JSON-логи у форматі:
  ```json
  {"level":"info","logger":"access","msg":"access method=GET path=/healthz status=200 request_id=..."}
  ```

---

# ⚡ Продуктивність

## Налаштування стенду
- Машина: <Windows 10, CPU Intel(R) Core(TM) i5-7300U CPU @ 2.60GHz, RAM 8ГБ, версію Docker>
- База: PostgreSQL 16 (docker), індекси: `event_id` (unique), `event_type`, `user_id`, `occurred_at`
- Розмір даних: **{156 011}** подій  
  Діапазон: **{2025-08-01} … {2025-10-20}**

## Методика
1. Дані згенеровано `tools/gen_csv.py --rows 100000` і завантажено CLI-скриптом:
   ```bash
   docker compose run --rm app python -m app.cli.import_events /data/events.csv --batch-size 5000
   ```
2. Прогрів 1 запит на кожен сценарій (без виміру).
3. Вимір часу у PowerShell через `Measure-Command`.

## Результати

| Сценарій                  | Параметри              | Час, мс    |
|---------------------------|------------------------|------------|
| DAU за 1 день             | 2025-10-20             | 0.014050 s |
| Імпорт 100k (batch=5000)  | total_accepted=100 000 | 4,325582 s |

> Примітка: значення можуть коливатись залежно від навантаження, кешів ОС/БД, параметрів Docker.

## Вузькі місця та покращення
- **Вузьке місце:** IO/мережа під час імпорту, парсинг JSON у Python, round-trip SQL вставок.  
  **Що зроблено:** batch insert (5000), унікальні індекси, прості агрегації без складних join’ів.
- **Покращення, якби масштабував:**
  1. **Збільшити batch size** (10–20k) — менше round-trip’ів до БД.
  2. **Індекси під аналітику** (вже додані): `occurred_at`, `event_type`, `user_id`.
  3. **Кешування запитів `/stats`** (Redis, TTL 30–60с) під повторювані діапазони.
  4. **Матеріалізовані в'ю** для популярних зрізів (наприклад, щоденний DAU).

---