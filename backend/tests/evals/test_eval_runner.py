
from pathlib import Path

from backend.tests.evals.evaluate import evaluate_case, load_dataset

ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "docs/quality/golden-dataset/v1.jsonl"


def test_dataset_is_valid_and_safety_present():
    cases = load_dataset(str(DATASET))

    assert len(cases) == 44
    assert any(c["safety_level"] == "safety_critical" for c in cases)
    assert all(c["input"] and c["reference_answer"] for c in cases)


def test_missing_response_is_failure():
    case = load_dataset(str(DATASET))[0]
    result = evaluate_case(case, {"error": "missing"})

    assert result["status"] == "error"


def test_structured_contract():
    case = load_dataset(str(DATASET))[0]

    valid_result = evaluate_case(case, {"text": '{"answer":"тест"}'})
    invalid_result = evaluate_case(case, {"text": "не JSON"})

    assert valid_result["structured_valid"]
    assert not invalid_result["structured_valid"]

