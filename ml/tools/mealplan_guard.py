"""Backend-side guard for draft contract and hard user constraints.

This is a conservative starter guard. Production allergen matching must use the
team's canonical product/allergen dictionary, not string matching alone.
"""
from __future__ import annotations
from typing import Any

REASONS = {"INVALID_CONTRACT", "DAY_COUNT_MISMATCH", "ALLERGEN_CONFLICT", "EXCLUDED_PRODUCT",
           "COOK_TIME_EXCEEDED", "DIET_CONFLICT", "MISSING_REQUIRED_INPUT", "UNSAFE_FOOD",
           "MVP_SCOPE_UNSUPPORTED", "TOOL_TIMEOUT", "TOOL_FAILURE"}

def validate_draft(draft: dict[str, Any], *, expected_days: int,
                   excluded_products: list[str] | None = None,
                   max_cook_time_min: float | None = None) -> dict[str, Any]:
    issues=[]
    if not isinstance(draft, dict) or not isinstance(draft.get("days"), list):
        return {"valid":False,"issues":[{"reason_code":"INVALID_CONTRACT","path":"days","message":"days must be a list"}]}
    days=draft["days"]
    if len(days)!=expected_days:
        issues.append({"reason_code":"DAY_COUNT_MISMATCH","path":"days","message":f"expected {expected_days} days, got {len(days)}"})
    excluded=[x.casefold().strip() for x in (excluded_products or []) if x.strip()]
    for di,day in enumerate(days):
        if not isinstance(day,dict) or not isinstance(day.get("meals"),list) or not day["meals"]:
            issues.append({"reason_code":"INVALID_CONTRACT","path":f"days[{di}].meals","message":"each day must contain meals"}); continue
        for mi,meal in enumerate(day["meals"]):
            path=f"days[{di}].meals[{mi}]"
            if not isinstance(meal,dict) or not isinstance(meal.get("ingredients"),list) or not meal["ingredients"]:
                issues.append({"reason_code":"INVALID_CONTRACT","path":path+".ingredients","message":"meal must contain ingredients"}); continue
            try: cook=float(meal.get("cook_time_min"))
            except (TypeError,ValueError): cook=None
            if cook is None or cook<0:
                issues.append({"reason_code":"INVALID_CONTRACT","path":path+".cook_time_min","message":"cook_time_min must be non-negative number"})
            elif max_cook_time_min is not None and cook>max_cook_time_min:
                issues.append({"reason_code":"COOK_TIME_EXCEEDED","path":path+".cook_time_min","message":f"{cook} exceeds {max_cook_time_min}"})
            for ii,ingredient in enumerate(meal["ingredients"]):
                name=str(ingredient.get("name","")).casefold().strip() if isinstance(ingredient,dict) else ""
                if not name:
                    issues.append({"reason_code":"INVALID_CONTRACT","path":path+f".ingredients[{ii}]","message":"ingredient name is required"}); continue
                if any(x in name for x in excluded):
                    issues.append({"reason_code":"EXCLUDED_PRODUCT","path":path+f".ingredients[{ii}]","message":"excluded product detected"})
    return {"valid":not issues,"issues":issues,"reason_codes":sorted({x["reason_code"] for x in issues})}
