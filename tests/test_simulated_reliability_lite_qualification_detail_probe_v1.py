from __future__ import annotations

from pathlib import Path

from scripts.evals.run_simulated_reliability_lite_qualification_detail_probe_v1 import (
    run,
)


def test_detail_probe_runs_one_selected_evidence_call(tmp_path: Path) -> None:
    contract = {
        "run_id": "test",
        "base_runtime_contract": {
            "path": "docs/evals/simulated-reliability-v1-runtime-contract-v14-transfer.json"
        },
        "source": {
            "case_id": "v1-case06-industry-funded-lab",
            "position_wrapper_path": "research/simulated-reliability-corpus-v1-2026-07-12/provider-free-role-input-preflight/transfer/v1-case06-industry-funded-lab/position-wrapper.json",
        },
        "review": {
            "call_artifact_path": "research/simulated-reliability-v1-lite-qualification-review-2026-07-13/a1/v1-case06-industry-funded-lab/call-01-qualification_review-result.json"
        },
        "operator": {
            "model": "google/gemini-3.1-flash-lite",
            "provider_slug": "google-vertex",
            "maximum_price_usd_per_million_tokens": {
                "prompt": 0.25,
                "completion": 1.5,
            },
        },
        "task_limit": {"max_output_tokens": 2500, "reasoning_effort": "medium"},
        "repeat_id": "qualification_detail",
        "seed": 787,
        "budget": {"maximum_provider_reported_cost_usd": 0.005},
    }
    seen = []

    def fake_call(**kwargs):
        seen.append(kwargs)
        return {
            "operational_status": "ok",
            "compiled": {"observations": [{"terminal_state": "admitted"}]},
            "provider_calls": 1,
            "provider_reported_cost_usd": 0.001,
            "served_model": "google/gemini-3.1-flash-lite",
            "served_provider": "Google",
        }

    output = tmp_path / "detail"
    output.mkdir()
    report = run(contract, output=output, call_fn=fake_call)
    assert len(seen) == 1
    assert seen[0]["task_id"] == "qualification_detail"
    assert seen[0]["contract"]["task_limits"]["qualification_detail"][
        "wire_mode"
    ] == "strict_json_schema"
    assert report["selected_review_evidence_ids"] == ["e052", "e097"]
    assert report["full_conversation_repeated"] is False
    assert report["provider_calls"] == 1
    assert report["cost_ceiling_met"] is True
    assert report["scalar_quality_score"] is None
