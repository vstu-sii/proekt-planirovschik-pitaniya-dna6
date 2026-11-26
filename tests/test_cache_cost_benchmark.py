from ml.experiments.cache_cost_benchmark import run_benchmark

def test_cache_cost_benchmark_replays_identical_requests():
    result = run_benchmark(requests=5, input_tokens_per_call=10, output_tokens_per_call=5)
    assert result["backend_calls_before"] == 5
    assert result["backend_calls_after"] == 1
    assert result["cache_hits"] == 4
    assert result["estimated_token_reduction_percent"] == 80.0
