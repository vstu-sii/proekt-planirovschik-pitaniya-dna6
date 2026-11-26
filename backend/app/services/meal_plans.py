import uuid
from collections import defaultdict
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import (
    MealPlanRequest,
    MealPlanResponse,
    PlanTotals,
    ShoppingItem,
    ValidationSummary,
)
from app.db.models import (
    DayPlan as DayPlanModel,
)
from app.db.models import (
    DietaryRestriction,
    MealIngredient,
    MealPlan,
    MealPlanResult,
    PantryItem,
    Product,
    ShoppingListItem,
    User,
)
from app.db.models import (
    Meal as MealModel,
)
from app.observability.tracing import emit_trace
from app.services.catalog import ALIASES, product_facts
from app.services.providers import provider_from_settings


class UnsafePlanError(ValueError):
    pass


def _target_calories(request: MealPlanRequest) -> float:
    """Simple MVP estimate; not a medical recommendation."""
    goal = request.goal.lower()
    multiplier = 0.85 if "сниж" in goal else 1.15 if "набор" in goal else 1.0
    return round(request.profile.weight_kg * 30 * multiplier, 0)


def _blocked_terms(request: MealPlanRequest) -> set[str]:
    blocked = {item.strip().lower() for item in request.excluded_products}
    for restriction in request.restrictions:
        lowered = restriction.strip().lower()
        if lowered.startswith("без "):
            blocked.add(lowered.removeprefix("без ").strip())
    return {ALIASES.get(term, term) for term in blocked if term}


def generate_and_store(db: Session, request: MealPlanRequest) -> MealPlanResponse:
    request_id = uuid.uuid4()
    target_calories = _target_calories(request)
    emit_trace(
        str(request_id),
        "generation.started",
        days=request.days,
        target_calories_per_day=target_calories,
    )
    try:
        for item in request.pantry:
            try:
                product_facts(item.name)
            except ValueError as exc:
                raise UnsafePlanError(
                    "Недопустимый продукт в запасах"
                ) from exc
        provider_result = provider_from_settings().generate(request, str(request_id))
        emit_trace(
            str(request_id),
            "provider.completed",
            provider=provider_result.provider,
            retry_count=provider_result.retry_count,
        )
        if [day.day for day in provider_result.days] != list(range(1, request.days + 1)):
            raise UnsafePlanError("AI вернул неверное количество дней")

        blocked = _blocked_terms(request)
        pantry_left: dict[str, float] = defaultdict(float)
        for item in request.pantry:
            pantry_left[product_facts(item.name).name.lower()] += item.amount_g
        shopping_amounts: dict[str, float] = defaultdict(float)
        nutrition = defaultdict(float)
        total_cost = 0.0

        for day in provider_result.days:
            for meal in day.meals:
                if meal.cook_time_min > request.max_cook_time_min:
                    raise UnsafePlanError("Превышено время приготовления")
                for ingredient in meal.ingredients:
                    lowered = ingredient.name.strip().lower()
                    lowered = ALIASES.get(lowered, lowered)
                    if any(term in lowered for term in blocked):
                        raise UnsafePlanError("Обнаружен запрещённый продукт")
                    try:
                        facts = product_facts(ingredient.name)
                    except ValueError as exc:
                        raise UnsafePlanError("Продукт вне проверенного каталога") from exc
                    ratio = ingredient.amount_g / 100
                    nutrition["calories"] += facts.calories * ratio
                    nutrition["protein_g"] += facts.protein * ratio
                    nutrition["fat_g"] += facts.fat * ratio
                    nutrition["carbs_g"] += facts.carbs * ratio
                    available = pantry_left.get(lowered, 0)
                    required = max(0.0, ingredient.amount_g - available)
                    pantry_left[lowered] = max(0.0, available - ingredient.amount_g)
                    shopping_amounts[ingredient.name] += required

        shopping_list = []
        for name, amount in shopping_amounts.items():
            facts = product_facts(name)
            cost = amount / 1000 * facts.price_per_kg
            total_cost += cost
            if amount > 0:
                shopping_list.append(
                    ShoppingItem(
                        name=name,
                        amount_g=round(amount, 2),
                        estimated_cost=round(cost, 2),
                    )
                )

        if total_cost > request.budget.amount:
            raise UnsafePlanError("План превышает заданный бюджет")

        response = MealPlanResponse(
            request_id=request_id,
            days=provider_result.days,
            shopping_list=shopping_list,
            totals=PlanTotals(
                cost=round(total_cost, 2),
                currency=request.budget.currency,
                calories=round(nutrition["calories"], 2),
                protein_g=round(nutrition["protein_g"], 2),
                fat_g=round(nutrition["fat_g"], 2),
                carbs_g=round(nutrition["carbs_g"], 2),
                target_calories_per_day=target_calories,
            ),
            validation=ValidationSummary(
                schema_valid=True,
                constraints_valid=True,
                retry_count=provider_result.retry_count,
            ),
        )
        _persist(db, request, response)
        emit_trace(str(request_id), "generation.persisted", total_cost=round(total_cost, 2))
        return response
    except Exception as exc:
        db.rollback()
        emit_trace(str(request_id), "generation.failed", error_type=type(exc).__name__)
        raise


