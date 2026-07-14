#!/usr/bin/env python3
"""Run the frozen one-call chronological shard probe."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_chronological_shard_reader import (  # noqa: E402
    build_shard_prompts,
    shard_response_schema,
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


def validate(contract: dict, contract_path: Path, authorization: dict | None = None) -> dict:
    if contract.get("schema_version") != "lolla.reasoning_process_chronological_shard_probe_contract.v1":
        raise RuntimeError("unexpected shard probe contract")
    for item in contract["frozen_inputs"]:
        if _sha(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"frozen input drifted: {item['path']}")
    job = contract["job"]
    packet_path = ROOT / job["packet_path"]
    if _sha(packet_path) != job["packet_sha256"]:
        raise RuntimeError("probe packet drifted")
    wrapper = _load(packet_path)
    prompts = build_shard_prompts(wrapper)
    schema = shard_response_schema(job["view_kind"])
    observed = {
        "system_prompt_sha256": prompts["system_prompt_sha256"],
        "user_prompt_sha256": prompts["user_prompt_sha256"],
        "response_schema_sha256": sha256_bytes(canonical_json_bytes(schema)),
    }
    if any(job[key] != value for key, value in observed.items()):
        raise RuntimeError("probe prompt or schema drifted")
    if contract["call_configuration"]["provider"] != "openrouter" or contract["call_configuration"]["model"] != MODEL:
        raise RuntimeError("probe route drifted")
    if authorization is not None:
        expected = {
            "schema_version": "lolla.reasoning_process_chronological_shard_probe_authorization.v1",
            "status": "authorized_once_under_founder_continuation_mandate",
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
        if authorization != expected:
            raise RuntimeError("probe authorization drifted")
    return {"status": "chronological_shard_probe_contract_valid", "provider_calls_made": 0}


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
    if args.dry_run:
        print(json.dumps(validate(contract, contract_path), indent=2, sort_keys=True))
        return 0
    if args.authorization is None or args.env_file is None or args.output is None:
        raise RuntimeError("execution arguments are missing")
    authorization = _load(args.authorization.resolve())
    validate(contract, contract_path, authorization)
    output = args.output.resolve()
    if output.exists():
        raise RuntimeError("probe output already exists")
    _load_env(args.env_file.resolve())
    snapshot = _load(ROOT / "docs/evals/reasoning-process-phase3-model-snapshot-v1.json")
    call = run_job(contract=contract, job=contract["job"], snapshot=snapshot)
    result = {
        "schema_version": "lolla.reasoning_process_chronological_shard_probe_result.v1",
        "status": "one_probe_call_preserved",
        "run_id": contract["run_id"],
        "call": call,
        "provider_request_count": call.get("provider_calls", 0),
        "semantic_review_status": "pending_source_first_review",
        "boundary": contract["boundary"],
    }
    _write(output, result)
    print(json.dumps({"operational_status": call["operational_status"], "typed_status": call["typed_status"], "admitted_record_count": call.get("admitted_record_count", 0), "estimated_cost_usd": call.get("estimated_cost_usd")}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
