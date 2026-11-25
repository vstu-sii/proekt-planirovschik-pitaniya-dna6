# Burndown. План

> [!INFO]
>
> Вместо «Недель» фиксируются **Гейты**: G1 23.11 – 27.11, G2 30.11 – 04.12, G3 07.12 – 11.12.
>
> Сводка: [burndown.md](burndown.md) 
> План: [burndown-plan.md](burndown-plan.md)
> Приемка: [acceptance.md](acceptance.md)
> 
> Генерация графика burndown: _директория burndown-chart_

| Поле                           | Значение                                                                                 |
| ------------------------------ | ---------------------------------------------------------------------------------------- |
| Спринт                         | Спринт 4 (Лабораторная работа 4)                                                         |
| Период                         | 23.11 – 11.12                                                                            |
| Владелец                       | PRODUCT / VO                                                                             |
| Единица измерения              | SP (1 SP = 2 ч)                                                                          |
| Дата планирования              | 23.11.2026                                                                               |
| Источники                      | iteration-notes.md, bug-list.md, quality-sync-report.md, roadmap.md, delivery-answers.md |
| План-линия (остаток по гейтам) | 82 --> 65 --> 33 --> 0 SP                                                                |
| Сводка по факту                | burndown.md, п. 2 – 3                                                                    |

## План по гейтам

### 1. План G1 (23.11 – 27.11)

| ID           | Задача                                           | Роль                | Приоритет | Источник (BUG/CH)                                            | Оценка, SP |
| ------------ | ------------------------------------------------ | ------------------- | --------- | ------------------------------------------------------------ | ---------: |
| DOC-01       | Обработать ответы Quality, Delivery              | PRODUCT             | P1        | iteration-notes §5, quality-safety-answers, delivery-answers |          2 |
| DOC-02       | Подготовить формы спринта                        | PRODUCT             | P1        | burndown, burndown-plan                                      |          1 |
| BUG-001      | Авторизация демо-пользователя                    | DELIVERY            | P0        | BUG-001                                                      |          3 |
| BUG-006      | Кнопка «Сохранить профиль» и сообщение об успехе | DELIVERY            | P0        | BUG-006                                                      |          2 |
| BUG-010      | Заменить фиксированный список «Мои продукты»     | DELIVERY            | P0        | BUG-010                                                      |          2 |
| BUG-011      | Форма «Добавить продукт»                         | PRODUCT<br>DELIVERY | P0        | BUG-011                                                      |          3 |
| BUG-018      | Выбор длительности 7/3/1                         | PRODUCT<br>DELIVERY | P0        | BUG-018                                                      |          2 |
| BUG-023      | Отображение всех 7 дней меню                     | DELIVERY<br>PRODUCT | P0        | BUG-023                                                      |          2 |
| **Итого G1** |                                                  |                     |           |                                                              |     **17** |

### 2. План G2 (30.11 – 04.12)

