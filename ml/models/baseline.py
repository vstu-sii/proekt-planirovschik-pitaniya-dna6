"""GigaChat baseline for Meal Planner MVP.

The LLM proposes a structured draft. Deterministic calculations/constraints must be
performed outside the LLM before a response is returned to a client.
"""
from __future__ import annotations

import json
import os
import re
import time
import uuid
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

from ml.tracing.tracer import trace_llm_call


# GigaChat-2 is the operational default used in the submitted Golden Dataset run.
# It replaced GigaChat-2-Lite after connection errors; override via GIGACHAT_MODEL.
MODEL_NAME = os.getenv("GIGACHAT_MODEL", "GigaChat-2")
TIMEOUT_SEC = float(os.getenv("GIGACHAT_TIMEOUT_SEC", "25"))
MAX_RETRIES = 1


class Ingredient(BaseModel):
    name: str = Field(min_length=1)
    amount_g: float = Field(ge=0)


class Meal(BaseModel):
    name: str = Field(min_length=1)
    meal_type: str
    ingredients: list[Ingredient] = Field(min_length=1)
    cook_time_min: float = Field(ge=0)


class DayPlan(BaseModel):
    day: int = Field(ge=1)
    meals: list[Meal] = Field(min_length=1)


class MealPlanDraft(BaseModel):
    days: list[DayPlan] = Field(min_length=1)
    notes: str = ""


SYSTEM_PROMPT = """Ты AI-модуль проекта «Планировщик питания».
Отвечай на русском языке.
Учитывай все ограничения пользователя одновременно.
Не выдумывай точную стоимость и КБЖУ: они рассчитываются программно.
Не используй запрещённые продукты.
Учитывай продукты pantry, если они переданы.
Не превышай max_cook_time_min.
Верни только JSON без Markdown:
{
  "days": [
    {
      "day": 1,
      "meals": [
        {
          "name": "...",
          "meal_type": "breakfast|lunch|dinner|snack",
          "ingredients": [{"name": "...", "amount_g": 100}],
          "cook_time_min": 20
        }
      ]
    }
  ],
  "notes": "..."
}
"""


@dataclass
class BaselineResult:
    request_id: str
    status: str
    draft: MealPlanDraft | None
    raw_text: str | None
    latency_sec: float
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    retry_count: int
    error: str | None = None


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.S)
        if not match:
            raise
        return json.loads(match.group(0))


def _usage(response: Any) -> tuple[int | None, int | None, int | None]:
    usage = getattr(response, "usage", None)
    if usage is None:
        return None, None, None
    return (
        getattr(usage, "prompt_tokens", None),
        getattr(usage, "completion_tokens", None),
        getattr(usage, "total_tokens", None),
    )


class GigaChatBaseline:
    def __init__(self, credentials: str | None = None):
        credentials = credentials or os.getenv("GIGACHAT_CREDENTIALS")
        if not credentials:
            raise RuntimeError("GIGACHAT_CREDENTIALS is not configured")
        self.client = GigaChat(
            credentials=credentials,
            model=MODEL_NAME,
            verify_ssl_certs=os.getenv("GIGACHAT_VERIFY_SSL", "false").lower() == "true",
        )

    @staticmethod
    def build_user_prompt(request: dict[str, Any]) -> str:
        return (
            "Сформируй структурированный черновик плана питания по входным данным.\n"
            f"{json.dumps(request, ensure_ascii=False, indent=2)}\n"
            "Все ограничения действуют одновременно."
        )

    def generate(self, request: dict[str, Any], request_id: str | None = None) -> BaselineResult:
        request_id = request_id or str(uuid.uuid4())
        user_prompt = self.build_user_prompt(request)
        last_error = None
        retry_count = 0
        started_all = time.perf_counter()

        for attempt in range(MAX_RETRIES + 1):
            started = time.perf_counter()
            try:
                response = self.client.chat(Chat(messages=[
                    Messages(role=MessagesRole.SYSTEM, content=SYSTEM_PROMPT),
                    Messages(role=MessagesRole.USER, content=user_prompt),
                ]))
                latency = time.perf_counter() - started
                # Extract only assistant message content; never stringify the SDK response.
                text = response.choices[0].message.content
                p, o, t = _usage(response)
                try:
                    draft = MealPlanDraft.model_validate(_extract_json(text))
                    validation_status = "valid"
                    validation_error = None
                except Exception as validation_exc:
                    validation_status = "invalid"
                    validation_error = str(validation_exc)
                    raise
                trace_llm_call(
                    request_id=request_id, model=MODEL_NAME, attempt=attempt + 1,
                    latency_sec=round(latency, 4), status="ok",
                    input_tokens=p, output_tokens=o, total_tokens=t,
                    prompt=user_prompt, response=text,
                    validation_status=validation_status,
                )
                return BaselineResult(
                    request_id=request_id,
                    status="ok",
                    draft=draft,
                    raw_text=text,
                    latency_sec=round(latency, 4),
                    input_tokens=p,
                    output_tokens=o,
                    total_tokens=t,
                    retry_count=retry_count,
                )
            except Exception as exc:
                last_error = str(exc)
                # Trace failures too; do not include credentials or request headers.
                try:
                    trace_llm_call(
                        request_id=request_id, model=MODEL_NAME, attempt=attempt + 1,
                        latency_sec=round(time.perf_counter() - started, 4),
                        status="error", error_type=type(exc).__name__,
                        error=str(exc)[:1000], prompt=user_prompt,
                        validation_status="failed_or_unavailable",
                    )
                except Exception:
                    # Observability failure must not mask the provider/validation error.
                    pass
                if attempt < MAX_RETRIES:
                    retry_count += 1
                    continue

        return BaselineResult(
            request_id=request_id,
            status="error",
            draft=None,
            raw_text=None,
            latency_sec=round(time.perf_counter() - started_all, 4),
            input_tokens=None,
            output_tokens=None,
            total_tokens=None,
            retry_count=retry_count,
            error=last_error,
        )
