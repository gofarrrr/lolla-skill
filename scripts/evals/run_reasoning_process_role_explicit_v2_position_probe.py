#!/usr/bin/env python3
"""Run the frozen one-call role-explicit Case-05 position probe."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_chronological_shard_reader_v2 import (  # noqa: E402
    build_shard_prompts_v2,
    shard_response_schema_v2,
)
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes  # noqa: E402
from scripts.evals.run_conversation_state_microtask_probe import _load_env  # noqa: E402
from scripts.evals.run_reasoning_process_phase4_transfer import (  # noqa: E402
    MODEL,
    _load,
    _sha,
    _write,
    run_job,
)


CONTRACT_SCHEMA = "lolla.reasoning_process_role_explicit_v2_position_probe_contract.v1"
AUTH_SCHEMA = "lolla.reasoning_process_role_explicit_v2_position_probe_authorization.v1"


def validate_contract(contract: dict, contract_path: Path) -> dict:
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise RuntimeError("unexpected role-explicit position probe contract")
    if contract.get("status") != "frozen_before_one_provider_call":
        raise RuntimeError("position probe contract is not frozen")
    for item in contract["frozen_inputs"]:
        if _sha(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"frozen input drifted: {item['path']}")
    if _sha(ROOT / contract["model_snapshot"]["path"]) != contract["model_snapshot"]["sha256"]:
        raise RuntimeError("model snapshot drifted")
    job = contract["job"]
    packet_path = ROOT / job["packet_path"]
    if _sha(packet_path) != job["packet_sha256"]:
        raise RuntimeError("position probe packet drifted")
    wrapper = _load(packet_path)
    prompts = build_shard_prompts_v2(wrapper)
    schema = shard_response_schema_v2(job["view_kind"])
    observed = {
        "system_prompt_sha256": prompts["system_prompt_sha256"],
        "user_prompt_sha256": prompts["user_prompt_sha256"],
        "response_schema_sha256": sha256_bytes(canonical_json_bytes(schema)),
    }
    if any(job[key] != value for key, value in observed.items()):
        raise RuntimeError("position probe prompt or schema drifted")
    config = contract["call_configuration"]
    if (
        config["provider"] != "openrouter"
        or config["model"] != MODEL
        or config["allow_provider_fallbacks"] is not False
        or config["automatic_retries"] != 0
        or config["response_healing"] is not False
    ):
        raise RuntimeError("position probe route or failure policy drifted")
    if contract["budget"] != {
        "maximum_provider_calls": 1,
        "maximum_estimated_cost_usd": 0.01,
        "automatic_retries": 0,
        "semantic_retries": 0,
        "fallback_models": 0,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
    }:
        raise RuntimeError("position probe budget drifted")
    return {
        "status": "role_explicit_v2_position_probe_contract_valid",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "provider_calls_made": 0,
    }


def validate_authorization(value: dict, *, contract: dict, contract_path: Path) -> None:
    expected = {
        "schema_version": AUTH_SCHEMA,
        "status": "authorized_once_after_provider_free_and_cold_reader_gates",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": _sha(contract_path),
        "run_id": contract["run_id"],
        "maximum_provider_calls": 1,
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
        raise RuntimeError("position probe authorization drifted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    contract_path = args.contract.resolve()
    contract = _load(contract_path)
    validation = validate_contract(contract, contract_path)
    if args.dry_run:
        print(json.dumps(validation, indent=2, sort_keys=True))
        return 0
    if args.authorization is None or args.env_file is None or args.output is None:
        raise RuntimeError("execution arguments are missing")
    validate_authorization(
        _load(args.authorization.resolve()), contract=contract, contract_path=contract_path
    )
    output = args.output.resolve()
    if output.exists():
        raise RuntimeError("position probe output already exists")
    _load_env(args.env_file.resolve())
    snapshot = _load(ROOT / contract["model_snapshot"]["path"])
    call = run_job(contract=contract, job=contract["job"], snapshot=snapshot)
    result = {
        "schema_version": "lolla.reasoning_process_role_explicit_v2_position_probe_result.v1",
        "status": "one_position_probe_call_preserved",
        "run_id": contract["run_id"],
        "call": call,
        "provider_request_count": call.get("provider_calls", 0),
        "semantic_review_status": "pending_source_first_review",
        "boundary": contract["boundary"],
    }
    _write(output, result)
    print(
        json.dumps(
            {
                "operational_status": call["operational_status"],
                "typed_status": call["typed_status"],
                "admitted_record_count": call.get("admitted_record_count", 0),
                "quarantined_record_count": call.get("quarantined_record_count", 0),
                "estimated_cost_usd": call.get("estimated_cost_usd"),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
