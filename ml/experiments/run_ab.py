"""Repeatable paired prompt A/B evaluation against the supplied Golden Dataset.

Requires GIGACHAT_CREDENTIALS and `pip install gigachat`. Results are written to JSON/CSV.
"""
from __future__ import annotations
import argparse, csv, json, os, re, time, traceback
from pathlib import Path
from typing import Any

PROMPT_V1 = """Ты AI-модуль проекта «Планировщик питания». Отвечай на русском языке. Учитывай все ограничения пользователя одновременно. Не выдумывай точную стоимость и КБЖУ: они рассчитываются программно. Не используй запрещённые продукты. Учитывай продукты pantry, если они переданы. Не превышай max_cook_time_min. Верни только JSON без Markdown с полями answer, assumptions, warnings."""
PROMPT_V2 = Path(__file__).resolve().parents[1] / "prompts_v2" / "eval_v2.txt"


# Enforce the shared output contract through GigaChat structured output.
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"anyOf": [
            {"type": "string"},
            {"type": "object", "additionalProperties": True},
            {"type": "array", "items": {"anyOf": [
                {"type": "string"}, {"type": "object", "additionalProperties": True}
            ]}}
        ]},
        "assumptions": {"anyOf": [
            {"type": "array", "items": {"type": "string"}},
            {"type": "object", "additionalProperties": True}, {"type": "string"}
        ]},
        "warnings": {"anyOf": [
            {"type": "array", "items": {"type": "string"}},
            {"type": "object", "additionalProperties": True}, {"type": "string"}
        ]}
    },
    "required": ["answer", "assumptions", "warnings"],
    "additionalProperties": False
}
RESPONSE_FORMAT = {"type": "json_schema", "schema": RESPONSE_SCHEMA, "strict": True}


