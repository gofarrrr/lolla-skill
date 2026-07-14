#!/usr/bin/env python3
"""Run one frozen Gemini Lite paired-role call with strict wire enforcement."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Callable, Mapping

from engine.system_b.reasoning_process_position_role_first_v242 import (
    compile_response_v242,
)
from scripts.evals.run_simulated_reliability_case_v1 import (
    ROOT,
    V1RunError,
    file_sha,
    load,
    load_contract,
    load_env,
    provider_call,
    write,
)


SCHEMA = "lolla.simulated_reliability_lite_stage2b_strict_contract.v1"
AUTH_SCHEMA = "lolla.simulated_reliability_lite_stage2b_strict_authorization.v1"
RESULT_SCHEMA = "lolla.simulated_reliability_lite_stage2b_strict_result.v1"


def _validate(contract_path: Path, authorization_path: Path) -> dict[str, Any]:
    contract = load(contract_path)
    if contract.get("schema_version") != SCHEMA:
        raise V1RunError("unexpected Lite stage-2b contract schema")
    if contract.get("status") != "frozen_before_one_strict_wire_call":
        raise V1RunError("Lite stage-2b contract is not frozen")
    if contract.get("budget", {}).get("maximum_provider_calls") != 1:
        raise V1RunError("Lite stage-2b call ceiling drifted")
    if contract.get("only_runtime_change") != {
        "task": "current_qualification",
        "field": "wire_mode",
        "from": "json_object_schema_in_prompt",
        "to": "strict_json_schema",
    }:
        raise V1RunError("Lite stage-2b transport-only boundary drifted")
    for row in contract["frozen_inputs"]:
        path = ROOT / row["path"]
        if not path.is_file() or file_sha(path) != row["sha256"]:
            raise V1RunError(f"frozen input drifted: {row['path']}")
    authorization = load(authorization_path)
    expected = {
        "schema_version": AUTH_SCHEMA,
        "status": "authorized_once_by_founder_for_affordable_model_selection",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": file_sha(contract_path),
        "maximum_provider_calls": 1,
        "maximum_provider_reported_cost_usd": contract["budget"][
            "maximum_provider_reported_cost_usd"
        ],
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
    }
    if authorization != expected:
        raise V1RunError("Lite stage-2b authorization drifted")
    return contract


def run(
    contract: Mapping[str, Any],
    *,
    output: Path,
    call_fn: Callable[..., dict[str, Any]] = provider_call,
) -> dict[str, Any]:
    runtime = copy.deepcopy(
        load_contract(ROOT / contract["base_runtime_contract"]["path"])
    )
    model = contract["operator"]
    runtime["provider_request"]["model"] = model["model"]
    runtime["provider_request"]["provider_order"] = [model["provider_slug"]]
    runtime["provider_request"]["provider_only"] = [model["provider_slug"]]
    runtime["provider_request"]["max_price_usd_per_million_tokens"] = dict(
        model["maximum_price_usd_per_million_tokens"]
    )
    runtime["task_limits"]["current_qualification"]["reasoning_effort"] = model[
        "reasoning_effort"
    ]
    runtime["task_limits"]["current_qualification"]["wire_mode"] = (
        "strict_json_schema"
    )
    runtime["seeds"][contract["repeat_id"]] = contract["seed"]
    bundle = load(ROOT / contract["microtask"]["role_request_bundle_path"])
    wrapper = load(ROOT / contract["microtask"]["position_wrapper_path"])
    spec = bundle["requests"]["current_qualification"]
    result = call_fn(
        output=output,
        ordinal=1,
        task_id="current_qualification",
        case_id=contract["microtask"]["case_id"],
        repeat_id=contract["repeat_id"],
        contract=runtime,
        prompts=spec["prompts"],
        schema=spec["response_schema"],
        schema_name="lolla_v1_current_qualification",
        compile_candidate=lambda candidate: compile_response_v242(
            response=candidate,
            wrapper=wrapper,
            producer_kind="simulated_reliability_lite_stage2b_strict_probe_v1",
            producer_id=model["model"],
        ),
    )
    compiled = result.get("compiled")
    observations = compiled.get("observations", []) if isinstance(compiled, Mapping) else []
    admitted = [row for row in observations if row.get("terminal_state") == "admitted"]
    cost = result.get("provider_reported_cost_usd")
    report = {
        "schema_version": RESULT_SCHEMA,
        "status": "one_strict_call_preserved_source_review_required",
        "run_id": contract["run_id"],
        "case_id": contract["microtask"]["case_id"],
        "task_id": "current_qualification",
        "wire_mode": "strict_json_schema",
        "requested_model": model["model"],
        "requested_provider": model["provider_slug"],
        "operational_status": result.get("operational_status"),
        "compiled": compiled,
        "admitted_observation_count": len(admitted),
        "validation_error": result.get("validation_error", ""),
        "served_model": result.get("served_model", ""),
        "served_provider": result.get("served_provider", ""),
        "provider_calls": result.get("provider_calls", 0),
        "provider_reported_cost_usd": cost,
        "duration_seconds": result.get("duration_seconds"),
        "cost_ceiling_met": cost is not None
        and float(cost)
        <= float(contract["budget"]["maximum_provider_reported_cost_usd"]),
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "source_review_status": "required",
        "production_model_selected": False,
        "scalar_quality_score": None,
    }
    write(output / "result.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    contract_path = args.contract.resolve()
    authorization_path = args.authorization.resolve()
    contract = _validate(contract_path, authorization_path)
    if args.dry_run:
        print(json.dumps({"status": "dry_run_valid", "provider_calls": 0}, indent=2))
        return 0
    output = args.output.resolve()
    if output.exists():
        raise V1RunError("Lite stage-2b output path must not exist")
    output.mkdir(parents=True)
    load_env(args.env_file.resolve())
    report = run(contract, output=output)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["cost_ceiling_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
