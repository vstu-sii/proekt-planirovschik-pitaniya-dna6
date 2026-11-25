# Изменения AI-части за Lab 4

## Что добавлено в пакет

- Prompt v2 для production MealPlanDraft и отдельный eval prompt для честного A/B на StructuredAnswer.
- Error taxonomy, связанная с Golden Dataset: ложная точность, аллергены, пищевой safety, prompt injection, отсутствующие данные, противоречия и границы MVP.
- Paired A/B runner для GigaChat с сохранением JSON/CSV.
- Python cost model с конфигурируемыми тарифами.
- SQLite TTL cache с ключом request + model + prompt version.
- Read-only tool `nutrition.calculate` по доверенному каталогу, с проверкой allowlist/role, ограничением входа и тайм-аутом.
- Unit tests для расчётов, cache key, timeout, отказов и cost math.

## Не выполнено/не заявляется

- Cache не интегрирован в текущий backend endpoint и cache hit rate не измерен.
- Nutrition tool является изолированным модулем-прототипом; подключение к актуальному backend/catalog требует интеграции Delivery и согласования API-контракта.
- Не заявляется production deploy, CI run или подтверждённый прирост качества.

## Цена решения

Принят локальный SQLite cache и read-only Python tool вместо дополнительного агентского фреймворка или RAG. Это снижает сложность и сохраняет детерминированность расчётов, но требует аккуратной интеграции с backend, защиты cache-файла и согласования каталога. Новые внешние зависимости для основной логики не нужны; `gigachat` требуется только для live A/B.

## Следующий критерий принятия

Принимать prompt v2 после полного paired eval и ручной проверки safety-critical кейсов. Инструмент подключать только после проверки контракта, тайм-аута, allowlist и детерминированных результатов в backend integration tests.

## Earlier live Colab run (historical)

The earlier strict-schema live run returned 78/88 API responses (A_v1 43/44, B_v2 35/44). All successful responses passed the required `answer`, `assumptions`, `warnings` JSON contract. Ten calls failed before local output validation: nine B_v2 SDK `ValidationError` cases with empty message content and missing role, plus one A_v1 `ReadTimeout`. This run is historical and superseded by the latest run below.

## Latest executed run (2026-11-25)

The latest executed notebook and its exported raw JSON/CSV reconcile to **80/88 final API successes**: A_v1 44/44, B_v2 36/44. All 80 successful outputs passed the strict JSON contract. There were 9 retry attempts, 1 recovered logical case, and 8 B_v2 SDK `ValidationError` failures remain. Successful-call usage was 18,894 tokens (11,261 input; 7,633 output). 22 offline tests passed. The full A/B remains partial; no prompt winner is declared.

Safety review output in this latest run remains **16 pending, 0 passed, 0 violations**. Manual review is still outstanding; pending is not pass. The export cell generated the 8-row failure CSV and reconciled the current artifacts.
