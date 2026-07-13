from scripts.evals.run_simulated_reliability_lite_factored_completion_v1 import run


MISSING = "counterpressure_acknowledged_not_integrated"


def test_completion_preserves_eight_users_and_calls_only_needed_coverage(tmp_path):
    contract = {
        "run_id": "test-completion",
        "case_id": "v1-case01-flood-infrastructure",
        "missing_user_mechanism_id": MISSING,
        "inputs": {
            "parent_mechanism_request_path": "research/simulated-reliability-v1-transfer-2026-07-12/t1/v1-case01-flood-infrastructure-primary/mechanism-request.json",
            "partial_full_case_result_path": "research/simulated-reliability-v1-lite-full-factored-case01-2026-07-13/t1/result.json",
        },
        "base_runtime_contract": {
            "path": "docs/evals/simulated-reliability-v1-runtime-contract-v14-transfer.json"
        },
        "operator": {
            "model": "test-model",
            "provider_slug": "test-provider",
            "maximum_price_usd_per_million_tokens": {"prompt": 1, "completion": 1},
        },
        "task_limit": {"max_output_tokens": 1000, "reasoning_effort": "minimal"},
        "seed_base": 1600,
        "budget": {"maximum_provider_reported_cost_usd": 0.02},
    }

    def fake_user_call(**kwargs):
        candidate = {
            "mechanism_id": MISSING,
            "mechanism_observation": "observed",
            "integration_status": "not_integrated",
            "pattern_state": "present",
            "source_role_record_ids": ["rprolev22-qualification-01-aaa69b13c9b0e2"],
        }
        return {
            "operational_status": "ok",
            "compiled": kwargs["compile_candidate"](candidate),
            "provider_calls": 1,
            "provider_reported_cost_usd": 0.001,
        }

    def fake_coverage_call(**kwargs):
        mechanism_id = kwargs["schema_name"].split("lolla_v1_coverage_completion_")[-1]
        if mechanism_id == MISSING:
            candidate = {
                "mechanism_id": mechanism_id,
                "vanilla_answer_coverage": "not_covered",
                "source_assistant_contribution_ids": [],
            }
        else:
            candidate = {
                "mechanism_id": mechanism_id,
                "vanilla_answer_coverage": "operationalized",
                "source_assistant_contribution_ids": ["assistant-turn-007"],
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

    assert result["preserved_user_factor_count"] == 8
    assert result["provider_calls"] == 3
    assert result["coverage_call_plan"]["assistant_coverage_call_count"] == 2
    assert result["joined_full_portfolio"]["counts"]["routing_mechanisms"] == 1
    assert result["combined_case_provider_calls"] == 12
