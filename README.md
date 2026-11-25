# Планировщик питания

Проект курса «Системы искусственного интеллекта». AI-ассистент для персонального планирования питания: меню под бюджет, КБЖУ, аллергены и продукты, которые уже есть дома.

> **Актуальный этап:** Sprint 4 / Lab 4 — Production-ready инфраструктура.
>
> **Ветка:** `lab4-product-infrastructure`
>
> **Формат сдачи:** PR от каждой роли, заголовок `Lab4: [Role] — Infrastructure Deliverables` (`docs/tasks/lab4.md`).

## Что важно знать о проекте

- **Проблема:** молодые люди, живущие отдельно, конфликтуют между бюджетом, временем и здоровьем; ручной подсчёт КБЖУ и планирование меню требуют слишком много ресурса (`docs/prd.md`).
- **ЦА:** молодые люди в съёмной квартире/общежитии с ограниченным бюджетом на питание; в нарративе — Кирилл, 24 года, Волгоград, панкреатит (`docs/brief.md`).
- **North Star:** к декабрю ≥40% активных пользователей завершают 4 недельных цикла планирования подряд (`docs/prd.md`).
- **SLO/SLA:** генерация меню — 95% успешных запросов <10 с, SLA 99% <15 с (`docs/prd.md`).
- **Архитектура:** Direct Prompt + Structured JSON + Python tools; LLM формирует черновик, Python считает стоимость/КБЖУ и проверяет ограничения (`docs/adr/adr-01-ai-pipeline-architecture.md`).
- **Модель:** GigaChat 2 Lite как основной адаптер; один retry при transient error; отказ — `503 Service Unavailable + request_id`, без mock-ответа `200` (`docs/adr/adr-02-model-selection.md`).
- **Безопасность:** zero trust к свободному тексту LLM; детерминированная серверная валидация, allowlist инструментов, минимальные права (`docs/adr/adr-03-security-boundaries.md`).
- **Источник истины для чисел:** backend-каталог и детерминированные инструменты, а не модель (`docs/sprint-4/mvp-scope.md`, `docs/adr/adr-01-ai-pipeline-architecture.md`).

## Sprint 4: текущее состояние

- **Период:** 23.11–11.12, 15 рабочих дней = 3 календарные недели.
- **Гейты:** G1 23.11–27.11, G2 30.11–04.12, G3 07.12–11.12.
- **Единица оценки:** SP, 1 SP = 2 ч.
- **Базовый план:** 70 SP; план-линия `70 → 53 → 31 → 0 SP`.
- **Факт G1 на 24.11:** 67 SP; принят DOC-01 (3 SP), 6 P0-задач на 14 SP остаются в бэклоге до 27.11.
- **IN:** UC-1 авторизация/профиль, UC-2 локальная БД «Мои продукты», UC-3 персонализированное меню.
- **CONDITIONAL:** RES-01 мобильная верстка, RES-02 ручной ввод КБЖУ, RES-03 P1 UC-1, RES-04 P1 UC-2.
- **CUT:** UC-4 замена блюда, UC-5 перенос меню, UC-6 рецепт из остатков, UC-7 быстрый ужин, UC-8 КБЖУ по фото, UC-9 «Коллекции».

Ключевые файлы спринта:

| Тема | Документ |
| --- | --- |
| Зафиксированный скоуп | [docs/sprint-4/mvp-scope.md](docs/sprint-4/mvp-scope.md) |
| Сводка burndown | [docs/sprint-4/burndown.md](docs/sprint-4/burndown.md) |
| План burndown | [docs/sprint-4/burndown-plan.md](docs/sprint-4/burndown-plan.md) |
| Факт burndown | [docs/sprint-4/burndown-fact.md](docs/sprint-4/burndown-fact.md) |
| Приёмка по DoD | [docs/sprint-4/acceptance.md](docs/sprint-4/acceptance.md) |
| Итоги прототипа и план | [docs/sprint-4/iteration-notes.md](docs/sprint-4/iteration-notes.md) |

Burndown разделён: `burndown.md` содержит примечание о сжатых сроках, §2 «План и факт» и §3 «Анализ отклонений от плана»; `burndown-plan.md` хранит план на 70 SP; `burndown-fact.md` — факт G1–G3 (§1–3). Приёмка связана с фактом через §1–3 в `docs/sprint-4/acceptance.md`.

