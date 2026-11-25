# Планировщик питания

Проект курса «Системы искусственного интеллекта». 

Планировщик питания – AI-ассистент для персонального планирования питания: меню под бюджет, КБЖУ, аллергены и продукты, которые уже есть дома.

> **Актуальный этап:** Спринт 4 / Lab 4 – Production-ready инфраструктура.
>
> **Ветка:** `lab4-product-infrastructure`

## Важно знать о проекте

- **Проблема:** молодые люди, живущие отдельно, имеют конфликт бюджета, времени и здоровья. Ручной подсчет КБЖУ и планирование меню требуют слишком много ментальных ресурсов (подробнее см. `docs/prd.md`).
- **ЦА:** молодые люди в съемной квартире/общежитии с ограниченным бюджетом на питание; в нарративе – Кирилл, 24 года, г. Волгоград, панкреатит (`docs/brief.md`).
- **North Star:** ≥40% активных пользователей завершают 4 недельных цикла планирования подряд; уточнения v3 — окно 28 дней после приёмки G3 и 0 открытых P0 по UC-1–UC-3, пороги `Target >=40% / Guardrail 25-39% / Miss <25%`, до старта окна только proxy-замер ([docs/north-star.md](docs/north-star.md), [docs/prd.md](docs/prd.md)).
- **SLO/SLA:** генерация меню – 95% успешных запросов <10 с, SLA 99% <15 с (`docs/prd.md`).
- **Архитектура:** Direct Prompt + Structured JSON + Python tools; LLM формирует черновик, Python считает стоимость/КБЖУ и проверяет ограничения (`docs/adr/adr-01-ai-pipeline-architecture.md`).
- **Модель:** GigaChat 2 Lite как основной адаптер; один retry при transient error; отказ – `503 Service Unavailable + request_id`, без mock-ответа `200` (`docs/adr/adr-02-model-selection.md`).
- **Безопасность:** zero trust к свободному тексту LLM; детерминированная серверная валидация, allowlist инструментов, минимальные права (`docs/adr/adr-03-security-boundaries.md`).
- **Источник истины для чисел:** backend-каталог и детерминированные инструменты, а не модель (`docs/sprint-4/mvp-scope.md`, `docs/adr/adr-01-ai-pipeline-architecture.md`).

## Спринт 4: текущее состояние проекта

- **Период:** 23.11 – 11.12, 15 рабочих дней = 3 календарные недели.
- **Гейты:** **G1** 23.11 – 27.11, **G2** 30.11 – 04.12, **G3** 07.12 – 11.12.
- **Единица оценки:** SP, 1 SP = 2 ч.
- **Базовый план:** 82 SP после переоценки 25.11 по delivery-answers; план-линия `82 → 65 → 33 → 0 SP`.
- **Факт G1 на 24.11:** 79 SP; приняты DOC-01 и DOC-02 (3 SP), 6 P0-задач на 14 SP остаются в бэклоге до 27.11.
- **IN:** UC-1 авторизация/профиль, UC-2 локальная БД «Мои продукты», UC-3 персонализированное меню.
- **CONDITIONAL:** RES-01 мобильная верстка, RES-02 ручной ввод КБЖУ, RES-03 P1 UC-1, RES-04 P1 UC-2 (BUG-014 переведен в базовый план G2).
- **CUT:** UC-4 замена блюда, UC-5 перенос меню, UC-6 рецепт из остатков, UC-7 быстрый ужин, UC-8 КБЖУ по фото, UC-9 «Коллекции».

#### Для работы со скриптом `plot_burndown.py`:
1. Зависимости
`python -m pip install matplotlib`

2. Запуск из корня репозитория:
`python docs/sprint-4/burndown-chart/plot_burndown.py`

3. Результат 
Создается файл `docs/sprint-4/burndown-chart/burndown-chart-vN.png`, где N берется как следующее значение по уже существующим `v*.png` в этой папке; на графике добавляется подпись с датой генерации: `Сгенерировано: DD.MM`.

4. Обновление данных
Скрипт автоматически читает `docs/sprint-4/burndown-fact.md`: 
- план-линию (`82 --> 65 --> 33 --> 0 SP`)
- даты гейтов из заголовков `### N. Факт Gx (DD.MM – DD.MM)` 
- факт из строк `Остаток спринта после Gx: N SP`. 
При обновлении факта править только `burndown-fact.md`, затем повторно запутстить скрипт, после чего автоматически создается новый PNG `burndown-chart-vN.png`.

#### Ключевые файлы спринта:

