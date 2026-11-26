# Lab 4 AI Engineer Infrastructure Deliverables

Артефакты роли AI Engineer для спринта 4. Пакет рассчитан на перенос в ветку `lab4-ai-engineer-infrastructure` проекта `vstu-sii/proekt-planirovschik-pitaniya-dna6`.

## Что внутри

- `ml/prompts_v2/` — production prompt v2, eval prompt v2 и taxonomy ошибок.
- `ml/experiments/run_ab.py` — paired A/B runner на Golden Dataset v1; сохраняет JSON и CSV, использует GigaChat `json_schema` strict и локально проверяет контракт.
- `ml/experiments/cost_model.py` — расчёт токенов/стоимости с configurable provider rates.
- `ml/tools/nutrition_catalog.py` — read-only расчёт КБЖУ/стоимости по доверенному каталогу.
- `ml/tools/tool_runtime.py` — allowlist, role authorization, timeout и обработка ошибок.
- `ml/tools/cache.py` — SQLite TTL response cache, ключ включает модель и prompt version.
- `ml/tools/mealplan_guard.py` — базовые детерминированные проверки контракта, исключений и времени.
- `ml/tools/safety_review.py` — ручная сверка safety-critical с reason codes; pending не считается pass.
- `tests/` — Golden Dataset v1 и unit tests.
- `notebooks/Lab4_AI_Engineer_AB_Cost.ipynb` — последний выполненный ноутбук с экспортной ячейкой.
- `results/` — сырые результаты последнего запуска, failure CSV, сводка, safety review и cost accounting.
- `docs/` — отчёты, tool contract, trace policy, safety reconciliation, ADR, `prompt-evaluation.md` и `criteria-closure.md`.

## Быстрый offline check

```bash
python -m pip install -r requirements-dev.txt
pytest -q tests
```

## Live A/B

```bash
export GIGACHAT_CREDENTIALS='...'
export GIGACHAT_CA_BUNDLE_FILE='/path/to/ca-bundle.pem'
python -m ml.experiments.run_ab --dataset tests/v1.json --output results/lab4_ab.json --model GigaChat-2
```

Полный eval делает 44 кейса × 2 варианта = 88 логических записей. Не публикуйте credentials или OAuth-токены.

## Последний запуск Colab (25.11.2026)

- OAuth preflight и A/B smoke test прошли.
- Полный A/B: **80/88 успешных API вызовов** (A_v1 44/44; B_v2 36/44).
- Все 80 успешных ответов прошли JSON-контракт; invalid JSON = 0, schema-invalid = 0.
- После retry: 9 дополнительных попыток; 1 восстановленный кейс; 8 ошибок B_v2 остались.
- Live notebook offline tests: **22 passed, 0 failed**; supplemental package validation after adding the cache benchmark regression test: **23 passed, 0 failed**.
- Safety review: **16 кейсов pending manual review**, 0 passed, 0 violations.
- Usage успешных вызовов: **18 894 токена** (11 261 input, 7 633 output). Freemium денежное списание: 0 ₽ в пределах доступной бесплатной квоты; выдуманные token rates не применяются.

Raw JSON/CSV, failure CSV, summary и cost accounting обновлены из архива результатов последнего запуска. `notebook_run_summary.json` и `cost_accounting_freemium.json` согласованы с 88 строками `lab4_ab.json`/`.csv`. Полный A/B остаётся частичным, поэтому победитель prompt v2 не объявляется. Все 16 safety-critical кейсов требуют ручной проверки.

См. `results/notebook_run_summary.json`, `results/notebook_run_notes.md` и `docs/experiments/lab4.md`.

## Ответ преподавателю

См. `docs/tracing-policy.md`: полная трассировка нужна для контролируемого eval/debug и анализа причин ошибок; production default рекомендуется `TRACE_CAPTURE_CONTENT=false`, с временным разрешённым захватом, редактированием данных и сроком хранения.

## Закрытие замечаний агента проверки

См. `docs/criteria-closure.md`. Добавлен измеренный controlled cache replay: 100 одинаковых запросов, 100→1 backend calls, 99 hits, 99% token-equivalent reduction (не production traffic и не денежная экономия Freemium). Добавлено same-dataset сравнение версий prompt с обоснованием изменения и честным выводом: B_v2 использует на 4.14% меньше токенов на успешный вызов, но имеет 8/44 API/SDK failures, поэтому победитель не объявляется. Все исходные результаты последнего live запуска сохранены.