## Качество и известные ограничения

Baseline Quality (`docs/quality/lab3-eval-report.md`, `docs/quality/summary-full-v1.json`):

- 44 кейса Golden Dataset v1; получено 13/44 ответов, ошибок 31/44.
- Структурно валидны 13/13 полученных ответов, но общий порог 95% не достигнут.
- Safety-critical: 16 кейсов; ответ получен только в 2, ошибка в 14.
- Средняя задержка 3,2641 с, p95 15,2794 с — только по 13 полученным ответам.
- `budget_accuracy`, `nutrition_accuracy`, `allergen_compliance`, `critical_violations_verified` не подтверждены; `null` означает «не проверено», а не «нарушений нет».
- Показатель 43/44 из отчёта AI Engineer относится к другому прогону и не заменяет 13/44 (`docs/use-cases/validation-report/ai-engineer-answers.md`).

Главный реестр находок прототипа — `docs/use-cases/validation-report/bug-list.md`: 50 находок, из них 17 P0, 22 P1, 11 P2. Валидация 9 UC: полностью не работает ни один, 3 частично, 6 не реализованы (`docs/use-cases/validation-report/01-summary.md`).

## Карта документации

### Продукт и требования

| Файл | Назначение |
| --- | --- |
| [docs/brief.md](docs/brief.md) | Бриф «итоговая картинка», нарратив North Star |
| [docs/brief.pptx](docs/brief.pptx) | Презентация-бриф |
| [docs/prd.md](docs/prd.md) | PRD v2: сегмент, боли, North Star, SLI/SLO/SLA, out of scope |
| [docs/hypotheses.md](docs/hypotheses.md) | 5 фальсифицируемых гипотез и пороги опровержения |
| [docs/insights.md](docs/insights.md) | Вопросы интервью и инсайты по пищевому поведению |
| [docs/business-rules.md](docs/business-rules.md) | FACT / CONSTRAINT / ACTION / INFERENCE / COMPUTATION правила |
| [docs/glossary.md](docs/glossary.md) | Глоссарий терминов проекта |
| [docs/roadmap.md](docs/roadmap.md) | Вехи, MVP / Release 2.0, out of scope |
| [docs/sprint-4/iteration-notes.md](docs/sprint-4/iteration-notes.md) | Итоги Sprint 3, техдолг, вопросы Q-01–Q-09, план Sprint 4 |
| [docs/sprint-4/mvp-scope.md](docs/sprint-4/mvp-scope.md) | IN / CONDITIONAL / CUT Sprint 4 |
| [docs/sprint-4/burndown.md](docs/sprint-4/burndown.md) | Сводка: План и факт, анализ отклонений |
| [docs/sprint-4/burndown-plan.md](docs/sprint-4/burndown-plan.md) | План сгорания: 25 задач, 70 SP |
| [docs/sprint-4/burndown-fact.md](docs/sprint-4/burndown-fact.md) | Факт сгорания по G1–G3 |
| [docs/sprint-4/acceptance.md](docs/sprint-4/acceptance.md) | Приёмка инкрементов по гейтам и DoD |

### Use cases и диаграммы

| Файл | Назначение |
| --- | --- |
| [docs/use-cases/description/in-scope/use-cases-list.md](docs/use-cases/description/in-scope/use-cases-list.md) | Сводный список UC v2 |
| [docs/use-cases/description/in-scope/use-case-1.md](docs/use-cases/description/in-scope/use-case-1.md) | UC-1. Настроить профиль |
| [docs/use-cases/description/in-scope/use-case-2.md](docs/use-cases/description/in-scope/use-case-2.md) | UC-2. Пополнить локальную БД «Мои продукты» |
| [docs/use-cases/description/in-scope/use-case-3.md](docs/use-cases/description/in-scope/use-case-3.md) | UC-3. Сгенерировать персонализированное меню |
| [docs/use-cases/description/in-scope/use-case-4.md](docs/use-cases/description/in-scope/use-case-4.md) | UC-4. Заменить блюдо — в CUT Sprint 4 |
| [docs/use-cases/description/in-scope/use-case-5.md](docs/use-cases/description/in-scope/use-case-5.md) | UC-5. Перенести меню — в CUT Sprint 4 |
| [docs/use-cases/description/in-scope/use-case-6.md](docs/use-cases/description/in-scope/use-case-6.md) | UC-6. Рецепт из остатков — в CUT Sprint 4 |
| [docs/use-cases/description/in-scope/use-case-7.md](docs/use-cases/description/in-scope/use-case-7.md) | UC-7. Быстрый ужин — в CUT Sprint 4 |
| [docs/use-cases/description/out-of-scope/use-case-8.md](docs/use-cases/description/out-of-scope/use-case-8.md) | UC-8. КБЖУ по фото, вне MVP |
| [docs/use-cases/description/out-of-scope/use-case-9.md](docs/use-cases/description/out-of-scope/use-case-9.md) | UC-9. «Коллекции», вне MVP |
| [docs/use-cases/diagrams/plantuml-full-v2.md](docs/use-cases/diagrams/plantuml-full-v2.md) | PlantUML-диаграмма UC1–UC7 |

