from __future__ import annotations

from pathlib import Path

from scripts.evals.run_simulated_reliability_lite_mechanism_probe_v1 import (
    _stable_schema,
    run,
)


def test_mechanism_schema_enum_order_is_stable() -> None:
    value = {"properties": {"state": {"enum": ["z", "a", "m"]}}}
    stable = _stable_schema(value)
    assert stable["properties"]["state"]["enum"] == ["a", "m", "z"]


def test_mechanism_probe_runs_one_pinned_call_without_runtime_effect(tmp_path: Path) -> None:
    contract = {
        "run_id": "test",
        "case_id": "v1-case06-industry-funded-lab",
        "arm_id": "v1-case06-industry-funded-lab-lite-probe",
        "base_runtime_contract": {
            "path": "docs/evals/simulated-reliability-v1-runtime-contract-v14-transfer.json"
        },
        "inputs": {
            "role_portfolio_path": "research/simulated-reliability-v1-lite-role-joins-2026-07-13/a1/case06-role-portfolio.json",
            "source_path": "research/simulated-reliability-corpus-v1-2026-07-12/naturalized-transfer-sources/v1-case06-industry-funded-lab.txt",
            "source_sha256": "3c6c0bc8937f06a639f3356b1009a754b7239e8cb510d1389a9174bbf52b0f22",
        },
        "operator": {
            "model": "google/gemini-3.1-flash-lite",
            "provider_slug": "google-vertex",
            "maximum_price_usd_per_million_tokens": {
                "prompt": 0.25,
                "completion": 1.5,
            },
        },
        "task_limit": {"max_output_tokens": 6000, "reasoning_effort": "low"},
        "repeat_id": "mechanism_probe",
        "seed": 797,
        "budget": {"maximum_provider_reported_cost_usd": 0.01},
    }
    seen = []

    def fake_call(**kwargs):
        seen.append(kwargs)
        return {
            "operational_status": "ok",
            "compiled": {
                "routing_projection": {
                    "pattern_nodes": [{"mechanism_id": "missing_reversal_condition"}]
                }
            },
            "provider_calls": 1,
            "provider_reported_cost_usd": 0.004,
            "served_model": "google/gemini-3.1-flash-lite",
            "served_provider": "Google",
        }

    output = tmp_path / "mechanism"
    output.mkdir()
    report = run(contract, output=output, call_fn=fake_call)
    assert len(seen) == 1
    assert seen[0]["contract"]["task_limits"]["mechanism"]["wire_mode"] == (
        "json_object_schema_in_prompt"
    )
    assert seen[0]["contract"]["provider_request"]["provider_only"] == [
        "google-vertex"
    ]
    assert report["provider_calls"] == 1
    assert report["runtime_effect"] == "none"
    assert report["routing_mechanism_ids"] == ["missing_reversal_condition"]
    assert report["cost_ceiling_met"] is True
    assert report["scalar_quality_score"] is None
