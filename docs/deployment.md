# Деплой прототипа

Публичный прототип состоит из backend, PostgreSQL и web-export Expo. В production локальные
заглушки Compose не публикуются.

## Backend на Render

- Root Directory: `backend`
- Build Command: `pip install .`
- Start Command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health Check Path: `/health`

Обязательные env:

```env
APP_ENV=production
DATABASE_URL=<Render PostgreSQL external/internal URL>
AI_PROVIDER=demo
CORS_ORIGINS=<URL web-клиента>
TRACE_COLLECTOR_URL=
```

Для реального GigaChat вместо demo:

```env
AI_PROVIDER=gigachat
GIGACHAT_CREDENTIALS=<secret>
GIGACHAT_MODEL=GigaChat-2
```

Секрет добавляется только в настройках Render и не коммитится.

## Web-клиент на Render Static Site

- Root Directory: `mobile`
- Build Command: `npm ci && npm run export:web`
- Publish Directory: `dist-web`
- env `EXPO_PUBLIC_API_URL`: публичный URL backend без завершающего `/`.

После создания Static Site его URL добавляется в `CORS_ORIGINS` backend, затем оба сервиса
перезапускаются. Финальные URL фиксируются в корневом README перед сдачей.
