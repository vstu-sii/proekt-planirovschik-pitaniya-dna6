# Планировщик питания

[![CI](https://github.com/vstu-sii/proekt-planirovschik-pitaniya-dna6/actions/workflows/ci.yml/badge.svg)](https://github.com/vstu-sii/proekt-planirovschik-pitaniya-dna6/actions/workflows/ci.yml)

Учебный проект по дисциплине «Системы искусственного интеллекта». Приложение составляет
персональный план питания с учётом параметров пользователя, бюджета, целевого КБЖУ и
ограничений по продуктам.

В лабораторной работе №3 прототип стал системой: UI вызывает API, AI-провайдер формирует
черновик меню, backend проверяет ограничения и рассчитывает показатели, а результат
сохраняется в PostgreSQL. Весь контур вместе с трассировкой запускается одной командой.

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
docker compose -f compose.dev.yml up -d --build --wait
```

Compose одной командой запускает:

- FastAPI backend;
- PostgreSQL;
- применение миграций Alembic;
- локальную заглушку AI-провайдера `llm-mock`;
- web-клиент `frontend`;
- сервис сбора трасс `tracing`;
- health checks сервисов.

После запуска доступны:

| Компонент | URL |
|---|---|
| Web-прототип | http://localhost:8080 |
| API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |
| Трассы запросов | http://localhost:9411/traces |

Ожидаемый ответ hello-world:

```json
{
  "message": "Meal Planner API is running"
}
```

Остановка окружения:

```bash
docker compose -f compose.dev.yml down
```

Удаление локального тома базы данных:

```bash
docker compose -f compose.dev.yml down --volumes
```

## Мобильный клиент

Пользовательский клиент проекта разрабатывается как нативное мобильное приложение на React Native и Expo.

Клиент отправляет параметры в FastAPI и отображает сохранённый результат. Во время запроса
показывается loading state, при сетевой или серверной ошибке — понятное сообщение и кнопка
повтора. CI проверяет TypeScript, Android bundle и web-export.

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

Для отдельного запуска клиента выполните `npm run web`. Для интеграционной проверки
используйте Compose и адрес `http://localhost:8080`.

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
в `backend/app/db/models.py` и миграции `backend/migrations/versions/`. Миграция `0002`
добавляет сохранение готового валидированного ответа. Compose применяет миграции до старта API.

## Агентная разработка

Что было сгенерировано, какие командные материалы использованы и что исправлено при ревью,
описано в [`docs/agent-development-report.md`](docs/agent-development-report.md).

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
│   ├── app/services/            # AI provider, расчёты и сохранение
│   ├── migrations/              # миграции Alembic
│   └── tests/                   # backend-тесты
├── docs/
│   ├── adr/                     # архитектурные решения
│   ├── architecture/            # C4 Context и Container
│   ├── data/                    # ERD и описание схемы
│   ├── agent-development-report.md
│   └── deployment.md
├── mobile/
│   ├── docs/screenshots/        # скриншоты UI-прототипа
│   ├── Dockerfile               # web-export для общего контура
│   └── App.tsx                  # API, loading, error и result states
├── stubs/llm/                   # локальная заглушка AI-провайдера
├── stubs/tracing/               # локальный сборщик трасс
├── .env.example                # пример переменных окружения
├── .gitignore                  # исключения для Git
├── aact.config.ts              # правила проверки архитектуры
├── compose.yaml                # полный dev-контур и health checks
├── compose.dev.yml             # явный compose-файл для автопроверки
├── CONTRIBUTING.md             # правила веток и Pull Request
├── package.json                # команды архитектурной проверки
└── README.md                   # описание проекта и инструкции
```

## Переменные окружения

Локальный `.env` создаётся копированием `.env.example`. Файл `.env` запрещено коммитить.
При добавлении новой переменной необходимо одновременно обновить `.env.example` и этот
раздел README.

`EXPO_PUBLIC_API_URL` задаёт адрес backend для Android, `WEB_API_URL` — для web-сборки.
`AI_PROVIDER=http` использует `llm-mock`, `demo` работает автономно, `gigachat` требует
секрет `GIGACHAT_CREDENTIALS`. `TRACE_COLLECTOR_URL` указывает на сервис трассировки.
Секреты нельзя коммитить.

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

Backend первой версии уже развёрнут на Render. После деплоя Lab 3 этот же адрес должен
обслуживать настоящий API, а URL web-клиента будет добавлен в таблицу.

| Компонент | Публичный URL |
|---|---|
| API | https://meal-planner-dna6-api.onrender.com |
| Swagger UI | https://meal-planner-dna6-api.onrender.com/docs |
| Health check | https://meal-planner-dna6-api.onrender.com/health |
| Web-прототип | будет добавлен после создания Render Static Site |

Полная инструкция для backend, PostgreSQL и Static Site находится в
[`docs/deployment.md`](docs/deployment.md).

Бесплатный экземпляр Render может переходить в спящий режим при отсутствии запросов, поэтому первое открытие после простоя иногда занимает некоторое время.
