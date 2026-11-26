import json
import os
import re
from dataclasses import dataclass
from typing import Any, Protocol

import httpx

from app.api.schemas import DayPlan, MealPlanRequest
from app.core.config import settings
from app.services.catalog import CATALOG


@dataclass(frozen=True)
class ProviderResult:
    days: list[DayPlan]
    retry_count: int
    provider: str


class MealPlanProvider(Protocol):
    def generate(self, request: MealPlanRequest, request_id: str) -> ProviderResult: ...


def demo_days(count: int, max_cook_time_min: int = 240) -> list[dict[str, Any]]:
    templates = [
        {
            "name": "Овсянка с яблоком",
            "meal_type": "breakfast",
            "cook_time_min": 10,
            "ingredients": [
                {"name": "Овсяные хлопья", "amount_g": 70},
                {"name": "Яблоко", "amount_g": 150},
                {"name": "Молоко", "amount_g": 150},
            ],
        },
        {
            "name": "Гречка с курицей",
            "meal_type": "lunch",
            "cook_time_min": 25,
            "ingredients": [
                {"name": "Гречка", "amount_g": 90},
                {"name": "Куриная грудка", "amount_g": 160},
                {"name": "Морковь", "amount_g": 80},
            ],
        },
        {
            "name": "Тёплый салат с фасолью",
            "meal_type": "dinner",
            "cook_time_min": 20,
            "ingredients": [
                {"name": "Фасоль консервированная", "amount_g": 180},
                {"name": "Помидор", "amount_g": 150},
                {"name": "Яйцо", "amount_g": 60},
            ],
        },
    ]
    adapted = [
        {**meal, "cook_time_min": min(meal["cook_time_min"], max_cook_time_min)}
        for meal in templates
    ]
    return [{"day": day, "meals": adapted} for day in range(1, count + 1)]


class DemoProvider:
    def generate(self, request: MealPlanRequest, request_id: str) -> ProviderResult:
        return ProviderResult(
            days=[
                DayPlan.model_validate(day)
                for day in demo_days(request.days, request.max_cook_time_min)
            ],
            retry_count=0,
            provider="demo",
        )


class HttpProvider:
    def generate(self, request: MealPlanRequest, request_id: str) -> ProviderResult:
        response = httpx.post(
            f"{settings.llm_base_url.rstrip('/')}/v1/generate",
            json={"request_id": request_id, **request.model_dump(mode="json")},
            timeout=settings.llm_timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        return ProviderResult(
            days=[DayPlan.model_validate(day) for day in payload["days"]],
            retry_count=int(payload.get("retry_count", 0)),
            provider="http-mock",
        )


class GigaChatProvider:
    """Adapted from the AI Engineer Lab 3 baseline with one corrective retry."""

    def generate(self, request: MealPlanRequest, request_id: str) -> ProviderResult:
        try:
            from gigachat import GigaChat
            from gigachat.models import Chat, Messages, MessagesRole
        except ImportError as exc:
            raise RuntimeError("GigaChat dependency is not installed") from exc

        credentials = os.getenv("GIGACHAT_CREDENTIALS")
        if not credentials:
            raise RuntimeError("GIGACHAT_CREDENTIALS is not configured")

        system = (
            "Ты модуль планировщика питания. Верни только JSON вида "
            '{"days":[{"day":1,"meals":[{"name":"...","meal_type":"breakfast|lunch|dinner|snack",'
            '"ingredients":[{"name":"...","amount_g":100}],"cook_time_min":20}]}]}. '
            f"Разрешённые продукты: {', '.join(item.name for item in CATALOG.values())}. "
            "Не выдумывай стоимость и КБЖУ: сервер рассчитает их сам."
        )
        client = GigaChat(
            credentials=credentials,
            model=os.getenv("GIGACHAT_MODEL", "GigaChat-2"),
            verify_ssl_certs=os.getenv("GIGACHAT_VERIFY_SSL", "false").lower() == "true",
        )
        last_error: Exception | None = None
        for attempt in range(2):
            try:
                response = client.chat(
                    Chat(
                        messages=[
                            Messages(role=MessagesRole.SYSTEM, content=system),
                            Messages(
                                role=MessagesRole.USER,
                                content=json.dumps(
                                    request.model_dump(mode="json"), ensure_ascii=False
                                ),
                            ),
                        ]
                    )
                )
                text = response.choices[0].message.content.strip()
                match = re.search(r"\{.*\}", text, flags=re.S)
                payload = json.loads(match.group(0) if match else text)
                return ProviderResult(
                    days=[DayPlan.model_validate(day) for day in payload["days"]],
                    retry_count=attempt,
                    provider="gigachat",
                )
            except Exception as exc:
                last_error = exc
        raise RuntimeError(f"GigaChat response validation failed: {last_error}")


def provider_from_settings() -> MealPlanProvider:
    if settings.ai_provider == "http":
        return HttpProvider()
    if settings.ai_provider == "gigachat":
        return GigaChatProvider()
    return DemoProvider()
