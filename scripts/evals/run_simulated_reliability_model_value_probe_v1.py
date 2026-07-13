#!/usr/bin/env python3
"""Run a tiny frozen cheaper-model probe against one exact V1 microtask."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Mapping

from engine.system_b.reasoning_process_position_role_first_v24 import (
    compile_position_starting_response_v24,
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


SCHEMA = "lolla.simulated_reliability_model_value_probe_contract.v1"
AUTH_SCHEMA = "lolla.simulated_reliability_model_value_probe_authorization.v1"
RESULT_SCHEMA = "lolla.simulated_reliability_model_value_probe_result.v1"


def _validate(contract_path: Path, authorization_path: Path) -> dict[str, Any]:
    contract = load(contract_path)
    if contract.get("schema_version") != SCHEMA:
        raise V1RunError("unexpected model-value contract schema")
    if contract.get("status") != "frozen_before_two_starting_calls":
        raise V1RunError("model-value contract is not frozen")
    if contract.get("budget", {}).get("maximum_provider_calls") != 2:
        raise V1RunError("model-value call ceiling drifted")
    if contract.get("budget", {}).get("automatic_retries") != 0:
        raise V1RunError("automatic retries are forbidden")
    if len(contract.get("jobs", [])) != 2:
        raise V1RunError("exactly two jobs are required")
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
        "authorized_job_ids": [row["job_id"] for row in contract["jobs"]],
        "maximum_provider_calls": 2,
        "maximum_provider_reported_cost_usd": contract["budget"][
            "maximum_provider_reported_cost_usd"
        ],
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
    }
    if authorization != expected:
        raise V1RunError("model-value authorization drifted")
    return contract


def run(
    contract: Mapping[str, Any],
    *,
    output: Path,
    call_fn: Callable[..., dict[str, Any]] = provider_call,
) -> dict[str, Any]:
    base_contract_path = ROOT / contract["base_runtime_contract"]["path"]
    base = load_contract(base_contract_path)
    role_bundle = load(ROOT / contract["microtask"]["role_request_bundle_path"])
    spec = role_bundle["requests"]["starting"]
    calls = []
    for job in contract["jobs"]:
        job_dir = output / job["job_id"]
        job_dir.mkdir(parents=True, exist_ok=False)
        runtime = copy.deepcopy(base)
        runtime["provider_request"]["model"] = job["model"]
        runtime["provider_request"]["provider_order"] = [job["provider_slug"]]
        runtime["provider_request"]["provider_only"] = [job["provider_slug"]]
        runtime["provider_request"]["max_price_usd_per_million_tokens"] = {
            "prompt": job["maximum_price_usd_per_million_tokens"]["prompt"],
            "completion": job["maximum_price_usd_per_million_tokens"]["completion"],
        }
        runtime["task_limits"]["starting"]["reasoning_effort"] = job[
            "reasoning_effort"
        ]
        runtime["seeds"][contract["repeat_id"]] = contract["seed"]
        result = call_fn(
            output=job_dir,
            ordinal=1,
            task_id="starting",
            case_id=contract["microtask"]["case_id"],
            repeat_id=contract["repeat_id"],
            contract=runtime,
            prompts=spec["prompts"],
            schema=spec["response_schema"],
            schema_name="lolla_v1_starting",
            compile_candidate=lambda candidate, model=job["model"]: compile_position_starting_response_v24(
                response=candidate,
                packet=spec["packet"],
                producer_kind="simulated_reliability_model_value_probe_v1",
                producer_id=model,
            ),
        )
        call_artifact = job_dir / "call-01-starting-result.json"
        try:
            call_artifact_label = str(call_artifact.relative_to(ROOT))
        except ValueError:
            # Unit tests may deliberately place disposable output outside the repo.
            call_artifact_label = str(call_artifact)
        calls.append(
            {
                "job_id": job["job_id"],
                "model": job["model"],
                "provider_slug": job["provider_slug"],
                "operational_status": result.get("operational_status"),
                "compiled": result.get("compiled"),
                "validation_error": result.get("validation_error", ""),
                "served_model": result.get("served_model", ""),
                "served_provider": result.get("served_provider", ""),
                "provider_calls": result.get("provider_calls", 0),
                "provider_reported_cost_usd": result.get(
                    "provider_reported_cost_usd"
                ),
                "prompt_tokens": (result.get("usage") or {}).get("prompt_tokens"),
                "completion_tokens": (result.get("usage") or {}).get(
                    "completion_tokens"
                ),
                "reasoning_tokens": (
                    ((result.get("usage") or {}).get("completion_tokens_details") or {}).get(
                        "reasoning_tokens"
                    )
                ),
                "duration_seconds": result.get("duration_seconds"),
                "call_artifact": call_artifact_label,
            }
        )
    total_calls = sum(int(row["provider_calls"] or 0) for row in calls)
    known_costs = [
        float(row["provider_reported_cost_usd"])
        for row in calls
        if row["provider_reported_cost_usd"] is not None
    ]
    total_cost = round(sum(known_costs), 12) if len(known_costs) == total_calls else None
    report = {
        "schema_version": RESULT_SCHEMA,
        "status": "two_calls_preserved_source_review_required",
        "run_id": contract["run_id"],
        "case_id": contract["microtask"]["case_id"],
        "task_id": "starting",
        "calls": calls,
        "provider_calls": total_calls,
        "provider_reported_cost_usd": total_cost,
        "cost_ceiling_met": total_cost is not None
        and total_cost
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
        print(
            json.dumps(
                {
                    "status": "dry_run_valid",
                    "provider_calls": 0,
                    "job_ids": [row["job_id"] for row in contract["jobs"]],
                },
                indent=2,
            )
        )
        return 0
    output = args.output.resolve()
    if output.exists():
        raise V1RunError("model-value output path must not exist")
    output.mkdir(parents=True)
    load_env(args.env_file.resolve())
    report = run(contract, output=output)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["cost_ceiling_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
