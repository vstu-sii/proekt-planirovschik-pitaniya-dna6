"""Token/cost scenario calculator. Prices are user-supplied, never hard-coded provider claims."""
from __future__ import annotations
import argparse, json

def estimate(*, requests: int, input_tokens: float, output_tokens: float,
             input_price_per_million: float, output_price_per_million: float,
             cache_hit_rate: float = 0.0, context_reduction: float = 0.0) -> dict:
    if requests < 0 or input_tokens < 0 or output_tokens < 0: raise ValueError("counts must be non-negative")
    if not 0 <= cache_hit_rate <= 1 or not 0 <= context_reduction < 1: raise ValueError("rates out of range")
    uncached = requests * (1-cache_hit_rate)
    effective_input = input_tokens * (1-context_reduction)
    in_tok = uncached * effective_input
    out_tok = uncached * output_tokens
    cost = (in_tok*input_price_per_million + out_tok*output_price_per_million)/1_000_000
    return {"requests": requests, "cache_hit_rate": cache_hit_rate, "context_reduction": context_reduction,
            "effective_input_tokens_per_miss": effective_input, "input_tokens_billed": round(in_tok),
            "output_tokens_billed": round(out_tok), "estimated_cost": round(cost, 6),
            "currency": "configured_by_rate_input", "note": "Estimate only; enter actual provider rates and cache billing rules."}

if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("--requests",type=int,default=1000); p.add_argument("--input-tokens",type=float,default=220.82); p.add_argument("--output-tokens",type=float,default=145.52); p.add_argument("--input-price",type=float,required=True,help="price per 1M input tokens"); p.add_argument("--output-price",type=float,required=True,help="price per 1M output tokens"); p.add_argument("--cache-hit",type=float,default=0); p.add_argument("--context-reduction",type=float,default=0)
    a=p.parse_args(); print(json.dumps(estimate(requests=a.requests,input_tokens=a.input_tokens,output_tokens=a.output_tokens,input_price_per_million=a.input_price,output_price_per_million=a.output_price,cache_hit_rate=a.cache_hit,context_reduction=a.context_reduction),ensure_ascii=False,indent=2))
