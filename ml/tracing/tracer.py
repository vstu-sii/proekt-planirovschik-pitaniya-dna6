"""Small trace adapter.

Writes one JSON object per LLM call to JSONL. If Langfuse is configured, the same
call can also be mirrored there. No credentials are written to traces.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

TRACE_PATH = Path(os.getenv("TRACE_PATH", "artifacts/traces.jsonl"))
TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)

try:
    from langfuse import Langfuse
except Exception:
    Langfuse = None

_langfuse = None
if Langfuse and os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"):
    _langfuse = Langfuse()


def trace_llm_call(**event):
    event = dict(event)
    event["timestamp"] = time.time()
    # Prompt/response capture is opt-in to avoid persisting personal input by default.
    capture_content = os.getenv("TRACE_CAPTURE_CONTENT", "false").lower() == "true"
    if not capture_content:
        event.pop("prompt", None)
        event.pop("response", None)
    event["content_captured"] = capture_content
    with TRACE_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    if _langfuse:
        try:
            generation = _langfuse.generation(
                name="meal-planner-baseline",
                model=event.get("model"),
                input=event.get("prompt"),
                output=event.get("response"),
                metadata={k: v for k, v in event.items() if k not in {"prompt", "response"}},
            )
            generation.end()
            _langfuse.flush()
        except Exception:
            pass
