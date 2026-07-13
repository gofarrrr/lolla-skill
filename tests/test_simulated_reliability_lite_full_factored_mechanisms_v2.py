from scripts.evals.run_simulated_reliability_lite_full_factored_mechanisms_v2 import run


COUNTERPRESSURE = "counterpressure_acknowledged_not_integrated"


def test_dual_effort_runner_separates_user_and_coverage_calls(tmp_path):
    contract = {
        "run_id": "test-run",
        "case_id": "v1-case07-cooperative-scheduling",
        "inputs": {
            "parent_mechanism_request_path": "research/simulated-reliability-v1-transfer-2026-07-12/t1/v1-case07-cooperative-scheduling-primary/mechanism-request.json"
        },
        "base_runtime_contract": {
            "path": "docs/evals/simulated-reliability-v1-runtime-contract-v14-transfer.json"
        },
        "operator": {
            "model": "test-model",
            "provider_slug": "test-provider",
            "maximum_price_usd_per_million_tokens": {"prompt": 1, "completion": 1},
        },
        "task_limits": {
            "user_factor": {"max_output_tokens": 1000, "reasoning_effort": "low"},
            "assistant_coverage": {"max_output_tokens": 1000, "reasoning_effort": "minimal"},
        },
        "seed_base": 1000,
        "budget": {"maximum_provider_reported_cost_usd": 0.1},
    }
    called = {"user": [], "coverage": []}

    def fake_user_call(**kwargs):
        assert kwargs["task_id"] == "mechanism_user_factor"
        assert kwargs["contract"]["task_limits"]["mechanism_user_factor"]["reasoning_effort"] == "low"
        mechanism_id = kwargs["schema_name"].split("lolla_v1_user_factor_")[-1]
        called["user"].append(mechanism_id)
        if mechanism_id == COUNTERPRESSURE:
            candidate = {
                "mechanism_id": mechanism_id,
                "mechanism_observation": "observed",
                "integration_status": "integrated",
                "pattern_state": "not_applicable",
                "source_role_record_ids": [
                    "rprolev22-starting-01-5811f15d32fc53",
                    "rprolev22-current-01-c822692e4e9b47",
                ],
            }
        else:
            candidate = {
                "mechanism_id": mechanism_id,
                "mechanism_observation": "not_observed",
                "integration_status": "not_applicable",
                "pattern_state": "not_applicable",
                "source_role_record_ids": [],
            }
        return {
            "operational_status": "ok",
            "compiled": kwargs["compile_candidate"](candidate),
            "provider_calls": 1,
            "provider_reported_cost_usd": 0.001,
        }

    def fake_coverage_call(**kwargs):
        assert kwargs["task_id"] == "mechanism_assistant_coverage"
        assert kwargs["contract"]["task_limits"]["mechanism_assistant_coverage"]["reasoning_effort"] == "minimal"
        mechanism_id = kwargs["schema_name"].split("lolla_v1_coverage_")[-1]
        called["coverage"].append(mechanism_id)
        candidate = {
            "mechanism_id": mechanism_id,
            "vanilla_answer_coverage": "operationalized",
            "source_assistant_contribution_ids": ["assistant-turn-001"],
        }
        return {
            "operational_status": "ok",
            "compiled": kwargs["compile_candidate"](candidate),
            "provider_calls": 1,
            "provider_reported_cost_usd": 0.001,
        }

    output = tmp_path / "out"
    output.mkdir()
    result = run(
        contract,
        output=output,
        user_call_fn=fake_user_call,
        coverage_call_fn=fake_coverage_call,
    )

    assert len(called["user"]) == 9
    assert called["coverage"] == [COUNTERPRESSURE]
    assert result["provider_calls"] == 10
    assert result["joined"]["counts"]["total_model_calls"] == 10
    assert result["joined"]["counts"]["routing_mechanisms"] == 0
    assert result["user_factor_reasoning_effort"] == "low"
    assert result["assistant_coverage_reasoning_effort"] == "minimal"
