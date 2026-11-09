# LLM tracing

Baseline writes one JSON object per LLM call to `artifacts/traces.jsonl`.
Optional Langfuse mirroring is enabled when `LANGFUSE_PUBLIC_KEY` and
`LANGFUSE_SECRET_KEY` are configured.

Secrets are never included in the trace payload.