| Тема | Документ |
| --- | --- |
| Зафиксированный скоуп | [docs/sprint-4/mvp-scope.md](docs/sprint-4/mvp-scope.md) |
| Сводка burndown | [docs/sprint-4/burndown.md](docs/sprint-4/burndown.md) |
| План burndown | [docs/sprint-4/burndown-plan.md](docs/sprint-4/burndown-plan.md) |
| Факт burndown | [docs/sprint-4/burndown-fact.md](docs/sprint-4/burndown-fact.md) |
| Приемка по DoD | [docs/sprint-4/acceptance.md](docs/sprint-4/acceptance.md) |
| Итоги прототипа и план | [docs/sprint-4/iteration-notes.md](docs/sprint-4/iteration-notes.md) |

## Качество и известные ограничения

Baseline Quality (`docs/quality/lab3-eval-report.md`, `docs/quality/summary-full-v1.json`):

- 44 кейса Golden Dataset v1; получено 13/44 ответов, ошибок 31/44.
- Структурно валидны 13/13 полученных ответов, но общий порог 95% не достигнут.
- Safety-critical: 16 кейсов; ответ получен только в 2, ошибка в 14.
- Средняя задержка 3,2641 с, p95 15,2794 с – только по 13 полученным ответам.
- `budget_accuracy`, `nutrition_accuracy`, `allergen_compliance`, `critical_violations_verified` не подтверждены; `null` означает «не проверено», а не «нарушений нет».
- Показатель 43/44 из отчета AI Engineer относится к другому прогону и не заменяет 13/44 (`docs/use-cases/validation-report/ai-engineer-answers.md`).

Главный реестр находок прототипа – `docs/use-cases/validation-report/bug-list.md`: 50 находок, из них 17 P0, 22 P1, 11 P2. Валидация 9 UC: полностью не работает ни один, 3 частично, 6 не реализованы (`docs/use-cases/validation-report/01-summary.md`).

## Карта документации

### Продукт и требования

| Файл | Назначение |
| --- | --- |
| [docs/brief.md](docs/brief.md) | Бриф «итоговая картинка», нарратив North Star |
| [docs/brief.pptx](docs/brief.pptx) | Презентация-бриф |
| [docs/prd.md](docs/prd.md) | PRD v3: сегмент, боли, North Star, SLI/SLO/SLA, out of scope |
| [docs/hypotheses.md](docs/hypotheses.md) | 5 фальсифицируемых гипотез и пороги опровержения |
| [docs/insights.md](docs/insights.md) | Вопросы интервью и инсайты по пищевому поведению |
| [docs/business-rules.md](docs/business-rules.md) | FACT / CONSTRAINT / ACTION / INFERENCE / COMPUTATION правила |
| [docs/glossary.md](docs/glossary.md) | Глоссарий терминов проекта |
| [docs/roadmap.md](docs/roadmap.md) | Вехи, MVP / Release 2.0, out of scope |
| [docs/sprint-4/iteration-notes.md](docs/sprint-4/iteration-notes.md) | Итоги Спринта 3, техдолг, вопросы Q-01–Q-09, план Спринта 4 |
| [docs/sprint-4/mvp-scope.md](docs/sprint-4/mvp-scope.md) | IN / CONDITIONAL / CUT Спринта 4 |
| [docs/sprint-4/burndown.md](docs/sprint-4/burndown.md) | Сводка: План и факт, анализ отклонений |
| [docs/sprint-4/burndown-plan.md](docs/sprint-4/burndown-plan.md) | План сгорания: 30 задач, 82 SP |
| [docs/sprint-4/burndown-fact.md](docs/sprint-4/burndown-fact.md) | Факт сгорания по G1–G3 |
| [docs/sprint-4/acceptance.md](docs/sprint-4/acceptance.md) | Приемка инкрементов по гейтам и DoD |

### Use cases и диаграммы

| Файл | Назначение |
| --- | --- |
| [docs/use-cases/description/in-scope/use-cases-list.md](docs/use-cases/description/01-in-scope/use-cases-list.md) | Сводный список UC v2 |
| [docs/use-cases/description/in-scope/use-case-1.md](docs/use-cases/description/01-in-scope/use-case-1.md) | UC-1. Настроить профиль |
| [docs/use-cases/description/in-scope/use-case-2.md](docs/use-cases/description/01-in-scope/use-case-2.md) | UC-2. Пополнить локальную БД «Мои продукты» |
| [docs/use-cases/description/in-scope/use-case-3.md](docs/use-cases/description/01-in-scope/use-case-3.md) | UC-3. Сгенерировать персонализированное меню |
| [docs/use-cases/description/backlog/use-case-4.md](docs/use-cases/description/02-backlog/use-case-4.md) | UC-4. Заменить блюдо – в CUT Спринта 4 |
| [docs/use-cases/description/backlog/use-case-5.md](docs/use-cases/description/02-backlog/use-case-5.md) | UC-5. Перенести меню – в CUT Спринта 4 |
| [docs/use-cases/description/backlog/use-case-6.md](docs/use-cases/description/02-backlog/use-case-6.md) | UC-6. Рецепт из остатков – в CUT Спринта 4 |
| [docs/use-cases/description/backlog/use-case-7.md](docs/use-cases/description/02-backlog/use-case-7.md) | UC-7. Быстрый ужин – в CUT Спринта 4 |
| [docs/use-cases/description/out-of-scope/use-case-8.md](docs/use-cases/description/03-out-of-scope/use-case-8.md) | UC-8. КБЖУ по фото, вне MVP |
| [docs/use-cases/description/out-of-scope/use-case-9.md](docs/use-cases/description/03-out-of-scope/use-case-9.md) | UC-9. «Коллекции», вне MVP |
| [docs/use-cases/diagrams/plantuml-full-v2.md](docs/use-cases/diagrams/plantuml-full-v2.md) | PlantUML-диаграмма UC1–UC7 |

