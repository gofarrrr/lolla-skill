from __future__ import annotations

from pathlib import Path

from scripts.evals.run_simulated_reliability_lite_stage2b_strict_probe_v1 import run


def test_stage2b_changes_only_wire_mode_for_one_call(tmp_path: Path) -> None:
    contract = {
        "run_id": "test",
        "base_runtime_contract": {
            "path": "docs/evals/simulated-reliability-v1-runtime-contract-v14-transfer.json"
        },
        "microtask": {
            "case_id": "v1-case06-industry-funded-lab",
            "role_request_bundle_path": "research/simulated-reliability-corpus-v1-2026-07-12/provider-free-role-input-preflight/transfer/v1-case06-industry-funded-lab/role-request-bundle.json",
            "position_wrapper_path": "research/simulated-reliability-corpus-v1-2026-07-12/provider-free-role-input-preflight/transfer/v1-case06-industry-funded-lab/position-wrapper.json"
        },
        "operator": {
            "model": "google/gemini-3.1-flash-lite",
            "provider_slug": "google-vertex",
            "maximum_price_usd_per_million_tokens": {
                "prompt": 0.25,
                "completion": 1.5,
            },
            "reasoning_effort": "medium",
        },
        "repeat_id": "lite_stage2b",
        "seed": 717,
        "budget": {"maximum_provider_reported_cost_usd": 0.02},
    }
    seen = []

    def fake_call(**kwargs):
        seen.append(kwargs)
        return {
            "operational_status": "ok",
            "compiled": {
                "observations": [
                    {"terminal_state": "admitted"},
                    {"terminal_state": "admitted"},
                ]
            },
            "provider_calls": 1,
            "provider_reported_cost_usd": 0.003,
            "served_model": "google/gemini-3.1-flash-lite",
            "served_provider": "Google",
        }

    output = tmp_path / "stage2b"
    output.mkdir()
    report = run(contract, output=output, call_fn=fake_call)
    assert len(seen) == 1
    runtime = seen[0]["contract"]
    assert runtime["task_limits"]["current_qualification"]["wire_mode"] == (
        "strict_json_schema"
    )
    assert runtime["provider_request"]["provider_only"] == ["google-vertex"]
    assert runtime["provider_request"]["allow_fallbacks"] is False
    assert runtime["provider_request"]["zdr"] is True
    assert report["admitted_observation_count"] == 2
    assert report["provider_calls"] == 1
    assert report["scalar_quality_score"] is None
