# Agent site-check: criterion closure evidence

This document maps the criteria marked open by the external site-check agent to concrete artifacts and measurements in this submission.

## 1. Scenario cost before and after optimization

**Closed as a measured controlled scenario, not as production billing.**

- Reproducible benchmark: `ml/experiments/cache_cost_benchmark.py`.
- Actual SQLite cache exercised; backend is mocked to avoid live API calls.
- 100 identical requests: 100 backend calls without cache vs 1 with cache; 99 hits.
- Token-equivalent based on latest live-run mean usage: 23,617.50 vs 236.18, reduction 99.00%.
- Evidence: `results/cache_cost_benchmark.json`, detailed method and limitations in `docs/ml-cost.md`.

Freemium monetary charge remains 0 ₽ before and after. Production traffic hit rate and endpoint integration are not claimed.

## 2. Versioned prompts and iteration run

**Closed as versioned artifacts with a documented reason and executed same-dataset comparison. Quality approval is not claimed.**

- Prompt artifacts: `ml/prompts_v2/system_v2.txt`, `ml/prompts_v2/eval_v2.txt`; v1 remains the baseline in `run_ab.py`.
- Change rationale and actual A_v1/B_v2 results: `docs/prompt-evaluation.md`, `results/prompt_comparison.json`.
- Same Golden Dataset v1: A_v1 44/44 API success; B_v2 36/44. Contract validity among successful responses: 100% for both.
- B_v2 successful-call mean token usage: 230.694 vs 240.659 for A_v1, 4.14% lower, but the B_v2 successful sample is incomplete and has 8 SDK/API failures. No winner is declared.

## Remaining human acceptance

The latest safety review has 16 pending cases. They are explicitly not marked passed. A human reviewer must adjudicate these cases before the semantic safety gate can be considered complete. The archive closes the two documentary/evidence gaps reported by the agent; it does not fabricate an external approval or a production deployment.
