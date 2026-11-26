import asyncio
import os
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault('DATABASE_URL', 'sqlite://')
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'backend'))
from app.main import app
from app.db.session import get_db
from app.db.models import Base, MealPlanResult
from app.services import meal_plans
from app.services.providers import DemoProvider, ProviderResult
from app.api.schemas import DayPlan
from ml.tools.tool_runtime import ToolRuntime


@pytest.fixture
def api(monkeypatch):
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)
    def db():
        with session() as s:
            yield s
    previous = dict(app.dependency_overrides)
    app.dependency_overrides[get_db] = db
    monkeypatch.setattr(meal_plans, 'provider_from_settings', lambda: DemoProvider())
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client, session
    app.dependency_overrides.clear(); app.dependency_overrides.update(previous)
    engine.dispose()


def payload():
    return {'profile': {'height_cm': 178, 'weight_kg': 74}, 'goal': 'поддержание веса',
            'budget': {'amount': 3500, 'currency': 'RUB'}, 'days': 1, 'restrictions': [],
            'excluded_products': [], 'pantry': [], 'max_cook_time_min': 30}


def inject(monkeypatch, name='Рис', day=1, cook=10, error=None):
    def generate(*args):
        if error: raise error
        return ProviderResult([DayPlan.model_validate({'day': day, 'meals': [{'name': 'Блюдо',
            'meal_type': 'lunch', 'cook_time_min': cook, 'ingredients': [{'name': name, 'amount_g': 100}]}]})], 0, 'test')
    monkeypatch.setattr(meal_plans, 'provider_from_settings', lambda: SimpleNamespace(generate=generate))


def rejected(api, data, status=422):
    client, session = api
    response = client.post('/api/v1/ai/meal-plans', json=data)
    assert response.status_code == status, response.status_code
    with session() as s:
        assert s.scalar(select(func.count()).select_from(MealPlanResult)) == 0
    return response


@pytest.mark.parametrize('days', [1, 3, 7])
def test_uc3_persist(api, days):
    client, _ = api; data = payload(); data['days'] = days
    response = client.post('/api/v1/ai/meal-plans', json=data)
    assert response.status_code == 200, response.text
    body = response.json(); assert len(body['days']) == days
    assert client.get('/api/v1/meal-plans/' + body['request_id']).json() == body


@pytest.mark.parametrize('field,value', [('days', 15), ('goal', 'x'*201), ('pantry', [{'name':'x'*101,'amount_g':1}]), ('excluded_products', ['x']*51)])
def test_input_limits(api, field, value):
    data = payload(); data[field] = value; rejected(api, data)


def test_sec_budget(api, monkeypatch):
    inject(monkeypatch); data = payload(); data['budget']['amount'] = 1; rejected(api, data)


def test_sec_exclusion(api, monkeypatch):
    inject(monkeypatch, 'Молоко'); data = payload(); data['excluded_products'] = ['молоко']; rejected(api, data)


def test_sec_alias(api, monkeypatch):
    inject(monkeypatch, 'Яйцо'); data = payload(); data['excluded_products'] = ['яйца']; rejected(api, data)


def test_sec_day_index(api, monkeypatch):
    inject(monkeypatch, day=2); rejected(api, payload())


def test_sec_unknown_product(api, monkeypatch):
    inject(monkeypatch, 'Тестовый неизвестный продукт'); rejected(api, payload())


def test_sec_time(api, monkeypatch):
    inject(monkeypatch, cook=31); rejected(api, payload())


def test_sec_secret_error(api, monkeypatch):
    inject(monkeypatch, error=RuntimeError('SYNTHETIC_SECRET_123'))
    response = rejected(api, payload(), 503)
    assert 'SYNTHETIC_SECRET_123' not in response.text


def test_sec_timeout(api, monkeypatch):
    inject(monkeypatch, error=httpx.ReadTimeout('test')); rejected(api, payload(), 504)


def test_sec_validation_echo(api):
    data = payload(); data['goal'] = 'SYNTHETIC_SECRET_123'*20
    response = rejected(api, data); assert 'SYNTHETIC_SECRET_123' not in response.text


