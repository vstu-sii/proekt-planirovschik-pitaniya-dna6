"""Read-only deterministic nutrition/cost calculator over a trusted local catalog."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping, Any


@dataclass(frozen=True)
class Product:
    product_id: str
    name: str
    kcal_per_100g: float
    protein_g_per_100g: float
    fat_g_per_100g: float
    carbs_g_per_100g: float
    price_per_kg: float | None = None
    currency: str = "RUB"
    allergens: tuple[str, ...] = ()


class CatalogError(ValueError):
    pass


class NutritionCatalog:
    """Catalog is injected by backend; model cannot write or add products to it."""
    def __init__(self, products: Mapping[str, Product]):
        self._products = dict(products)

    def calculate(self, ingredients: list[dict[str, Any]], *, max_ingredients: int = 100) -> dict[str, Any]:
        if not isinstance(ingredients, list) or not ingredients:
            raise CatalogError("ingredients must be a non-empty list")
        if len(ingredients) > max_ingredients:
            raise CatalogError("too many ingredients")
        totals = {"kcal": 0.0, "protein_g": 0.0, "fat_g": 0.0, "carbs_g": 0.0}
        cost = 0.0
        priced = True
        currency = None
        normalized = []
        for item in ingredients:
            if not isinstance(item, dict):
                raise CatalogError("ingredient must be an object")
            pid = item.get("product_id")
            grams = item.get("amount_g")
            if pid not in self._products:
                raise CatalogError(f"unknown product_id: {pid}")
            if isinstance(grams, bool) or not isinstance(grams, (int, float)) or not 0 < grams <= 5000:
                raise CatalogError("amount_g must be >0 and <=5000")
            p = self._products[pid]
            factor = float(grams) / 100.0
            for key, attr in (("kcal", "kcal_per_100g"), ("protein_g", "protein_g_per_100g"),
                              ("fat_g", "fat_g_per_100g"), ("carbs_g", "carbs_g_per_100g")):
                value = getattr(p, attr)
                if value < 0:
                    raise CatalogError(f"negative catalog value: {attr}")
                totals[key] += value * factor
            if p.price_per_kg is None:
                priced = False
            else:
                if currency is not None and currency != p.currency:
                    raise CatalogError("mixed currencies in one calculation")
                currency = p.currency
                cost += p.price_per_kg * float(grams) / 1000.0
            normalized.append({"product_id": pid, "name": p.name, "amount_g": float(grams), "allergens": list(p.allergens)})
        return {"ingredients": normalized, "totals": {k: round(v, 2) for k, v in totals.items()},
                "cost": round(cost, 2) if priced else None, "currency": currency if priced else None,
                "price_status": "catalog_price" if priced else "missing_catalog_price"}
