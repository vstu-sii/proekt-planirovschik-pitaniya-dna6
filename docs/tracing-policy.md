# Trace content policy and answer to instructor

## Why full prompt/response capture was enabled for evaluation

Полное сохранение текста запроса и ответа по умолчанию в контролируемом eval/debug-окружении выбрано для observability и воспроизводимости. Метаданные (latency, tokens, status) показывают, что вызов был медленным или невалидным, но не объясняют причину. Содержимое помогает определить, какие инструкции модель увидела, как интерпретировала ограничения, где нарушила JSON-контракт, пропустила аллерген или поддалась недоверенному тексту. Это особенно полезно при парном сравнении prompt v1/v2 и расследовании safety-кейсов.

## Why this should not be the production default

Prompt/response may contain personal profile details, budget, pantry, allergies and other sensitive context. Full capture increases data exposure, retention and access-control risks. Therefore evaluation default and production default must be separate:

- Eval/debug: content capture explicitly enabled for a bounded test run, synthetic or minimized data, restricted access and retention.
- Production: content capture disabled by default; store request_id, model/prompt version, status, latency, token counts, validation and reason codes.
- Incident/debug: temporary, approved, sampled capture with redaction and expiry; turn off after investigation.

## Configuration recommendation

Use `TRACE_CAPTURE_CONTENT=false` as production default. For an explicit evaluation run set `TRACE_CAPTURE_CONTENT=true` only in a local/staging environment and document the dataset and retention. Avoid logging credentials, authorization headers, full profile records or unrelated history. Traces must have access controls and deletion/retention policy.

## Instructor answer

«Мы включили полное сохранение prompt и response по умолчанию на этапе лабораторной, потому что для анализа ошибок одной статистики недостаточно: нужен исходный контекст и фактический ответ. Это позволяет воспроизводить eval, находить причину нарушения контракта и проверять prompt injection/safety. Но это решение предназначено для контролируемого evaluation, а не для production. В production безопаснее сохранять метаданные, а содержимое включать временно, по явному разрешению, с редактированием чувствительных данных и ограниченным сроком хранения. Таким образом, полнота диагностики не должна достигаться ценой постоянного накопления пользовательских данных».
