#!/usr/bin/env python3
"""Run one target-blind local exploration development window."""
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_exploration_local import (  # noqa: E402
    build_local_prompts,
    compile_local_response,
    local_response_schema,
    validate_local_response,
)
from scripts.evals import run_reasoning_process_view_specific_probe as base  # noqa: E402


_ORIGINAL_WRAPPER = base._wrapper


def _local_wrapper(job: Mapping[str, Any]) -> dict[str, Any]:
    wrapper = _ORIGINAL_WRAPPER(job)
    value = dict(wrapper)
    value["reader_packet"] = wrapper["packet"]
    return value


def _compile_adapter(
    *,
    target: Mapping[str, Any],
    response: Mapping[str, Any],
    wrapper: Mapping[str, Any],
    base_ledger: Mapping[str, Any],
    catalog,
    producer_kind: str,
    producer_id: str,
    call_metadata: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    del base_ledger, catalog
    metadata = call_metadata or {}
    return compile_local_response(
        response=response,
        wrapper=wrapper,
        producer_kind=producer_kind,
        producer_id=producer_id,
        record_identity=str(target["target_id"]),
        call_metadata={
            "call_id": metadata.get("call_id", ""),
            "model": metadata.get("model", ""),
            "prompt_sha256": metadata.get("prompt_sha256", ""),
        },
    )


def _activate() -> None:
    base._wrapper = _local_wrapper
    base.build_view_specific_prompts = build_local_prompts
    base.view_specific_response_schema = lambda view_kind: local_response_schema()
    base.validate_view_specific_response = validate_local_response
    base.compile_protected_fixture = _compile_adapter


def _validate_contract(contract: Mapping[str, Any]) -> dict[str, Any]:
    if contract.get("schema_version") != "lolla.reasoning_process_exploration_local_probe_contract.v1":
        raise base.ViewSpecificProbeRunnerError("unexpected local exploration contract")
    if contract.get("status") != "frozen_before_single_provider_call":
        raise base.ViewSpecificProbeRunnerError("local exploration contract is not frozen")
    if len(contract.get("jobs", [])) != 1:
        raise base.ViewSpecificProbeRunnerError("local exploration probe requires one job")
    for ref in contract["frozen_inputs"]:
        path = base._repo_path(ref["path"], label="frozen input")
        if base._file_sha(path) != ref["sha256"]:
            raise base.ViewSpecificProbeRunnerError(f"frozen input drifted: {ref['path']}")
    job = contract["jobs"][0]
    wrapper = base._load(base._repo_path(job["packet_path"], label="local packet"))
    prompts = build_local_prompts(wrapper)
    schema = local_response_schema()
    observed = {
        "job_id": job["job_id"],
        "view_kind": "exploration_and_alternatives",
        "packet_path": job["packet_path"],
        "packet_sha256": base._file_sha(
            base._repo_path(job["packet_path"], label="local packet")
        ),
        "input_utf8_bytes": wrapper["metrics"]["input_utf8_bytes"],
        "focal_turn_index": wrapper["packet"]["focal_turn_index"],
        "system_prompt_sha256": prompts["system_prompt_sha256"],
        "user_prompt_sha256": prompts["user_prompt_sha256"],
        "response_schema_sha256": base._json_sha(schema),
    }
    if observed != job:
        raise base.ViewSpecificProbeRunnerError("local job, prompt, packet, or schema drifted")
    config = contract["call_configuration"]
    if config["provider"] != "openrouter" or config["model"] != "google/gemini-3.1-flash-lite":
        raise base.ViewSpecificProbeRunnerError("local probe route drifted")
    if contract["budget"] != {
        "maximum_provider_calls": 1,
        "maximum_estimated_cost_usd": 0.01,
        "automatic_retries": 0,
        "fallback_models": 0,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
    }:
        raise base.ViewSpecificProbeRunnerError("local probe budget drifted")
    return {
        "status": "contract_valid",
        "case_id": contract["case"]["case_id"],
        "focal_turn_index": job["focal_turn_index"],
        "job_count": 1,
        "provider_calls_made": 0,
    }


def main() -> int:
    _activate()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    contract_path = args.contract.resolve()
    contract = base._load(contract_path)
    validation = _validate_contract(contract)
    if args.dry_run:
        print(json.dumps(validation, indent=2, sort_keys=True))
        return 0
    if args.authorization is None or args.env_file is None or args.output is None:
        raise base.ViewSpecificProbeRunnerError("execution arguments are missing")
    authorization = base._load(args.authorization.resolve())
    if authorization.get("contract_sha256") != base._file_sha(contract_path):
        raise base.ViewSpecificProbeRunnerError("authorization contract hash drifted")
    if authorization.get("maximum_provider_calls") != 1:
        raise base.ViewSpecificProbeRunnerError("authorization call ceiling drifted")
    base._load_env(args.env_file.resolve())
    snapshot = base._load(
        base._repo_path(contract["model_snapshot"]["path"], label="model snapshot")
    )
    call = base.run_job(contract=contract, job=contract["jobs"][0], snapshot=snapshot)
    output = args.output.resolve()
    base._write(output / "call.json", call)
    result = {
        "schema_version": "lolla.reasoning_process_exploration_local_probe_result.v1",
        "status": "single_local_call_preserved",
        "run_id": contract["run_id"],
        "case_id": contract["case"]["case_id"],
        "focal_turn_index": contract["jobs"][0]["focal_turn_index"],
        "operational_status": call["operational_status"],
        "typed_status": call["typed_status"],
        "provider_calls": call["provider_calls"],
        "estimated_cost_usd": call.get("estimated_cost_usd"),
        "call_path": str((output / "call.json").relative_to(ROOT)),
        "call_sha256": base._file_sha(output / "call.json"),
        "semantic_review_status": "pending_source_first_review",
        "boundary": {
            "protected_target_seen_by_model": False,
            "other_six_windows_called": False,
            "provider_retries": 0,
            "phase4_transfer_authorized": False,
        },
    }
    base._write(output / "result.json", result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
