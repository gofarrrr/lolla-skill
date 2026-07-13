#!/usr/bin/env python3
"""Replay frozen V1 pressure packets without repeating upstream provider calls."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.simulated_reliability_v1 import (  # noqa: E402
    build_pressure_prompts,
    compile_pressure_response,
)
from scripts.evals.run_simulated_reliability_case_v1 import (  # noqa: E402
    V1RunError,
    file_sha,
    load,
    load_env,
    provider_call,
    validate_contract,
    write,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--repeat-id", default="primary")
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    contract_path = args.contract.resolve()
    authorization_path = args.authorization.resolve()
    contract = validate_contract(
        contract_path, authorization_path, args.case_id, args.repeat_id
    )
    replay = contract["calibration"].get("pressure_replay")
    if not isinstance(replay, dict) or replay.get("case_id") != args.case_id:
        raise V1RunError("pressure replay is not frozen for this case")
    bundle_path = ROOT / replay["bundle_path"]
    if file_sha(bundle_path) != replay["bundle_sha256"]:
        raise V1RunError("pressure replay bundle drifted")
    bundle = load(bundle_path)
    arms = bundle.get("arms", {})
    arm_names = ["direct_pressure", "graph_expanded_pressure"]
    if any(not arms.get(name, {}).get("call_required") for name in arm_names):
        raise V1RunError("pressure replay lacks a required active arm")
    if args.dry_run:
        print(json.dumps({"status": "pressure_replay_contract_valid", "provider_calls": 0}, indent=2))
        return 0

    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        raise V1RunError("output directory is not empty")
    output.mkdir(parents=True, exist_ok=True)
    load_env(args.env_file.resolve() if args.env_file else None)
    results = {}
    for ordinal, arm_name in enumerate(arm_names, start=1):
        arm = arms[arm_name]
        packet = arm["packet"]
        prompts = build_pressure_prompts(packet)
        call = provider_call(
            output=output,
            ordinal=ordinal,
            task_id=arm_name,
            case_id=args.case_id,
            repeat_id=args.repeat_id,
            contract=contract,
            prompts=prompts,
            schema=arm["response_schema"],
            schema_name="lolla_v1_replay_" + arm_name,
            compile_candidate=lambda candidate, packet=packet: compile_pressure_response(
                response=candidate, packet=packet
            ),
        )
        results[arm_name] = call
        if call.get("compiled") is None:
            write(
                output / "result.json",
                {
                    "status": "stopped_after_" + arm_name + "_failure",
                    "case_id": args.case_id,
                    "results": results,
                    "provider_request_count": sum(
                        int(value.get("provider_calls", 0)) for value in results.values()
                    ),
                },
            )
            return 1
    result = {
        "schema_version": "lolla.simulated_reliability_pressure_replay_result.v1",
        "status": "pressure_replay_complete_source_review_required",
        "case_id": args.case_id,
        "source_bundle_path": replay["bundle_path"],
        "source_bundle_sha256": replay["bundle_sha256"],
        "results": results,
        "provider_request_count": 2,
        "provider_reported_cost_usd": round(
            sum(float(value.get("provider_reported_cost_usd") or 0) for value in results.values()),
            12,
        ),
        "automatic_retries": 0,
        "response_healing": False,
        "source_review_status": "required",
    }
    write(output / "result.json", result)
    print(json.dumps({key: result[key] for key in ("status", "case_id", "provider_request_count", "provider_reported_cost_usd")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
