# Lab 3 experiment runner

## Re-run

From the repository root:

```bash
export GIGACHAT_CREDENTIALS="..."
export GIGACHAT_MODEL="GigaChat-2"
export TRACE_CAPTURE_CONTENT="true"

python -m pip install -r requirements.txt
python tests/evals/run_golden.py   --dataset docs/quality/golden-dataset/v1.json   --out docs/experiments/golden_eval_results.json   --summary-out docs/experiments/golden_eval_summary.json   --csv-out docs/experiments/golden_eval_results.csv
```

The same runner is used by CI. `TRACE_CAPTURE_CONTENT=true` ensures that every call is recorded with its prompt and response when a response is returned.

## Existing recorded run

The repository already contains the completed run artifacts:
- `golden_eval_results.json`
- `golden_eval_results.csv`
- `golden_eval_summary.json`
- `llm_traces.jsonl`

The recorded run contains 44 cases and 48 trace events including the smoke test and retry attempts.

The original dataset upload was not present as a standalone file in the supplied archive. `docs/quality/golden-dataset/v1.json` was reconstructed from the exact recorded result rows so the run can be repeated from a clean checkout. Its provenance is explicitly marked in the JSON.
