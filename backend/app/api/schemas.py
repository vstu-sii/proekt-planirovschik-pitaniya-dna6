import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Budget(BaseModel):
    model_config = ConfigDict(extra="forbid")
    amount: float = Field(gt=0)
    currency: str = Field(pattern=r"^[A-Z]{3}$")


class PantryItemInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    amount_g: float = Field(gt=0)


class UserProfileInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    height_cm: int = Field(ge=120, le=230)
    weight_kg: float = Field(ge=35, le=250)


class MealPlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    profile: UserProfileInput
    goal: str = Field(min_length=1, max_length=200)
    budget: Budget
    days: int = Field(ge=1, le=14)
    restrictions: list[str] = Field(default_factory=list, max_length=20)
    excluded_products: list[str] = Field(default_factory=list, max_length=50)
    pantry: list[PantryItemInput] = Field(default_factory=list, max_length=100)
    max_cook_time_min: int = Field(ge=1, le=240)


class Ingredient(BaseModel):
    name: str
    amount_g: float = Field(gt=0)


class Meal(BaseModel):
    name: str
    meal_type: Literal["breakfast", "lunch", "dinner", "snack"]
    ingredients: list[Ingredient] = Field(min_length=1)
    cook_time_min: int = Field(ge=0)


class DayPlan(BaseModel):
    day: int = Field(ge=1)
    meals: list[Meal] = Field(min_length=1)


class ShoppingItem(BaseModel):
    name: str
    amount_g: float = Field(ge=0)
    estimated_cost: float = Field(ge=0)


class PlanTotals(BaseModel):
    cost: float = Field(ge=0)
    currency: str
    calories: float = Field(ge=0)
    protein_g: float = Field(ge=0)
    fat_g: float = Field(ge=0)
    carbs_g: float = Field(ge=0)
    target_calories_per_day: float = Field(gt=0)


class ValidationSummary(BaseModel):
    schema_valid: bool
    constraints_valid: bool
    retry_count: int = Field(ge=0, le=1)


class MealPlanResponse(BaseModel):
    request_id: uuid.UUID
    days: list[DayPlan]
    shopping_list: list[ShoppingItem]
    totals: PlanTotals
    validation: ValidationSummary
