#!/usr/bin/env python3
"""Run one frozen three-call paired role-first v2.4 probe."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_position_role_first_v24 import (  # noqa: E402
    build_position_current_qualification_packet_v24,
    build_position_current_qualification_prompts_v24,
    build_position_relation_packet_v24, build_position_relation_prompts_v24,
    build_position_starting_packet_v24, build_position_starting_prompts_v24,
    compile_position_current_qualification_response_v24,
    compile_position_relation_response_v24, compile_position_starting_response_v24,
    join_position_role_first_v24, position_current_qualification_response_schema_v24,
    position_relation_response_schema_v24, position_starting_response_schema_v24,
)
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes  # noqa: E402
from scripts.evals.reasoning_process_position_decomposition_transport import run_decomposed_task  # noqa: E402
from scripts.evals.run_conversation_state_microtask_probe import _load_env  # noqa: E402
from scripts.evals.run_reasoning_process_phase4_transfer import _load, _sha, _write  # noqa: E402
from scripts.evals.run_reasoning_process_position_role_first_v2_probe import _call_passed, _started  # noqa: E402

CONTRACT_SCHEMA = "lolla.reasoning_process_position_role_first_v24_probe_contract.v1"
AUTH_SCHEMA = "lolla.reasoning_process_position_role_first_v24_probe_authorization.v1"
BUDGET = {"maximum_provider_calls": 3, "maximum_estimated_cost_usd": 0.01, "automatic_retries": 0, "semantic_retries": 0, "fallback_models": 0, "evaluator_calls": 0, "embedding_calls": 0, "graph_calls": 0, "pipeline_calls": 0, "runtime_calls": 0}
CONFIG = {"provider": "openrouter", "endpoint": "https://openrouter.ai/api/v1/chat/completions", "wire_mode": "strict_json_schema", "temperature": 0.0, "seed": 0, "reasoning_enabled": False, "max_output_tokens": 1600, "provider_timeout_seconds": 90, "require_supported_parameters": True, "allow_provider_fallbacks": False, "automatic_retries": 0, "response_healing": False, "parallel_calls": False}


def validate_contract(contract: dict, contract_path: Path) -> dict:
    if contract.get("schema_version") != CONTRACT_SCHEMA or contract.get("status") != "frozen_before_at_most_three_v24_new_case_calls":
        raise RuntimeError("unexpected or unfrozen v2.4 contract")
    for item in contract["frozen_inputs"]:
        if _sha(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"frozen input drifted: {item['path']}")
    job = contract["job"]
    packet_path = ROOT / job["packet_path"]
    if _sha(packet_path) != job["packet_sha256"]:
        raise RuntimeError("v2.4 packet drifted")
    wrapper = _load(packet_path)
    starting_packet = build_position_starting_packet_v24(wrapper=wrapper, role="starting")
    starting_prompts = build_position_starting_prompts_v24(starting_packet)
    paired_packet = build_position_current_qualification_packet_v24(wrapper=wrapper)
    paired_prompts = build_position_current_qualification_prompts_v24(paired_packet)
    expected = {
        "starting": {"system_prompt_sha256": starting_prompts["system_prompt_sha256"], "user_prompt_sha256": starting_prompts["user_prompt_sha256"], "response_schema_sha256": sha256_bytes(canonical_json_bytes(position_starting_response_schema_v24("starting")))},
        "current_qualification": {"system_prompt_sha256": paired_prompts["system_prompt_sha256"], "user_prompt_sha256": paired_prompts["user_prompt_sha256"], "response_schema_sha256": sha256_bytes(canonical_json_bytes(position_current_qualification_response_schema_v24()))},
    }
    if job["request_contracts"] != expected or job["relation_response_schema_sha256"] != sha256_bytes(canonical_json_bytes(position_relation_response_schema_v24())):
        raise RuntimeError("v2.4 request contracts drifted")
    if job["case_id"] != "amb3-case05-registry-pharma-partnership" or job["model"] != "deepseek/deepseek-v4-flash" or job["provider_slug"] != "alibaba":
        raise RuntimeError("v2.4 case or route drifted")
    if contract["budget"] != BUDGET or contract["call_configuration"] != CONFIG:
        raise RuntimeError("v2.4 budget or configuration drifted")
    return {"status": "position_role_first_v24_probe_contract_valid", "contract_path": str(contract_path.relative_to(ROOT)), "provider_calls_made": 0}


def validate_authorization(value: dict, *, contract: dict, contract_path: Path) -> None:
    expected = {"schema_version": AUTH_SCHEMA, "status": "authorized_once_after_v24_new_case_target_and_adversarial_gates", "contract_path": str(contract_path.relative_to(ROOT)), "contract_sha256": _sha(contract_path), "run_id": contract["run_id"], "maximum_provider_calls": 3, "automatic_retries": 0, "semantic_retries": 0, "fallback_models": 0, "evaluator_calls": 0, "embedding_calls": 0, "graph_calls": 0, "pipeline_calls": 0, "runtime_calls": 0}
    if value != expected:
        raise RuntimeError("v2.4 authorization drifted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    contract_path, contract = args.contract.resolve(), _load(args.contract.resolve())
    validation = validate_contract(contract, contract_path)
    if args.dry_run:
        print(json.dumps(validation, indent=2, sort_keys=True))
        return 0
    if args.authorization is None or args.env_file is None or args.output_dir is None:
        raise RuntimeError("execution arguments missing")
    validate_authorization(_load(args.authorization.resolve()), contract=contract, contract_path=contract_path)
    output = args.output_dir.resolve()
    if not output.is_dir() or (output / "result.json").exists() or list(output.glob("call-*-started.json")):
        raise RuntimeError("v2.4 output absent, complete, or previously started")
    _load_env(args.env_file.resolve())
    wrapper, calls, roles = _load(ROOT / contract["job"]["packet_path"]), [], {}

    starting_packet = build_position_starting_packet_v24(wrapper=wrapper, role="starting")
    starting_prompts = build_position_starting_prompts_v24(starting_packet)
    _write(output / "starting-packet.json", starting_packet)
    _started(output / "call-01-started.json", contract=contract, task_id="role-starting")
    starting_call = run_decomposed_task(task_id="role-starting", contract=contract, prompts=starting_prompts, schema=position_starting_response_schema_v24("starting"), response_schema_name="lolla_position_starting_v24", compile_candidate=lambda candidate: compile_position_starting_response_v24(response=candidate, packet=starting_packet, producer_kind="model_operator_eval", producer_id=contract["job"]["model"], call_metadata={"call_id": "role-starting", "model": contract["job"]["model"], "prompt_sha256": "sha256:" + starting_prompts["user_prompt_sha256"]}))
    _write(output / "call-01-result.json", starting_call)
    calls.append(starting_call)
    if starting_call.get("compiled") is not None:
        roles["starting"] = starting_call["compiled"]

    paired_packet = build_position_current_qualification_packet_v24(wrapper=wrapper)
    paired_prompts = build_position_current_qualification_prompts_v24(paired_packet)
    _write(output / "paired-packet.json", paired_packet)
    _started(output / "call-02-started.json", contract=contract, task_id="current-qualification")
    paired_call = run_decomposed_task(task_id="current-qualification", contract=contract, prompts=paired_prompts, schema=position_current_qualification_response_schema_v24(), response_schema_name="lolla_position_current_qualification_v24", compile_candidate=lambda candidate: compile_position_current_qualification_response_v24(response=candidate, wrapper=wrapper, producer_kind="model_operator_eval", producer_id=contract["job"]["model"], call_metadata={"call_id": "current-qualification", "model": contract["job"]["model"], "prompt_sha256": "sha256:" + paired_prompts["user_prompt_sha256"]}))
    _write(output / "call-02-result.json", paired_call)
    calls.append(paired_call)
    if paired_call.get("compiled") is not None:
        roles.update(paired_call["compiled"]["role_compiled"])

    relation_call, relation_compiled, block_reason = None, None, ""
    if not _call_passed(starting_call) or not _call_passed(paired_call) or set(roles) != {"starting", "current", "qualification"}:
        block_reason = "starting_or_paired_wire_or_admission_gate_failed"
    else:
        relation_packet = build_position_relation_packet_v24(role_compiled_by_role=roles)
        relation_prompts = build_position_relation_prompts_v24(relation_packet)
        _write(output / "relation-packet.json", relation_packet)
        _started(output / "call-03-started.json", contract=contract, task_id="relation")
        relation_call = run_decomposed_task(task_id="relation", contract=contract, prompts=relation_prompts, schema=position_relation_response_schema_v24(), response_schema_name="lolla_position_relation_v24", compile_candidate=lambda candidate: compile_position_relation_response_v24(response=candidate, packet=relation_packet, producer_kind="model_operator_eval", producer_id=contract["job"]["model"]))
        _write(output / "call-03-result.json", relation_call)
        calls.append(relation_call)
        relation_compiled = relation_call.get("compiled")
        if not _call_passed(relation_call):
            block_reason = "relation_wire_or_admission_gate_failed"
    joined = join_position_role_first_v24(role_compiled_by_role=roles, relation_compiled=relation_compiled) if set(roles) == {"starting", "current", "qualification"} else None
    result = {"schema_version": "lolla.reasoning_process_position_role_first_v24_probe_result.v1", "status": "new_case_paired_role_probe_preserved", "run_id": contract["run_id"], "calls": calls, "provider_request_count": sum(item.get("provider_calls", 0) for item in calls), "estimated_cost_usd": round(sum(float(item.get("estimated_cost_usd") or 0) for item in calls), 12), "provider_reported_cost_usd": round(sum(float(item.get("provider_reported_cost_usd") or 0) for item in calls), 12), "relation_block_reason": block_reason, "joined": joined, "semantic_review_status": "source_first_review_required", "boundary": contract["boundary"]}
    _write(output / "result.json", result)
    print(json.dumps({"provider_request_count": result["provider_request_count"], "estimated_cost_usd": result["estimated_cost_usd"], "relation_block_reason": block_reason, "join_status": joined.get("status") if joined else "not_available", "calls": [{"task_id": item["task_id"], "operational_status": item["operational_status"], "admitted_record_count": item.get("admitted_record_count", 0), "quarantined_record_count": item.get("quarantined_record_count", 0)} for item in calls]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
