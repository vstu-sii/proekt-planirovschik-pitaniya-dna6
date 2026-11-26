# Prompt versioning and evaluation evidence

## Change reason

Prompt v2 was introduced to separate the production `MealPlanDraft` prompt from the evaluation `StructuredAnswer` prompt and to apply the error taxonomy/explicit structured-output guidance. Prompt files are stored as versioned artifacts under `ml/prompts_v2/`; the A/B runner records the version and reads the v2 files from disk. Prompt v1 remains in the runner as the baseline.

## Same-dataset comparison

Source: latest executed notebook and exported raw JSON/CSV, 2026-11-25. Golden Dataset v1, 44 logical cases per variant.

| Metric | A_v1 | B_v2 |
|---|---:|---:|
| API success | 44/44 (100%) | 36/44 (81.82%) |
| Contract-valid among successful | 44/44 (100%) | 36/36 (100%) |
| Mean tokens per successful call | 240.659 | 230.694 |
| Mean latency (s) | 1.794 | 0.980 |
| Retry attempts | 1 (recovered) | 8 (0 recovered) |

Among successful responses only, B_v2 used 9.965 fewer tokens per call on average (4.14% reduction). This is descriptive and not a causal quality comparison: B_v2 has 8 missing API responses, so its successful sample is incomplete. All successful responses pass the strict JSON contract, but that does not establish semantic quality or safety.

## Decision

The iteration is versioned and backed by an executed same-dataset A/B run. **No prompt winner is accepted.** B_v2's lower observed token mean is not sufficient to outweigh its 8 SDK/API failures. The prompt quality gate remains blocked pending a complete paired run and human safety review.
