# Отчёт агентной разработки — лабораторная работа №3

## Что было сгенерировано агентом

- FastAPI-схемы и маршруты генерации/чтения плана;
- сервис детерминированного расчёта стоимости и КБЖУ;
- сохранение пользователей, планов, дней, блюд, ингредиентов и готового ответа;
- миграции `0002_store_plan_results` и `0003_user_profile`;
- подключение Expo UI к API;
- loading, error и retry состояния;
- Dockerfile web-клиента и общий Compose-контур;
- локальные сервисы LLM и трассировки;
- unit/integration тесты и CI smoke test.

## Использованные командные артефакты

- контракт `api/openapi.yaml` из Lab 2;
- AI-прототип из ветки `lab3-ai_engineer-prototype`;
- Test Plan и Threat Model из ветки `lab2-quality_safety-design`.

Чужие ветки не сливались целиком. AI baseline был отревьюен и адаптирован к существующей
архитектуре Delivery.

## Что исправлено при ревью

1. Поля AI-router приведены к OpenAPI: `days`, `max_cook_time_min`, структурированный pantry.
2. Обязательные поля больше не являются опциональными, неизвестные поля запрещены.
3. AI output не считается готовым результатом без server-side validation.
4. Стоимость и КБЖУ рассчитываются по серверному каталогу, а не берутся из LLM.
5. Запрещённые продукты, бюджет и время готовки проверяются до сохранения.
6. Результат сохраняется в PostgreSQL и доступен повторно по UUID.
7. Секрет GigaChat читается только из env; локальный запуск не требует секрета.
8. Ошибка трассировки не ломает пользовательский запрос.
9. UI больше не показывает статический слайд: он вызывает API и обрабатывает состояния.
10. `ml/` не оставлен вне Docker build context: provider интегрирован в пакет backend.
11. Статические поля прототипа заменены рабочей формой: профиль, бюджет, цель, время,
    запасы и исключения валидируются и передаются в API.

## Режимы AI

- `AI_PROVIDER=http` — локальный Compose использует `llm-mock`;
- `AI_PROVIDER=demo` — автономная публичная демонстрация без секрета;
- `AI_PROVIDER=gigachat` — реальный GigaChat при наличии `GIGACHAT_CREDENTIALS`.

LLM отвечает только за смысловой черновик. Backend остаётся источником истины для чисел,
ограничений и сохранения данных.

## Проверки

```bash
cd backend
pip install ".[dev]"
ruff check .
ruff format --check .
pytest

cd ../mobile
npm ci
npm run lint
npm run format
npm run typecheck
npm run export:android
npm run export:web

cd ..
docker compose -f compose.dev.yml up -d --build --wait
```
