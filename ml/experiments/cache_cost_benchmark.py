"""Reproducible local cache cost benchmark using observed latest-run token usage.

This is a controlled replay of 100 identical requests, not a production traffic claim.
The backend call is mocked; the SQLite cache itself is real and exercised.
"""
from __future__ import annotations
import argparse, json, tempfile
from pathlib import Path
from ml.tools.cache import ResponseCache

def run_benchmark(*, requests: int = 100, input_tokens_per_call: float = 11261/80,
                  output_tokens_per_call: float = 7633/80) -> dict:
    if requests < 1:
        raise ValueError("requests must be >= 1")
    # Same canonical request every time: a valid cache hit scenario.
    request = {"operation": "mealplan", "profile": {"goal": "maintenance"},
               "constraints": ["no_allergens"], "pantry": ["rice", "chicken"]}
    model, prompt_version = "GigaChat-2", "v2"
    response = {"answer": {"status": "benchmark-fixture"}}
    with tempfile.TemporaryDirectory() as td:
        cache = ResponseCache(Path(td) / "cache.sqlite3", ttl_sec=3600)
        key = cache.key(request, model=model, prompt_version=prompt_version)
        # Before: every request reaches the model.
        before_api_calls = requests
        before_input = requests * input_tokens_per_call
        before_output = requests * output_tokens_per_call
        # After: cache lookup for each request, one model miss then cached replay.
        api_calls = 0
        cache_hits = 0
        for _ in range(requests):
            cached = cache.get(key)
            if cached is not None:
                cache_hits += 1
                continue
            api_calls += 1
            cache.set(key, response)
        after_input = api_calls * input_tokens_per_call
        after_output = api_calls * output_tokens_per_call
    before_total = before_input + before_output
    after_total = after_input + after_output
    return {
        "benchmark": "sqlite_response_cache_identical_request_replay",
        "requests": requests,
        "unique_requests": 1,
        "model": model,
        "prompt_version": prompt_version,
        "token_basis": "Observed latest A/B usage: 11,261 input + 7,633 output tokens across 80 successful API calls; mean usage per successful call applied to a controlled replay.",
        "backend_calls_before": before_api_calls,
        "backend_calls_after": api_calls,
        "cache_hits": cache_hits,
        "cache_hit_rate": cache_hits / requests,
        "input_tokens_before_estimated": round(before_input, 3),
        "output_tokens_before_estimated": round(before_output, 3),
        "total_tokens_before_estimated": round(before_total, 3),
        "input_tokens_after_estimated": round(after_input, 3),
        "output_tokens_after_estimated": round(after_output, 3),
        "total_tokens_after_estimated": round(after_total, 3),
        "estimated_token_reduction_percent": round((1-after_total/before_total)*100, 2),
        "freemium_actual_charge_before_rub": 0,
        "freemium_actual_charge_after_rub": 0,
        "monetary_savings_rub": 0,
        "limitations": [
            "Controlled local replay; not measured production traffic or live provider billing.",
            "All 100 requests are deliberately identical; cache savings depend on real duplicate rate.",
            "Cache is a prototype module and is not yet wired into the production endpoint.",
            "Token equivalents use the latest-run mean usage; cached responses make no provider call."
        ]
    }

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--requests", type=int, default=100)
    p.add_argument("--output", default="results/cache_cost_benchmark.json")
    a = p.parse_args()
    result = run_benchmark(requests=a.requests)
    out = Path(a.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
