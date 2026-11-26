"""Synthetic tests of the merge decision. No network or human approvals are created."""
import hashlib

import pytest

from quality_lab4.live import assess, digest, payload


def fixture():
    cases = [{'id': str(i), 'safety_level': 'safety_critical' if i < 23 else 'normal',
              'must_contain': [], 'must_not_contain': []} for i in range(54)]
    manifest = {'test_only': True}
    answer = '{"answer":"synthetic test only","assumptions":[],"warnings":[]}'
    rows = [{'id': c['id'], 'answer': answer, 'answer_sha256': hashlib.sha256(answer.encode()).hexdigest()} for c in cases]
    report = {'manifest': manifest, 'rows': rows}
    report['run_sha256'] = digest(payload(report))
    # These approvals are synthetic fixtures only, never written to a project decisions file.
    review = {'run_sha256': report['run_sha256'], 'decisions': {
        r['id']: {'answer_sha256': r['answer_sha256'], 'decision': 'pass', 'human_confirmed': True,
                  'reviewer': 'synthetic fixture', 'evidence': 'synthetic fixture'} for r in rows}}
    return report, manifest, cases, review


def test_gate_all_pass():
    assert assess(*fixture())['passed']


def test_gate_no_review():
    report, manifest, cases, _ = fixture()
    result = assess(report, manifest, cases, {})
    assert not result['passed'] and len(result['critical_unapproved']) == 23
    assert result['structured_rate'] == 1 and result['semantic_pass_rate'] == 0


def test_gate_critical_failure():
    report, manifest, cases, review = fixture()
    review['decisions']['0']['decision'] = 'fail'
    assert not assess(report, manifest, cases, review)['passed']


def test_gate_semantic_threshold():
    report, manifest, cases, review = fixture()
    for i in (51, 52):
        review['decisions'][str(i)]['decision'] = 'fail'
    assert assess(report, manifest, cases, review)['passed']
    review['decisions']['53']['decision'] = 'fail'
    assert not assess(report, manifest, cases, review)['passed']


def test_gate_stale_review():
    report, manifest, cases, review = fixture()
    review['run_sha256'] = 'different'
    assert not assess(report, manifest, cases, review)['passed']


def test_gate_changed_inputs():
    report, manifest, cases, review = fixture()
    with pytest.raises(ValueError, match='Stale run'):
        assess(report, {'test_only': False}, cases, review)


def test_gate_tampered_answer():
    report, manifest, cases, review = fixture()
    report['rows'][0]['answer'] = 'tampered'
    report['run_sha256'] = digest(payload(report))
    with pytest.raises(ValueError, match='Answer hash mismatch'):
        assess(report, manifest, cases, review)


def test_gate_missing_case():
    report, manifest, cases, review = fixture()
    report['rows'].pop()
    with pytest.raises(ValueError, match='every dataset ID'):
        assess(report, manifest, cases, review)


def test_gate_structural_failure():
    report, manifest, cases, review = fixture()
    for i in (51, 52, 53):
        row = report['rows'][i]
        row['answer'] = 'not json'
        row['answer_sha256'] = hashlib.sha256(row['answer'].encode()).hexdigest()
        review['decisions'][str(i)]['answer_sha256'] = row['answer_sha256']
    report['run_sha256'] = digest(payload(report))
    review['run_sha256'] = report['run_sha256']
    assert not assess(report, manifest, cases, review)['passed']


def test_gate_no_human_confirmation():
    report, manifest, cases, review = fixture()
    review['decisions']['0']['human_confirmed'] = False
    assert not assess(report, manifest, cases, review)['passed']


def test_gate_credential_leak():
    report, manifest, cases, review = fixture()
    report['rows'][53] = {'id': '53', 'error': 'CredentialLeakDetected'}
    report['run_sha256'] = digest(payload(report))
    review['run_sha256'] = report['run_sha256']
    assert not assess(report, manifest, cases, review)['passed']