### validation report

| Файл | Назначение |
| --- | --- |
| [docs/use-cases/validation-report/README.md](docs/use-cases/validation-report/README.md) | Навигация; `bug-list.md` – главный источник истины |
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
| [docs/quality/eval-report-1.md](docs/quality/eval-report-1.md) | Отчет «где врем»: 44 кейса, 13/44 ответов |
| [docs/quality/lab3-eval-report.md](docs/quality/lab3-eval-report.md) | Технический baseline Quality и приоритетные действия |
| [docs/quality/summary-full-v1.json](docs/quality/summary-full-v1.json) | Машиночитаемые метрики baseline |
| [docs/quality/baseline-full-v1.jsonl](docs/quality/baseline-full-v1.jsonl) | Сырые 44 кейса прогона от 05.11 |

### Задания лабораторных работ – спринтов

| Файл                                     | Спринт   | Тема                                                                       |
| ---------------------------------------- | -------- | -------------------------------------------------------------------------- |
| [docs/tasks/lab1.md](docs/tasks/lab1.md) | Спринт 1 | Инициация: PRD, гипотезы, интервью, глоссарий, бриф                        |
| [docs/tasks/lab2.md](docs/tasks/lab2.md) | Спринт 2 | Дизайн: UC, roadmap, ADR, C4, API, golden dataset, threat model            |
| [docs/tasks/lab3.md](docs/tasks/lab3.md) | Спринт 3 | Прототип: валидация UC, baseline, evals, iteration notes                   |
| [docs/tasks/lab4.md](docs/tasks/lab4.md) | Спринт 4 | Инфраструктура: burndown, scope, acceptance, CI/CD, staging, observability |
| [docs/tasks/lab5.md](docs/tasks/lab5.md) | Спринт 5 | Тестирование: North Star, финальные evals, ablation, нагрузка              |
| [docs/tasks/lab6.md](docs/tasks/lab6.md) | Спринт 6 | Демо: презентация, репетиции, видео, trust block                           |
| [docs/tasks/lab7.md](docs/tasks/lab7.md) | Спринт 7 | Ревью: deploy-check, независимые evals, red team, ретро                    |

## Структура репозитория

- `docs/` – вся техническая документация и документация от Product VO перечислена выше.
- `backend/` – каталог зарезервирован под код сервиса; в текущей ветке он пуст.
- `.env` – локальные переменные окружения; значения не публикуются.

Целевые артефакты инфраструктуры из `docs/tasks/lab4.md` – `.github/workflows/deploy.yml`, `.github/workflows/quality-gates.yml`, `compose.staging.yml`, `monitoring/`, `tests/`, `backend/limits/`, `backend/guards/` – в этой ветке еще не созданы и описаны только в задании.

## Команда

| Роль | Имя | Ответственность в Спринте 4 |
| --- | --- | --- |
| PRODUCT / VO | Медведева С. | Скоуп, burndown, приемка, требования |
| AI ENGINEER | Черепова А. | Промпты v2, evals, стоимость, инструменты |
| DELIVERY | Карпов Р. | CI/CD, staging, observability, лимиты |
| QUALITY & SAFETY | Карпова М. | Quality-gates, атаки, тесты критических путей |

## Известные расхождения в документации

- `docs/tasks/lab4.md` описывает 28 дней / недели 7–10, а файлы Product'а Спринт 4 используют сжатый период 23.11 – 11.12 на 3 гейта.
- `docs/roadmap.md` все еще включает UC-4–UC-5 в MVP; актуальный скоуп – `docs/sprint-4/mvp-scope.md` (UC-1–UC-3).
- В старых разделах глоссария и UC встречается RAG; PRD v2 и ADR фиксируют отказ от RAG в MVP.
- `43/44` (AI Engineer) и `13/44` (Quality) – разные прогоны, не следует их смешивать.
