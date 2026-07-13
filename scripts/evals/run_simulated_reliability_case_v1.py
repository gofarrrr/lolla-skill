#!/usr/bin/env python3
"""Run one frozen simulated-reliability V1 case with complete call custody."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any
from urllib import error, request


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.canonical_model_selection import build_assessment_cards
from engine.system_b.fresh_reasoning_pressure import compile_control_response
from engine.system_b.reasoning_process_position_role_first_v24 import (
    compile_position_starting_response_v24,
)
from engine.system_b.reasoning_process_position_role_first_v242 import (
    compile_response_v242,
)
from engine.system_b.simulated_reliability_v1 import (
    build_direct_ledger,
    build_graph_ledger,
    build_mechanism_input_v1,
    build_mechanism_prompts_v1,
    build_three_arm_bundle,
    compile_mechanism_response_v1,
    compile_pressure_response,
    join_role_records_v1,
    mechanism_response_schema_v1,
)


MANIFEST = ROOT / "research/simulated-reliability-corpus-v1-2026-07-12/manifest.json"
ROUTING = ROOT / "docs/conversation-understanding/reasoning-pattern-shadow-routing-v0.json"
KNOWLEDGE = ROOT / "data/knowledge_graph.json"
RELATIONSHIP = ROOT / "data/relationship_graph.json"


class V1RunError(RuntimeError):
    pass


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def value_sha(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def merge_contract(base: Mapping[str, Any], overlay: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in overlay.items():
        if key in {"base_contract_path", "base_contract_sha256"}:
            continue
        if isinstance(value, Mapping) and isinstance(result.get(key), Mapping):
            result[key] = merge_contract(result[key], value)
        else:
            result[key] = value
    return result


def load_contract(path: Path) -> dict[str, Any]:
    contract = load(path)
    base_path_value = contract.get("base_contract_path")
    if not base_path_value:
        return contract
    base_path = ROOT / str(base_path_value)
    if file_sha(base_path) != contract.get("base_contract_sha256"):
        raise V1RunError("base runtime contract drifted")
    resolved = merge_contract(load_contract(base_path), contract)
    replacements = {
        item["path"]: item["sha256"] for item in contract.get("frozen_input_overrides", [])
    }
    frozen = []
    seen: set[str] = set()
    for item in resolved["frozen_inputs"]:
        path_value = item["path"]
        frozen.append(
            {"path": path_value, "sha256": replacements.get(path_value, item["sha256"])}
        )
        seen.add(path_value)
    for path_value, digest in replacements.items():
        if path_value not in seen:
            frozen.append({"path": path_value, "sha256": digest})
    resolved["frozen_inputs"] = frozen
    return resolved


def write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_env(path: Path | None) -> None:
    if path is None or not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        os.environ.setdefault(key.strip(), value)


def extract_object(content: str) -> dict[str, Any]:
    try:
        value = json.loads(content)
    except json.JSONDecodeError as exc:
        raise V1RunError("provider content is not strict JSON") from exc
    if not isinstance(value, dict):
        raise V1RunError("provider content is not a JSON object")
    return value


def provider_call(
    *,
    output: Path,
    ordinal: int,
    task_id: str,
    case_id: str,
    repeat_id: str,
    contract: Mapping[str, Any],
    prompts: Mapping[str, str],
    schema: Mapping[str, Any],
    schema_name: str,
    compile_candidate: Callable[[dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    config = contract["provider_request"]
    task_config = contract["task_limits"][task_id]
    reasoning_effort = task_config.get("reasoning_effort", "medium")
    if reasoning_effort not in {"low", "medium", "high"}:
        raise V1RunError("task reasoning effort is invalid")
    seed = int(contract["seeds"][repeat_id])
    wire_mode = task_config.get("wire_mode", "strict_json_schema")
    if wire_mode not in {"strict_json_schema", "json_object_schema_in_prompt"}:
        raise V1RunError("task wire mode is invalid")
    effective_user_prompt = prompts["user_prompt"]
    response_format: dict[str, Any]
    if wire_mode == "strict_json_schema":
        response_format = {
            "type": "json_schema",
            "json_schema": {"name": schema_name, "strict": True, "schema": schema},
        }
    else:
        effective_user_prompt += (
            "\n\nMODEL-FACING OUTPUT SCHEMA\n"
            + canonical(schema)
            + "\n\nReturn exactly one JSON object matching this schema. Do not add markdown, commentary, or fields."
        )
        response_format = {"type": "json_object"}
    provider = {
        "order": list(config["provider_order"]),
        "only": list(config["provider_only"]),
        "allow_fallbacks": False,
        "require_parameters": True,
        "data_collection": "deny",
        "zdr": True,
        "max_price": dict(config["max_price_usd_per_million_tokens"]),
    }
    body = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": prompts["system_prompt"]},
            {"role": "user", "content": effective_user_prompt},
        ],
        "response_format": response_format,
        "provider": provider,
        "seed": seed,
        "max_tokens": task_config["max_output_tokens"],
        "reasoning": {"effort": reasoning_effort, "exclude": True},
        "stream": False,
    }
    prefix = f"call-{ordinal:02d}-{task_id}"
    started_path = output / f"{prefix}-started.json"
    result_path = output / f"{prefix}-result.json"
    if started_path.exists() or result_path.exists():
        raise V1RunError(f"call artifact already exists: {prefix}")
    base = {
        "task_id": task_id,
        "case_id": case_id,
        "repeat_id": repeat_id,
        "requested_model": config["model"],
        "provider_order": provider["order"],
        "provider_only": provider["only"],
        "zdr": True,
        "data_collection": "deny",
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "temperature_supplied": False,
        "top_p_supplied": False,
        "seed": seed,
        "reasoning_effort": reasoning_effort,
        "reasoning_content_excluded": True,
        "max_output_tokens": task_config["max_output_tokens"],
        "wire_mode": wire_mode,
        "system_prompt_sha256": prompts["system_prompt_sha256"],
        "base_user_prompt_sha256": prompts["user_prompt_sha256"],
        "effective_user_prompt_sha256": hashlib.sha256(effective_user_prompt.encode("utf-8")).hexdigest(),
        "response_schema_sha256": value_sha(schema),
        "request_body_sha256": value_sha(body),
    }
    write(started_path, {**base, "status": "started_before_network_transport", "started_at_unix": time.time()})
    api_key = os.getenv("LOLLA_OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        result = {**base, "operational_status": "missing_api_key", "provider_calls": 0}
        write(result_path, result)
        return result
    req = request.Request(
        config["endpoint"],
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    started = time.monotonic()
    try:
        with request.urlopen(req, timeout=config["timeout_seconds"]) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            error_payload = json.loads(raw)
        except json.JSONDecodeError:
            error_payload = {"message": raw[:3000]}
        result = {
            **base,
            "operational_status": f"http_error_{exc.code}",
            "http_status": exc.code,
            "provider_calls": 1,
            "provider_error": error_payload,
            "provider_payload_sha256": value_sha(error_payload),
            "duration_seconds": round(time.monotonic() - started, 3),
        }
        write(result_path, result)
        return result
    except Exception as exc:  # noqa: BLE001
        result = {
            **base,
            "operational_status": "transport_error",
            "provider_calls": 1,
            "error_type": type(exc).__name__,
            "error_message": str(exc)[:1000],
            "duration_seconds": round(time.monotonic() - started, 3),
        }
        write(result_path, result)
        return result

    choices = payload.get("choices") if isinstance(payload.get("choices"), list) else []
    choice = choices[0] if choices and isinstance(choices[0], Mapping) else {}
    message = choice.get("message") if isinstance(choice.get("message"), Mapping) else {}
    content = str(message.get("content", ""))
    candidate = None
    compiled = None
    validation_error = ""
    try:
        candidate = extract_object(content)
        compiled = compile_candidate(candidate)
    except Exception as exc:  # noqa: BLE001
        validation_error = f"{type(exc).__name__}: {exc}"
    usage = payload.get("usage") if isinstance(payload.get("usage"), Mapping) else {}
    result = {
        **base,
        "operational_status": "ok" if compiled is not None else "local_validation_failed",
        "provider_calls": 1,
        "served_model": str(payload.get("model", "")),
        "served_provider": str(payload.get("provider", "")),
        "generation_id": str(payload.get("id", "")),
        "finish_reason": str(choice.get("finish_reason", "")),
        "usage": dict(usage),
        "provider_reported_cost_usd": usage.get("cost"),
        "raw_content": content,
        "raw_content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "candidate": candidate,
        "compiled": compiled,
        "validation_error": validation_error,
        "provider_payload_sha256": value_sha(payload),
        "reasoning_content_returned": bool(message.get("reasoning") or message.get("reasoning_details")),
        "duration_seconds": round(time.monotonic() - started, 3),
    }
    write(result_path, result)
    return result


def validate_contract(
    contract_path: Path,
    authorization_path: Path,
    case_id: str,
    repeat_id: str,
    phase: str = "calibration",
) -> dict[str, Any]:
    contract = load_contract(contract_path)
    if phase not in {"calibration", "transfer"}:
        raise V1RunError("runtime phase is invalid")
    expected_contract_status = (
        "frozen_before_calibration_calls"
        if phase == "calibration"
        else "frozen_before_transfer_calls"
    )
    if contract.get("status") != expected_contract_status:
        raise V1RunError("runtime contract is not frozen")
    phase_config = contract[phase]
    if case_id not in phase_config["authorized_case_ids"]:
        raise V1RunError(f"case is not authorized for {phase}")
    if repeat_id not in contract["seeds"]:
        raise V1RunError("repeat identity is not frozen")
    for item in contract["frozen_inputs"]:
        if file_sha(ROOT / item["path"]) != item["sha256"]:
            raise V1RunError(f"frozen input drifted: {item['path']}")
    authorization = load(authorization_path)
    expected = {
        "schema_version": f"lolla.simulated_reliability_{phase}_authorization.v1",
        "status": (
            "authorized_once_after_provider_free_and_current_practice_gates"
            if phase == "calibration"
            else "authorized_once_after_calibration_and_freeze_gates"
        ),
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": file_sha(contract_path),
        "authorized_case_ids": phase_config["authorized_case_ids"],
        "maximum_provider_calls": phase_config["maximum_provider_calls"],
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
    }
    if authorization != expected:
        raise V1RunError("calibration authorization drifted")
    return contract


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--repeat-id", default="primary")
    parser.add_argument("--phase", choices=["calibration", "transfer"], default="calibration")
    parser.add_argument("--role-input-root", type=Path, required=True)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    contract_path = args.contract.resolve()
    authorization_path = args.authorization.resolve()
    contract = validate_contract(
        contract_path, authorization_path, args.case_id, args.repeat_id, args.phase
    )
    if args.dry_run:
        print(json.dumps({"status": "runtime_contract_valid", "provider_calls": 0}, indent=2))
        return 0

    manifest = load(MANIFEST)
    case = next(
        (
            {**item, "split": split_name}
            for split_name, key in (("calibration", "calibration_cases"), ("transfer", "transfer_cases"))
            for item in manifest[key]
            if item["case_id"] == args.case_id
        ),
        None,
    )
    if case is None:
        case = next(
            (
                {**item, "split": "calibration_control"}
                for item in contract["calibration"].get("external_controls", [])
                if item["case_id"] == args.case_id
            ),
            None,
        )
    allowed_splits = {"calibration", "calibration_control"} if args.phase == "calibration" else {"transfer"}
    if case is None or case["split"] not in allowed_splits:
        raise V1RunError(f"{args.phase} case is absent from the frozen sources")
    source = ROOT / case["path"]
    if file_sha(source) != case["sha256"]:
        raise V1RunError("case source drifted")
    role_dir = args.role_input_root.resolve() / case["split"] / args.case_id
    wrapper = load(role_dir / "position-wrapper.json")
    role_bundle = load(role_dir / "role-request-bundle.json")
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        raise V1RunError("output directory is not empty")
    output.mkdir(parents=True, exist_ok=True)
    load_env(args.env_file.resolve() if args.env_file else None)

    calls: list[dict[str, Any]] = []
    request_specs = role_bundle["requests"]
    starting = provider_call(
        output=output,
        ordinal=1,
        task_id="starting",
        case_id=args.case_id,
        repeat_id=args.repeat_id,
        contract=contract,
        prompts=request_specs["starting"]["prompts"],
        schema=request_specs["starting"]["response_schema"],
        schema_name="lolla_v1_starting",
        compile_candidate=lambda candidate: compile_position_starting_response_v24(
            response=candidate,
            packet=request_specs["starting"]["packet"],
            producer_kind="simulated_reliability_v1",
            producer_id=contract["provider_request"]["model"],
        ),
    )
    calls.append(starting)
    if starting.get("compiled") is None:
        write(output / "result.json", {"status": "stopped_after_starting_failure", "calls": calls})
        return 1

    paired = provider_call(
        output=output,
        ordinal=2,
        task_id="current_qualification",
        case_id=args.case_id,
        repeat_id=args.repeat_id,
        contract=contract,
        prompts=request_specs["current_qualification"]["prompts"],
        schema=request_specs["current_qualification"]["response_schema"],
        schema_name="lolla_v1_current_qualification",
        compile_candidate=lambda candidate: compile_response_v242(
            response=candidate,
            wrapper=wrapper,
            producer_kind="simulated_reliability_v1",
            producer_id=contract["provider_request"]["model"],
        ),
    )
    calls.append(paired)
    if paired.get("compiled") is None:
        write(output / "result.json", {"status": "stopped_after_current_qualification_failure", "calls": calls})
        return 1
    try:
        joined = join_role_records_v1(
            starting_compiled=starting["compiled"], paired_compiled=paired["compiled"]
        )
    except Exception as exc:  # noqa: BLE001
        write(
            output / "result.json",
            {
                "status": "stopped_after_role_join_failure",
                "calls": calls,
                "join_error": f"{type(exc).__name__}: {exc}",
            },
        )
        return 1
    write(output / "joined-role-records.json", joined)

    mechanism_packet = build_mechanism_input_v1(
        case_id=args.case_id,
        arm_id=args.case_id + "-primary",
        joined=joined,
        conversation=source.read_text(encoding="utf-8"),
        source_refs=[{"path": case["path"], "sha256": case["sha256"]}],
    )
    mechanism_prompts = build_mechanism_prompts_v1(mechanism_packet)
    mechanism_schema = mechanism_response_schema_v1()
    write(
        output / "mechanism-request.json",
        {"packet": mechanism_packet, "prompts": mechanism_prompts, "response_schema": mechanism_schema},
    )
    mechanism = provider_call(
        output=output,
        ordinal=3,
        task_id="mechanism",
        case_id=args.case_id,
        repeat_id=args.repeat_id,
        contract=contract,
        prompts=mechanism_prompts,
        schema=mechanism_schema,
        schema_name="lolla_v1_mechanism",
        compile_candidate=lambda candidate: compile_mechanism_response_v1(
            response=candidate,
            packet=mechanism_packet,
            producer_kind="simulated_reliability_v1",
            producer_id=contract["provider_request"]["model"],
        ),
    )
    calls.append(mechanism)
    if mechanism.get("compiled") is None:
        write(output / "result.json", {"status": "stopped_after_mechanism_failure", "calls": calls})
        return 1

    unresolved = [
        item["mechanism_id"]
        for item in mechanism["compiled"]["routing_projection"]["pattern_nodes"]
    ]
    routing = load(ROUTING)["mechanism_seed_models"]
    knowledge = load(KNOWLEDGE)
    relationship = load(RELATIONSHIP)
    direct = build_direct_ledger(
        unresolved_mechanism_ids=unresolved,
        mechanism_seed_models=routing,
        canonical_model_ids=set(knowledge["models"]),
    )
    graph = build_graph_ledger(
        direct_ledger=direct,
        relation_graph=relationship,
        canonical_model_ids=set(knowledge["models"]),
    )
    arm_bundle = build_three_arm_bundle(
        case_id=args.case_id,
        conversation=source.read_text(encoding="utf-8"),
        direct_ledger=direct,
        graph_ledger=graph,
        challenge_cards=build_assessment_cards(knowledge["models"]),
        source_refs=[{"path": case["path"], "sha256": case["sha256"]}],
    )
    write(output / "direct-ledger.json", direct)
    write(output / "graph-ledger.json", graph)
    write(output / "three-arm-bundle.json", arm_bundle)

    call_arms = [name for name, arm in arm_bundle["arms"].items() if arm["call_required"]]
    call_arms.sort(key=lambda name: hashlib.sha256(f"{contract['run_id']}|{args.case_id}|{args.repeat_id}|{name}".encode()).hexdigest())
    ordinal = 4
    arm_results: dict[str, Any] = {}
    for arm_name in call_arms:
        arm = arm_bundle["arms"][arm_name]
        compiler = (
            (lambda candidate, packet=arm["packet"]: compile_control_response(response=candidate, packet=packet))
            if arm_name == "transcript_only"
            else (lambda candidate, packet=arm["packet"]: compile_pressure_response(response=candidate, packet=packet))
        )
        call = provider_call(
            output=output,
            ordinal=ordinal,
            task_id=arm_name,
            case_id=args.case_id,
            repeat_id=args.repeat_id,
            contract=contract,
            prompts=arm["prompts"],
            schema=arm["response_schema"],
            schema_name="lolla_v1_" + arm_name,
            compile_candidate=compiler,
        )
        ordinal += 1
        calls.append(call)
        arm_results[arm_name] = call
        if call.get("compiled") is None:
            write(
                output / "result.json",
                {"status": f"stopped_after_{arm_name}_failure", "calls": calls, "arm_results": arm_results},
            )
            return 1
    for arm_name, arm in arm_bundle["arms"].items():
        if not arm["call_required"]:
            arm_results[arm_name] = arm

    result = {
        "schema_version": "lolla.simulated_reliability_case_result.v1",
        "status": f"{args.phase}_case_execution_complete_source_review_required",
        "case_id": args.case_id,
        "repeat_id": args.repeat_id,
        "joined_role_records": joined,
        "unresolved_mechanism_ids": unresolved,
        "direct_candidate_count": len(direct["active_candidates"]),
        "direct_reserve_count": len(direct["reserve_candidates"]),
        "graph_candidate_count": len(graph["active_candidates"]),
        "graph_reserve_count": len(graph["reserve_candidates"]),
        "arm_call_order": call_arms,
        "arm_results": arm_results,
        "provider_request_count": sum(int(call.get("provider_calls", 0)) for call in calls),
        "provider_reported_cost_usd": round(
            sum(float(call.get("provider_reported_cost_usd") or 0) for call in calls), 12
        ),
        "automatic_retries": 0,
        "runtime_effect": "none",
        "source_review_status": "required",
        "scalar_quality_score": None,
    }
    write(output / "result.json", result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "case_id": args.case_id,
                "provider_request_count": result["provider_request_count"],
                "provider_reported_cost_usd": result["provider_reported_cost_usd"],
                "unresolved_mechanism_ids": unresolved,
                "direct_candidate_count": result["direct_candidate_count"],
                "graph_candidate_count": result["graph_candidate_count"],
                "arm_call_order": call_arms,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
