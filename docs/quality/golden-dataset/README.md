# Golden Dataset

`run_golden.py` and the Lab 3 notebook require the **approved team dataset** at `v1.json`.
The source dataset is intentionally not reconstructed from model answers or result files.
Add the approved file here before running live evaluations.

Expected minimal shape:

```json
{
  "dataset": "Golden Dataset",
  "version": "1.0",
  "record_count": 44,
  "cases": [
    {
      "id": "GD-...",
      "input": "User request",
      "must_contain": [],
      "must_not_contain": [],
      "constraints": [],
      "safety_level": "normal",
      "human_review_status": "pending"
    }
  ]
}
```

The exact field names and reference criteria should follow the team's canonical dataset. `input` must be a string. Do not copy generated answers into the dataset as reference answers.

## Run

```bash
export GIGACHAT_CREDENTIALS="..."
export GIGACHAT_MODEL="GigaChat-2"
python tests/evals/run_golden.py \
  --dataset docs/quality/golden-dataset/v1.json \
  --out docs/experiments/golden_eval_current.json \
  --summary-out docs/experiments/golden_eval_current_summary.json \
  --csv-out docs/experiments/golden_eval_current.csv
```

`GIGACHAT_MODEL` defaults to `GigaChat-2` because that was the operational model used after connection errors with `GigaChat-2-Lite`. This does not establish that the models are equivalent; always record the actual model used.

## Interpretation

- Provider response rate and structured-output validity are separate metrics.
- JSON/Pydantic validity does not establish semantic correctness.
- Literal `must_contain` checks are diagnostic only; they do not understand synonyms or paraphrases.
- Human review is required for semantic and safety-critical cases.
- If token usage is not returned by the SDK, token metrics are `null` rather than estimated.
- Live eval CI is skipped when credentials are unavailable and emits a warning; a skipped job is **not** a passing quality evaluation.
- No quality threshold is configured yet. Set it only after a reproducible baseline and manual review establish a defensible threshold.


## Latest recorded run (2026-10-28)

The latest executed notebook processed 44 cases in structured mode using the configured model alias `GigaChat-2`. Recorded results: API success 44/44; JSON/schema valid 43/44 (97.73%); mean latency 1.523 s; maximum latency 4.291 s; mean total tokens 366.34. The raw artifacts are in `docs/experiments/golden_eval_results.json`, `.csv`, and `golden_eval_summary.json`.

This run used a `v1.json` uploaded into the notebook session. The canonical dataset file is still absent from the repository, so the exact run cannot be reproduced from a clean clone until the approved source dataset is committed. All human review statuses remain pending; this is not a semantic or safety approval.
