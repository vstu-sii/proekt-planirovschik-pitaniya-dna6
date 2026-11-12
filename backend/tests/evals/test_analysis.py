
from backend.tests.evals.analyze_results import summarize


def test_real_baseline_summary():
    summary = summarize(
        "docs/quality/golden-dataset/v1.jsonl",
        "backend/tests/evals/results/baseline-full-v1.jsonl",
    )

    assert summary["total"] == 44
    assert summary["received"] == 13
    assert summary["errors"] == 31
