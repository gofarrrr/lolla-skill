import json

from scripts.evals.run_simulated_reliability_lite_mechanism_split_probe_v1 import run


def test_split_probe_joins_two_model_tasks(monkeypatch, tmp_path):
    parent = {
        "packet": {
            "case_id": "case-1",
            "role_records": [
                {"role_record_id": "starting-1", "role": "starting"},
                {"role_record_id": "current-1", "role": "current"},
            ],
            "assistant_contributions": [
                {"contribution_id": "assistant-turn-001", "text": "Use a test."}
            ],
        }
    }
    source = tmp_path / "parent.json"
    source.write_text(json.dumps(parent))
    contract = {
        "run_id": "run-1",
        "case_id": "case-1",
        "mechanism_id": "counterpressure_acknowledged_not_integrated",
        "inputs": {"parent_mechanism_request_path": "parent.json"},
        "base_runtime_contract": {"path": "unused.json"},
        "operator": {
            "model": "model",
            "provider_slug": "provider",
            "maximum_price_usd_per_million_tokens": {"prompt": 1, "completion": 1},
        },
        "task_limit": {"max_output_tokens": 100, "reasoning_effort": "low"},
        "seeds": {"user_status": 1, "assistant_coverage": 2},
        "budget": {"maximum_provider_reported_cost_usd": 0.01},
    }
    runtime = {
        "provider_request": {}, "task_limits": {}, "seeds": {}
    }
    import scripts.evals.run_simulated_reliability_lite_mechanism_split_probe_v1 as module
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "load_contract", lambda path: runtime)

    def fake_call(**kwargs):
        if kwargs["task_id"] == "mechanism_user_status":
            candidate = {
                "mechanism_id": contract["mechanism_id"],
                "user_process_status": "resolved",
                "pattern_state": "not_applicable",
                "source_role_record_ids": ["starting-1", "current-1"],
            }
        else:
            candidate = {
                "mechanism_id": contract["mechanism_id"],
                "vanilla_answer_coverage": "operationalized",
                "source_assistant_contribution_ids": ["assistant-turn-001"],
            }
        return {
            "operational_status": "ok",
            "compiled": kwargs["compile_candidate"](candidate),
            "provider_calls": 1,
            "provider_reported_cost_usd": 0.001,
        }

    report = run(contract, output=tmp_path / "out", call_fn=fake_call)
    assert report["provider_calls"] == 2
    assert report["provider_reported_cost_usd"] == 0.002
    assert report["joined"]["assessment"]["routing_disposition"] == "preserve_no_route"
