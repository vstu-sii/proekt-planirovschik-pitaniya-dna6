"""Append a documented incident to the active golden dataset (v4)."""
import argparse
import json
from pathlib import Path


DEFAULT_DATASET = Path('docs/quality/golden-dataset/v4.jsonl')
TEXT_FIELDS = ('id', 'input', 'reference_answer', 'source_reference', 'source_type')
LIST_FIELDS = ('must_contain', 'must_not_contain', 'constraints')


def append_case(case_path: Path, target: Path = DEFAULT_DATASET) -> str:
    case = json.loads(case_path.read_text(encoding='utf-8-sig'))
    if not isinstance(case, dict):
        raise ValueError('Incident must be a JSON object')
    for field in TEXT_FIELDS:
        if not isinstance(case.get(field), str) or not case[field].strip():
            raise ValueError(f'Missing or invalid field: {field}')
    for field in LIST_FIELDS:
        if not isinstance(case.get(field), list) or not all(
            isinstance(x, str) and x.strip() for x in case[field]
        ):
            raise ValueError(f'Expected a list of nonempty strings: {field}')
    if not case['constraints']:
        raise ValueError('At least one acceptance constraint is required')
    if case.get('safety_level') not in {'normal', 'safety_critical'}:
        raise ValueError('Invalid safety_level')
    if case.get('mvp_scope') not in {
        'in_scope_reference', 'in_scope_regression', 'cut_historical_reference'
    }:
        raise ValueError('Invalid mvp_scope')
    if not isinstance(case.get('evaluation_kind'), str) or not case['evaluation_kind'].strip():
        raise ValueError('Missing evaluation_kind')
    if case.get('criteria_mode') != 'semantic':
        raise ValueError('v4 requires semantic criteria')
    raw = target.read_bytes()
    existing = [json.loads(line) for line in raw.decode('utf-8-sig').splitlines() if line.strip()]
    ids = [row['id'] for row in existing]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError('Existing dataset is empty or contains duplicate IDs')
    if case['id'] in ids:
        raise ValueError(f"Duplicate ID: {case['id']}")
    versions = {row.get('version') for row in existing}
    if len(versions) != 1 or None in versions:
        raise ValueError('Dataset revision is inconsistent')
    case['version'] = next(iter(versions))
    case['human_review_status'] = 'pending'
    case['human_review_owner'] = 'Quality & Safety'
    for field in ('semantic_review_status', 'safety_review_status', 'product_vo_review'):
        case.pop(field, None)
    record = json.dumps(case, ensure_ascii=False, allow_nan=False).encode('utf-8') + b'\n'
    with target.open('ab') as output:
        if raw and not raw.endswith(b'\n'):
            output.write(b'\n')
        output.write(record)
    return case['id']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('case', type=Path)
    parser.add_argument('--dataset', type=Path, default=DEFAULT_DATASET)
    args = parser.parse_args()
    try:
        case_id = append_case(args.case, args.dataset)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f'Regression not added: {exc}\n')
    print(f'Added {case_id} to {args.dataset}; human review pending')


if __name__ == '__main__':
    main()
