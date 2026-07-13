from scripts.evals.run_simulated_reliability_lite_coverage_recovery_v1 import run


def test_recovery_call_completes_full_portfolio_provider_free(tmp_path):
    contract = {
        "run_id": "test",
        "case_id": "v1-case07-cooperative-scheduling",
        "mechanism_id": "acknowledged_constraint_not_gated",
        "inputs": {
            "parent_mechanism_request_path": "research/simulated-reliability-v1-transfer-2026-07-12/t1/v1-case07-cooperative-scheduling-primary/mechanism-request.json",
            "failed_full_case_result_path": "research/simulated-reliability-v1-lite-full-factored-case07-2026-07-13/t1/result.json",
        },
        "base_runtime_contract": {"path": "docs/evals/simulated-reliability-v1-runtime-contract-v14-transfer.json"},
        "operator": {"model": "test", "provider_slug": "test", "maximum_price_usd_per_million_tokens": {"prompt": 1, "completion": 1}},
        "task_limit": {"max_output_tokens": 1000, "reasoning_effort": "minimal"},
        "seed": 1,
        "budget": {"maximum_provider_reported_cost_usd": 0.01},
    }

    def fake_call(**kwargs):
        candidate = {
            "mechanism_id": contract["mechanism_id"],
            "vanilla_answer_coverage": "operationalized",
            "source_assistant_contribution_ids": ["assistant-turn-001"],
        }
        return {"operational_status": "ok", "compiled": kwargs["compile_candidate"](candidate), "provider_calls": 1, "provider_reported_cost_usd": 0.001}

    output = tmp_path / "out"
    output.mkdir()
    result = run(contract, output=output, call_fn=fake_call)
    assert result["joined_full_portfolio"]["counts"]["total_model_calls"] == 11
    assert result["joined_full_portfolio"]["counts"]["routing_mechanisms"] == 0
