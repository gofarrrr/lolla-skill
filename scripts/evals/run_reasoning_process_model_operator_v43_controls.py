#!/usr/bin/env python3
"""Run two stronger v4.3 model/operator controls with durable custody."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_chronological_shard_reader_v43 import (  # noqa: E402
    build_shard_prompts_v43,
    compile_shard_response_recordwise_v43,
    shard_response_schema_v43,
)
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes  # noqa: E402
from scripts.evals.reasoning_process_model_operator_transport import run_model_operator_job  # noqa: E402
from scripts.evals.run_conversation_state_microtask_probe import _load_env  # noqa: E402
from scripts.evals.run_reasoning_process_phase4_transfer import _load, _sha, _write  # noqa: E402

CONTRACT_SCHEMA = "lolla.reasoning_process_model_operator_v43_controls_contract.v1"
AUTH_SCHEMA = "lolla.reasoning_process_model_operator_v43_controls_authorization.v1"


def validate_contract(contract: dict, contract_path: Path) -> dict:
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise RuntimeError("unexpected v4.3 controls contract")
    if contract.get("status") != "frozen_before_two_stronger_v43_control_calls":
        raise RuntimeError("v4.3 controls contract is not frozen")
    for item in contract["frozen_inputs"]:
        if _sha(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"frozen input drifted: {item['path']}")
    wrapper = _load(ROOT / contract["packet"]["path"])
    prompts = build_shard_prompts_v43(wrapper)
    schema = shard_response_schema_v43("position_and_decision_trajectory")
    observed = {
        "system_prompt_sha256": prompts["system_prompt_sha256"],
        "user_prompt_sha256": prompts["user_prompt_sha256"],
        "response_schema_sha256": sha256_bytes(canonical_json_bytes(schema)),
    }
    if any(contract["request_contract"][key] != value for key, value in observed.items()):
        raise RuntimeError("v4.3 controls prompt or schema drifted")
    expected = {
        ("deepseek/deepseek-v4-pro", "alibaba"),
        ("minimax/minimax-m3", "parasail"),
    }
    jobs = contract["jobs"]
    if len(jobs) != 2 or {(job["model"], job["provider_slug"]) for job in jobs} != expected:
        raise RuntimeError("v4.3 control pairs drifted")
    if contract["budget"]["maximum_provider_calls"] != 2:
        raise RuntimeError("v4.3 controls budget drifted")
    if not all(contract["custody"].values()):
        raise RuntimeError("v4.3 controls custody drifted")
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
        raise RuntimeError("v4.3 controls call configuration drifted")
    return {
        "status": "model_operator_v43_controls_contract_valid",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "provider_calls_made": 0,
    }


def validate_authorization(value: dict, *, contract: dict, contract_path: Path) -> None:
    expected = {
        "schema_version": AUTH_SCHEMA,
        "status": "authorized_once_after_v43_flash_source_review_failure",
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
        raise RuntimeError("v4.3 controls authorization drifted")


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
    aggregate_path = output_dir / "result.json"
    if not output_dir.is_dir() or aggregate_path.exists():
        raise RuntimeError("v4.3 controls output already exists or directory is absent")
    _load_env(args.env_file.resolve())
    wrapper = _load(ROOT / contract["packet"]["path"])
    results = []
    for index, job in enumerate(contract["jobs"], start=1):
        started_path = output_dir / f"call-{index:02d}-started.json"
        result_path = output_dir / f"call-{index:02d}-result.json"
        if started_path.exists() or result_path.exists():
            raise RuntimeError(f"v4.3 control {index} already started; rerun forbidden")
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
        result = run_model_operator_job(
            contract=contract,
            job=job,
            wrapper=wrapper,
            build_prompts=build_shard_prompts_v43,
            build_schema=shard_response_schema_v43,
            compile_response=compile_shard_response_recordwise_v43,
            response_schema_name="lolla_reasoning_process_stance_object_v43_control",
        )
        _write(result_path, result)
        results.append(result)
    aggregate = {
        "schema_version": "lolla.reasoning_process_model_operator_v43_controls_result.v1",
        "status": "two_stronger_v43_control_calls_preserved",
        "run_id": contract["run_id"],
        "calls": results,
        "provider_request_count": sum(item.get("provider_calls", 0) for item in results),
        "wire_accepted_count": sum(item.get("wire_schema_accepted") is True for item in results),
        "admitted_pair_count": sum(item.get("admitted_record_count", 0) > 0 for item in results),
        "semantic_review_status": "synthetic_source_review_required",
        "boundary": contract["boundary"],
    }
    _write(aggregate_path, aggregate)
    print(
        json.dumps(
            {
                "provider_request_count": aggregate["provider_request_count"],
                "wire_accepted_count": aggregate["wire_accepted_count"],
                "admitted_pair_count": aggregate["admitted_pair_count"],
                "calls": [
                    {
                        "job_id": item["job_id"],
                        "operational_status": item["operational_status"],
                        "terminal_disposition": item.get(
                            "deterministic_terminal_disposition", "not_observed"
                        ),
                        "admitted_record_count": item.get("admitted_record_count", 0),
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
