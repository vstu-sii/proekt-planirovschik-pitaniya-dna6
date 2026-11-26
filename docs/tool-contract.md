# Tool contract: `nutrition.calculate`

## Purpose

Детерминированно рассчитывает пищевую ценность и ориентировочную стоимость ингредиентов по доверенному локальному каталогу. Tool read-only: не меняет продукты, профиль, меню или список покупок.

## Input

```json
{
  "ingredients": [
    {"product_id": "rice_001", "amount_g": 70},
    {"product_id": "chicken_001", "amount_g": 150}
  ]
}
```

Rules: `ingredients` is a non-empty list, maximum 100 entries; each `product_id` must exist in backend catalog; `amount_g` must be numeric, >0 and ≤5000. Unknown product IDs are rejected. Catalog price must have one currency per calculation.

## Output

```json
{
  "ingredients": [{"product_id":"rice_001","name":"Рис","amount_g":70,"allergens":[]}],
  "totals": {"kcal":252,"protein_g":4.9,"fat_g":0.7,"carbs_g":56},
  "cost": 8.4,
  "currency": "RUB",
  "price_status": "catalog_price"
}
```

If one or more prices are missing, `cost` and `currency` return `null`, with `price_status=missing_catalog_price`; no price is invented. Values are catalog estimates per 100 g multiplied by amount/100. The backend should aggregate per meal/day/plan after validating the draft.

## Timeout and failure

Runtime timeout is configurable but clamped to 50 ms–10 s; default 2 s. `call()` raises a typed `tool_timeout`; `call_or_fallback()` returns `{ok:false,error_code:TOOL_TIMEOUT,message:...}` so the model/backend can explain that calculation is unavailable. It explicitly instructs not to invent values. Validation/catalog errors return a typed failure; no fallback to LLM arithmetic.

## Authorization

Only `ai_model` and `backend` callers may request the allowlisted tool. The allowlist is checked in Python, not only in the prompt. Tool has no database write method, filesystem access, network access, or arbitrary code execution. Production adapter must derive the catalog from backend-owned data and enforce user/profile ownership before invocation.

## Security caveat

String-based `excluded_products` matching is only a guardrail. Production allergen and diet checks must use the canonical allergen/diet mapping in the shared backend catalog (BUG-022), with aliases and cross-contamination policy reviewed by Quality. This prototype does not certify food safety.
