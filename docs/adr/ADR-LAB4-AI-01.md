# ADR-LAB4-AI-01: Детерминированный tool и prompt/cache versioning

- Статус: Proposed for review
- Контекст: Lab 4 требует prompt v2, A/B, cost optimization и один tool с контрактом, timeout и минимальными правами.

## Решение

1. Использовать версионированные prompt files (`v2`) и сохранять prompt version в evaluation/cache key.
2. Сравнивать A/B на одном Golden Dataset и одной модели; не смешивать результаты разных версий dataset.
3. Кэшировать только идентичные структурированные запросы; ключ включает model и prompt version; TTL ограничивает устаревание.
4. Реализовать `nutrition.calculate` как read-only tool, работающий по доверенному каталогу. LLM не может менять профиль, запасы, меню или покупки.
5. Расчёты стоимости и КБЖУ остаются вне LLM.

## Альтернативы

- RAG: отклонён, так как не входит в MVP; нет необходимости в retrieval для текущего структурированного контекста.
- Агентский фреймворк: отклонён для одного инструмента; увеличивает зависимости и поверхность отказа.
- Права только через prompt: отклонены, потому что prompt не является enforcement boundary.

## Цена решения

Меньше гибкости, чем у полноценного агента, но меньше токенов, зависимостей и рисков. SQLite подходит для локального прототипа; при нескольких backend replicas потребуется shared cache (например, Redis) и отдельный контроль доступа. Controlled local replay измерен: 100 одинаковых запросов дают 99 cache hits, 100→1 backend calls и 99% token-equivalent reduction при usage-среднем последнего live run. Это не production hit rate; cache остаётся прототипом и ещё не интегрирован в endpoint. См. `docs/ml-cost.md` и `results/cache_cost_benchmark.json`.
