"""Offline summary from actual eval outputs. Run from project root."""

import argparse
import json
import math
import pathlib
import statistics
import sys


def read_jsonl(path):
    return [
        json.loads(line)
        for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def summarize(dataset, results):
    cases = read_jsonl(dataset)
    records = read_jsonl(results)
    by_id = {r["id"]: r for r in records}
    if len(by_id) != len(records):
        raise ValueError("Duplicate result IDs")
    if len({c["id"] for c in cases}) != len(cases):
        raise ValueError("Duplicate dataset IDs")
    if set(by_id) != {c["id"] for c in cases}:
        raise ValueError("Results and dataset IDs differ")
    ok = [r for r in records if r.get("status") == "received"]
    failed = [r for r in records if r.get("status") != "received"]
    structured = [r for r in ok if r.get("structured_valid") is True]
    critical_ids = {c["id"] for c in cases if c.get("safety_level") == "safety_critical"}
    lat = sorted(float(r["latency_sec"]) for r in ok if r.get("latency_sec") is not None)
    validation_errors = sum("validation error" in str(r.get("error", "")).lower() for r in failed)
    return {
        "total": len(cases),
        "received": len(ok),
        "errors": len(failed),
        "response_rate": len(ok) / len(cases),
        "structured_valid": len(structured),
        "structured_rate_all_cases": len(structured) / len(cases),
        "structured_rate_received": len(structured) / len(ok) if ok else None,
        "validation_error_cases": validation_errors,
        "critical_total": len(critical_ids),
        "critical_received": sum(r["id"] in critical_ids for r in ok),
        "critical_errors": sum(r["id"] in critical_ids for r in failed),
        "critical_safety_compliance": None,
        "nutrition_accuracy": None,
        "budget_accuracy": None,
        "latency_mean_sec_received_only": statistics.mean(lat) if lat else None,
        "latency_p95_sec_received_only": lat[math.ceil(0.95 * len(lat)) - 1] if lat else None,
        "retrieval_metrics": None,
        "failure_ids": [r["id"] for r in failed],
        "notes": [
            "Failed calls are not counted as successful responses.",
            "Safety/nutrition/budget require independent validators or human review.",
            "Latency statistics exclude failed calls; not overall service latency.",
        ],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", default="docs/quality/golden-dataset/v1.jsonl")
    p.add_argument("--results", default="backend/tests/evals/results/baseline-full-v1.jsonl")
    p.add_argument("--output", default="backend/tests/evals/results/verified-summary.json")
    p.add_argument("--gate", action="store_true")
    p.add_argument("--min-response-rate", type=float, default=0.95)
    p.add_argument("--min-structured-rate", type=float, default=0.95)
    args = p.parse_args()
    summary = summarize(args.dataset, args.results)
    pathlib.Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(args.output).write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.gate and (
        summary["response_rate"] < args.min_response_rate
        or summary["structured_rate_all_cases"] < args.min_structured_rate
    ):
        sys.exit(1)


if __name__ == "__main__":
    main()
