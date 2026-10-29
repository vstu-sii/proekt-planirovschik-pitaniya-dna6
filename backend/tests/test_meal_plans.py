from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.models import Base, Product
from app.db.session import get_db
from app.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, expire_on_commit=False)
Base.metadata.create_all(engine)


def override_db() -> Generator[Session, None, None]:
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


app.dependency_overrides[get_db] = override_db
client = TestClient(app)


def test_generate_and_read_persisted_plan() -> None:
    response = client.post(
        "/api/v1/ai/meal-plans",
        json={
            "profile": {"height_cm": 178, "weight_kg": 74},
            "goal": "поддержание веса",
            "budget": {"amount": 3500, "currency": "RUB"},
            "days": 1,
            "restrictions": [],
            "excluded_products": ["арахис"],
            "pantry": [
                {"name": "Гречка", "amount_g": 50},
                {"name": "Яйца", "amount_g": 360},
            ],
            "max_cook_time_min": 30,
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["validation"] == {
        "schema_valid": True,
        "constraints_valid": True,
        "retry_count": 0,
    }
    assert payload["totals"]["cost"] > 0
    assert payload["totals"]["target_calories_per_day"] == 2220
    assert payload["days"][0]["meals"]

    stored = client.get(f"/api/v1/meal-plans/{payload['request_id']}")
    assert stored.status_code == 200
    assert stored.json() == payload

    repeat = client.post(
        "/api/v1/ai/meal-plans",
        json={
            "profile": {"height_cm": 169, "weight_kg": 74},
            "goal": "снижение веса",
            "budget": {"amount": 3500, "currency": "RUB"},
            "days": 1,
            "restrictions": [],
            "excluded_products": [],
            "pantry": [{"name": "Яйца", "amount_g": 360}],
            "max_cook_time_min": 30,
        },
    )
    assert repeat.status_code == 200, repeat.text
    assert repeat.json()["totals"]["target_calories_per_day"] == 1887
    with TestingSession() as session:
        assert len(session.scalars(select(Product).where(Product.name == "Яйцо")).all()) == 1


def test_rejects_unknown_request_fields() -> None:
    response = client.post(
        "/api/v1/ai/meal-plans",
        json={
            "profile": {"height_cm": 178, "weight_kg": 74},
            "goal": "поддержание веса",
            "budget": {"amount": 3500, "currency": "RUB"},
            "days": 1,
            "restrictions": [],
            "excluded_products": [],
            "pantry": [],
            "max_cook_time_min": 30,
            "unexpected": "field",
        },
    )
    assert response.status_code == 422
