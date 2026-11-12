import json
from pathlib import Path


def test_v2_regression_coverage():
    p = Path('docs/quality/golden-dataset/v2.jsonl')
    cases = [json.loads(s) for s in p.read_text(encoding='utf-8').splitlines() if s.strip()]
    assert len(cases) == 48
    assert len({c['id'] for c in cases}) == 48
    assert sum('received_semantic_review' in c.get('regression_groups', []) for c in cases) == 13
    assert sum('safety_regression' in c.get('regression_groups', []) for c in cases) == 16
    assert sum('structural_edge_regression' in c.get('regression_groups', []) for c in cases) == 7
    assert sum('product_vo_review' in c for c in cases) == 11
    assert sum('candidate_new_case_not_yet_run' in c.get('regression_groups', []) for c in cases) == 4
    assert all(c.get('input') and c.get('reference_answer') for c in cases)