def _get_or_create_product(db: Session, name: str) -> Product:
    facts = product_facts(name)
    product = db.scalar(select(Product).where(Product.name == facts.name))
    if product:
        return product
    product = Product(
        name=facts.name,
        price_per_kg=Decimal(str(facts.price_per_kg)),
        calories_per_100g=Decimal(str(facts.calories)),
        protein_per_100g=Decimal(str(facts.protein)),
        fat_per_100g=Decimal(str(facts.fat)),
        carbs_per_100g=Decimal(str(facts.carbs)),
    )
    db.add(product)
    db.flush()
    return product


def _persist(db: Session, request: MealPlanRequest, response: MealPlanResponse) -> None:
    user = db.scalar(select(User).where(User.email == "demo@meal-planner.local"))
    if user is None:
        user = User(email="demo@meal-planner.local")
        db.add(user)
        db.flush()
    user.height_cm = request.profile.height_cm
    user.weight_kg = Decimal(str(request.profile.weight_kg))

    plan = MealPlan(
        id=response.request_id,
        user_id=user.id,
        goal=request.goal,
        budget_amount=Decimal(str(request.budget.amount)),
        budget_currency=request.budget.currency,
        days_count=request.days,
        max_cook_time_min=request.max_cook_time_min,
        status="ready",
    )
    db.add(plan)
    # Persist the parent before inserting days that reference its UUID.
    db.flush()
    for restriction in [*request.restrictions, *request.excluded_products]:
        db.add(
            DietaryRestriction(
                user_id=user.id,
                name=restriction,
                restriction_type="excluded"
                if restriction in request.excluded_products
                else "dietary",
            )
        )
    for item in request.pantry:
        product = _get_or_create_product(db, item.name)
        db.add(PantryItem(user_id=user.id, product_id=product.id, amount_g=item.amount_g))
    for day in response.days:
        day_model = DayPlanModel(plan_id=plan.id, day_number=day.day)
        db.add(day_model)
        db.flush()
        for meal in day.meals:
            meal_model = MealModel(
                day_plan_id=day_model.id,
                name=meal.name,
                meal_type=meal.meal_type,
                cook_time_min=meal.cook_time_min,
            )
            db.add(meal_model)
            db.flush()
            for ingredient in meal.ingredients:
                product = _get_or_create_product(db, ingredient.name)
                db.add(
                    MealIngredient(
                        meal_id=meal_model.id,
                        product_id=product.id,
                        amount_g=ingredient.amount_g,
                    )
                )
    for item in response.shopping_list:
        product = _get_or_create_product(db, item.name)
        db.add(
            ShoppingListItem(
                plan_id=plan.id,
                product_id=product.id,
                amount_g=item.amount_g,
                estimated_cost=item.estimated_cost,
            )
        )
    db.add(MealPlanResult(plan_id=plan.id, payload=response.model_dump(mode="json")))
    db.commit()


def get_stored_plan(db: Session, plan_id: uuid.UUID) -> MealPlanResponse | None:
    stored = db.get(MealPlanResult, plan_id)
    return MealPlanResponse.model_validate(stored.payload) if stored else None
