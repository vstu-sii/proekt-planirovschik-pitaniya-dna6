import json
from backend.tests.evals.analyze_results import summarize

def test_real_baseline_summary():
    s = summarize("docs/quality/golden-dataset/v1.jsonl", "backend/tests/evals/results/baseline-full-v1.jsonl")
    assert s["total"] == 44
    assert s["received"] == 13
    assert s["errors"] == 31
    assert s["structured_valid"] == 13
    assert s["critical_total"] == 16
    assert s["critical_received"] == 2
    assert s["critical_safety_compliance"] is None
