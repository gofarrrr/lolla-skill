from __future__ import annotations

from pathlib import Path

from scripts.evals.run_simulated_reliability_lite_mechanism_microtask_probe_v1 import (
    run,
)


def test_difficult_trio_runs_three_strict_calls_without_model_routing(tmp_path: Path) -> None:
    mechanism_ids = [
        "acknowledged_constraint_not_gated",
        "counterpressure_acknowledged_not_integrated",
        "missing_reversal_condition",
    ]
    contract = {
        "run_id": "test",
        "case_id": "v1-case06-industry-funded-lab",
        "base_runtime_contract": {
            "path": "docs/evals/simulated-reliability-v1-runtime-contract-v14-transfer.json"
        },
        "inputs": {
            "parent_mechanism_request_path": "research/simulated-reliability-v1-lite-mechanism-2026-07-13/a1/mechanism-request.json"
        },
        "mechanism_ids": mechanism_ids,
        "operator": {
            "model": "google/gemini-3.1-flash-lite",
            "provider_slug": "google-vertex",
            "maximum_price_usd_per_million_tokens": {
                "prompt": 0.25,
                "completion": 1.5,
            },
        },
        "task_limit": {"max_output_tokens": 1500, "reasoning_effort": "medium"},
        "tasks": {
            mechanism_id: {
                "repeat_id": "micro_" + str(index),
                "seed": 800 + index,
            }
            for index, mechanism_id in enumerate(mechanism_ids, 1)
        },
        "budget": {"maximum_provider_reported_cost_usd": 0.02},
    }
    seen = []

    def fake_call(**kwargs):
        seen.append(kwargs)
        mechanism_id = kwargs["schema"]["properties"]["mechanism_id"]["enum"][0]
        compiled = {
            "assessment": {
                "mechanism_id": mechanism_id,
                "routing_disposition": "preserve_no_route",
            }
        }
        return {
            "operational_status": "ok",
            "compiled": compiled,
            "provider_calls": 1,
            "provider_reported_cost_usd": 0.002,
            "served_model": "google/gemini-3.1-flash-lite",
            "served_provider": "Google",
        }

    output = tmp_path / "microtasks"
    output.mkdir()
    report = run(contract, output=output, call_fn=fake_call)
    assert len(seen) == 3
    assert all(row["task_id"] == "mechanism_microtask" for row in seen)
    assert all(
        row["contract"]["task_limits"]["mechanism_microtask"]["wire_mode"]
        == "strict_json_schema"
        for row in seen
    )
    assert all(
        "routing_disposition" not in row["schema"]["properties"] for row in seen
    )
    assert report["provider_calls"] == 3
    assert report["provider_reported_cost_usd"] == 0.006
    assert report["routing_disposition_model_authored"] is False
    assert report["runtime_effect"] == "none"
    assert report["scalar_quality_score"] is None
