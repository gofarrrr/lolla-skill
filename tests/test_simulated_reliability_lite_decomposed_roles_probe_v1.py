from __future__ import annotations

from pathlib import Path

from scripts.evals.run_simulated_reliability_lite_decomposed_roles_probe_v1 import (
    run,
)


def test_decomposed_probe_runs_two_strict_single_role_calls(tmp_path: Path) -> None:
    contract = {
        "run_id": "test",
        "base_runtime_contract": {
            "path": "docs/evals/simulated-reliability-v1-runtime-contract-v14-transfer.json"
        },
        "source": {
            "case_id": "v1-case06-industry-funded-lab",
            "position_wrapper_path": "research/simulated-reliability-corpus-v1-2026-07-12/provider-free-role-input-preflight/transfer/v1-case06-industry-funded-lab/position-wrapper.json",
        },
        "operator": {
            "model": "google/gemini-3.1-flash-lite",
            "provider_slug": "google-vertex",
            "maximum_price_usd_per_million_tokens": {
                "prompt": 0.25,
                "completion": 1.5,
            },
        },
        "task_limits": {
            "current": {
                "max_output_tokens": 4000,
                "reasoning_effort": "medium",
                "repeat_id": "decomposed_current",
                "seed": 727,
            },
            "qualification": {
                "max_output_tokens": 4000,
                "reasoning_effort": "medium",
                "repeat_id": "decomposed_qualification",
                "seed": 737,
            },
        },
        "budget": {"maximum_provider_reported_cost_usd": 0.02},
    }
    seen = []

    def fake_call(**kwargs):
        seen.append(kwargs)
        return {
            "operational_status": "ok",
            "compiled": {"observations": [{"terminal_state": "admitted"}]},
            "provider_calls": 1,
            "provider_reported_cost_usd": 0.002,
            "served_model": "google/gemini-3.1-flash-lite",
            "served_provider": "Google",
        }

    output = tmp_path / "decomposed"
    output.mkdir()
    report = run(contract, output=output, call_fn=fake_call)
    assert [row["task_id"] for row in seen] == ["current", "qualification"]
    assert all(
        row["contract"]["task_limits"][row["task_id"]]["wire_mode"]
        == "strict_json_schema"
        for row in seen
    )
    assert all(
        row["contract"]["provider_request"]["provider_only"]
        == ["google-vertex"]
        for row in seen
    )
    assert report["provider_calls"] == 2
    assert report["provider_reported_cost_usd"] == 0.004
    assert report["deterministic_semantic_inference"] is False
    assert report["joined_for_runtime"] is False
    assert report["scalar_quality_score"] is None
