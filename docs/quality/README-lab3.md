# Lab 3 — Quality & Safety (только файлы своей роли)

Это не весь проект. Скопируйте папки `backend/tests/evals`, `docs/quality` и `.github/workflows` в корень актуального проекта Delivery + AI Engineer, сохранив структуру. Не заменяйте другие файлы команды.

## Проверка (Windows PowerShell из папки project)

```powershell
python -m pip install pytest
python -m pytest -q backend/tests/evals/test_eval_runner.py backend/tests/evals/test_analysis.py
python -m backend.tests.evals.analyze_results
```

Проверка порога:

```powershell
python -m backend.tests.evals.analyze_results --gate
```

На фактическом baseline 13/44 этот шаг **ожидаемо падает** (exit code 1). Это корректное выявление регрессии/невыполнения требований, а не неисправность инструмента.

Для нового live-прогона (после настройки AI Engineer и GigaChat) запускайте из `project`:

```powershell
python -m backend.tests.evals.evaluate --mode live --dataset docs/quality/golden-dataset/v1.jsonl --out backend/tests/evals/results/new-baseline.jsonl --summary backend/tests/evals/results/new-summary.json
```

Файл `evaluate.py` сохранён из пользовательского запуска, включая его текущую логику. Параметры `--out` и `--summary` предотвращают перезапись исходного прогона.

## Важно о CI

Workflow `eval-quality.yml` выполняет локальные тесты и проверяет **сохранённый снимок baseline**. Он не обращается к GigaChat. На текущем снимке PR будет красным, потому что 31/44 случаев завершились ошибкой. Для живого eval в CI потребуется отдельный job с секретом API и зависимостями AI Engineer. Это нельзя считать уже проверенным без запуска на GitHub.

## Содержимое

- `backend/tests/evals/evaluate.py` — исходный eval runner пользователя
- `backend/tests/evals/analyze_results.py` — независимый пересчёт сохранённых результатов
- `backend/tests/evals/test_eval_runner.py`, `test_analysis.py` — тесты
- `backend/tests/evals/results/` — реальные результаты baseline + сводка
- `docs/quality/golden-dataset/v1.jsonl`, `v2.jsonl` — датасеты
- `docs/quality/lab3-eval-report.md` — итоговый отчёт
- `.github/workflows/eval-quality.yml` — CI заготовка с порогом

Перед публикацией результатов убедитесь, что ответы не содержат персональных данных. Токены и ключи в архив не включены.

## Обновление после Product VO

Добавлен `docs/quality/product-vo-eval-report.md`; в `v2.jsonl` размечены 13 семантических, 16 safety и 7 структурных регрессионных случаев. Всего по-прежнему 48 уникальных кейсов. Исходные данные v1 и результаты 44-кейсного baseline не менялись. Новые метки **не** означают автоматического прохождения критериев.

Запуск проверки: `python -m pytest -q backend/tests/evals/`. При переносе файлов не удаляйте другие модули команды.
