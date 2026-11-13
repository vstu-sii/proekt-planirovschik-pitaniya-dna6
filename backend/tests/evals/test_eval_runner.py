from pathlib import Path

from backend.tests.evals.evaluate import (
    evaluate_case,
    load_dataset,
)


ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "docs/quality/golden-dataset/v1.jsonl"


def test_dataset_is_valid_and_safety_present():
    cases = load_dataset(str(DATASET))

    assert len(cases) == 44
    assert any(case.get("safety_critical") for case in cases)


def test_missing_response_is_failure():
    case = load_dataset(str(DATASET))[0]

    result = evaluate_case(case, None)

    assert not result["passed"]


def test_structured_contract():
    case = load_dataset(str(DATASET))[0]

    result = evaluate_case(case, {})

    assert not result["passed"]
