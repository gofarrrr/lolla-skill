from __future__ import annotations

from pathlib import Path

from scripts.evals.run_simulated_reliability_lite_stage2_probe_v1 import run


def test_lite_stage2_runs_one_pinned_call_without_scalar(tmp_path: Path) -> None:
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
        "repeat_id": "lite_stage2",
        "seed": 717,
        "budget": {"maximum_provider_reported_cost_usd": 0.02},
    }
    seen = []

    def fake_call(**kwargs):
        seen.append(kwargs["contract"])
        return {
            "operational_status": "ok",
            "compiled": {"observations": []},
            "provider_calls": 1,
            "provider_reported_cost_usd": 0.002,
            "served_model": "google/gemini-3.1-flash-lite",
            "served_provider": "Google",
            "duration_seconds": 1.0,
        }

    output = tmp_path / "stage2"
    output.mkdir()
    report = run(contract, output=output, call_fn=fake_call)
    assert len(seen) == 1
    assert seen[0]["provider_request"]["provider_only"] == ["google-vertex"]
    assert seen[0]["provider_request"]["allow_fallbacks"] is False
    assert seen[0]["provider_request"]["zdr"] is True
    assert report["provider_calls"] == 1
    assert report["cost_ceiling_met"] is True
    assert report["automatic_retries"] == 0
    assert report["scalar_quality_score"] is None
