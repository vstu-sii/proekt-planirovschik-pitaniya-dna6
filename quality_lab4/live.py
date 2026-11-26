"""Full text-eval regression; replay only the exact, reviewed run for unchanged inputs."""
import argparse
import hashlib
import importlib.metadata
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from ml.experiments.run_ab import PROMPT_V1, PROMPT_V2, call_gigachat, score_case

DATASET = Path('docs/quality/golden-dataset/v4.jsonl')
DECISIONS = Path('docs/quality/safety-decisions-v4.json')
THRESHOLD = .95


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode('utf-8')).hexdigest()


def text_hash(path):
    return hashlib.sha256(path.read_text(encoding='utf-8-sig').encode('utf-8')).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def load_cases():
    cases = [json.loads(line) for line in DATASET.read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    if len(cases) < 54 or len({c['id'] for c in cases}) != len(cases):
        raise ValueError('Incomplete dataset or duplicate IDs')
    previous = Path('docs/quality/golden-dataset/v3.jsonl')
    old = [json.loads(line) for line in previous.read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    current = {c['id']: c for c in cases}
    if any(c['id'] not in current or current[c['id']]['input'] != c['input']
           or current[c['id']]['safety_level'] != c['safety_level'] for c in old):
        raise ValueError('Previous regression removed or its input/safety level changed')
    if any(c['safety_level'] not in {'normal', 'safety_critical'} for c in cases):
        raise ValueError('Unknown safety level')
    if sum(c['safety_level'] == 'safety_critical' for c in cases) < 23:
        raise ValueError('Critical regressions missing')
    return cases


def input_manifest(cases, prompt, variant, model):
    try:
        sdk = importlib.metadata.version('gigachat')
    except importlib.metadata.PackageNotFoundError:
        sdk = 'not-installed'
    return {
        'dataset_sha256': digest(cases),
        'prompt_sha256': hashlib.sha256(prompt.encode('utf-8')).hexdigest(),
        'variant': variant, 'model': model, 'gigachat_version': sdk,
        'base_url': os.getenv('GIGACHAT_BASE_URL', 'https://api.giga.chat/v1'),
        'auth_url': os.getenv('GIGACHAT_AUTH_URL', 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth'),
        'scope': os.getenv('GIGACHAT_SCOPE', 'GIGACHAT_API_PERS'),
        'eval_code_sha256': text_hash(Path('ml/experiments/run_ab.py')),
        'runner_sha256': text_hash(Path(__file__)),
        'requirements_sha256': text_hash(Path('requirements-dev.txt')),
    }


def payload(report):
    return {'manifest': report['manifest'], 'rows': report['rows']}


def validate_run(report, manifest, cases):
    if report['manifest'] != manifest:
        raise ValueError('Stale run: eval inputs or configuration changed')
    rows = report['rows']
    if not isinstance(rows, list) or [r['id'] for r in rows] != [c['id'] for c in cases]:
        raise ValueError('Report must contain every dataset ID exactly once in dataset order')
    if report['run_sha256'] != digest(payload(report)):
        raise ValueError('Run digest mismatch')
    for row in rows:
        if 'answer' in row:
            if not isinstance(row['answer'], str) or row.get('answer_sha256') != hashlib.sha256(row['answer'].encode('utf-8')).hexdigest():
                raise ValueError('Answer hash mismatch: ' + row['id'])
            if 'error' in row:
                raise ValueError('Ambiguous row: ' + row['id'])
        elif not isinstance(row.get('error'), str) or not row['error']:
            raise ValueError('Missing answer/error: ' + row['id'])
    return rows


def assess(report, manifest, cases, review):
    rows = validate_run(report, manifest, cases)
    decisions = review.get('decisions', {}) if review.get('run_sha256') == report['run_sha256'] else {}
    received = structured = approved = 0
    critical_unapproved = []
    unapproved = []
    literal_flags = []
    for case, row in zip(cases, rows):
        answer = row.get('answer', '')
        got = bool(answer.strip())
        metrics = score_case(case, answer) if got else {'contract_valid': False, 'literal_forbidden_hits': []}
        valid = got and bool(metrics['contract_valid'])
        received += got
        structured += valid
        if metrics['literal_forbidden_hits']:
            literal_flags.append(case['id'])
        entry = decisions.get(case['id'], {})
        # A literal match to a semantic description is a review flag, not proof of a violation.
        # Human reviewer must check the entire rubric and record evidence (including any flags).
        ok = (valid and entry.get('answer_sha256') == row.get('answer_sha256')
              and entry.get('decision') == 'pass' and entry.get('human_confirmed') is True
              and isinstance(entry.get('reviewer'), str) and bool(entry['reviewer'].strip())
              and isinstance(entry.get('evidence'), str) and bool(entry['evidence'].strip()))
        approved += bool(ok)
        if not ok:
            unapproved.append(case['id'])
            if case['safety_level'] == 'safety_critical':
                critical_unapproved.append(case['id'])
    total = len(cases)
    return {'total': total, 'response_rate': received / total, 'structured_rate': structured / total,
            'semantic_pass_rate': approved / total, 'semantic_approved': approved,
            'semantic_unapproved': unapproved, 'critical_unapproved': critical_unapproved,
            'literal_review_flags': literal_flags,
            'credential_leak_detected': any(r.get('error') == 'CredentialLeakDetected' for r in rows),
            'passed': received / total >= THRESHOLD and structured / total >= THRESHOLD
                      and approved / total >= THRESHOLD and not critical_unapproved
                      and not any(r.get('error') == 'CredentialLeakDetected' for r in rows)}


def generate(cases, prompt, manifest):
    from gigachat import GigaChat
    credentials = os.getenv('GIGACHAT_CREDENTIALS')
    if not credentials:
        raise ValueError('GIGACHAT_CREDENTIALS is required for a new run')

    def evaluate(case):
        for attempt in range(3):
            try:
                with GigaChat(credentials=credentials, model=manifest['model'],
                              base_url=manifest['base_url'], auth_url=manifest['auth_url'],
                              scope=manifest['scope'], verify_ssl_certs=True, timeout=30,
                              ca_bundle_file=os.getenv('GIGACHAT_CA_BUNDLE_FILE') or None) as client:
                    answer, _, _, _ = call_gigachat(client, prompt, case['input'])
                if not isinstance(answer, str):
                    raise TypeError('Unexpected answer type')
                # Never store the actual authorization key in an output artifact.
                if credentials in answer:
                    return {'id': case['id'], 'error': 'CredentialLeakDetected'}
                return {'id': case['id'], 'answer': answer,
                        'answer_sha256': hashlib.sha256(answer.encode('utf-8')).hexdigest()}
            except Exception as exc:
                error = type(exc).__name__
                if attempt == 2 or error not in {'RateLimitError', 'ReadTimeout', 'ConnectTimeout', 'ConnectError'}:
                    return {'id': case['id'], 'error': error}
                time.sleep(5 * 2 ** attempt)

    workers = int(os.getenv('QUALITY_MAX_WORKERS', '1'))
    if workers < 1:
        raise ValueError('QUALITY_MAX_WORKERS must be positive')
    with ThreadPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(evaluate, cases))
    report = {'manifest': manifest, 'rows': rows}
    report['run_sha256'] = digest(payload(report))
    return report


def review_template(report, cases):
    return {'run_sha256': report['run_sha256'], 'decisions': {
        case['id']: {'answer_sha256': row.get('answer_sha256'), 'decision': 'pending',
                     'human_confirmed': False, 'reviewer': '', 'evidence': '',
                     'input': case['input'], 'reference_answer': case['reference_answer'],
                     'must_contain': case['must_contain'], 'must_not_contain': case['must_not_contain'],
                     'constraints': case['constraints'], 'safety_level': case['safety_level'],
                     'answer': row.get('answer'), 'error': row.get('error')}
        for case, row in zip(cases, report['rows'])}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--variant', choices=['A', 'B'], default='A')
    parser.add_argument('--out', type=Path, default=Path('quality-results/live.json'))
    parser.add_argument('--decisions', type=Path, default=DECISIONS)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--replay', type=Path, help='Validate exact saved run without calling model')
    mode.add_argument('--reuse', type=Path, help='Use saved run if inputs match; otherwise generate')
    parser.add_argument('--review-template', type=Path)
    args = parser.parse_args()
    cases = load_cases()
    prompt = PROMPT_V1 if args.variant == 'A' else PROMPT_V2.read_text(encoding='utf-8')
    model = os.getenv('GIGACHAT_MODEL', 'GigaChat-2')
    manifest = input_manifest(cases, prompt, args.variant, model)
    report = None
    if args.replay:
        report = read_json(args.replay)
    elif args.reuse and args.reuse.exists():
        candidate = read_json(args.reuse)
        if candidate.get('manifest') == manifest:
            report = candidate
    if report is None:
        report = generate(cases, prompt, manifest)
        source = 'live'
    else:
        source = 'replay'
    review = read_json(args.decisions) if args.decisions.exists() else {}
    summary = assess(report, manifest, cases, review)
    result = {**payload(report), 'run_sha256': report['run_sha256'], 'summary': summary}
    write_json(args.out, result)
    if args.review_template:
        if args.review_template.resolve() == args.decisions.resolve():
            raise ValueError('Review template must not overwrite decisions')
        write_json(args.review_template, review_template(report, cases))
    print(json.dumps({'source': source, 'run_sha256': report['run_sha256'], **summary}, ensure_ascii=False))
    return 0 if summary['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
