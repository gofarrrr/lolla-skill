#!/usr/bin/env python3
"""Run two frozen source-linked qualification-review microtasks with Gemini Lite."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Callable, Mapping

from engine.system_b.reasoning_process_qualification_review_v1 import (
    build_qualification_review_packet_v1,
    build_qualification_review_prompts_v1,
    compile_qualification_review_response_v1,
    qualification_review_response_schema_v1,
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


SCHEMA = "lolla.simulated_reliability_lite_qualification_review_contract.v1"
AUTH_SCHEMA = "lolla.simulated_reliability_lite_qualification_review_authorization.v1"
RESULT_SCHEMA = "lolla.simulated_reliability_lite_qualification_review_result.v1"


def build_request(case: Mapping[str, Any]) -> dict[str, Any]:
    wrapper = load(ROOT / case["position_wrapper_path"])
    packet = build_qualification_review_packet_v1(wrapper=wrapper)
    prompts = build_qualification_review_prompts_v1(packet)
    schema = qualification_review_response_schema_v1()
    return {"packet": packet, "prompts": prompts, "response_schema": schema}


def request_attestation(case: Mapping[str, Any]) -> dict[str, str]:
    request = build_request(case)
    return {
        "packet_sha256": value_sha(request["packet"]),
        "system_prompt_sha256": request["prompts"]["system_prompt_sha256"],
        "user_prompt_sha256": request["prompts"]["user_prompt_sha256"],
        "response_schema_sha256": value_sha(request["response_schema"]),
    }


def _validate(contract_path: Path, authorization_path: Path) -> dict[str, Any]:
    contract = load(contract_path)
    if contract.get("schema_version") != SCHEMA:
        raise V1RunError("unexpected qualification-review contract schema")
    if contract.get("status") != "frozen_before_present_and_quiet_calls":
        raise V1RunError("qualification-review contract is not frozen")
    cases = contract.get("cases", [])
    if len(cases) != 2 or [case["expected_outcome_class"] for case in cases] != [
        "present",
        "quiet",
    ]:
        raise V1RunError("qualification-review case classes drifted")
    if contract.get("budget", {}).get("maximum_provider_calls") != 2:
        raise V1RunError("qualification-review call ceiling drifted")
    if contract.get("budget", {}).get("automatic_retries") != 0:
        raise V1RunError("automatic retries are forbidden")
    for row in contract["frozen_inputs"]:
        path = ROOT / row["path"]
        if not path.is_file() or file_sha(path) != row["sha256"]:
            raise V1RunError(f"frozen input drifted: {row['path']}")
    observed = {case["case_id"]: request_attestation(case) for case in cases}
    if observed != contract["request_attestation"]:
        raise V1RunError("qualification-review request bytes drifted")
    authorization = load(authorization_path)
    expected = {
        "schema_version": AUTH_SCHEMA,
        "status": "authorized_once_by_founder_for_affordable_model_selection",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": file_sha(contract_path),
        "authorized_case_ids": [case["case_id"] for case in cases],
        "maximum_provider_calls": 2,
        "maximum_provider_reported_cost_usd": contract["budget"][
            "maximum_provider_reported_cost_usd"
        ],
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
    }
    if authorization != expected:
        raise V1RunError("qualification-review authorization drifted")
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
    operator = contract["operator"]
    runtime["provider_request"]["model"] = operator["model"]
    runtime["provider_request"]["provider_order"] = [operator["provider_slug"]]
    runtime["provider_request"]["provider_only"] = [operator["provider_slug"]]
    runtime["provider_request"]["max_price_usd_per_million_tokens"] = dict(
        operator["maximum_price_usd_per_million_tokens"]
    )
    runtime["task_limits"]["qualification_review"] = {
        "max_output_tokens": contract["task_limit"]["max_output_tokens"],
        "reasoning_effort": contract["task_limit"]["reasoning_effort"],
        "wire_mode": "strict_json_schema",
    }
    rows = []
    for ordinal, case in enumerate(contract["cases"], 1):
        case_dir = output / case["case_id"]
        case_dir.mkdir(parents=True, exist_ok=False)
        request = build_request(case)
        repeat_id = case["repeat_id"]
        runtime["seeds"][repeat_id] = case["seed"]
        result = call_fn(
            output=case_dir,
            ordinal=ordinal,
            task_id="qualification_review",
            case_id=case["case_id"],
            repeat_id=repeat_id,
            contract=runtime,
            prompts=request["prompts"],
            schema=request["response_schema"],
            schema_name="lolla_v1_qualification_review",
            compile_candidate=lambda candidate, packet=request["packet"]: compile_qualification_review_response_v1(
                response=candidate,
                packet=packet,
                producer_kind="simulated_reliability_lite_qualification_review_probe_v1",
                producer_id=operator["model"],
            ),
        )
        rows.append(
            {
                "case_id": case["case_id"],
                "expected_outcome_class": case["expected_outcome_class"],
                "operational_status": result.get("operational_status"),
                "compiled": result.get("compiled"),
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
        "status": "present_and_quiet_calls_preserved_source_review_required",
        "run_id": contract["run_id"],
        "cases": rows,
        "provider_calls": total_calls,
        "provider_reported_cost_usd": total_cost,
        "cost_ceiling_met": total_cost is not None
        and total_cost
        <= float(contract["budget"]["maximum_provider_reported_cost_usd"]),
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "deterministic_semantic_inference": False,
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
        raise V1RunError("qualification-review output path must not exist")
    output.mkdir(parents=True)
    load_env(args.env_file.resolve())
    report = run(contract, output=output)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["cost_ceiling_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
