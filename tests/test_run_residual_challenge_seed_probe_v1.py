from scripts.evals.run_residual_challenge_seed_probe_v1 import run


def test_seed_runner_defers_enrichment_and_calls_coverage_conditionally(tmp_path):
    contract = {
        "run_id": "test-seed",
        "case_id": "v1-case01-flood-infrastructure",
        "inputs": {
            "position_wrapper_path": "research/simulated-reliability-corpus-v1-2026-07-12/provider-free-role-input-preflight/transfer/v1-case01-flood-infrastructure/position-wrapper.json"
        },
        "base_runtime_contract": {"path": "docs/evals/simulated-reliability-v1-runtime-contract-v14-transfer.json"},
        "operator": {
            "model": "test-model",
            "provider_slug": "test-provider",
            "maximum_price_usd_per_million_tokens": {"prompt": 1, "completion": 1},
        },
        "task_limits": {
            "discovery": {"max_output_tokens": 1400, "reasoning_effort": "low"},
            "coverage": {"max_output_tokens": 600, "reasoning_effort": "minimal"},
        },
        "seed_base": 1800,
        "budget": {"maximum_provider_reported_cost_usd": 0.01},
    }

    def fake_discovery_call(**kwargs):
        candidate = {
            "candidate_id": "rc1",
            "candidate_kind": "time_horizon",
            "challenge_question": "Who funds recurring operating capacity after capital funding ends?",
            "source_evidence_ids": ["e024", "e078", "e099"],
            "claim_status": "question_not_external_fact",
        }
        return {
            "operational_status": "ok",
            "compiled": kwargs["compile_candidate"]({"candidates": [candidate]}),
            "provider_calls": 1,
            "provider_reported_cost_usd": 0.001,
        }

    def fake_coverage_call(**kwargs):
        return {
            "operational_status": "ok",
            "compiled": kwargs["compile_candidate"](
                {"candidate_id": "rc1", "joint_coverage": "not_covered", "source_evidence_ids": []}
            ),
            "provider_calls": 1,
            "provider_reported_cost_usd": 0.001,
        }

    output = tmp_path / "out"
    output.mkdir()
    result = run(
        contract,
        output=output,
        discovery_call_fn=fake_discovery_call,
        coverage_call_fn=fake_coverage_call,
    )
    assert result["provider_calls"] == 2
    assert result["enrichment_calls"] == 0
    assert result["joined_seed_portfolio"]["counts"]["active_working_set"] == 1
    assert result["joined_seed_portfolio"]["portfolio_items"][0]["enrichment_status"] == "required_before_consumer_or_graph"
