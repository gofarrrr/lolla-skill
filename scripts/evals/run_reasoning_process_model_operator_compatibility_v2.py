#!/usr/bin/env python3
"""Run provider-pinned compatibility calls with durable per-call custody."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_chronological_shard_reader_v42 import (  # noqa: E402
    build_shard_prompts_v42,
    shard_response_schema_v42,
)
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes  # noqa: E402
from scripts.evals.run_conversation_state_microtask_probe import _load_env  # noqa: E402
from scripts.evals.run_reasoning_process_model_operator_compatibility import _run_job  # noqa: E402
from scripts.evals.run_reasoning_process_phase4_transfer import _load, _sha, _write  # noqa: E402

CONTRACT_SCHEMA = "lolla.reasoning_process_model_operator_compatibility_contract.v2"
AUTH_SCHEMA = "lolla.reasoning_process_model_operator_compatibility_authorization.v2"


def validate_contract(contract: dict, contract_path: Path) -> dict:
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise RuntimeError("unexpected compatibility recovery contract")
    if contract.get("status") != "frozen_after_custody_incident_before_recovery_calls":
        raise RuntimeError("compatibility recovery contract is not frozen")
    for item in contract["frozen_inputs"]:
        if _sha(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"frozen input drifted: {item['path']}")
    packet_path = ROOT / contract["packet"]["path"]
    if _sha(packet_path) != contract["packet"]["sha256"]:
        raise RuntimeError("synthetic packet drifted")
    wrapper = _load(packet_path)
    prompts = build_shard_prompts_v42(wrapper)
    schema = shard_response_schema_v42("position_and_decision_trajectory")
    observed = {
        "system_prompt_sha256": prompts["system_prompt_sha256"],
        "user_prompt_sha256": prompts["user_prompt_sha256"],
        "response_schema_sha256": sha256_bytes(canonical_json_bytes(schema)),
    }
    if any(contract["request_contract"][key] != value for key, value in observed.items()):
        raise RuntimeError("compatibility request contract drifted")
    jobs = contract.get("jobs")
    if not isinstance(jobs, list) or len(jobs) != 2:
        raise RuntimeError("exactly two recovery jobs are required")
    expected = {
        ("deepseek/deepseek-v4-flash", "deepinfra"),
        ("z-ai/glm-5.2", "deepinfra"),
    }
    if {(job["model"], job["provider_slug"]) for job in jobs} != expected:
        raise RuntimeError("recovery shortlist drifted")
    config = contract["call_configuration"]
    if config != {
        "provider": "openrouter",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "wire_mode": "strict_json_schema",
        "temperature": 0.0,
        "seed": 0,
        "reasoning_enabled": False,
        "max_output_tokens": 1600,
        "provider_timeout_seconds": 90,
        "require_supported_parameters": True,
        "allow_provider_fallbacks": False,
        "automatic_retries": 0,
        "response_healing": False,
        "parallel_calls": False,
    }:
        raise RuntimeError("recovery call configuration drifted")
    if contract["budget"]["maximum_provider_calls"] != 2:
        raise RuntimeError("recovery budget drifted")
    if contract["custody"]["write_started_marker_before_each_call"] is not True:
        raise RuntimeError("started-marker custody is not enabled")
    if contract["custody"]["write_result_before_next_call"] is not True:
        raise RuntimeError("per-call result custody is not enabled")
    return {
        "status": "model_operator_compatibility_recovery_contract_valid",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "provider_calls_made": 0,
    }


def validate_authorization(value: dict, *, contract: dict, contract_path: Path) -> None:
    expected = {
        "schema_version": AUTH_SCHEMA,
        "status": "authorized_once_after_unknown_custody_incident",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": _sha(contract_path),
        "run_id": contract["run_id"],
        "maximum_provider_calls": 2,
        "automatic_retries": 0,
        "semantic_retries": 0,
        "fallback_models": 0,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
    }
    if value != expected:
        raise RuntimeError("compatibility recovery authorization drifted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    contract_path = args.contract.resolve()
    contract = _load(contract_path)
    validation = validate_contract(contract, contract_path)
    if args.dry_run:
        print(json.dumps(validation, indent=2, sort_keys=True))
        return 0
    if args.authorization is None or args.env_file is None or args.output_dir is None:
        raise RuntimeError("execution arguments are missing")
    validate_authorization(
        _load(args.authorization.resolve()), contract=contract, contract_path=contract_path
    )
    output_dir = args.output_dir.resolve()
    if not output_dir.is_dir():
        raise RuntimeError("recovery output directory does not exist")
    aggregate_path = output_dir / "result.json"
    if aggregate_path.exists():
        raise RuntimeError("compatibility recovery aggregate already exists")
    _load_env(args.env_file.resolve())
    wrapper = _load(ROOT / contract["packet"]["path"])
    results = []
    for index, job in enumerate(contract["jobs"], start=1):
        started_path = output_dir / f"call-{index:02d}-started.json"
        result_path = output_dir / f"call-{index:02d}-result.json"
        if started_path.exists() or result_path.exists():
            raise RuntimeError(f"call {index} already started; rerun forbidden")
        _write(
            started_path,
            {
                "schema_version": "lolla.reasoning_process_compatibility_call_started.v1",
                "status": "provider_call_may_have_started_do_not_rerun_if_result_missing",
                "run_id": contract["run_id"],
                "job_id": job["job_id"],
                "model": job["model"],
                "provider_slug": job["provider_slug"],
                "started_at_utc": datetime.now(timezone.utc).isoformat(),
            },
        )
        result = _run_job(contract=contract, job=job, wrapper=wrapper)
        _write(result_path, result)
        results.append(result)
    aggregate = {
        "schema_version": "lolla.reasoning_process_model_operator_compatibility_result.v2",
        "status": "two_recovery_calls_with_per_call_custody_preserved",
        "run_id": contract["run_id"],
        "calls": results,
        "provider_request_count": sum(item.get("provider_calls", 0) for item in results),
        "wire_accepted_count": sum(item.get("wire_schema_accepted") is True for item in results),
        "strict_generation_pass_count": sum(
            item.get("strict_schema_generation_pass") is True for item in results
        ),
        "semantic_review_status": "not_applicable_synthetic_compatibility_only",
        "boundary": contract["boundary"],
    }
    _write(aggregate_path, aggregate)
    print(
        json.dumps(
            {
                "provider_request_count": aggregate["provider_request_count"],
                "wire_accepted_count": aggregate["wire_accepted_count"],
                "strict_generation_pass_count": aggregate["strict_generation_pass_count"],
                "calls": [
                    {
                        "job_id": item["job_id"],
                        "operational_status": item["operational_status"],
                        "wire_schema_accepted": item.get("wire_schema_accepted", False),
                        "strict_schema_generation_pass": item.get(
                            "strict_schema_generation_pass", False
                        ),
                        "estimated_cost_usd": item.get("estimated_cost_usd"),
                    }
                    for item in results
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
