# Lab 4 execution results

## Run evidence

Source: latest executed user Colab notebook `Lab4_AI_Engineer_AB_Cost_itog.ipynb` and its exported `lab4_ab_results_same_run(1).zip`, run 2026-11-25, model `GigaChat-2`, Golden Dataset v1.

- OAuth preflight: passed.
- Smoke test: A_v1 and B_v2 each returned a response and passed the JSON contract.
- Full paired A/B: **80/88 final API calls succeeded**. A_v1: 44/44; B_v2: 36/44.
- Retry: 9 additional attempts; 1 logical case recovered; 8 remained failed.
- Retry distribution: A_v1 had 1 retry and recovered; B_v2 had 8 retry attempts and 0 recovered.
- Among successful responses, JSON and contract validation: A_v1 44/44; B_v2 36/36. Invalid JSON = 0; schema-invalid = 0.
- Offline tests: 22 passed, 0 failed.
- Safety review: 16/16 safety-critical cases pending manual review; 0 passed, 0 violations adjudicated.

## Remaining API/SDK failures

8 B_v2 calls failed after bounded retry. The SDK raised `pydantic_core.ValidationError`: `choices.0.message.role` is missing and `content` is empty. Case IDs: GD-0.2-002, GD-0.2-007, GD-0.2-011, GD-0.2-013, GD-0.2-017, GD-0.2-021, GD-0.2-028, GD-0.2-039.

These occur while parsing the provider response, before local JSON-schema validation. The precise upstream cause is not established. No prompt-quality winner can be declared from incomplete A/B results.

## Token usage and Freemium cost

Successful calls returned **18,894 tokens** (11,261 input; 7,633 output). Monetary charge is 0 ₽ within the available physical-person Freemium allowance. No fabricated input/output token prices are used. The reported 250M Lite / 12-month quota gives an approximate usage share of **0.007558%**; provider accounting may differ.

## Artifacts and export

`results/lab4_ab.json` and `results/lab4_ab.csv` contain the same 88 logical case/variant rows. `results/lab4_ab_failures.csv` contains the 8 final failed rows. The latest executed notebook's export cell generates the failure CSV from raw JSON, validates JSON/CSV row keys, recalculates the summary and Freemium accounting from the same run, and exports current runtime artifacts. It does not rerun the model.

## Interpretation

OAuth, smoke test, bounded retry and structured-output validation work. Full A/B remains **partial** due to 8 B_v2 SDK response failures. All successful responses pass the JSON contract, but semantic quality and safety require human evaluation. The literal forbidden-string count is zero; this does not establish semantic safety. The safety-review count remains 16 pending in this latest run; pending is not a pass.
