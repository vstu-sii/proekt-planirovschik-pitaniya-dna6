# Test Plan — Quality & Safety

## 1. Назначение

План связывает требования Lab 2 с PRD, `success-criteria.md` и `golden-dataset-plan.md`.

LLM используется для смысловых задач, но критические числовые и бизнес-ограничения должны проходить детерминированную проверку.

## 2. Unit tests

Проверяются:
- расчёт стоимости;
- расчёт калорий и БЖУ;
- сравнение с бюджетом;
- ограничения/запрещённые продукты;
- агрегация ингредиентов;
- учёт запасов;
- schema validation structured output;
- перенос блюда и согласованный пересчёт.

## 3. Integration tests

Проверяются цепочки:
1. Mobile → Backend.
2. Backend → DB.
3. Backend → AI endpoint.
4. AI response → schema validator.
5. Validated result → deterministic calculations.
6. Изменение меню → список покупок.
7. Изменение меню → бюджет.
8. Изменение меню → КБЖУ.
9. AI timeout/error → безопасная обработка.
10. Health checks.

## 4. Golden Dataset

Файл: `docs/quality/golden-dataset/v1.jsonl`.

В наборе **35 примеров**. Это соответствует требованию Lab 2: 30–50.

Схема записей соответствует `docs/quality/golden-dataset/golden-dataset-plan.md`:
- `id`;
- `version`;
- `source_type`;
- `source_reference`;
- `input`;
- `reference_answer`;
- `must_contain`;
- `must_not_contain`;
- `constraints`;
- `safety_level`;
- `notes`.

Первые 10 записей сохранены из Lab 1. Они не являются интервью, поскольку в исходных материалах нет стенограмм/ответов респондентов.

## 5. Автоматические eval

Автоматически проверяются, где это поддерживает реализация:
- структура ответа;
- обязательные поля;
- бюджет;
- отклонение КБЖУ;
- запрещённые продукты/аллергены;
- учёт запасов;
- число вариантов быстрой еды;
- время приготовления;
- HTTP/LLM success и latency;
- стоимость запроса при наличии token/cost telemetry.

Нельзя объявлять метрику автоматически измеряемой без источника данных для её расчёта.

## 6. Целевые метрики из Lab 1

| Метрика | Цель |
|---|---:|
| Соблюдение жёстких ограничений | ≥98% |
| Корректность бюджета | ≥95% |
| Попадание в КБЖУ | ≥90% |
| Полнота меню | ≥95% |
| Корректность списка покупок | ≥95% |
| Использование имеющихся продуктов | ≥95% |
| Сценарии «из остатков» | ≥95% |
| Быстрая еда | ≥90% |
| Тон | ≥90% |
| Полезность | ≥90% |
| Критические нарушения | 0% |

Критическим считается нарушение аллергии/запрета, игнорирование критического ограничения, опасный совет или необоснованная медицинская/диетологическая гарантия.

## 7. Safety tests

Минимальный набор:
- direct prompt injection;
- indirect injection в retrieved/введённом тексте;
- system prompt/secret leakage;
- excessive agency;
- обход бюджета;
- обход аллергии/запрета;
- malformed structured output;
- ложная точность КБЖУ;
- oversized input;
- повторные запросы/лимиты.

Критические дефекты добавляются в Golden Dataset как regression cases.

## 8. CI

На Pull Request:
- lint;
- format;
- unit tests;
- typecheck;
- OpenAPI/schema validation;
- JSON/JSONL validation;
- Compose validation;
- secret scanning;
- smoke eval для изменённых/критичных кейсов.

## 9. Nightly / полный прогон

После изменений модели, prompt, RAG, AI API или Use Cases:
- полный Golden Dataset;
- полный safety eval;
- integration tests;
- regression suite;
- performance/SLO checks.

## 10. SLO/SLA

| Сценарий | SLO | SLA |
|---|---:|---:|
| Генерация меню | p95 ≤10 с | ≤15 с для 99% |
| Рецепт из остатков | p95 ≤5 с | ≤8 с для 99% |
| Основной интерфейс/API | ≤200 мс для 99% | доступность ≥99% |

Также контролируется доля неуспешных LLM-запросов ≤5%.

## 11. Владельцы

- Quality & Safety — Golden Dataset, Test Plan, safety/regression criteria.
- AI Engineer — AI/eval execution и исправление AI-дефектов.
- Delivery — CI/integration/infrastructure.
- Product VO — ожидаемое поведение Use Cases и приёмка.

## 12. Release gate

Нельзя считать изменение готовым, если:
- не проходит критическое ограничение;
- structured output не валиден;
- раскрыт секрет;
- выполнено недопустимое действие;
- критическая метрика ниже порога без согласованного исключения.
