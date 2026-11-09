# Lab 3 — AI Engineer prototype

## Быстрый повторный запуск

Требуется Python 3.11+ и зависимости из `requirements.txt`.

Linux/macOS:
```bash
export GIGACHAT_CREDENTIALS="..."
export GIGACHAT_MODEL="GigaChat-2"
export TRACE_CAPTURE_CONTENT="true"

python -m pip install -r requirements.txt
python tests/evals/run_golden.py   --dataset docs/quality/golden-dataset/v1.json   --out docs/experiments/golden_eval_results.json   --summary-out docs/experiments/golden_eval_summary.json   --csv-out docs/experiments/golden_eval_results.csv
```

Windows PowerShell:
```powershell
$env:GIGACHAT_CREDENTIALS="..."
$env:GIGACHAT_MODEL="GigaChat-2"
$env:TRACE_CAPTURE_CONTENT="true"

python -m pip install -r requirements.txt
python tests/evals/run_golden.py `
  --dataset docs/quality/golden-dataset/v1.json `
  --out docs/experiments/golden_eval_results.json `
  --summary-out docs/experiments/golden_eval_summary.json `
  --csv-out docs/experiments/golden_eval_results.csv
```

После запуска результаты и трасса находятся в `docs/experiments/`. Каждый вызов LLM получает отдельную JSONL-запись с идентификатором, попыткой, prompt, response, latency, token usage, статусом и результатом валидации.

## Артефакты лабораторной

- `docs/quality/golden-dataset/v1.json` — датасет из 44 кейсов, восстановленный из точных записей фактического прогона, потому что исходный upload датасета отсутствовал в переданном архиве.
- `docs/experiments/golden_eval_results.json` — результаты по каждому кейсу.
- `docs/experiments/golden_eval_results.csv` — табличная версия результатов.
- `docs/experiments/golden_eval_summary.json` — агрегированные latency/token/validation метрики.
- `docs/experiments/llm_traces.jsonl` — трасса каждого зафиксированного LLM-вызова.
- `artifacts/traces.jsonl` — копия трассы в стандартном пути tracer.

## Воспроизводимость

Репозиторий содержит код запуска, исходный датасет для повторного запуска и уже сохранённые результаты. Для воспроизведения необходимы только зависимости и `GIGACHAT_CREDENTIALS`.

Фактический запуск 2026-10-28:
- 44 кейса;
- API success: 44/44;
- structured JSON/schema: 43/44 (97.73%);
- средняя latency: 1.523 s;
- максимум: 4.291 s;
- средние токены: input 220.82, output 145.52, total 366.34.

## Важное ограничение по provenance

В исходном архиве не было отдельного файла `v1.json`; он был загружен в notebook-сессию. Поэтому файл `docs/quality/golden-dataset/v1.json` в этой исправленной версии восстановлен из `golden_eval_results.json`: сохранены исходные `id`, `input`, `must_contain`, `must_not_contain`, safety/source поля. Это делает прогон воспроизводимым по имеющимся артефактам, но не является новым утверждением, что файл был отдельным утверждённым командным upload.

## Tracing

`TRACE_CAPTURE_CONTENT=true` включён по умолчанию. При таком режиме prompt и response не удаляются из trace. Для приватных запусков можно выставить `TRACE_CAPTURE_CONTENT=false`, но такой запуск не удовлетворяет критерию содержательной трассировки.

Секреты и авторизационные заголовки в trace не записываются.
