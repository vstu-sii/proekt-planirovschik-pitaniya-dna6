# Схема данных

[`erd.puml`](erd.puml) описывает основную схему PostgreSQL. Ей соответствуют:

- SQLAlchemy-модели: `backend/app/db/models.py`;
- начальная Alembic-миграция: `backend/migrations/versions/0001_initial_schema.py`;
- сохранение валидированного API-ответа: `0002_store_plan_results.py`.
- профиль для персонализации: `0003_user_profile.py`.

Миграции применяются сервисом `migrate` перед запуском backend:

```bash
docker compose up --build
```

Проверить текущую ревизию вручную:

```bash
docker compose run --rm migrate alembic current
```
