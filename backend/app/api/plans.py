import uuid
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import MealPlanRequest, MealPlanResponse
from app.db.session import get_db
from app.services.meal_plans import UnsafePlanError, generate_and_store, get_stored_plan

router = APIRouter(prefix="/api/v1", tags=["Meal Planning"])


@router.post("/ai/meal-plans", response_model=MealPlanResponse)
def generate_meal_plan(
    payload: MealPlanRequest, db: Annotated[Session, Depends(get_db)]
) -> MealPlanResponse:
    try:
        return generate_and_store(db, payload)
    except UnsafePlanError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="AI provider timeout") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="AI provider error") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/meal-plans/{plan_id}", response_model=MealPlanResponse)
def read_meal_plan(plan_id: uuid.UUID, db: Annotated[Session, Depends(get_db)]) -> MealPlanResponse:
    result = get_stored_plan(db, plan_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return result
