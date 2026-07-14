from __future__ import annotations

from pathlib import Path

from scripts.evals.run_simulated_reliability_model_value_probe_v1 import run


def test_model_value_probe_runs_exactly_two_jobs_without_scalar(tmp_path: Path) -> None:
    contract = {
        "base_runtime_contract": {
            "path": "docs/evals/simulated-reliability-v1-runtime-contract-v14-transfer.json"
        },
        "microtask": {
            "case_id": "v1-case06-industry-funded-lab",
            "role_request_bundle_path": "research/simulated-reliability-corpus-v1-2026-07-12/provider-free-role-input-preflight/transfer/v1-case06-industry-funded-lab/role-request-bundle.json",
        },
        "repeat_id": "model_value_probe",
        "seed": 707,
        "jobs": [
            {
                "job_id": "deepseek",
                "model": "deepseek/deepseek-v4-flash",
                "provider_slug": "deepinfra",
                "maximum_price_usd_per_million_tokens": {
                    "prompt": 0.09,
                    "completion": 0.18,
                },
                "reasoning_effort": "medium",
            },
            {
                "job_id": "gemini-lite",
                "model": "google/gemini-3.1-flash-lite",
                "provider_slug": "google-vertex",
                "maximum_price_usd_per_million_tokens": {
                    "prompt": 0.25,
                    "completion": 1.5,
                },
                "reasoning_effort": "medium",
            },
        ],
        "run_id": "test",
        "budget": {"maximum_provider_reported_cost_usd": 0.02},
    }
    seen = []

    def fake_call(**kwargs):
        seen.append(
            (
                kwargs["contract"]["provider_request"]["model"],
                kwargs["contract"]["provider_request"]["provider_only"],
                kwargs["contract"]["provider_request"]["max_price_usd_per_million_tokens"],
            )
        )
        return {
            "operational_status": "ok",
            "compiled": {"records": [{"terminal_state": "admitted"}]},
            "provider_calls": 1,
            "provider_reported_cost_usd": 0.001,
            "served_model": kwargs["contract"]["provider_request"]["model"],
            "served_provider": "provider",
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 100,
                "completion_tokens_details": {"reasoning_tokens": 0},
            },
        }

    output = tmp_path / "probe"
    output.mkdir()
    report = run(contract, output=output, call_fn=fake_call)
    assert len(seen) == 2
    assert seen[0] == (
        "deepseek/deepseek-v4-flash",
        ["deepinfra"],
        {"prompt": 0.09, "completion": 0.18},
    )
    assert report["provider_calls"] == 2
    assert report["provider_reported_cost_usd"] == 0.002
    assert report["cost_ceiling_met"] is True
    assert report["automatic_retries"] == 0
    assert report["scalar_quality_score"] is None
