#!/usr/bin/env python3
"""Run a frozen difficult trio of one-mechanism Gemini Lite microtasks."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Callable, Mapping

from engine.system_b.reasoning_mechanism_microtask_v1 import (
    build_mechanism_microtask_packet_v1,
    build_mechanism_microtask_prompts_v1,
    compile_mechanism_microtask_response_v1,
    mechanism_microtask_response_schema_v1,
)
from scripts.evals.run_simulated_reliability_case_v1 import (
    ROOT,
    V1RunError,
    file_sha,
    load,
    load_contract,
    load_env,
    provider_call,
    value_sha,
    write,
)


SCHEMA = "lolla.simulated_reliability_lite_mechanism_microtask_contract.v1"
AUTH_SCHEMA = "lolla.simulated_reliability_lite_mechanism_microtask_authorization.v1"
RESULT_SCHEMA = "lolla.simulated_reliability_lite_mechanism_microtask_result.v1"


def build_requests(contract: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    parent = load(ROOT / contract["inputs"]["parent_mechanism_request_path"])["packet"]
    result = {}
    for mechanism_id in contract["mechanism_ids"]:
        packet = build_mechanism_microtask_packet_v1(
            parent_packet=parent, mechanism_id=mechanism_id
        )
        prompts = build_mechanism_microtask_prompts_v1(packet)
        schema = mechanism_microtask_response_schema_v1(mechanism_id)
        result[mechanism_id] = {
            "packet": packet,
            "prompts": prompts,
            "response_schema": schema,
        }
    return result


def request_attestation(contract: Mapping[str, Any]) -> dict[str, Any]:
    requests = build_requests(contract)
    return {
        mechanism_id: {
            "packet_sha256": value_sha(requests[mechanism_id]["packet"]),
            "role_record_count": len(requests[mechanism_id]["packet"]["role_records"]),
            "assistant_contribution_count": len(
                requests[mechanism_id]["packet"]["assistant_contributions"]
            ),
            "system_prompt_sha256": requests[mechanism_id]["prompts"][
                "system_prompt_sha256"
            ],
            "user_prompt_sha256": requests[mechanism_id]["prompts"][
                "user_prompt_sha256"
            ],
            "response_schema_sha256": value_sha(
                requests[mechanism_id]["response_schema"]
            ),
        }
        for mechanism_id in contract["mechanism_ids"]
    }


def _validate(contract_path: Path, authorization_path: Path) -> dict[str, Any]:
    contract = load(contract_path)
    if contract.get("schema_version") != SCHEMA:
        raise V1RunError("unexpected mechanism-microtask contract schema")
    if contract.get("status") != "frozen_before_three_difficult_microtasks":
        raise V1RunError("mechanism-microtask contract is not frozen")
    if len(contract.get("mechanism_ids", [])) != 3:
        raise V1RunError("mechanism-microtask difficult trio drifted")
    if contract.get("budget", {}).get("maximum_provider_calls") != 3:
        raise V1RunError("mechanism-microtask call ceiling drifted")
    if contract.get("budget", {}).get("automatic_retries") != 0:
        raise V1RunError("automatic retries are forbidden")
    for row in contract["frozen_inputs"]:
        path = ROOT / row["path"]
        if not path.is_file() or file_sha(path) != row["sha256"]:
            raise V1RunError(f"frozen input drifted: {row['path']}")
    if request_attestation(contract) != contract["request_attestation"]:
        raise V1RunError("mechanism-microtask request bytes drifted")
    authorization = load(authorization_path)
    expected = {
        "schema_version": AUTH_SCHEMA,
        "status": "authorized_once_by_founder_for_affordable_model_selection",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": file_sha(contract_path),
        "authorized_mechanism_ids": contract["mechanism_ids"],
        "maximum_provider_calls": 3,
        "maximum_provider_reported_cost_usd": contract["budget"][
            "maximum_provider_reported_cost_usd"
        ],
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
    }
    if authorization != expected:
        raise V1RunError("mechanism-microtask authorization drifted")
    return contract


def run(
    contract: Mapping[str, Any],
    *,
    output: Path,
    call_fn: Callable[..., dict[str, Any]] = provider_call,
) -> dict[str, Any]:
    requests = build_requests(contract)
    runtime = copy.deepcopy(
        load_contract(ROOT / contract["base_runtime_contract"]["path"])
    )
    operator = contract["operator"]
    runtime["provider_request"]["model"] = operator["model"]
    runtime["provider_request"]["provider_order"] = [operator["provider_slug"]]
    runtime["provider_request"]["provider_only"] = [operator["provider_slug"]]
    runtime["provider_request"]["max_price_usd_per_million_tokens"] = dict(
        operator["maximum_price_usd_per_million_tokens"]
    )
    runtime["task_limits"]["mechanism_microtask"] = {
        "max_output_tokens": contract["task_limit"]["max_output_tokens"],
        "reasoning_effort": contract["task_limit"]["reasoning_effort"],
        "wire_mode": "strict_json_schema",
    }
    rows = []
    for ordinal, mechanism_id in enumerate(contract["mechanism_ids"], 1):
        item_dir = output / mechanism_id
        item_dir.mkdir(parents=True, exist_ok=False)
        repeat_id = contract["tasks"][mechanism_id]["repeat_id"]
        runtime["seeds"][repeat_id] = contract["tasks"][mechanism_id]["seed"]
        request = requests[mechanism_id]
        result = call_fn(
            output=item_dir,
            ordinal=ordinal,
            task_id="mechanism_microtask",
            case_id=contract["case_id"],
            repeat_id=repeat_id,
            contract=runtime,
            prompts=request["prompts"],
            schema=request["response_schema"],
            schema_name="lolla_v1_mechanism_" + mechanism_id,
            compile_candidate=lambda candidate, packet=request["packet"]: compile_mechanism_microtask_response_v1(
                response=candidate,
                packet=packet,
                producer_kind="simulated_reliability_lite_mechanism_microtask_probe_v1",
                producer_id=operator["model"],
            ),
        )
        compiled = result.get("compiled")
        rows.append(
            {
                "mechanism_id": mechanism_id,
                "operational_status": result.get("operational_status"),
                "compiled": compiled,
                "assessment": compiled.get("assessment")
                if isinstance(compiled, Mapping)
                else None,
                "validation_error": result.get("validation_error", ""),
                "served_model": result.get("served_model", ""),
                "served_provider": result.get("served_provider", ""),
                "provider_calls": result.get("provider_calls", 0),
                "provider_reported_cost_usd": result.get(
                    "provider_reported_cost_usd"
                ),
                "duration_seconds": result.get("duration_seconds"),
            }
        )
    total_calls = sum(int(row["provider_calls"] or 0) for row in rows)
    known_costs = [
        float(row["provider_reported_cost_usd"])
        for row in rows
        if row["provider_reported_cost_usd"] is not None
    ]
    total_cost = round(sum(known_costs), 12) if len(known_costs) == total_calls else None
    report = {
        "schema_version": RESULT_SCHEMA,
        "status": "three_microtasks_preserved_source_review_required",
        "run_id": contract["run_id"],
        "case_id": contract["case_id"],
        "microtasks": rows,
        "provider_calls": total_calls,
        "provider_reported_cost_usd": total_cost,
        "cost_ceiling_met": total_cost is not None
        and total_cost
        <= float(contract["budget"]["maximum_provider_reported_cost_usd"]),
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "routing_disposition_model_authored": False,
        "runtime_effect": "none",
        "joined_for_runtime": False,
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
    contract = _validate(args.contract.resolve(), args.authorization.resolve())
    if args.dry_run:
        print(json.dumps({"status": "dry_run_valid", "provider_calls": 0}, indent=2))
        return 0
    output = args.output.resolve()
    if output.exists():
        raise V1RunError("mechanism-microtask output path must not exist")
    output.mkdir(parents=True)
    load_env(args.env_file.resolve())
    report = run(contract, output=output)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["cost_ceiling_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
