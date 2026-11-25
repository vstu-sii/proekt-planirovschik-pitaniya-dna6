# Burndown. Сводка

> [!INFO]
> Сроки сжаты.
>
> 23.11 – 11.12 (15 рабочих дней = 3 календарные недели).
>
> Вместо полноценных «Недель» принята концепция «**Гейтов**»:
>
> - **G1**: 23.11 – 27.11
> - **G2**: 30.11 – 04.12
> - **G3**: 07.12 – 11.12
>
> Все таблицы считаются **по гейтам**, а не по неделям.
>
> Сводка: [burndown.md](burndown.md) 
> План: [burndown-plan.md](burndown-plan.md)
> Приемка: [acceptance.md](acceptance.md)

## 1. Обзор

| Поле                           | Значение                         |
| ------------------------------ | -------------------------------- |
| Спринт                         | Спринт 4 (Лабораторная работа 4) |
| Период                         | 23.11 – 11.12                    |
| Владелец                       | PRODUCT / VO                     |
| Единица измерения              | SP (1 SP = 2 ч)                  |
| Дата планирования              | 23.11.2026                       |
| План-линия (остаток по гейтам) | 70 --> 53 --> 31 --> 0 SP        |
| План                           | burndown-plan.md, п. 1 – 3       |
| Факт                           | burndown-fact.md, п. 1 – 3       |
| Приемка по гейтам              | acceptance.md, п. 1 – 3          |

### 1.1. Расшифровка ID и источники истины

| Префикс | Расшифровка                                                | Примеры                        | Источник истины                                                                                                                                                                                                                                                                                                                                                 |
| ------- | ---------------------------------------------------------- | ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `G`     | Гейт - контрольная точка спринта, а не календарная неделя  | G1, G2, G3                     | Даты и границы burndown.md; приемка [acceptance.md](acceptance.md) §1–3; скоуп по гейтам [mvp-scope.md](mvp-scope.md)                                                                                                                                                                                                                                           |
| `DOC`   | Документ / артефакт от Product VO                          | DOC-01 - DOC-04                | [iteration-notes.md](iteration-notes.md) §5, [quality-safety-answers.md](../use-cases/validation-report/quality-safety-answers.md) и [delivery-answers.md](../use-cases/validation-report/delivery-answers.md) — DOC-01; [roadmap.md](../roadmap.md) Веха 3/4 и [use-cases-list.md](../use-cases/description/in-scope/use-cases-list.md) — DOC-02/DOC-04; [prd.md](../prd.md) / [business-rules.md](../business-rules.md) — North Star для DOC-03 |
| `BUG`   | Баг/разрыв прототипа; `BUG-E*` - модельные находки Quality | BUG-001-BUG-050, BUG-E1-BUG-E8 | [bug-list.md](../use-cases/validation-report/bug-list.md) главный реестр `BUG-001…050`; [quality-sync-report.md](../use-cases/validation-report/quality-sync-report.md) `BUG-E1…E8`; доказательства [lab3-eval-report.md](../quality/lab3-eval-report.md), [eval-report-1.md](../quality/eval-report-1.md), [delivery-answers.md](../use-cases/validation-report/delivery-answers.md) — уточнения по BUG-020/021/022/024/025 |
| `INFRA` | Инфраструктурная задача Спринта 4                          | INFRA-01 - INFRA-03            | [roadmap.md](../roadmap.md) Веха 3 (CI/CD, staging, observability, лимиты); [delivery-answers.md](../use-cases/validation-report/delivery-answers.md) — CI smoke test; [adr-02-model-selection.md](../adr/adr-02-model-selection.md), [adr-03-security-boundaries.md](../adr/adr-03-security-boundaries.md) — INFRA-03 |
| `SEC`   | Безопасность и атаки по Threat Model                       | SEC-01                         | [adr-03-security-boundaries.md](../adr/adr-03-security-boundaries.md); Threat model и атаки — [roadmap.md](../roadmap.md) Веха 1 и 3; [delivery-answers.md](../use-cases/validation-report/delivery-answers.md) — safe-refusal и причины отказов; факт — [burndown-fact.md](burndown-fact.md) §3 |
| `CH`    | Change / правка Use Case по итогам валидации прототипа     | CH-01 - CH-46                  | [05-changes.md](../use-cases/validation-report/05-changes.md) — реестр правок; связанные баги — [bug-list.md](../use-cases/validation-report/bug-list.md); актуальные UC — [use-cases-list.md](../use-cases/description/in-scope/use-cases-list.md)                                                                                                             |
| `UC`    | Use Case. Пользовательский сценарий продукта               | UC-1 - UC-9                    | [use-cases-list.md](../use-cases/description/in-scope/use-cases-list.md) (v2), [01-summary.md](../use-cases/validation-report/01-summary.md) — статус после прототипа; [mvp-scope.md](mvp-scope.md) — IN/CONDITIONAL/CUT Спринта 4                                                                                                                              |
| `Q`     | Открытый вопрос по итогам валидации                        | Q-01 - Q-09                    | [iteration-notes.md](iteration-notes.md) §5 — реестр вопросов и статусов; ответы — [ai-engineer-answers.md](../use-cases/validation-report/ai-engineer-answers.md), [quality-safety-answers.md](../use-cases/validation-report/quality-safety-answers.md), [delivery-answers.md](../use-cases/validation-report/delivery-answers.md) |

## 2. План и факт

| Гейт           | План (остаток SP, по гейтам) | Факт (остаток SP) | Отклонение                  | Коммит |
| -------------- | ---------------------------: | ----------------: | --------------------------- | ------ |
| G1 23–27.11    |                           53 |                67 | +14 (промежуточно на 24.11) | –      |
| G2 30.11–04.12 |                           31 |                 – | –                           | –      |
| G3 07–11.12    |                            0 |                 – | –                           | –      |

## 3. Анализ отклонений от плана

| Гейт | План/факт | Причина отклонения                                                                | Управленческое решение                                                        | Ответственный | Дата  | Коммит/PR |
| ---- | --------- | --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | ------------- | ----- | --------- |
| G1   | 17 / 3    | DOC-01/DOC-02 приняты; P0-код еще не принят; BUG-020 — пустой список допустим, отдельно `Failed to fetch`; BUG-021 — прод-провайдер не подтвержден; BUG-025 — сохранение есть, UI не восстанавливает | Скоуп UC-4…UC-9 зафиксирован в CUT; G2 не расширять, дедлайн 11.12 не двигать | PRODUCT / VO  | 24.11 | –         |
| G2   | 22 / –    | Плановое отклонение отсутствует                                                   | Приоритет BUG-E1 и BUG-E3; сверить `totals` и коды причин, при красном gate вырезать P1, а не двигать дедлайн | AI ENGINEER   | 04.12 | –         |
| G3   | 31 / –    | Плановое отклонение отсутствует                                                   | Финальная приемка строго по DoD; исправить CI smoke test и расширить safety-проверки; незакрытое перенести в бэклог Спринта 5 | PRODUCT / VO  | 11.12 | –         |