| ID           | Задача                                              | Роль                               | Приоритет | Источник (BUG/CH)                       | Оценка, SP |
| ------------ | --------------------------------------------------- | ---------------------------------- | --------- | --------------------------------------- | ---------: |
| BUG-021      | Проверить/переключить прод на реальный GigaChat     | DELIVERY<br>AI ENGINEER            | P0        | BUG-021, BUG-E6, Q-06, delivery-answers |          5 |
| BUG-E1       | Исправить контракт MealPlanDraft                    | AI ENGINEER                        | P0        | BUG-E1                                  |          3 |
| BUG-E3       | Safety-critical: сверка 16/2/14 и коды причин       | AI ENGINEER<br>QUALITY             | P0        | BUG-E3, BUG-022, Q-03, delivery-answers |          4 |
| BUG-022      | Справочник диет/аллергенов и проверка ингредиентов  | DELIVERY<br>QUALITY                | P0        | BUG-022, BUG-E3, Q-09, delivery-answers |          3 |
| INFRA-04     | Проверка опубликованной версии: провайдер, URL, E2E | DELIVERY                           | P0        | Q-06, delivery-answers §1/§4            |          3 |
| BUG-012      | Поиск и подсказки при добавлении продукта           | DELIVERY<br>AI ENGINEER            | P0        | BUG-012, CH-01, delivery-answers Q-05   |          3 |
| BUG-020      | Уточнить ошибку при пустом списке                   | DELIVERY<br>AI ENGINEER            | P0        | BUG-020, delivery-answers               |          2 |
| BUG-025      | Восстановление плана/профиля в UI после F5          | DELIVERY                           | P0        | BUG-025, Q-07, delivery-answers         |          3 |
| BUG-E4       | Согласовать контракт `totals`/КБЖУ/стоимости        | AI ENGINEER<br>DELIVERY<br>QUALITY | P1        | BUG-E4, Q-02/Q-08, delivery-answers     |          2 |
| BUG-014      | Обновление запасов без дублирования при повторе     | DELIVERY                           | P1        | BUG-014, BUG-019, Q-07                  |          2 |
| BUG-019      | Загрузка/обновление ограничений из профиля          | DELIVERY                           | P1        | BUG-019, Q-07, delivery-answers         |          2 |
| **Итого G2** |                                                     |                                    |           |                                         |     **32** |

### 3. План G3 (07.12 – 11.12)

| ID           | Задача                                                        | Роль                             | Приоритет | Источник (BUG/CH)                             | Оценка, SP |
| ------------ | ------------------------------------------------------------- | -------------------------------- | --------- | --------------------------------------------- | ---------: |
| INFRA-01     | CI/CD при мерже в main и rollback одной командой              | DELIVERY                         | P1        | roadmap, Веха 3                               |          4 |
| INFRA-02     | Staging и единый дашборд метрик/логов/трейсов                 | DELIVERY                         | P1        | roadmap, Веха 3                               |          4 |
| INFRA-03     | Лимиты запросов/токенов, алерты, 503 + request_id             | DELIVERY                         | P0        | ADR-02, ADR-03                                |          4 |
| INFRA-05     | Исправление smoke test (`profile` обязателен) и защиты ветки | DELIVERY                         | P0        | delivery-answers §1, roadmap, Веха 3          |          2 |
| EVAL-01      | Полный eval и валидаторы вместо null; `null` ≠ 0, N/A по CH-01 | QUALITY                          | P0        | BUG-E4, BUG-E5, BUG-E6, Q-03/Q-05, delivery-answers | 4 |
| SEC-01       | Атаки по Threat Model, safe-refusal, коды причин, регресс     | QUALITY                          | P0        | ADR-03, Threat Model, delivery-answers        |          4 |
| BUG-026      | Отображение списка покупок                                    | DELIVERY                         | P1        | BUG-026                                       |          2 |
| BUG-024      | Фактические дневные КБЖУ и уточнение `totals`                 | DELIVERY                         | P1        | BUG-024, BUG-E4, Q-08, delivery-answers       |          2 |
| BUG-004      | Авторасчет целевого КБЖУ в профиле                            | AI ENGINEER<br>PRODUCT           | P1        | BUG-004                                       |          2 |
| DOC-04       | PRD v3 и обновленные Use Cases                                | PRODUCT                          | P1        | roadmap, Веха 3, delivery-answers §3          |          3 |
| DOC-03       | Финальная приемка и замер North Star                         | PRODUCT                          | P1        | roadmap, Веха 3/4                             |          2 |
| **Итого G3** |                                                               |                                  |           |                                               |     **33** |

## Итоги плана по гейтам

| Гейт      |  Задач | Оценка, SP | Остаток после гейта, SP |
| --------- | -----: | ---------: | ----------------------: |
| G1        |      8 |         17 |                      65 |
| G2        |     11 |         32 |                      33 |
| G3        |     11 |         33 |                       0 |
| **Итого** | **30** |     **82** |                       – |
