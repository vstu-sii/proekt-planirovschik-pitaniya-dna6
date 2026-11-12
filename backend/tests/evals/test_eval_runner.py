import json
from pathlib import Path
from backend.tests.evals.evaluate import load_dataset, evaluate_case

def test_dataset_is_valid_and_safety_present():
    cases=load_dataset('docs/quality/golden-dataset/v1.jsonl')
    assert len(cases)==44
    assert any(c['safety_level']=='safety_critical' for c in cases)
    assert all(c['input'] and c['reference_answer'] for c in cases)

def test_missing_response_is_failure():
    case=load_dataset('docs/quality/golden-dataset/v1.jsonl')[0]
    assert evaluate_case(case,{'error':'missing'})['status']=='error'

def test_structured_contract():
    case=load_dataset('docs/quality/golden-dataset/v1.jsonl')[0]
    assert evaluate_case(case,{'text':'{"answer":"тест"}'})['structured_valid']
    assert not evaluate_case(case,{'text':'не JSON'})['structured_valid']