def validate_output_contract(answer: str) -> dict[str, Any]:
    text = (answer or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    try:
        parsed = json.loads(text)
    except Exception as exc:
        return {"json_valid": False, "contract_valid": False,
                "format_error": f"invalid_json: {type(exc).__name__}: {exc}"}
    if not isinstance(parsed, dict):
        return {"json_valid": True, "contract_valid": False,
                "format_error": "top_level_not_object"}
    required = {"answer", "assumptions", "warnings"}
    if set(parsed) != required:
        return {"json_valid": True, "contract_valid": False,
                "format_error": f"wrong_keys: missing={sorted(required-set(parsed))}; extra={sorted(set(parsed)-required)}"}
    if not isinstance(parsed["answer"], (str, dict, list)):
        return {"json_valid": True, "contract_valid": False,
                "format_error": "answer_wrong_type"}
    if isinstance(parsed["answer"], list) and any(not isinstance(x, (str, dict)) for x in parsed["answer"]):
        return {"json_valid": True, "contract_valid": False,
                "format_error": "answer_array_item_wrong_type"}
    for key in ("assumptions", "warnings"):
        value = parsed[key]
        if not isinstance(value, (str, dict, list)):
            return {"json_valid": True, "contract_valid": False,
                    "format_error": f"{key}_wrong_type"}
        if isinstance(value, list) and any(not isinstance(x, str) for x in value):
            return {"json_valid": True, "contract_valid": False,
                    "format_error": f"{key}_array_item_wrong_type"}
    return {"json_valid": True, "contract_valid": True, "format_error": None}


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()


def score_case(case: dict[str, Any], answer: str) -> dict[str, Any]:
    text = norm(answer)
    required = [norm(x) for x in case.get("must_contain", [])]
    forbidden = [norm(x) for x in case.get("must_not_contain", [])]
    # Dataset's must_not_contain entries often describe semantic failures rather than
    # literal strings. This metric intentionally only detects literal occurrences.
    found = [x for x in required if x and x in text]
    literal_bad = [x for x in forbidden if x and x in text]
    format_metrics = validate_output_contract(answer)
    return {"must_contain_total": len(required), "must_contain_found": len(found),
            "must_contain_rate": len(found)/len(required) if required else None,
            "literal_forbidden_hits": literal_bad, **format_metrics,
            "safety_level": case.get("safety_level", "normal"),
            "manual_review_required": case.get("safety_level") == "safety_critical" or case.get("human_review_status") != "approved"}


def redact_diagnostics(text: str, credentials: str | None = None) -> str:
    """Redact secrets from exception text/tracebacks before writing diagnostic files."""
    if credentials:
        text = text.replace(credentials, "[REDACTED_CREDENTIALS]")
    # Common authorization and OAuth secret formats.
    text = re.sub(r"(?i)(authorization\s*[:=]\s*)(?:bearer|basic)?\s*[^\r\n,;]+", r"\1[REDACTED]", text)
    text = re.sub(r"(?i)(access_token|refresh_token|client_secret|client_id|password|credentials)(\s*[:=]\s*)([^&;,\s\"']+)", r"\1\2[REDACTED]", text)
    text = re.sub(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+", "Bearer [REDACTED]", text)
    return text


def safe_error_message(exc: Exception, credentials: str | None = None) -> str:
    """Return bounded diagnostics without credentials or request/user content."""
    return redact_diagnostics(str(exc), credentials)[:2000]


def exception_diagnostics(exc: Exception, credentials: str | None = None) -> dict[str, str]:
    """Capture full traceback and nested causes, with secrets redacted."""
    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    chain = []
    current = exc
    seen = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        chain.append(f"{type(current).__module__}.{type(current).__name__}: {current}")
        current = current.__cause__ or current.__context__
    return {
        "error_type": f"{type(exc).__module__}.{type(exc).__name__}",
        "error_message_full": redact_diagnostics(str(exc), credentials)[:10000],
        "error_chain": redact_diagnostics("\nCaused by: ".join(chain), credentials)[:20000],
        "error_traceback": redact_diagnostics(tb, credentials)[:30000],
    }




def is_retryable_call_error(exc: Exception) -> bool:
    """Retry only known transient transport or malformed-empty SDK response failures."""
    name = type(exc).__name__
    module = type(exc).__module__
    message = str(exc)
    if name == "ReadTimeout" and module.startswith("httpx"):
        return True
    if name == "ValidationError" and "choices.0.message.role" in message and "content" in message:
        return True
    return False


def call_gigachat(client: Any, system: str, user: str) -> tuple[str, int | None, int | None, int | None]:
    from gigachat.models import Chat, Messages, MessagesRole
    response = client.chat(Chat(messages=[Messages(role=MessagesRole.SYSTEM, content=system),
                                          Messages(role=MessagesRole.USER, content=user)],
                                response_format=RESPONSE_FORMAT))
    content = response.choices[0].message.content or ""
    usage = getattr(response, "usage", None)
    return content, getattr(usage, "prompt_tokens", None), getattr(usage, "completion_tokens", None), getattr(usage, "total_tokens", None)


def run(dataset_path: Path, output: Path, model: str, limit: int | None = None) -> dict[str, Any]:
    credentials = os.getenv("GIGACHAT_CREDENTIALS")
    if not credentials: raise RuntimeError("Set GIGACHAT_CREDENTIALS; no live A/B results are fabricated.")
    from gigachat import GigaChat
    data = json.loads(dataset_path.read_text(encoding="utf-8"))
    cases = data["cases"][:limit] if limit else data["cases"]
    prompts = {"A_v1": PROMPT_V1, "B_v2": PROMPT_V2.read_text(encoding="utf-8")}
    rows = []
    with GigaChat(credentials=credentials, model=model, verify_ssl_certs=True, ca_bundle_file=os.getenv("GIGACHAT_CA_BUNDLE_FILE") or None) as client:
        for case_index, case in enumerate(cases):
            # Balance order across cases to reduce systematic A-first timing/provider bias.
            variants = list(prompts.items())
            if case_index % 2:
                variants.reverse()
            for variant, system in variants:
                start = time.perf_counter()
                attempt = 1
                retry_errors = []
                try:
                    while True:
                        try:
                            answer, inp, out, total = call_gigachat(client, system, case["input"])
                            break
                        except Exception as attempt_exc:
                            if attempt < 2 and is_retryable_call_error(attempt_exc):
                                retry_errors.append({
                                    "attempt": attempt,
                                    "error_type": f"{type(attempt_exc).__module__}.{type(attempt_exc).__name__}",
                                    "error_message": safe_error_message(attempt_exc, credentials)
                                })
                                attempt += 1
                                time.sleep(1.25)
                                continue
                            raise
                    latency = time.perf_counter() - start
                    metrics = score_case(case, answer)
                    rows.append({"case_id": case["id"], "variant": variant, "status": "ok", "latency_sec": round(latency, 4),
                                 "attempts": attempt, "retry_errors": retry_errors,
                                 "input_tokens": inp, "output_tokens": out, "total_tokens": total,
                                 "answer": answer, **metrics})
                except Exception as exc:
                    # Preserve the underlying network/TLS/DNS exception for diagnosis.
                    # Redact credentials before saving anything to disk.
                    diagnostics = exception_diagnostics(exc, credentials)
                    rows.append({"case_id": case["id"], "variant": variant, "status": "error",
                                 "latency_sec": round(time.perf_counter()-start, 4),
                                 "attempts": attempt, "retry_errors": retry_errors,
                                 "error": type(exc).__name__,
                                 "error_message": safe_error_message(exc, credentials),
                                 **diagnostics})
    output.parent.mkdir(parents=True, exist_ok=True)
    summary = {}
    for variant in prompts:
        subset = [r for r in rows if r["variant"] == variant]
        ok = [r for r in subset if r["status"] == "ok"]
        summary[variant] = {
            "cases": len(subset), "successful": len(ok),
            "api_success_rate": len(ok)/len(subset) if subset else 0,
            "calls_with_retry": sum(int(r.get("attempts", 1)) > 1 for r in subset),
            "retry_attempts": sum(max(0, int(r.get("attempts", 1)) - 1) for r in subset),
            "retry_recovered": sum(r.get("status") == "ok" and int(r.get("attempts", 1)) > 1 for r in subset),
            "mean_latency_sec": sum(r["latency_sec"] for r in ok)/len(ok) if ok else None,
            "mean_total_tokens": sum(r["total_tokens"] for r in ok if r.get("total_tokens") is not None)/sum(r.get("total_tokens") is not None for r in ok) if any(r.get("total_tokens") is not None for r in ok) else None,
            "literal_must_contain_rate": sum(r["must_contain_rate"] for r in ok if r.get("must_contain_rate") is not None)/sum(r.get("must_contain_rate") is not None for r in ok) if any(r.get("must_contain_rate") is not None for r in ok) else None,
            "literal_forbidden_hits": sum(len(r.get("literal_forbidden_hits", [])) for r in ok),
            "json_valid_count": sum(bool(r.get("json_valid")) for r in ok),
            "contract_valid_count": sum(bool(r.get("contract_valid")) for r in ok),
            "contract_valid_rate": sum(bool(r.get("contract_valid")) for r in ok)/len(ok) if ok else 0,
            "invalid_json_count": sum(not bool(r.get("json_valid")) for r in ok),
            "schema_invalid_count": sum(bool(r.get("json_valid")) and not bool(r.get("contract_valid")) for r in ok),
            "all_cases_pending_manual_review": sum(bool(r.get("manual_review_required")) for r in ok),
            "safety_critical_cases_pending_manual_review": len({r["case_id"] for r in ok if r.get("safety_level") == "safety_critical" and r.get("manual_review_required")}),
        }
    result = {"dataset": data.get("dataset"), "dataset_version": data.get("version"), "model": model,
              "method": "paired sequential A/B with alternating order; same cases; literal checks are not semantic eval",
              "rows": rows, "summary": summary}
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    csv_path = output.with_suffix(".csv")
    keys = sorted({k for row in rows for k in row if k not in {"answer", "literal_forbidden_hits"}})
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore"); writer.writeheader(); writer.writerows(rows)
    return result

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", default="tests/v1.json")
    p.add_argument("--output", default="results/lab4_ab.json")
    p.add_argument("--model", default=os.getenv("GIGACHAT_MODEL", "GigaChat-2"))
    p.add_argument("--limit", type=int)
    a = p.parse_args()
    result = run(Path(a.dataset), Path(a.output), a.model, a.limit)
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
