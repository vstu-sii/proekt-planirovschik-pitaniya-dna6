import time
from typing import Any

import httpx

from app.core.config import settings


def emit_trace(request_id: str, event: str, **attributes: Any) -> None:
    if not settings.trace_collector_url:
        return
    payload = {
        "request_id": request_id,
        "event": event,
        "timestamp": time.time(),
        "attributes": attributes,
    }
    try:
        httpx.post(
            f"{settings.trace_collector_url.rstrip('/')}/v1/traces",
            json=payload,
            timeout=0.5,
        )
    except Exception:
        # Observability failure must never break the user request.
        pass
