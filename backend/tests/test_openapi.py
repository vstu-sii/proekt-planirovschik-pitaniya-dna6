from pathlib import Path

import yaml
from openapi_spec_validator import validate


def test_openapi_contract_is_valid() -> None:
    contract_path = Path(__file__).parents[2] / "api" / "openapi.yaml"
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    validate(contract)
    assert "/api/v1/ai/meal-plans" in contract["paths"]
    assert "/api/v1/meal-plans/{plan_id}" in contract["paths"]
