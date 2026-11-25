"""Small allowlisted, read-only tool executor with timeout and bounded inputs."""
from __future__ import annotations
import asyncio
from typing import Any, Callable

class ToolError(RuntimeError): pass

class ToolRuntime:
    def __init__(self, tools: dict[str, Callable[[dict[str, Any]], Any]], *, timeout_sec: float = 2.0,
                 allowed_tools: frozenset[str] = frozenset({"nutrition.calculate"})):
        self._tools = dict(tools)
        self.timeout_sec = max(0.05, min(float(timeout_sec), 10.0))
        self.allowed_tools = allowed_tools

    async def call(self, tool_name: str, args: dict[str, Any], *, caller_role: str) -> dict[str, Any]:
        if caller_role not in {"ai_model", "backend"}:
            raise ToolError("caller is not authorized")
        if tool_name not in self.allowed_tools or tool_name not in self._tools:
            raise ToolError("tool is not allowlisted")
        if not isinstance(args, dict) or len(args) > 10:
            raise ToolError("invalid tool arguments")
        try:
            result = await asyncio.wait_for(asyncio.to_thread(self._tools[tool_name], args), timeout=self.timeout_sec)
        except asyncio.TimeoutError as exc:
            raise ToolError("tool_timeout: calculation unavailable; do not invent values") from exc
        except Exception as exc:
            raise ToolError(f"tool_failed: {type(exc).__name__}") from exc
        return {"ok": True, "result": result}

    async def call_or_fallback(self, tool_name: str, args: dict[str, Any], *, caller_role: str) -> dict[str, Any]:
        """Return a model-safe failure envelope instead of fabricated calculation values."""
        try:
            return await self.call(tool_name, args, caller_role=caller_role)
        except ToolError as exc:
            message = str(exc)
            if message.startswith("tool_timeout"):
                code = "TOOL_TIMEOUT"
            elif "not authorized" in message or "allowlisted" in message:
                code = "TOOL_FORBIDDEN"
            else:
                code = "TOOL_FAILURE"
            return {"ok": False, "error_code": code,
                    "message": "Расчёт сейчас недоступен. Не придумывай значения; сообщи пользователю, что расчёт не выполнен."}
