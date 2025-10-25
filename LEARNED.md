# 🧭 LEARNED.md — Key Lessons Learned

## 💡 Технічні уроки

1. Ідемпотентність через `ON CONFLICT DO NOTHING` — найпростіше рішення для ingestion.
2. Асинхронний SQLAlchemy 2.0 помітно швидший при пакетних вставках.
3. Alembic може створити конфлікти ревізій між контейнерами — варто централізувати генерацію.
4. Помилка `functions in index expression must be marked IMMUTABLE` вирішується спрощенням індексу.
5. Prometheus не дозволяє подвійної реєстрації метрик — створено централізовано в `metrics.py`.
6. JSON-логи через `logging` — легка інтеграція з Grafana/Loki.
7. CLI-імпорт через `docker compose run --rm` — чисто та зручно.

---

## 🧠 Концептуальні уроки

- **Observability early:** логування та `/metrics` потрібно додавати з самого початку.
- **Асинхронність має сенс лише після оптимізації SQL.**
- **MVP simplicity:** PostgreSQL + FastAPI — достатньо для масштабування на початковому етапі.
- **Migration hygiene:** одна зіпсована ревізія Alembic може заблокувати деплой.

---

## 🔭 Ідеї для розвитку

- Інтеграція з Grafana Dashboard.
- Додати Redis cache для `/stats`.
- Валідація CSV через Pydantic v2.
- Новий endpoint `/stats/hourly-active`.
- Автоматичні тести у GitHub Actions.
