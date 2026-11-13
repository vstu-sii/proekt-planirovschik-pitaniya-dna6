# Как опубликовать Lab 3 Quality & Safety

1. В своём репозитории на GitHub выберите ветку `lab3_quality-safety_prototype`.
2. Распакуйте `Lab3_Quality_Safety_GitHub_Only.zip`.
3. Через `Add file` → `Upload files` загрузите содержимое архива, сохранив пути `.github/workflows/`, `backend/tests/evals/`, `docs/quality/`.
4. Не загружайте целиком объединённый `project`, файлы `ml/`, `backend/app/`, `.env`, `__pycache__`, `.pytest_cache`.
5. После коммита откройте Actions → `Quality eval checks`. Тесты pytest должны пройти; порог 95% на сохранённом baseline 13/44 должен завершиться ошибкой.

Проверка локально из корня `project`:

```powershell
python -m pip install pytest
python -m pytest -q backend/tests/evals/
python -m backend.tests.evals.analyze_results
python -m backend.tests.evals.analyze_results --gate
```

Последняя команда ожидаемо возвращает код 1: baseline ниже порогов.