### validation report

| Файл | Назначение |
| --- | --- |
| [docs/use-cases/validation-report/README.md](docs/use-cases/validation-report/README.md) | Навигация; `bug-list.md` — главный источник истины |
| [docs/use-cases/validation-report/01-summary.md](docs/use-cases/validation-report/01-summary.md) | Сводка валидации 9 UC |
| [docs/use-cases/validation-report/02-breaks.md](docs/use-cases/validation-report/02-breaks.md) | Разрывы по UC с ID и владельцами |
| [docs/use-cases/validation-report/03-surprises.md](docs/use-cases/validation-report/03-surprises.md) | S-01–S-11: неожиданные находки |
| [docs/use-cases/validation-report/04-not-tested.md](docs/use-cases/validation-report/04-not-tested.md) | NT-01–NT-19: непроверенное и нереализованное |
| [docs/use-cases/validation-report/05-changes.md](docs/use-cases/validation-report/05-changes.md) | CH-01–CH-46: правки требований v2 |
| [docs/use-cases/validation-report/06-e2e.md](docs/use-cases/validation-report/06-e2e.md) | E2E-прогон и критические блокеры |
| [docs/use-cases/validation-report/bug-list.md](docs/use-cases/validation-report/bug-list.md) | Реестр 50 находок, приоритеты и владельцы |
| [docs/use-cases/validation-report/quality-sync-report.md](docs/use-cases/validation-report/quality-sync-report.md) | Синхронизация Quality / AI Engineer / UI |
| [docs/use-cases/validation-report/ai-engineer-answers.md](docs/use-cases/validation-report/ai-engineer-answers.md) | Ответы AI Engineer, прогон 43/44 |
| [docs/use-cases/validation-report/quality-safety-answers.md](docs/use-cases/validation-report/quality-safety-answers.md) | Ответы Q-01–Q-09 по качеству и безопасности |
| [docs/use-cases/validation-report/delivery-answers.md](docs/use-cases/validation-report/delivery-answers.md) | Ответы Delivery: CI, провайдеры, сохранение данных, контракты, безопасность |

### ADR и качество

| Файл | Назначение |
| --- | --- |
| [docs/adr/adr-01-ai-pipeline-architecture.md](docs/adr/adr-01-ai-pipeline-architecture.md) | Решение об AI-пайплайне |
| [docs/adr/adr-02-model-selection.md](docs/adr/adr-02-model-selection.md) | Выбор и интеграция GigaChat 2 Lite |
| [docs/adr/adr-03-security-boundaries.md](docs/adr/adr-03-security-boundaries.md) | Границы безопасности AI-компонента |
| [docs/adr/adr-template.md](docs/adr/adr-template.md) | Шаблон ADR |
| [docs/quality/eval-report-1.md](docs/quality/eval-report-1.md) | Отчёт «где врём»: 44 кейса, 13/44 ответов |
| [docs/quality/lab3-eval-report.md](docs/quality/lab3-eval-report.md) | Технический baseline Quality и приоритетные действия |
| [docs/quality/summary-full-v1.json](docs/quality/summary-full-v1.json) | Машиночитаемые метрики baseline |
| [docs/quality/baseline-full-v1.jsonl](docs/quality/baseline-full-v1.jsonl) | Сырые 44 кейса прогона от 05.11 |

### Задания лабораторных

