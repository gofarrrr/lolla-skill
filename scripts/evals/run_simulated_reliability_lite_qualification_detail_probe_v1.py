#!/usr/bin/env python3
"""Run one frozen qualification-detail call from reviewed source evidence only."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Callable, Mapping

from engine.system_b.reasoning_process_qualification_detail_v1 import (
    build_qualification_detail_packet_v1,
    build_qualification_detail_prompts_v1,
    compile_qualification_detail_response_v1,
    qualification_detail_response_schema_v1,
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


SCHEMA = "lolla.simulated_reliability_lite_qualification_detail_contract.v1"
AUTH_SCHEMA = "lolla.simulated_reliability_lite_qualification_detail_authorization.v1"
RESULT_SCHEMA = "lolla.simulated_reliability_lite_qualification_detail_result.v1"


def build_request(contract: Mapping[str, Any]) -> dict[str, Any]:
    wrapper = load(ROOT / contract["source"]["position_wrapper_path"])
    review_call = load(ROOT / contract["review"]["call_artifact_path"])
    review = review_call.get("compiled")
    if not isinstance(review, Mapping):
        raise V1RunError("qualification-detail review artifact lacks compiled review")
    packet = build_qualification_detail_packet_v1(wrapper=wrapper, review=review)
    prompts = build_qualification_detail_prompts_v1(packet)
    schema = qualification_detail_response_schema_v1()
    return {"packet": packet, "prompts": prompts, "response_schema": schema}


def request_attestation(contract: Mapping[str, Any]) -> dict[str, str]:
    request = build_request(contract)
    return {
        "packet_sha256": value_sha(request["packet"]),
        "system_prompt_sha256": request["prompts"]["system_prompt_sha256"],
        "user_prompt_sha256": request["prompts"]["user_prompt_sha256"],
        "response_schema_sha256": value_sha(request["response_schema"]),
    }


def _validate(contract_path: Path, authorization_path: Path) -> dict[str, Any]:
    contract = load(contract_path)
    if contract.get("schema_version") != SCHEMA:
        raise V1RunError("unexpected qualification-detail contract schema")
    if contract.get("status") != "frozen_before_one_review_bounded_detail_call":
        raise V1RunError("qualification-detail contract is not frozen")
    if contract.get("budget", {}).get("maximum_provider_calls") != 1:
        raise V1RunError("qualification-detail call ceiling drifted")
    if contract.get("budget", {}).get("automatic_retries") != 0:
        raise V1RunError("automatic retries are forbidden")
    for row in contract["frozen_inputs"]:
        path = ROOT / row["path"]
        if not path.is_file() or file_sha(path) != row["sha256"]:
            raise V1RunError(f"frozen input drifted: {row['path']}")
    if request_attestation(contract) != contract["request_attestation"]:
        raise V1RunError("qualification-detail request bytes drifted")
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
        raise V1RunError("qualification-detail authorization drifted")
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
    runtime["task_limits"]["qualification_detail"] = {
        "max_output_tokens": contract["task_limit"]["max_output_tokens"],
        "reasoning_effort": contract["task_limit"]["reasoning_effort"],
        "wire_mode": "strict_json_schema",
    }
    runtime["seeds"][contract["repeat_id"]] = contract["seed"]
    request = build_request(contract)
    result = call_fn(
        output=output,
        ordinal=1,
        task_id="qualification_detail",
        case_id=contract["source"]["case_id"],
        repeat_id=contract["repeat_id"],
        contract=runtime,
        prompts=request["prompts"],
        schema=request["response_schema"],
        schema_name="lolla_v1_qualification_detail",
        compile_candidate=lambda candidate: compile_qualification_detail_response_v1(
            response=candidate,
            packet=request["packet"],
            producer_kind="simulated_reliability_lite_qualification_detail_probe_v1",
            producer_id=operator["model"],
        ),
    )
    cost = result.get("provider_reported_cost_usd")
    compiled = result.get("compiled")
    report = {
        "schema_version": RESULT_SCHEMA,
        "status": "one_review_bounded_detail_call_preserved_source_review_required",
        "run_id": contract["run_id"],
        "case_id": contract["source"]["case_id"],
        "task_id": "qualification_detail",
        "selected_review_evidence_ids": request["packet"]["review_context"][
            "evidence_ids"
        ],
        "full_conversation_repeated": False,
        "operational_status": result.get("operational_status"),
        "compiled": compiled,
        "admitted_observation_count": len(compiled.get("observations", []))
        if isinstance(compiled, Mapping)
        else 0,
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
        raise V1RunError("qualification-detail output path must not exist")
    output.mkdir(parents=True)
    load_env(args.env_file.resolve())
    report = run(contract, output=output)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["cost_ceiling_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
