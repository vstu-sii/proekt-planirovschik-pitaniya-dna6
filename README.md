# Планировщик питания

[![CI](https://github.com/vstu-sii/proekt-planirovschik-pitaniya-dna6/actions/workflows/ci.yml/badge.svg)](https://github.com/vstu-sii/proekt-planirovschik-pitaniya-dna6/actions/workflows/ci.yml)

Учебный проект по дисциплине «Системы искусственного интеллекта». Приложение составляет
персональный план питания с учётом параметров пользователя, бюджета, целевого КБЖУ и
ограничений по продуктам.

Сейчас в репозитории находится каркас системы для лабораторной работы №1: нативный
hello-world клиент, API, PostgreSQL и воспроизводимое серверное dev-окружение.

## Технологии

- React Native, Expo и TypeScript — мобильное приложение;
- Python и FastAPI — HTTP API;
- PostgreSQL — хранение пользователей и планов питания;
- Docker Compose — локальная разработка;
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

В лабораторной работе №1 мобильный клиент представлен каркасом. CI проверяет форматирование, TypeScript и возможность собрать Android bundle. Запуск приложения на эмуляторе для проверки серверного hello-world не требуется.

Локальные проверки мобильного каркаса:

```bash
cd mobile
npm ci
npm run lint
npm run format
npm run typecheck
npm run export:android
```

Полноценный запуск интерфейса на Android-эмуляторе будет использоваться в следующих лабораторных работах.
## Структура репозитория

```text
.
├── .github/
│   ├── workflows/
│   │   └── ci.yml               # CI для Pull Request
│   └── pull_request_template.md # шаблон Pull Request
├── backend/                     # FastAPI и backend-тесты
├── docs/                        # архитектура и ADR следующих лабораторных
├── mobile/                      # React Native/Expo приложение
├── .env.example                # пример переменных окружения
├── .gitignore                  # исключения для Git
├── compose.yaml                # backend и PostgreSQL
├── CONTRIBUTING.md             # правила веток и Pull Request
└── README.md                   # описание проекта и инструкции
```

## Переменные окружения

Локальный `.env` создаётся копированием `.env.example`. Файл `.env` запрещено коммитить.
При добавлении новой переменной необходимо одновременно обновить `.env.example` и этот
раздел README.

`EXPO_PUBLIC_API_URL` задаёт адрес backend, доступный мобильному устройству.
`LLM_API_KEY` оставлен пустым: в лабораторной №1 AI-интеграция является заглушкой.

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