@pytest.mark.parametrize('name,role', [('db.write','ai_model'), ('nutrition.calculate','guest')])
def test_sec_tool_rights(name, role):
    called = []
    runtime = ToolRuntime({'nutrition.calculate': lambda args: called.append(args)})
    result = asyncio.run(runtime.call_or_fallback(name, {}, caller_role=role))
    assert result['error_code'] == 'TOOL_FORBIDDEN' and not called


def test_sec_tool_timeout():
    runtime = ToolRuntime({'nutrition.calculate': lambda args: time.sleep(.1)}, timeout_sec=.05)
    result = asyncio.run(runtime.call_or_fallback('nutrition.calculate', {}, caller_role='ai_model'))
    assert result['error_code'] == 'TOOL_TIMEOUT' and 'result' not in result


# ============================================================
# Lab 4 — Additional critical path integration tests
# ============================================================

@pytest.mark.parametrize(
    "field,value",
    [
        # UC1 — границы параметров профиля
        ("profile.height_cm", 119),
        ("profile.height_cm", 231),
        ("profile.weight_kg", 34),
        ("profile.weight_kg", 251),

        # UC1 — бюджет и валюта
        ("budget.amount", 0),
        ("budget.amount", -100),
        ("budget.currency", "rub"),

        # UC3 — обязательные параметры генерации
        ("days", 0),
        ("goal", ""),
        ("restrictions", ["test"] * 21),

        # UC2 — ограничения запасов
        ("pantry", [
            {"name": "Рис", "amount_g": 100}
            for _ in range(101)
        ]),
        ("pantry", [
            {"name": "", "amount_g": 100}
        ]),
        ("pantry", [
            {"name": "Рис", "amount_g": 0}
        ]),
        ("pantry", [
            {"name": "Рис", "amount_g": -100}
        ]),

        # UC3 — границы времени приготовления
        ("max_cook_time_min", 0),
        ("max_cook_time_min", 241),
    ],
)
def test_critical_input_boundaries(api, monkeypatch, field, value):
    """Invalid input must be rejected before provider invocation."""

    calls = []

    def forbidden_provider():
        calls.append("called")
        raise AssertionError("Provider must not be called")

    monkeypatch.setattr(
        meal_plans,
        "provider_from_settings",
        forbidden_provider,
    )

    data = payload()

    if "." in field:
        parent, child = field.split(".", 1)
        data[parent][child] = value
    else:
        data[field] = value

    rejected(api, data)

    assert not calls


def test_uc2_unknown_pantry_product(api, monkeypatch):
    """Unknown pantry products must be rejected before AI calls."""

    calls = []

    def forbidden_provider():
        calls.append("called")
        raise AssertionError("Provider must not be called")

    monkeypatch.setattr(
        meal_plans,
        "provider_from_settings",
        forbidden_provider,
    )

    data = payload()
    data["pantry"] = [
        {
            "name": "Тестовый неизвестный продукт",
            "amount_g": 100,
        }
    ]

    response = rejected(api, data)

    assert "Недопустимый продукт в запасах" in response.text
    assert not calls


def test_recovery_after_provider_failure(api, monkeypatch):
    """A failed generation must not prevent subsequent requests."""

    inject(
        monkeypatch,
        error=RuntimeError("SYNTHETIC_PROVIDER_FAILURE"),
    )

    # Первый запрос: провайдер недоступен.
    response = rejected(api, payload(), 503)

    assert "SYNTHETIC_PROVIDER_FAILURE" not in response.text

    # Восстановление провайдера.
    monkeypatch.setattr(
        meal_plans,
        "provider_from_settings",
        lambda: DemoProvider(),
    )

    client, session = api

    # Повторный запрос должен завершиться успешно.
    response = client.post(
        "/api/v1/ai/meal-plans",
        json=payload(),
    )

    assert response.status_code == 200, response.text

    body = response.json()

    # Проверка доступности сохранённого результата.
    stored = client.get(
        "/api/v1/meal-plans/" + body["request_id"]
    )

    assert stored.status_code == 200
    assert stored.json() == body

    # Сохранён только один успешный результат.
    with session() as s:
        assert s.scalar(
            select(func.count()).select_from(MealPlanResult)
        ) == 1

