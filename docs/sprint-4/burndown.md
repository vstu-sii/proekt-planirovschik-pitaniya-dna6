# Burndown. Сводка

> [!ИНФОРМАЦИЯ]
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
> Факт: [burndown-fact.md](burndown-fact.md)
> Приемка: [acceptance.md](acceptance.md)

## 1. Обзор

| Поле                           | Значение                         |
| ------------------------------ | -------------------------------- |
| Спринт                         | Спринт 4 (Лабораторная работа 4) |
| Период                         | 23.11 – 11.12                    |
| Владелец                       | PRODUCT / VO                     |
| Единица измерения              | SP (1 SP = 2 ч)                  |
| Дата планирования              | 23.11.2026                       |
| План-линия (остаток по гейтам) | 82 --> 65 --> 33 --> 0 SP        |
| План                           | burndown-plan.md, п. 1 – 3       |
| Факт                           | burndown-fact.md, п. 1 – 3       |
| Приемка по гейтам              | acceptance.md, п. 1 – 3          |

### 1.1. Расшифровка ID и источники истины

| Префикс | Расшифровка                                                | Примеры                        | Источник истины                                                                                                                                                                                                                                                                                                                                                 |
| ------- | ---------------------------------------------------------- | ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `G`     | Гейт - контрольная точка спринта, а не календарная неделя  | G1, G2, G3                     | Даты и границы burndown.md; приемка [acceptance.md](acceptance.md) §1–3; скоуп по гейтам [mvp-scope.md](mvp-scope.md)                                                                                                                                                                                                                                           |
| `DOC`   | Документ / артефакт от Product VO                          | DOC-01 - DOC-04                | [iteration-notes.md](iteration-notes.md) §5, [quality-safety-answers.md](../use-cases/validation-report/quality-safety-answers.md) и [delivery-answers.md](../use-cases/validation-report/delivery-answers.md) – DOC-01; [roadmap.md](../roadmap.md) Веха 3/4 и [use-cases-list.md](../use-cases/description/01-in-scope/use-cases-list.md) – DOC-02/DOC-04; [prd.md](../prd.md) / [business-rules.md](../business-rules.md) – North Star для DOC-03 |
| `BUG`   | Баг/разрыв прототипа; `BUG-E*` - модельные находки Quality | BUG-001-BUG-050, BUG-E1-BUG-E8 | [bug-list.md](../use-cases/validation-report/bug-list.md) главный реестр `BUG-001…050`; [quality-sync-report.md](../use-cases/validation-report/quality-sync-report.md) `BUG-E1…E8`; доказательства [lab3-eval-report.md](../quality/lab3-eval-report.md), [eval-report-1.md](../quality/eval-report-1.md), [delivery-answers.md](../use-cases/validation-report/delivery-answers.md) – уточнения по BUG-014/020/021/022/024/025 и BUG-E4 |
| `INFRA` | Инфраструктурная задача Спринта 4                          | INFRA-01 - INFRA-05            | [roadmap.md](../roadmap.md) Веха 3 (CI/CD, staging, observability, лимиты); [delivery-answers.md](../use-cases/validation-report/delivery-answers.md) – INFRA-04 (проверка публикации) и INFRA-05 (CI smoke test); [adr-02-model-selection.md](../adr/adr-02-model-selection.md), [adr-03-security-boundaries.md](../adr/adr-03-security-boundaries.md) – INFRA-03 |
| `SEC`   | Безопасность и атаки по Threat Model                       | SEC-01                         | [adr-03-security-boundaries.md](../adr/adr-03-security-boundaries.md); Threat model и атаки – [roadmap.md](../roadmap.md) Веха 1 и 3; [delivery-answers.md](../use-cases/validation-report/delivery-answers.md) – safe-refusal и причины отказов; факт – [burndown-fact.md](burndown-fact.md) §3 |
| `CH`    | Change / правка Use Case по итогам валидации прототипа     | CH-01 - CH-46                  | [05-changes.md](../use-cases/validation-report/05-changes.md) – реестр правок; связанные баги – [bug-list.md](../use-cases/validation-report/bug-list.md); актуальные UC – [use-cases-list.md](../use-cases/description/01-in-scope/use-cases-list.md)                                                                                                             |
| `UC`    | Use Case. Пользовательский сценарий продукта               | UC-1 - UC-9                    | [use-cases-list.md](../use-cases/description/01-in-scope/use-cases-list.md) (v2), [01-summary.md](../use-cases/validation-report/01-summary.md) – статус после прототипа; [mvp-scope.md](mvp-scope.md) – IN/CONDITIONAL/CUT Спринта 4                                                                                                                              |
| `Q`     | Открытый вопрос по итогам валидации                        | Q-01 - Q-09                    | [iteration-notes.md](iteration-notes.md) §5 – реестр вопросов и статусов; ответы – [ai-engineer-answers.md](../use-cases/validation-report/ai-engineer-answers.md), [quality-safety-answers.md](../use-cases/validation-report/quality-safety-answers.md), [delivery-answers.md](../use-cases/validation-report/delivery-answers.md) |

## 2. План и факт

| Гейт           | План (остаток SP, по гейтам) | Факт (остаток SP) | Отклонение                  | Коммит |
| -------------- | ---------------------------: | ----------------: | --------------------------- | ------ |
| G1 23–27.11    |                           65 |                79 | +14 (промежуточно на 24.11) | –      |
| G2 30.11–04.12 |                           33 |                 – | –                           | –      |
| G3 07–11.12    |                            0 |                 – | –                           | –      |

## 3. Анализ отклонений от плана

| Гейт | План/факт | Причина отклонения                                                                                                                                                                                                                                   | Управленческое решение                                                                                                                                      | Ответственный           | Дата  | Коммит/PR |
| ---- | --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- | ----- | --------- |
| G1   | 17 / 3    | DOC-01/DOC-02 приняты; P0-код еще не принят; BUG-020 – пустой список допустим, отдельно `Failed to fetch`; BUG-021 – прод-провайдер не подтвержден; BUG-025 – сохранение есть, UI не восстанавливает. План переоценен 70 → 82 SP по ответам Delivery | Скоуп UC-4…UC-9 зафиксирован в CUT; G2 расширен только за счет уточнений Delivery, дедлайн 11.12 не двигать                                                 | PRODUCT / VO            | 25.11 | –         |
| G2   | 32 / –    | Отклонение по плану отсутствует; добавлены BUG-022, BUG-E4, BUG-014, INFRA-04 (+10 SP)                                                                                                                                                               | Приоритет BUG-E1, BUG-E3, BUG-022 и INFRA-04; сверить 16/2/14, `totals` и коды причин; при красном gate вырезать P1 (BUG-E4, BUG-014), а не двигать дедлайн | AI ENGINEER<br>DELIVERY | 04.12 | –         |
| G3   | 33 / –    | Отклонение по плану отсутствует; добавлен INFRA-05 (+2 SP)                                                                                                                                                                                           | Финальная приемка по DoD; INFRA-05 исправляет CI smoke test, BUG-022 расширяет safety-проверки; незакрытое перенести в бэклог Спринта 5                     | PRODUCT / VO            | 11.12 | –         |
