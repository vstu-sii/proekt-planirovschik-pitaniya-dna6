from dataclasses import dataclass


@dataclass(frozen=True)
class ProductFacts:
    name: str
    price_per_kg: float
    calories: float
    protein: float
    fat: float
    carbs: float


CATALOG = {
    item.name.lower(): item
    for item in (
        ProductFacts("Овсяные хлопья", 130, 352, 12.3, 6.1, 59.5),
        ProductFacts("Яблоко", 150, 47, 0.4, 0.4, 9.8),
        ProductFacts("Молоко", 95, 52, 2.8, 2.5, 4.7),
        ProductFacts("Гречка", 160, 308, 12.6, 3.3, 57.1),
        ProductFacts("Куриная грудка", 410, 165, 31.0, 3.6, 0.0),
        ProductFacts("Морковь", 70, 35, 1.3, 0.1, 6.9),
        ProductFacts("Фасоль консервированная", 220, 99, 6.7, 0.3, 17.4),
        ProductFacts("Помидор", 230, 18, 0.9, 0.2, 2.7),
        ProductFacts("Яйцо", 140, 157, 12.7, 11.5, 0.7),
        ProductFacts("Рис", 150, 344, 6.7, 0.7, 78.9),
    )
}

ALIASES = {
    "яйца": "яйцо",
}


def product_facts(name: str) -> ProductFacts:
    key = name.strip().lower()
    key = ALIASES.get(key, key)
    try:
        return CATALOG[key]
    except KeyError as exc:
        raise ValueError(f"Продукт отсутствует в проверенном каталоге: {name}") from exc
