from pathlib import Path

from backend.tests.evals.analyze_results import summarize


ROOT = Path(__file__).resolve().parents[3]


def test_real_baseline_summary():
    summary = summarize(
        str(ROOT / "docs/quality/golden-dataset/v1.jsonl"),
        str(ROOT / "backend/tests/evals/results/baseline-full-v1.jsonl"),
    )

    assert summary["total"] == 44
    assert summary["received"] == 13
    assert summary["errors"] == 31

