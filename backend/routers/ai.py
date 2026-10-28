"""AI API router for the prototype.

The LLM produces a draft only. Cost/nutrition and constraint checks must be
provided by deterministic services before this response is treated as final.
"""
from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from ml.models.baseline import GigaChatBaseline

router = APIRouter(prefix="/api/v1/ai", tags=["AI Meal Planning"])


class MealPlanRequest(BaseModel):
    goal: str | None = None
    budget: dict[str, Any] | None = None
    duration_days: int | None = Field(default=None, ge=1, le=31)
    restrictions: list[str] = Field(default_factory=list)
    excluded_products: list[str] = Field(default_factory=list)
    pantry: list[str] = Field(default_factory=list)
    max_cooking_time_min: int | None = Field(default=None, ge=1, le=1440)

    model_config = {"extra": "allow"}


@router.post("/meal-plans")
async def generate_meal_plan(payload: MealPlanRequest):
    request_id = str(uuid.uuid4())
    request_data = payload.model_dump(exclude_none=True)

    try:
        baseline = GigaChatBaseline()
        result = await run_in_threadpool(
            baseline.generate, request_data, request_id=request_id
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail={
            "error": "service_unavailable",
            "message": str(exc),
            "request_id": request_id,
        }) from exc

    if result.status != "ok" or result.draft is None:
        raise HTTPException(status_code=502, detail={
            "error": "provider_or_validation_error",
            "message": result.error or "AI provider/validation error",
            "request_id": request_id,
        })

    # Deliberately null until deterministic catalog/calculation services are wired in.
    # Do not interpret null as zero or as a successful constraints check.
    return {
        "request_id": request_id,
        "days": [day.model_dump() for day in result.draft.days],
        "shopping_list": [],
        "totals": {
            "cost": None,
            "currency": (payload.budget or {}).get("currency"),
            "calories": None,
            "protein_g": None,
            "fat_g": None,
            "carbs_g": None,
        },
        "validation": {
            "schema_valid": True,
            "constraints_valid": None,
            "retry_count": result.retry_count,
        },
        "status": "draft_requires_deterministic_validation",
    }
