# Lab4: AI Engineer — Infrastructure Deliverables

Branch: `lab4-ai-engineer-infrastructure`

## Summary

- Add prompt v2 and error taxonomy from Golden Dataset failure classes.
- Add repeatable paired A/B runner with JSON/CSV artifacts.
- Add configurable token-cost calculator and SQLite TTL cache.
- Add read-only nutrition/cost tool with explicit contract, allowlist, caller authorization and timeout.
- Add MealPlanDraft hard-constraint guard and safety-review reconciliation utilities.
- Add tests, latest executed notebook, cost report, trace policy, and ADR.

## Validation

- Offline unit tests: **22 passed, 0 failed** in the latest notebook run.
- OAuth preflight and A/B smoke test: passed.
- Latest live A/B: **80/88 API calls succeeded** (A_v1 44/44, B_v2 36/44). All 80 successful responses passed the JSON contract. 8 B_v2 SDK/API errors remained after retry.
- Successful-call token usage: 18,894 (11,261 input; 7,633 output); Freemium charge reported as 0 ₽ within the free allowance.
- Safety review: 16 cases pending manual review, 0 passed, 0 violations adjudicated.

No prompt winner or safety certification is claimed: the paired run is incomplete and human safety review remains pending.

## Notes

This PR adds isolated AI Engineer modules. Wiring the tool/cache into the current backend endpoint requires agreement with Delivery on the canonical product catalog and API contract. No deployment, CI pass, or production integration is claimed by this PR.