| Файл | Спринт | Тема |
| --- | --- | --- |
| [docs/tasks/lab1.md](docs/tasks/lab1.md) | Sprint 1 | Инициация: PRD, гипотезы, интервью, глоссарий, бриф |
| [docs/tasks/lab2.md](docs/tasks/lab2.md) | Sprint 2 | Дизайн: UC, roadmap, ADR, C4, API, golden dataset, threat model |
| [docs/tasks/lab3.md](docs/tasks/lab3.md) | Sprint 3 | Прототип: валидация UC, baseline, evals, iteration notes |
| [docs/tasks/lab4.md](docs/tasks/lab4.md) | Sprint 4 | Инфраструктура: burndown, scope, acceptance, CI/CD, staging, observability |
| [docs/tasks/lab5.md](docs/tasks/lab5.md) | Sprint 5 | Тестирование: North Star, финальные evals, ablation, нагрузка |
| [docs/tasks/lab6.md](docs/tasks/lab6.md) | Sprint 6 | Демо: презентация, репетиции, видео, trust block |
| [docs/tasks/lab7.md](docs/tasks/lab7.md) | Sprint 7 | Ревью: deploy-check, независимые evals, red team, ретро |

## Структура репозитория

- `docs/` — вся продуктовая и техническая документация перечислена выше.
- `backend/` — каталог зарезервирован под код сервиса; в текущей ветке он пуст.
- `README.md` — этот файл.
- `.env` — локальные переменные окружения; значения не публикуются.

Целевые артефакты инфраструктуры из `docs/tasks/lab4.md` — `.github/workflows/deploy.yml`, `.github/workflows/quality-gates.yml`, `compose.staging.yml`, `monitoring/`, `tests/`, `backend/limits/`, `backend/guards/` — в этой ветке ещё не созданы и описаны только в задании.

## Как читать документацию

1. Начать с [docs/brief.md](docs/brief.md) и [docs/prd.md](docs/prd.md) — зачем нужен продукт.
2. Затем [docs/use-cases/description/in-scope/use-cases-list.md](docs/use-cases/description/in-scope/use-cases-list.md) — что должен делать продукт.
3. Дать [docs/use-cases/validation-report/README.md](docs/use-cases/validation-report/README.md) и [docs/use-cases/validation-report/bug-list.md](docs/use-cases/validation-report/bug-list.md) — что сломалось после прототипа.
4. Перейти к [docs/sprint-4/iteration-notes.md](docs/sprint-4/iteration-notes.md), [docs/sprint-4/mvp-scope.md](docs/sprint-4/mvp-scope.md), [docs/sprint-4/burndown.md](docs/sprint-4/burndown.md), [docs/sprint-4/burndown-plan.md](docs/sprint-4/burndown-plan.md), [docs/sprint-4/burndown-fact.md](docs/sprint-4/burndown-fact.md), [docs/sprint-4/acceptance.md](docs/sprint-4/acceptance.md) — как реагируем на это в Sprint 4.
5. Для технических решений читать [docs/adr/](docs/adr/) и [docs/quality/](docs/quality/).

## Команда

| Роль | Имя | Ответственность в Sprint 4 |
| --- | --- | --- |
| PRODUCT / VO | Медведева С. | Скоуп, burndown, приёмка, требования |
| AI ENGINEER | Черепова А. | Промпты v2, evals, стоимость, инструменты |
| DELIVERY | Карпов Р. | CI/CD, staging, observability, лимиты |
| QUALITY & SAFETY | Карпова М. | Quality-gates, атаки, тесты критических путей |

## Известные расхождения в документации

- `docs/tasks/lab4.md` описывает 28 дней / недели 7–10, а продуктовые файлы Sprint 4 используют сжатый период 23.11–11.12 и 3 гейта.
- `docs/roadmap.md` всё ещё включает UC-4–UC-5 в MVP; актуальный скоуп — `docs/sprint-4/mvp-scope.md` (UC-1–UC-3).
- В старых разделах глоссария и UC встречается RAG; PRD v2 и ADR фиксируют отказ от RAG в MVP.
- `43/44` (AI Engineer) и `13/44` (Quality) — разные прогоны, не следует их вычитать или смешивать.
- Часть ссылок на отсутствующие файлы (`docs/model-candidates.md`, `docs/quality/golden-dataset/v1.jsonl`, `docs/quality/threat-model.md`) осталась из предыдущих лабораторных; в текущем `docs/` этих файлов нет.
