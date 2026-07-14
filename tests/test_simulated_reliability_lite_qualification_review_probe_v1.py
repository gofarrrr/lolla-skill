from __future__ import annotations

from pathlib import Path

from scripts.evals.run_simulated_reliability_lite_qualification_review_probe_v1 import (
    run,
)


def test_review_probe_runs_present_and_quiet_without_scalar(tmp_path: Path) -> None:
    base = (
        "research/simulated-reliability-corpus-v1-2026-07-12/"
        "provider-free-role-input-preflight/transfer"
    )
    contract = {
        "run_id": "test",
        "base_runtime_contract": {
            "path": "docs/evals/simulated-reliability-v1-runtime-contract-v14-transfer.json"
        },
        "operator": {
            "model": "google/gemini-3.1-flash-lite",
            "provider_slug": "google-vertex",
            "maximum_price_usd_per_million_tokens": {
                "prompt": 0.25,
                "completion": 1.5,
            },
        },
        "task_limit": {"max_output_tokens": 1500, "reasoning_effort": "medium"},
        "cases": [
            {
                "case_id": "v1-case06-industry-funded-lab",
                "expected_outcome_class": "present",
                "position_wrapper_path": f"{base}/v1-case06-industry-funded-lab/position-wrapper.json",
                "repeat_id": "review_present",
                "seed": 747,
            },
            {
                "case_id": "v1-case07-cooperative-scheduling",
                "expected_outcome_class": "quiet",
                "position_wrapper_path": f"{base}/v1-case07-cooperative-scheduling/position-wrapper.json",
                "repeat_id": "review_quiet",
                "seed": 757,
            },
        ],
        "budget": {"maximum_provider_reported_cost_usd": 0.01},
    }
    seen = []

    def fake_call(**kwargs):
        seen.append(kwargs)
        return {
            "operational_status": "ok",
            "compiled": {"outcome": "unresolved_qualification_present"},
            "provider_calls": 1,
            "provider_reported_cost_usd": 0.001,
            "served_model": "google/gemini-3.1-flash-lite",
            "served_provider": "Google",
        }

    output = tmp_path / "reviews"
    output.mkdir()
    report = run(contract, output=output, call_fn=fake_call)
    assert len(seen) == 2
    assert all(row["task_id"] == "qualification_review" for row in seen)
    assert all(
        row["contract"]["task_limits"]["qualification_review"]["wire_mode"]
        == "strict_json_schema"
        for row in seen
    )
    assert report["provider_calls"] == 2
    assert report["provider_reported_cost_usd"] == 0.002
    assert report["cost_ceiling_met"] is True
    assert report["deterministic_semantic_inference"] is False
    assert report["scalar_quality_score"] is None
