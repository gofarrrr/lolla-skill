#!/usr/bin/env python3
"""Run the six remaining local exploration windows for one development case."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_exploration_local import (  # noqa: E402
    build_local_prompts,
    local_response_schema,
)
from scripts.evals import run_reasoning_process_view_specific_probe as base  # noqa: E402
from scripts.evals.run_reasoning_process_exploration_local_probe import (  # noqa: E402
    _activate,
)


def _validate_contract(contract: Mapping[str, Any]) -> dict[str, Any]:
    if contract.get("schema_version") != "lolla.reasoning_process_exploration_local_case_contract.v1":
        raise base.ViewSpecificProbeRunnerError("unexpected local case contract")
    if contract.get("status") != "frozen_before_six_provider_calls":
        raise base.ViewSpecificProbeRunnerError("local case contract is not frozen")
    jobs = contract.get("jobs")
    if not isinstance(jobs, list) or len(jobs) != 6:
        raise base.ViewSpecificProbeRunnerError("local case contract requires six jobs")
    if [job["focal_turn_index"] for job in jobs] != [1, 2, 4, 5, 6, 7]:
        raise base.ViewSpecificProbeRunnerError("local case turn order drifted")
    for ref in contract["frozen_inputs"]:
        if base._file_sha(base._repo_path(ref["path"], label="frozen input")) != ref[
            "sha256"
        ]:
            raise base.ViewSpecificProbeRunnerError(f"frozen input drifted: {ref['path']}")
    schema_hash = base._json_sha(local_response_schema())
    for job in jobs:
        path = base._repo_path(job["packet_path"], label="local packet")
        wrapper = base._load(path)
        prompts = build_local_prompts(wrapper)
        observed = {
            "job_id": job["job_id"],
            "view_kind": "exploration_and_alternatives",
            "packet_path": job["packet_path"],
            "packet_sha256": base._file_sha(path),
            "input_utf8_bytes": wrapper["metrics"]["input_utf8_bytes"],
            "focal_turn_index": wrapper["packet"]["focal_turn_index"],
            "system_prompt_sha256": prompts["system_prompt_sha256"],
            "user_prompt_sha256": prompts["user_prompt_sha256"],
            "response_schema_sha256": schema_hash,
        }
        if observed != job:
            raise base.ViewSpecificProbeRunnerError("local case job lock drifted")
    if contract["budget"] != {
        "maximum_provider_calls": 6,
        "maximum_estimated_cost_usd": 0.05,
        "automatic_retries": 0,
        "fallback_models": 0,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
    }:
        raise base.ViewSpecificProbeRunnerError("local case budget drifted")
    return {"status": "contract_valid", "job_count": 6, "provider_calls_made": 0}


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
    if authorization.get("maximum_provider_calls") != 6:
        raise base.ViewSpecificProbeRunnerError("authorization call ceiling drifted")
    base._load_env(args.env_file.resolve())
    snapshot = base._load(
        base._repo_path(contract["model_snapshot"]["path"], label="model snapshot")
    )
    output = args.output.resolve()
    calls = []
    cost = 0.0
    for job in contract["jobs"]:
        call = base.run_job(contract=contract, job=job, snapshot=snapshot)
        calls.append(call)
        path = output / "calls" / f"turn-{job['focal_turn_index']:03d}.json"
        base._write(path, call)
        if isinstance(call.get("estimated_cost_usd"), (int, float)):
            cost += float(call["estimated_cost_usd"])
        if call.get("operational_status") == "missing_api_key":
            break
        if cost > contract["budget"]["maximum_estimated_cost_usd"]:
            break
    result = {
        "schema_version": "lolla.reasoning_process_exploration_local_case_result.v1",
        "status": "remaining_case_windows_preserved",
        "run_id": contract["run_id"],
        "case_id": contract["case"]["case_id"],
        "expected_call_count": 6,
        "attempted_call_count": len(calls),
        "provider_call_count": sum(call.get("provider_calls", 0) for call in calls),
        "operational_success_count": sum(
            call.get("operational_status") == "ok" for call in calls
        ),
        "typed_admission_count": sum(call.get("typed_status") == "admitted" for call in calls),
        "estimated_cost_usd": round(cost, 9),
        "call_artifacts": [
            {
                "focal_turn_index": call["compiled"]["observations"][0]["focal_turn_index"]
                if call.get("compiled", {}).get("observations")
                else job["focal_turn_index"],
                "operational_status": call["operational_status"],
                "typed_status": call["typed_status"],
            }
            for call, job in zip(calls, contract["jobs"])
        ],
        "semantic_review_status": "pending_source_first_review",
        "calls": {
            "automatic_retries": 0,
            "fallback_models": 0,
            "evaluator": 0,
            "embedding": 0,
            "graph": 0,
            "pipeline": 0,
            "runtime": 0,
        },
        "boundary": {
            "turn3_repeated": False,
            "phase4_transfer_authorized": False,
            "graph_or_runtime_authorized": False,
        },
    }
    base._write(output / "result.json", result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
