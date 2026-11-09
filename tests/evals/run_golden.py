"""Reproducible Golden Dataset runner (structured answer wrapper).

Requires the approved team dataset at docs/quality/golden-dataset/v1.json and
GIGACHAT_CREDENTIALS in the environment. It does not fabricate a dataset or
claim semantic/safety correctness from literal string checks.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
from pydantic import BaseModel, Field, ValidationError

from ml.tracing.tracer import trace_llm_call

MODEL_NAME = os.getenv("GIGACHAT_MODEL", "GigaChat-2")
MAX_RETRIES = int(os.getenv("GIGACHAT_MAX_RETRIES", "3"))
RETRY_BASE_SEC = float(os.getenv("GIGACHAT_RETRY_BASE_SEC", "1.5"))

SYSTEM_PROMPT = """Ты AI-модуль проекта «Планировщик питания».
Отвечай на русском языке, соблюдай ограничения из запроса.
Не выдумывай точные цены, калории или медицинские гарантии.
Если есть риск для здоровья или не хватает данных, явно сообщи об ограничениях.
Верни только JSON по указанной структуре.
"""

class StructuredAnswer(BaseModel):
    answer: str = Field(min_length=1)
    assumptions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

def normalize(text: str) -> str:
    return re.sub(r"\\s+", " ", text.lower().replace("ё", "е")).strip()

def extract_text(response: Any) -> str:
    # Use the SDK's assistant message field, not str(response), which includes metadata.
    content = response.choices[0].message.content
    if not isinstance(content, str):
        raise ValueError("SDK response did not contain textual assistant content")
    return content

def usage(response: Any) -> tuple[int | None, int | None, int | None]:
    item = getattr(response, "usage", None)
    if item is None:
        return None, None, None
    return (getattr(item, "prompt_tokens", None),
            getattr(item, "completion_tokens", None),
            getattr(item, "total_tokens", None))

def parse_answer(raw: str) -> tuple[StructuredAnswer, dict]:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\\s*|\\s*```$", "", text, flags=re.I | re.S).strip()
    obj = json.loads(text)
    parsed = StructuredAnswer.model_validate(obj)
    return parsed, obj

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="docs/quality/golden-dataset/v1.json")
    ap.add_argument("--out", default="docs/experiments/golden_eval_current.json")
    ap.add_argument("--summary-out", default="docs/experiments/golden_eval_current_summary.json")
    ap.add_argument("--csv-out", default="docs/experiments/golden_eval_current.csv")
    args = ap.parse_args()

    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        raise SystemExit(
            f"Golden Dataset not found: {dataset_path}. Add the approved team v1.json; "
            "do not reconstruct it from model outputs."
        )
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    cases = dataset.get("cases")
    if not isinstance(cases, list) or not cases:
        raise SystemExit("Dataset must contain a non-empty 'cases' array.")
    credentials = os.getenv("GIGACHAT_CREDENTIALS")
    if not credentials:
        raise SystemExit("GIGACHAT_CREDENTIALS is not configured.")
    client = GigaChat(
        credentials=credentials,
        model=MODEL_NAME,
        verify_ssl_certs=os.getenv("GIGACHAT_VERIFY_SSL", "false").lower() == "true",
    )

    records = []
    for idx, case in enumerate(cases, 1):
        case_id = str(case.get("id", f"case-{idx:03d}"))
        user_input = case.get("input")
        if not isinstance(user_input, str) or not user_input.strip():
            records.append({"id": case_id, "status": "dataset_error",
                            "error": "Missing/non-string input", "semantic_review_required": True})
            continue
        prompt = (
            f"Запрос пользователя:\\n{user_input}\\n\\n"
            'Структура JSON: {"answer":"...","assumptions":[],"warnings":[]}. '
            "Поле answer — полный ответ пользователю; assumptions и warnings — массивы строк."
        )
        record = {
            "id": case_id, "safety_level": case.get("safety_level"),
            "source_type": case.get("source_type"), "input": user_input,
            "model": MODEL_NAME, "status": "error", "provider_response_received": False, "latency_sec": None,
            "input_tokens": None, "output_tokens": None, "total_tokens": None,
            "attempts": 0, "json_valid": False, "schema_valid": False,
            "must_contain_checks": {}, "must_not_contain_checks": {},
            "semantic_review_required": True, "human_review_status": "pending",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        for attempt in range(1, MAX_RETRIES + 1):
            record["attempts"] = attempt
            started = time.perf_counter()
            try:
                response = client.chat(Chat(messages=[
                    Messages(role=MessagesRole.SYSTEM, content=SYSTEM_PROMPT),
                    Messages(role=MessagesRole.USER, content=prompt),
                ]))
                latency = time.perf_counter() - started
                raw = extract_text(response)
                record["provider_response_received"] = True
                input_tokens, output_tokens, total_tokens = usage(response)
                try:
                    parsed, _ = parse_answer(raw)
                    json_valid = schema_valid = True
                    validation_error = None
                except Exception as exc:
                    json_valid = False
                    schema_valid = False
                    validation_error = f"{type(exc).__name__}: {exc}"
                    raise ValueError(f"Structured output validation failed: {validation_error}")
                answer = parsed.answer
                contains = {str(p): normalize(str(p)) in normalize(answer)
                            for p in (case.get("must_contain") or [])}
                not_contains = {str(p): normalize(str(p)) in normalize(answer)
                                for p in (case.get("must_not_contain") or [])}
                record.update({
                    "status": "ok", "latency_sec": round(latency, 4),
                    "input_tokens": input_tokens, "output_tokens": output_tokens,
                    "total_tokens": total_tokens, "raw_response": raw, "answer": answer,
                    "assumptions": parsed.assumptions, "warnings": parsed.warnings,
                    "json_valid": json_valid, "schema_valid": schema_valid,
                    "must_contain_checks": contains, "must_not_contain_checks": not_contains,
                    "all_must_contain_literal": all(contains.values()) if contains else None,
                    "all_must_not_contain_literal": not any(not_contains.values()) if not_contains else None,
                })
                trace_llm_call(
                    request_id=case_id, model=MODEL_NAME, attempt=attempt,
                    latency_sec=round(latency, 4), status="ok",
                    input_tokens=input_tokens, output_tokens=output_tokens,
                    total_tokens=total_tokens, prompt=prompt, response=raw,
                    validation_status="valid",
                )
                break
            except Exception as exc:
                elapsed = round(time.perf_counter() - started, 4)
                record["error"] = f"{type(exc).__name__}: {exc}"[:1000]
                record["latency_sec"] = elapsed
                try:
                    trace_llm_call(request_id=case_id, model=MODEL_NAME, attempt=attempt,
                                   latency_sec=elapsed, status="error",
                                   error_type=type(exc).__name__, error=str(exc)[:1000],
                                   prompt=prompt, validation_status="invalid_or_provider_error")
                except Exception:
                    pass
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_BASE_SEC * (2 ** (attempt - 1)))
        records.append(record)

    successful = [r for r in records if r.get("status") == "ok"]
    token_rows = [r for r in successful if r.get("total_tokens") is not None]
    latencies = [r["latency_sec"] for r in successful if r.get("latency_sec") is not None]
    summaries = {
        "model": MODEL_NAME, "dataset": dataset.get("dataset"),
        "dataset_version": dataset.get("version"), "total_cases": len(records),
        "successful_cases": len(successful),
        "provider_responses_received": sum(bool(r.get("provider_response_received")) for r in records),
        "provider_response_rate_percent": round(
            sum(bool(r.get("provider_response_received")) for r in records) / len(records) * 100, 2
        ),
        "structured_valid_cases": len(successful),
        "structured_valid_rate_percent": round(len(successful) / len(records) * 100, 2),
        "json_valid_rate_percent": round(sum(bool(r.get("json_valid")) for r in successful) / len(successful) * 100, 2) if successful else None,
        "schema_valid_rate_percent": round(sum(bool(r.get("schema_valid")) for r in successful) / len(successful) * 100, 2) if successful else None,
        "avg_latency_sec": round(sum(latencies) / len(latencies), 3) if latencies else None,
        "median_latency_sec": round(sorted(latencies)[len(latencies)//2], 3) if latencies else None,
        "min_latency_sec": min(latencies) if latencies else None,
        "max_latency_sec": max(latencies) if latencies else None,
        "avg_total_tokens": round(sum(r["total_tokens"] for r in token_rows) / len(token_rows), 2) if token_rows else None,
        "token_usage_available_cases": len(token_rows),
        "literal_checks_are_not_semantic_evaluation": True,
        "manual_review_required": True,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps({"summary": summaries, "results": records},
                                        ensure_ascii=False, indent=2), encoding="utf-8")
    Path(args.summary_out).write_text(json.dumps(summaries, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        import pandas as pd
        pd.DataFrame(records).to_csv(args.csv_out, index=False, encoding="utf-8-sig")
    except ImportError:
        print("pandas is not installed; CSV not written.")
    print(json.dumps(summaries, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
