# Планировщик питания

[![CI](https://github.com/vstu-sii/proekt-planirovschik-pitaniya-dna6/actions/workflows/ci.yml/badge.svg)](https://github.com/vstu-sii/proekt-planirovschik-pitaniya-dna6/actions/workflows/ci.yml)

Учебный проект по дисциплине «Системы искусственного интеллекта». Приложение составляет
персональный план питания с учётом параметров пользователя, бюджета, целевого КБЖУ и
ограничений по продуктам.

В лабораторной работе №2 добавлены C4-диаграммы и архитектурная проверка, интерактивный
UI-прототип, OpenAPI-контракт AI-эндпоинта, ERD, модели и начальная миграция базы данных,
а также Compose-скелет будущей системы.

## Технологии

- React Native, Expo и TypeScript — мобильное приложение;
- Python и FastAPI — HTTP API;
- PostgreSQL — хранение пользователей и планов питания;
- Docker Compose — локальная разработка;
- PlantUML и C4-PlantUML — архитектура и ERD как код;
- aact — автоматическая проверка архитектурных правил;
- Alembic и SQLAlchemy — схема данных и миграции;
- GitHub Actions — lint, format, тесты и сборка.

## Быстрый запуск

Для запуска нужны Git, Docker Desktop и Docker Compose. На Windows рекомендуется использовать Docker Desktop с WSL2.

Клонируйте репозиторий:

```bash
git clone https://github.com/vstu-sii/proekt-planirovschik-pitaniya-dna6.git
cd proekt-planirovschik-pitaniya-dna6
```

Создайте локальный файл переменных окружения и поднимите dev-среду:

```bash
cp .env.example .env
docker compose up --build
```

Compose одной командой запускает:

- FastAPI backend;
- PostgreSQL;
- применение миграций Alembic;
- локальную заглушку AI-провайдера `llm-mock`;
- health checks сервисов.

После запуска доступны:

| Компонент | URL |
|---|---|
| Hello-world API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

Ожидаемый ответ hello-world:

```json
{
  "message": "Meal Planner API is running"
}
```

Остановка окружения:

```bash
docker compose down
```

Удаление локального тома базы данных:

```bash
docker compose down --volumes
```

## Мобильный клиент

Пользовательский клиент проекта разрабатывается как нативное мобильное приложение на React Native и Expo.

В лабораторной работе №2 мобильный клиент содержит интерактивный прототип трёх ключевых
экранов. CI проверяет форматирование, TypeScript, Android bundle и web-export. Скриншоты
хранятся рядом с описанием в [`mobile/docs`](mobile/docs/README.md).

Локальные проверки мобильного каркаса:

```bash
cd mobile
npm ci
npm run lint
npm run format
npm run typecheck
npm run export:android
npm run export:web
```

Для просмотра прототипа в браузере выполните `npm run web`.

## Архитектура

Система спроектирована как модульный монолит: мобильное приложение обращается к FastAPI,
backend владеет PostgreSQL и вызывает внешний GigaChat API. Обоснование решения записано в
[`ADR-004`](docs/adr/adr-04-modular-monolith.md).

- [C4 Context](docs/architecture/context.puml);
- [C4 Container](docs/architecture/container.puml);
- [описание архитектуры и границ](docs/architecture/README.md);
- [OpenAPI-контракт AI-эндпоинта](api/openapi.yaml).

Машинная проверка архитектуры:

```bash
npm ci
npm run architecture:check
```

Ожидаемый результат: `No violations found`.

## Схема данных

ERD находится в [`docs/data/erd.puml`](docs/data/erd.puml). Ей соответствуют SQLAlchemy-модели
в `backend/app/db/models.py` и миграция `backend/migrations/versions/0001_initial_schema.py`.
При запуске Compose миграции применяются автоматически до старта API.

## Структура репозитория

```text
.
├── .github/
│   ├── workflows/
│   │   └── ci.yml               # CI для Pull Request
│   └── pull_request_template.md # шаблон Pull Request
├── api/
│   └── openapi.yaml             # контракт AI-эндпоинта
├── backend/
│   ├── app/db/                  # SQLAlchemy-модели
│   ├── migrations/              # миграции Alembic
│   └── tests/                   # backend-тесты
├── docs/
│   ├── adr/                     # архитектурные решения
│   ├── architecture/            # C4 Context и Container
│   └── data/                    # ERD и описание схемы
├── mobile/
│   ├── docs/screenshots/        # скриншоты UI-прототипа
│   └── App.tsx                  # код ключевых экранов
├── stubs/llm/                   # локальная заглушка AI-провайдера
├── .env.example                # пример переменных окружения
├── .gitignore                  # исключения для Git
├── aact.config.ts              # правила проверки архитектуры
├── compose.yaml                # полный dev-контур и health checks
├── CONTRIBUTING.md             # правила веток и Pull Request
├── package.json                # команды архитектурной проверки
└── README.md                   # описание проекта и инструкции
```

## Переменные окружения

Локальный `.env` создаётся копированием `.env.example`. Файл `.env` запрещено коммитить.
При добавлении новой переменной необходимо одновременно обновить `.env.example` и этот
раздел README.

`EXPO_PUBLIC_API_URL` задаёт адрес backend, доступный мобильному устройству.
`LLM_BASE_URL` в dev-окружении указывает на `llm-mock`. `LLM_API_KEY` оставлен пустым и
потребуется только при подключении реального провайдера. Секреты нельзя коммитить.

## Команда

| Роль | Зона ответственности | Участник |
|---|---|---|
| Product | требования и пользовательские сценарии | Медведева Софья |
| AI Engineer | LLM и генерация плана питания | Черепова Анастасия |
| Delivery Engineer | архитектура, каркас, CI/CD и окружение | Карпов Роман |
| QUALITY & SAFETY | Метрики качества, evals, тестовый датасет и безопасность результатов | Карпова Мария |

## Правила разработки

Работа ведётся в отдельных ветках и попадает в `main` только через Pull Request после
успешного CI. Соглашение об именах веток и полный порядок merge описаны в
[`CONTRIBUTING.md`](CONTRIBUTING.md).

## Деплой

Hello-world backend развёрнут на Render.

| Компонент | Публичный URL |
|---|---|
| API | https://meal-planner-dna6-api.onrender.com |
| Swagger UI | https://meal-planner-dna6-api.onrender.com/docs |
| Health check | https://meal-planner-dna6-api.onrender.com/health |

### Как выполнить деплой

1. Создать на Render новый `Web Service`.
2. Указать публичный GitHub-репозиторий проекта.
3. Использовать следующие настройки:

| Настройка | Значение |
|---|---|
| Branch | `lab1-delivery-initiation` |
| Runtime | `Python 3` |
| Root Directory | `backend` |
| Build Command | `pip install .` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health Check Path | `/health` |

4. Добавить переменную окружения:

```env
APP_ENV=production
```

5. Запустить создание Web Service и дождаться статуса `Live`.

Бесплатный экземпляр Render может переходить в спящий режим при отсутствии запросов, поэтому первое открытие после простоя иногда занимает некоторое время.
