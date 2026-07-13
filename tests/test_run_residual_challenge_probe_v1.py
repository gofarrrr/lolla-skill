from scripts.evals.run_residual_challenge_probe_v1 import run


def test_runner_uses_low_discovery_and_minimal_conditional_coverage(tmp_path):
    contract = {
        "run_id": "test-residual",
        "case_id": "v1-case01-flood-infrastructure",
        "inputs": {
            "position_wrapper_path": "research/simulated-reliability-corpus-v1-2026-07-12/provider-free-role-input-preflight/transfer/v1-case01-flood-infrastructure/position-wrapper.json"
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
            "discovery": {"max_output_tokens": 1600, "reasoning_effort": "low"},
            "coverage": {"max_output_tokens": 1000, "reasoning_effort": "minimal"},
        },
        "seed_base": 1700,
        "budget": {"maximum_provider_reported_cost_usd": 0.01},
    }

    def fake_discovery_call(**kwargs):
        assert kwargs["contract"]["task_limits"]["residual_discovery"]["reasoning_effort"] == "low"
        candidate = {
            "candidate_id": "rc1",
            "candidate_kind": "time_horizon",
            "challenge_question": "Who owns and funds recurring operating capacity after capital funding ends?",
            "structural_pressure": "A capital commitment may depend on recurring operating capacity with a different funding horizon.",
            "applicability_condition": "The path requires continuing staffing, storage, transport, training, or review after installation.",
            "risk_if_ignored": "Installed protection may persist without the recurring capacity needed to deliver its service.",
            "force_boundary": "Do not assert that future funding disappears; ask for ownership and a renewal decision.",
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
        assert kwargs["contract"]["task_limits"]["residual_coverage"]["reasoning_effort"] == "minimal"
        return {
            "operational_status": "ok",
            "compiled": kwargs["compile_candidate"](
                {
                    "candidate_id": "rc1",
                    "joint_coverage": "not_covered",
                    "source_evidence_ids": [],
                }
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
    assert result["provider_reported_cost_usd"] == 0.002
    assert result["joined_portfolio"]["counts"]["active_working_set"] == 1
    assert result["joined_portfolio"]["graph_handoff"]["direct_graph_routing_allowed"] is False
