#!/usr/bin/env python3
"""Run one frozen reserved-case position decomposition probe via OpenRouter."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_position_decomposition_v1 import (  # noqa: E402
    ROLE_EVIDENCE_FIELDS,
    build_role_trajectory_prompts_v1,
    build_stance_role_packet_v1,
    build_stance_role_prompts_v1,
    compile_role_trajectory_response_v1,
    compile_stance_role_response_v1,
    join_position_decomposition_v1,
    role_trajectory_response_schema_v1,
    stance_role_response_schema_v1,
)
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes  # noqa: E402
from scripts.evals.reasoning_process_position_decomposition_transport import (  # noqa: E402
    run_decomposed_task,
)
from scripts.evals.run_conversation_state_microtask_probe import _load_env  # noqa: E402
from scripts.evals.run_reasoning_process_phase4_transfer import _load, _sha, _write  # noqa: E402

CONTRACT_SCHEMA = "lolla.reasoning_process_position_decomposition_probe_contract.v1"
AUTH_SCHEMA = "lolla.reasoning_process_position_decomposition_probe_authorization.v1"
ROLE_ORDER = tuple(ROLE_EVIDENCE_FIELDS)


def validate_contract(contract: dict, contract_path: Path) -> dict:
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise RuntimeError("unexpected position decomposition probe contract")
    if contract.get("status") != "frozen_before_at_most_four_reserved_case_calls":
        raise RuntimeError("position decomposition probe contract is not frozen")
    for item in contract["frozen_inputs"]:
        if _sha(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"frozen input drifted: {item['path']}")
    job = contract["job"]
    packet_path = ROOT / job["packet_path"]
    if _sha(packet_path) != job["packet_sha256"]:
        raise RuntimeError("reserved agency packet drifted")
    wrapper = _load(packet_path)
    prompts = build_role_trajectory_prompts_v1(wrapper)
    schema = role_trajectory_response_schema_v1()
    observed = {
        "system_prompt_sha256": prompts["system_prompt_sha256"],
        "user_prompt_sha256": prompts["user_prompt_sha256"],
        "response_schema_sha256": sha256_bytes(canonical_json_bytes(schema)),
    }
    if any(job["trajectory_request"][key] != value for key, value in observed.items()):
        raise RuntimeError("trajectory request contract drifted")
    observed_stance = {
        role: sha256_bytes(canonical_json_bytes(stance_role_response_schema_v1(role)))
        for role in ROLE_ORDER
    }
    if job["stance_schema_sha256_by_role"] != observed_stance:
        raise RuntimeError("stance response schemas drifted")
    if (
        job["case_id"] != "amb2-case03-agency-acquisition"
        or job["model"] != "deepseek/deepseek-v4-flash"
        or job["provider_slug"] != "alibaba"
    ):
        raise RuntimeError("reserved case or exact model/operator pair drifted")
    if contract["budget"] != {
        "maximum_provider_calls": 4,
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
        raise RuntimeError("position decomposition probe budget drifted")
    config = contract["call_configuration"]
    if config != {
        "provider": "openrouter",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "wire_mode": "strict_json_schema",
        "temperature": 0.0,
        "seed": 0,
        "reasoning_enabled": False,
        "max_output_tokens": 1200,
        "provider_timeout_seconds": 90,
        "require_supported_parameters": True,
        "allow_provider_fallbacks": False,
        "automatic_retries": 0,
        "response_healing": False,
        "parallel_calls": False,
    }:
        raise RuntimeError("position decomposition call configuration drifted")
    return {
        "status": "position_decomposition_probe_contract_valid",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "provider_calls_made": 0,
    }


def validate_authorization(value: dict, *, contract: dict, contract_path: Path) -> None:
    expected = {
        "schema_version": AUTH_SCHEMA,
        "status": "authorized_once_after_provider_free_decomposition_and_adversarial_gates",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": _sha(contract_path),
        "run_id": contract["run_id"],
        "maximum_provider_calls": 4,
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
        raise RuntimeError("position decomposition probe authorization drifted")


def _started(output: Path, *, contract: dict, task_id: str) -> None:
    _write(
        output,
        {
            "schema_version": "lolla.reasoning_process_decomposed_call_started.v1",
            "status": "provider_call_may_have_started_do_not_rerun_if_result_missing",
            "run_id": contract["run_id"],
            "task_id": task_id,
            "model": contract["job"]["model"],
            "provider_slug": contract["job"]["provider_slug"],
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
        },
    )


def _call_passed(call: dict) -> bool:
    return (
        call.get("operational_status") == "ok"
        and call.get("wire_schema_accepted") is True
        and call.get("provider_attribution_status") == "matched"
        and call.get("admitted_record_count", 0) >= 1
        and call.get("quarantined_record_count", 0) == 0
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    contract_path = args.contract.resolve()
    contract = _load(contract_path)
    validation = validate_contract(contract, contract_path)
    if args.dry_run:
        print(json.dumps(validation, indent=2, sort_keys=True))
        return 0
    if args.authorization is None or args.env_file is None or args.output_dir is None:
        raise RuntimeError("execution arguments are missing")
    validate_authorization(
        _load(args.authorization.resolve()), contract=contract, contract_path=contract_path
    )
    output_dir = args.output_dir.resolve()
    if not output_dir.is_dir() or (output_dir / "result.json").exists():
        raise RuntimeError("probe output directory is absent or already complete")
    if list(output_dir.glob("call-*-started.json")) or list(output_dir.glob("call-*-result.json")):
        raise RuntimeError("a decomposition call already started; rerun forbidden")
    _load_env(args.env_file.resolve())
    wrapper = _load(ROOT / contract["job"]["packet_path"])
    calls = []
    stance_packets = {}
    stance_compiled = {role: None for role in ROLE_ORDER}
    stop_reason = ""

    task_id = "trajectory"
    trajectory_prompts = build_role_trajectory_prompts_v1(wrapper)
    _started(output_dir / "call-01-started.json", contract=contract, task_id=task_id)
    trajectory_call = run_decomposed_task(
        task_id=task_id,
        contract=contract,
        prompts=trajectory_prompts,
        schema=role_trajectory_response_schema_v1(),
        response_schema_name="lolla_position_role_trajectory_v1",
        compile_candidate=lambda candidate: compile_role_trajectory_response_v1(
            response=candidate,
            wrapper=wrapper,
            producer_kind="model_operator_eval",
            producer_id=contract["job"]["model"],
            record_identity=task_id,
            call_metadata={
                "call_id": task_id,
                "model": contract["job"]["model"],
                "prompt_sha256": "sha256:" + trajectory_prompts["user_prompt_sha256"],
            },
        ),
    )
    _write(output_dir / "call-01-result.json", trajectory_call)
    calls.append(trajectory_call)
    trajectory_compiled = trajectory_call.get("compiled")
    if not _call_passed(trajectory_call) or not trajectory_compiled:
        stop_reason = "trajectory_wire_or_admission_gate_failed"
    else:
        next_call = 2
        for role in ROLE_ORDER:
            role_packet = build_stance_role_packet_v1(
                trajectory_compiled=trajectory_compiled,
                wrapper=wrapper,
                role=role,
            )
            stance_packets[role] = role_packet
            _write(output_dir / f"stance-packet-{role}.json", role_packet)
            if not role_packet["call_required"]:
                continue
            role_prompts = build_stance_role_prompts_v1(role_packet)
            _write(
                output_dir / f"stance-prompt-manifest-{role}.json",
                {
                    "role": role,
                    "system_prompt_sha256": role_prompts["system_prompt_sha256"],
                    "user_prompt_sha256": role_prompts["user_prompt_sha256"],
                    "response_schema_sha256": sha256_bytes(
                        canonical_json_bytes(stance_role_response_schema_v1(role))
                    ),
                },
            )
            role_task_id = f"stance-{role}"
            _started(
                output_dir / f"call-{next_call:02d}-started.json",
                contract=contract,
                task_id=role_task_id,
            )
            role_call = run_decomposed_task(
                task_id=role_task_id,
                contract=contract,
                prompts=role_prompts,
                schema=stance_role_response_schema_v1(role),
                response_schema_name=f"lolla_position_stance_{role}_v1",
                compile_candidate=lambda candidate, role=role, role_packet=role_packet, role_prompts=role_prompts: compile_stance_role_response_v1(
                    response=candidate,
                    packet=role_packet,
                    producer_kind="model_operator_eval",
                    producer_id=contract["job"]["model"],
                    call_metadata={
                        "call_id": f"stance-{role}",
                        "model": contract["job"]["model"],
                        "prompt_sha256": "sha256:" + role_prompts["user_prompt_sha256"],
                    },
                ),
            )
            _write(output_dir / f"call-{next_call:02d}-result.json", role_call)
            calls.append(role_call)
            stance_compiled[role] = role_call.get("compiled")
            next_call += 1
            if not _call_passed(role_call):
                stop_reason = f"{role}_stance_wire_or_admission_gate_failed"
                break

    joined = (
        join_position_decomposition_v1(
            trajectory_compiled=trajectory_compiled,
            stance_compiled_by_role=stance_compiled,
        )
        if trajectory_compiled
        else None
    )
    aggregate = {
        "schema_version": "lolla.reasoning_process_position_decomposition_probe_result.v1",
        "status": "reserved_case_decomposition_probe_preserved",
        "run_id": contract["run_id"],
        "calls": calls,
        "provider_request_count": sum(item.get("provider_calls", 0) for item in calls),
        "estimated_cost_usd": round(
            sum(float(item.get("estimated_cost_usd") or 0) for item in calls), 12
        ),
        "provider_reported_cost_usd": round(
            sum(float(item.get("provider_reported_cost_usd") or 0) for item in calls), 12
        ),
        "stop_reason": stop_reason,
        "stance_packets": stance_packets,
        "joined": joined,
        "semantic_review_status": (
            "source_first_review_required" if joined is not None else "not_applicable_no_trajectory"
        ),
        "boundary": contract["boundary"],
    }
    _write(output_dir / "result.json", aggregate)
    print(
        json.dumps(
            {
                "provider_request_count": aggregate["provider_request_count"],
                "estimated_cost_usd": aggregate["estimated_cost_usd"],
                "stop_reason": stop_reason,
                "join_status": joined.get("status") if joined else "not_available",
                "calls": [
                    {
                        "task_id": item["task_id"],
                        "operational_status": item["operational_status"],
                        "admitted_record_count": item.get("admitted_record_count", 0),
                        "quarantined_record_count": item.get("quarantined_record_count", 0),
                    }
                    for item in calls
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
