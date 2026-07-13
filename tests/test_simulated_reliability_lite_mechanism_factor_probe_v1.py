import json

from scripts.evals.run_simulated_reliability_lite_mechanism_factor_probe_v1 import run


def test_factor_probe_joins_resolved_and_covered(monkeypatch, tmp_path):
    parent = {"packet": {
        "case_id": "case-1",
        "role_records": [
            {"role_record_id": "starting-1", "role": "starting"},
            {"role_record_id": "current-1", "role": "current"}
        ],
        "assistant_contributions": [
            {"contribution_id": "assistant-turn-001", "text": "Add a threshold."}
        ]
    }}
    (tmp_path / "parent.json").write_text(json.dumps(parent))
    monkeypatch.setattr(
        "scripts.evals.run_simulated_reliability_lite_mechanism_factor_probe_v1.ROOT",
        tmp_path
    )
    monkeypatch.setattr(
        "scripts.evals.run_simulated_reliability_lite_mechanism_factor_probe_v1.load_contract",
        lambda path: {"provider_request": {}, "task_limits": {}, "seeds": {}}
    )
    contract = {
        "run_id": "run-1", "case_id": "case-1",
        "mechanism_id": "counterpressure_acknowledged_not_integrated",
        "inputs": {"parent_mechanism_request_path": "parent.json"},
        "base_runtime_contract": {"path": "base.json"},
        "operator": {"model": "model", "provider_slug": "provider", "maximum_price_usd_per_million_tokens": {"prompt": 1, "completion": 1}},
        "task_limit": {"max_output_tokens": 1000, "reasoning_effort": "low"},
        "seeds": {"user_factor": 1, "assistant_coverage": 2},
        "budget": {"maximum_provider_reported_cost_usd": 0.01}
    }

    def fake_call(**kwargs):
        if kwargs["task_id"] == "mechanism_user_factor":
            candidate = {
                "mechanism_id": contract["mechanism_id"],
                "mechanism_observation": "observed",
                "integration_status": "integrated",
                "pattern_state": "not_applicable",
                "source_role_record_ids": ["starting-1", "current-1"]
            }
        else:
            candidate = {
                "mechanism_id": contract["mechanism_id"],
                "vanilla_answer_coverage": "operationalized",
                "source_assistant_contribution_ids": ["assistant-turn-001"]
            }
        return {"operational_status": "ok", "compiled": kwargs["compile_candidate"](candidate), "provider_calls": 1, "provider_reported_cost_usd": 0.001}

    out = tmp_path / "out"
    out.mkdir()
    result = run(contract, output=out, call_fn=fake_call)
    assert result["joined"]["assessment"]["user_process_status"] == "resolved"
    assert result["joined"]["assessment"]["routing_disposition"] == "preserve_no_route"
