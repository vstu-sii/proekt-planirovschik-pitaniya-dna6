from app.db.models import Base


def test_expected_tables_are_registered() -> None:
    assert set(Base.metadata.tables) == {
        "users",
        "dietary_restrictions",
        "products",
        "pantry_items",
        "meal_plans",
        "day_plans",
        "meals",
        "meal_ingredients",
        "shopping_list_items",
        "meal_plan_results",
    }
