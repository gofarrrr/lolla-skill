#!/usr/bin/env python3
"""Run the frozen R4 complementary-reader diagnostic after explicit authorization."""
from __future__ import annotations

import argparse
import json
import os
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from urllib import error, request

from engine.system_b.conversation_state_fan_in import (
    assemble_conversation_state_fan_in,
    build_reader_result,
)
from engine.system_b.r4_complementary_readers import (
    build_relationship_packet_v1,
    build_relationship_prompts_v1,
    build_source_registry_v1,
    canonical_json_bytes,
    compile_relationship_response_v1,
    compile_uncertainty_response_v1,
    existing_reader_results_v1,
    planned_readers_v1,
    relationship_response_schema_v1,
    sha256_bytes,
    source_alias_catalog_v1,
    uncertainty_response_schema_v1,
    value_sha256,
)
from scripts.evals.build_r4_complementary_reader_preflight import (
    MODEL,
    PROVIDER,
    ROOT,
    TASKS,
    build_request_preview,
)


CONTRACT_SCHEMA = "lolla.r4_complementary_reader_experiment_contract.v1"
AUTH_SCHEMA = "lolla.r4_complementary_reader_experiment_authorization.v1"
RESULT_SCHEMA = "lolla.r4_complementary_reader_experiment_result.v1"


class R4ExperimentError(RuntimeError):
    """Raised when the frozen experiment or call custody drifts."""


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _render(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def _write(path: Path, value: Any) -> bytes:
    raw = _render(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return raw


def _file_sha(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def _load_env(path: Path) -> None:
    if not path.is_file():
        raise R4ExperimentError("environment file does not exist")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key.strip(), value)


def _validate_contract(contract_path: Path) -> dict[str, Any]:
    contract = _load(contract_path)
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise R4ExperimentError("unexpected experiment contract schema")
    if contract.get("status") != "frozen_provider_free_call_authorization_required":
        raise R4ExperimentError("experiment contract is not frozen")
    budget = contract.get("budget", {})
    expected_budget = {
        "maximum_provider_calls": 4,
        "maximum_calls_per_case": 2,
        "maximum_provider_reported_cost_per_case_usd": 0.015,
        "maximum_provider_reported_cost_total_usd": 0.03,
        "automatic_retries": 0,
        "semantic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
    }
    if budget != expected_budget:
        raise R4ExperimentError("experiment budget drifted")
    operator = contract.get("operator", {})
    if operator != {
        "model": MODEL,
        "allowed_served_model_ids": [
            "google/gemini-3.1-flash-lite",
            "google/gemini-3.1-flash-lite-20260507",
        ],
        "provider_slug": PROVIDER,
        "allowed_served_provider_names": ["Google"],
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "provider_order": [PROVIDER],
        "provider_only": [PROVIDER],
        "allow_fallbacks": False,
        "require_parameters": True,
        "data_collection": "deny",
        "zdr": True,
        "maximum_price_usd_per_million_tokens": {
            "prompt": 0.25,
            "completion": 1.5,
        },
    }:
        raise R4ExperimentError("experiment operator drifted")
    if contract.get("task_limits") != TASKS:
        raise R4ExperimentError("experiment task limits drifted")
    for row in contract.get("frozen_inputs", []):
        path = ROOT / row["path"]
        if not path.is_file() or _file_sha(path) != row["sha256"]:
            raise R4ExperimentError(f"frozen input drifted: {row['path']}")
    preflight = _load(ROOT / contract["preflight"]["path"])
    if (
        preflight.get("status")
        != "provider_free_preflight_pass_call_authorization_required"
        or preflight.get("decision", {}).get("provider_free_package_ready") is not True
        or preflight.get("decision", {}).get("provider_calls_authorized") is not False
    ):
        raise R4ExperimentError("provider-free preflight gate is not closed")
    if [row["case_id"] for row in contract.get("cases", [])] != [
        "v1-case02-discharge-transport",
        "v1-case03-executive-hire",
    ]:
        raise R4ExperimentError("experiment case order drifted")
    uncertainty_schema = uncertainty_response_schema_v1()
    relationship_schema = relationship_response_schema_v1()
    if value_sha256(uncertainty_schema) != contract["schemas"]["uncertainty_sha256"]:
        raise R4ExperimentError("uncertainty schema drifted")
    if value_sha256(relationship_schema) != contract["schemas"]["relationship_sha256"]:
        raise R4ExperimentError("relationship schema drifted")
    for case in contract["cases"]:
        preview = _load(ROOT / case["uncertainty_request_preview_path"])
        if preview.get("body_sha256") != case["uncertainty_request_body_sha256"]:
            raise R4ExperimentError("uncertainty request preview drifted")
        if preview["body"]["seed"] != case["seeds"]["uncertainty"]:
            raise R4ExperimentError("uncertainty seed drifted")
    return contract


def _validate_authorization(
    authorization_path: Path, *, contract: Mapping[str, Any], contract_path: Path
) -> None:
    authorization = _load(authorization_path)
    expected = {
        "schema_version": AUTH_SCHEMA,
        "status": "authorized_once_after_provider_free_preflight",
        "contract_path": _relative(contract_path),
        "contract_sha256": _file_sha(contract_path),
        "run_id": contract["run_id"],
        "authorized_case_ids": [row["case_id"] for row in contract["cases"]],
        "maximum_provider_calls": contract["budget"]["maximum_provider_calls"],
        "maximum_provider_reported_cost_per_case_usd": contract["budget"][
            "maximum_provider_reported_cost_per_case_usd"
        ],
        "maximum_provider_reported_cost_total_usd": contract["budget"][
            "maximum_provider_reported_cost_total_usd"
        ],
        "automatic_retries": 0,
        "semantic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
    }
    if authorization != expected:
        raise R4ExperimentError("experiment authorization drifted")


def _provider_call(
    *,
    output: Path,
    ordinal: int,
    case_id: str,
    task: str,
    preview: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    body = preview["body"]
    prefix = f"call-{ordinal:02d}-{task}"
    started_path = output / f"{prefix}-started.json"
    result_path = output / f"{prefix}-result.json"
    if started_path.exists() or result_path.exists():
        raise R4ExperimentError(f"call artifact already exists: {prefix}")
    base = {
        "task": task,
        "case_id": case_id,
        "requested_model": body["model"],
        "provider_order": body["provider"]["order"],
        "provider_only": body["provider"]["only"],
        "zdr": body["provider"]["zdr"],
        "data_collection": body["provider"]["data_collection"],
        "automatic_retries": 0,
        "semantic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "seed": body["seed"],
        "reasoning_effort": body["reasoning"]["effort"],
        "reasoning_content_excluded": body["reasoning"]["exclude"],
        "max_output_tokens": body["max_tokens"],
        "wire_mode": "strict_json_schema",
        "request_body_sha256": value_sha256(body),
        "system_prompt_sha256": sha256_bytes(
            body["messages"][0]["content"].encode("utf-8")
        ),
        "user_prompt_sha256": sha256_bytes(
            body["messages"][1]["content"].encode("utf-8")
        ),
        "response_schema_sha256": value_sha256(
            body["response_format"]["json_schema"]["schema"]
        ),
    }
    _write(
        started_path,
        {**base, "status": "started_before_network_transport", "started_at_unix": time.time()},
    )
    api_key = os.getenv("LOLLA_OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        result = {**base, "operational_status": "missing_api_key", "provider_calls": 0}
        _write(result_path, result)
        return result
    req = request.Request(
        contract["operator"]["endpoint"],
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    started = time.monotonic()
    try:
        with request.urlopen(req, timeout=180) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            provider_error = json.loads(raw)
        except json.JSONDecodeError:
            provider_error = {"message": raw[:3000]}
        result = {
            **base,
            "operational_status": f"http_error_{exc.code}",
            "http_status": exc.code,
            "provider_calls": 1,
            "provider_error": provider_error,
            "provider_payload_sha256": value_sha256(provider_error),
            "duration_seconds": round(time.monotonic() - started, 3),
        }
        _write(result_path, result)
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
        _write(result_path, result)
        return result

    choices = payload.get("choices") if isinstance(payload.get("choices"), list) else []
    choice = choices[0] if choices and isinstance(choices[0], Mapping) else {}
    message = choice.get("message") if isinstance(choice.get("message"), Mapping) else {}
    content = message.get("content", "")
    if not isinstance(content, str):
        content = json.dumps(content, ensure_ascii=False)
    candidate = None
    parse_error = ""
    try:
        candidate = json.loads(content)
        if not isinstance(candidate, dict):
            raise R4ExperimentError("provider content is not a JSON object")
    except Exception as exc:  # noqa: BLE001
        parse_error = f"{type(exc).__name__}: {exc}"
    usage = payload.get("usage") if isinstance(payload.get("usage"), Mapping) else {}
    served_model = str(payload.get("model", ""))
    served_provider = str(payload.get("provider", ""))
    attribution_ok = (
        served_model in contract["operator"]["allowed_served_model_ids"]
        and served_provider in contract["operator"]["allowed_served_provider_names"]
    )
    result = {
        **base,
        "operational_status": (
            "candidate_parsed"
            if candidate is not None and attribution_ok
            else "operator_attribution_failed"
            if candidate is not None
            else "candidate_parse_failed"
        ),
        "provider_calls": 1,
        "served_model": served_model,
        "served_provider": served_provider,
        "operator_attribution_ok": attribution_ok,
        "generation_id": str(payload.get("id", "")),
        "finish_reason": str(choice.get("finish_reason", "")),
        "usage": dict(usage),
        "provider_reported_cost_usd": usage.get("cost"),
        "raw_content": content,
        "raw_content_sha256": sha256_bytes(content.encode("utf-8")),
        "candidate": candidate,
        "parse_error": parse_error,
        "provider_payload_sha256": value_sha256(payload),
        "reasoning_content_returned": bool(
            message.get("reasoning") or message.get("reasoning_details")
        ),
        "duration_seconds": round(time.monotonic() - started, 3),
    }
    _write(result_path, result)
    return result


def _cost_value(call: Mapping[str, Any]) -> float | None:
    if int(call.get("provider_calls", 0)) == 0:
        return 0.0
    value = call.get("provider_reported_cost_usd")
    if not isinstance(value, (int, float)) or value < 0:
        return None
    return float(value)


def _issue_code(call: Mapping[str, Any]) -> str:
    status = str(call.get("operational_status", ""))
    if status == "missing_api_key":
        return "budget_preflight_failed"
    if status.startswith("http_error") or status == "transport_error":
        return "transport_failed"
    return "schema_or_custody_failed"


def _failed_uncertainty_results(
    *,
    readers: list[dict[str, str]],
    artifact_path: str,
    artifact_bytes: bytes,
    issue_code: str,
    detail: str,
) -> list[dict[str, Any]]:
    by_surface = {row["surface"]: row for row in readers}
    return [
        build_reader_result(
            reader=by_surface[surface],
            state="failed",
            records=[],
            artifact_path=artifact_path,
            artifact_bytes=artifact_bytes,
            issue_code=issue_code,
            issue_stage="uncertainty_reader_call_or_admission",
            safe_detail=detail,
        )
        for surface in ("unresolved_matter", "reopen_condition")
    ]


def _missing_relationship_result(readers: list[dict[str, str]]) -> dict[str, Any]:
    reader = next(
        row for row in readers if row["surface"] == "cross_thread_relationship"
    )
    return build_reader_result(
        reader=reader,
        state="missing",
        records=[],
        issue_code="upstream_dependency_unavailable",
        issue_stage="uncertainty_reader_dependency",
        safe_detail="The relationship call was not made because uncertainty records were unavailable.",
    )


def _failed_relationship_result(
    *,
    readers: list[dict[str, str]],
    artifact_path: str,
    artifact_bytes: bytes,
    issue_code: str,
    detail: str,
) -> dict[str, Any]:
    reader = next(
        row for row in readers if row["surface"] == "cross_thread_relationship"
    )
    return build_reader_result(
        reader=reader,
        state="failed",
        records=[],
        artifact_path=artifact_path,
        artifact_bytes=artifact_bytes,
        issue_code=issue_code,
        issue_stage="relationship_reader_call_or_admission",
        safe_detail=detail,
    )


def _case_sources(case: Mapping[str, Any]) -> dict[str, Any]:
    wrapper_path = ROOT / case["wrapper_path"]
    source_path = ROOT / case["source_path"]
    role_path = ROOT / case["role_artifact_path"]
    wrapper = _load(wrapper_path)
    source_bytes = source_path.read_bytes()
    role_bytes = role_path.read_bytes()
    role = json.loads(role_bytes)
    source_registry = build_source_registry_v1(wrapper=wrapper, source_bytes=source_bytes)
    readers = planned_readers_v1(
        case_id=case["case_id"],
        existing_producer_id="google/gemini-3.5-flash-20260519",
        complementary_producer_id=MODEL,
    )
    return {
        "wrapper": wrapper,
        "source_bytes": source_bytes,
        "role_path": role_path,
        "role_bytes": role_bytes,
        "role": role,
        "source_registry": source_registry,
        "readers": readers,
        "existing": existing_reader_results_v1(
            role_portfolio=role,
            source_registry=source_registry,
            planned_readers=readers,
            role_artifact_path=case["role_artifact_path"],
            role_artifact_bytes=role_bytes,
        ),
        "alias_text": {
            row["alias"]: row["text"] for row in source_alias_catalog_v1(wrapper)
        },
    }


def run(contract: Mapping[str, Any], *, output: Path) -> dict[str, Any]:
    uncertainty_schema = uncertainty_response_schema_v1()
    relationship_schema = relationship_response_schema_v1()
    all_calls: list[dict[str, Any]] = []
    case_results = []
    total_known_cost = 0.0
    call_ordinal = 0
    cost_custody_known = True

    for case in contract["cases"]:
        case_id = case["case_id"]
        case_dir = output / case_id
        case_dir.mkdir(parents=True, exist_ok=False)
        source = _case_sources(case)
        artifact_bytes = {case["role_artifact_path"]: source["role_bytes"]}
        case_calls: list[dict[str, Any]] = []
        case_cost = 0.0
        uncertainty_results: list[dict[str, Any]] | None = None
        relationship_result: dict[str, Any] | None = None

        if not cost_custody_known or total_known_cost >= contract["budget"][
            "maximum_provider_reported_cost_total_usd"
        ]:
            budget_path = case_dir / "budget-preflight-failure.json"
            budget_bytes = _write(
                budget_path,
                {
                    "status": "budget_preflight_failed_before_case",
                    "known_total_cost_usd": total_known_cost,
                    "cost_custody_known": cost_custody_known,
                },
            )
            relative_budget = _relative(budget_path)
            uncertainty_results = _failed_uncertainty_results(
                readers=source["readers"],
                artifact_path=relative_budget,
                artifact_bytes=budget_bytes,
                issue_code="budget_preflight_failed",
                detail="The frozen total-cost or cost-custody boundary blocked the call.",
            )
            relationship_result = _missing_relationship_result(source["readers"])
            artifact_bytes[relative_budget] = budget_bytes
        else:
            packet = _load(ROOT / case["uncertainty_packet_path"])
            prompts = _load(ROOT / case["uncertainty_prompts_path"])
            preview = build_request_preview(
                prompts=prompts,
                schema=uncertainty_schema,
                schema_name="lolla_r4_uncertainty_v1",
                task="uncertainty",
                seed=case["seeds"]["uncertainty"],
            )
            if preview["body_sha256"] != case["uncertainty_request_body_sha256"]:
                raise R4ExperimentError("live uncertainty request drifted")
            _write(case_dir / "uncertainty-request.json", preview)
            call_ordinal += 1
            call = _provider_call(
                output=case_dir,
                ordinal=call_ordinal,
                case_id=case_id,
                task="uncertainty",
                preview=preview,
                contract=contract,
            )
            all_calls.append(call)
            case_calls.append(call)
            call_cost = _cost_value(call)
            if call_cost is None:
                cost_custody_known = False
            else:
                total_known_cost += call_cost
                case_cost += call_cost
            call_result_path = case_dir / f"call-{call_ordinal:02d}-uncertainty-result.json"
            call_result_bytes = call_result_path.read_bytes()
            relative_call_result = _relative(call_result_path)
            artifact_bytes[relative_call_result] = call_result_bytes
            uncertainty_compiled = None
            if call.get("operational_status") == "candidate_parsed":
                candidate_path = case_dir / "uncertainty-candidate.json"
                candidate_bytes = _write(candidate_path, call["candidate"])
                relative_candidate = _relative(candidate_path)
                artifact_bytes[relative_candidate] = candidate_bytes
                try:
                    uncertainty_compiled = compile_uncertainty_response_v1(
                        response=call["candidate"],
                        packet=packet,
                        source_registry=source["source_registry"],
                        planned_readers=source["readers"],
                        artifact_path=relative_candidate,
                        artifact_bytes=candidate_bytes,
                    )
                    _write(case_dir / "uncertainty-compiled.json", uncertainty_compiled)
                except Exception as exc:  # noqa: BLE001
                    failure_path = case_dir / "uncertainty-admission-failure.json"
                    failure_bytes = _write(
                        failure_path,
                        {
                            "status": "uncertainty_local_admission_failed",
                            "error": f"{type(exc).__name__}: {exc}",
                            "candidate_sha256": sha256_bytes(candidate_bytes),
                        },
                    )
                    relative_failure = _relative(failure_path)
                    artifact_bytes[relative_failure] = failure_bytes
                    uncertainty_results = _failed_uncertainty_results(
                        readers=source["readers"],
                        artifact_path=relative_failure,
                        artifact_bytes=failure_bytes,
                        issue_code="schema_or_custody_failed",
                        detail="The provider candidate failed the frozen local admission contract.",
                    )
            if uncertainty_compiled is None and uncertainty_results is None:
                uncertainty_results = _failed_uncertainty_results(
                    readers=source["readers"],
                    artifact_path=relative_call_result,
                    artifact_bytes=call_result_bytes,
                    issue_code=_issue_code(call),
                    detail="The uncertainty call did not produce an attributable admitted candidate.",
                )
            elif uncertainty_compiled is not None:
                uncertainty_results = uncertainty_compiled["reader_results"]

            if uncertainty_compiled is None:
                relationship_result = _missing_relationship_result(source["readers"])
            else:
                pre_relationship = assemble_conversation_state_fan_in(
                    source_registry=source["source_registry"],
                    planned_readers=source["readers"],
                    reader_results=sorted(
                        [
                            *source["existing"],
                            *uncertainty_results,
                            _missing_relationship_result(source["readers"]),
                        ],
                        key=lambda row: row["reader_id"],
                    ),
                    source_bytes=source["source_bytes"],
                    artifact_bytes_by_path=artifact_bytes,
                )
                relationship_packet = build_relationship_packet_v1(
                    fan_in=pre_relationship, source_text_by_alias=source["alias_text"]
                )
                relationship_prompts = build_relationship_prompts_v1(relationship_packet)
                relationship_preview = build_request_preview(
                    prompts=relationship_prompts,
                    schema=relationship_schema,
                    schema_name="lolla_r4_relationship_v1",
                    task="relationship",
                    seed=case["seeds"]["relationship"],
                )
                _write(case_dir / "pre-relationship-fan-in.json", pre_relationship)
                _write(case_dir / "relationship-packet.json", relationship_packet)
                _write(case_dir / "relationship-prompts.json", relationship_prompts)
                _write(case_dir / "relationship-request.json", relationship_preview)
                budget_blocked = (
                    not cost_custody_known
                    or case_cost >= contract["budget"][
                        "maximum_provider_reported_cost_per_case_usd"
                    ]
                    or total_known_cost >= contract["budget"][
                        "maximum_provider_reported_cost_total_usd"
                    ]
                )
                if budget_blocked:
                    budget_path = case_dir / "relationship-budget-preflight-failure.json"
                    budget_bytes = _write(
                        budget_path,
                        {
                            "status": "budget_preflight_failed_before_relationship",
                            "known_case_cost_usd": case_cost,
                            "known_total_cost_usd": total_known_cost,
                            "cost_custody_known": cost_custody_known,
                        },
                    )
                    relative_budget = _relative(budget_path)
                    artifact_bytes[relative_budget] = budget_bytes
                    relationship_result = _failed_relationship_result(
                        readers=source["readers"],
                        artifact_path=relative_budget,
                        artifact_bytes=budget_bytes,
                        issue_code="budget_preflight_failed",
                        detail="The frozen case or total cost boundary blocked the relationship call.",
                    )
                else:
                    call_ordinal += 1
                    relation_call = _provider_call(
                        output=case_dir,
                        ordinal=call_ordinal,
                        case_id=case_id,
                        task="relationship",
                        preview=relationship_preview,
                        contract=contract,
                    )
                    all_calls.append(relation_call)
                    case_calls.append(relation_call)
                    relation_cost = _cost_value(relation_call)
                    if relation_cost is None:
                        cost_custody_known = False
                    else:
                        total_known_cost += relation_cost
                        case_cost += relation_cost
                    relation_result_path = (
                        case_dir / f"call-{call_ordinal:02d}-relationship-result.json"
                    )
                    relation_result_bytes = relation_result_path.read_bytes()
                    relative_relation_result = _relative(relation_result_path)
                    artifact_bytes[relative_relation_result] = relation_result_bytes
                    relationship_compiled = None
                    if relation_call.get("operational_status") == "candidate_parsed":
                        candidate_path = case_dir / "relationship-candidate.json"
                        candidate_bytes = _write(candidate_path, relation_call["candidate"])
                        relative_candidate = _relative(candidate_path)
                        artifact_bytes[relative_candidate] = candidate_bytes
                        try:
                            relationship_compiled = compile_relationship_response_v1(
                                response=relation_call["candidate"],
                                packet=relationship_packet,
                                source_registry=source["source_registry"],
                                planned_readers=source["readers"],
                                artifact_path=relative_candidate,
                                artifact_bytes=candidate_bytes,
                            )
                            _write(
                                case_dir / "relationship-compiled.json",
                                relationship_compiled,
                            )
                        except Exception as exc:  # noqa: BLE001
                            failure_path = case_dir / "relationship-admission-failure.json"
                            failure_bytes = _write(
                                failure_path,
                                {
                                    "status": "relationship_local_admission_failed",
                                    "error": f"{type(exc).__name__}: {exc}",
                                    "candidate_sha256": sha256_bytes(candidate_bytes),
                                },
                            )
                            relative_failure = _relative(failure_path)
                            artifact_bytes[relative_failure] = failure_bytes
                            relationship_result = _failed_relationship_result(
                                readers=source["readers"],
                                artifact_path=relative_failure,
                                artifact_bytes=failure_bytes,
                                issue_code="schema_or_custody_failed",
                                detail="The relationship candidate failed the frozen local admission contract.",
                            )
                    if relationship_compiled is None and relationship_result is None:
                        relationship_result = _failed_relationship_result(
                            readers=source["readers"],
                            artifact_path=relative_relation_result,
                            artifact_bytes=relation_result_bytes,
                            issue_code=_issue_code(relation_call),
                            detail="The relationship call did not produce an attributable admitted candidate.",
                        )
                    elif relationship_compiled is not None:
                        relationship_result = relationship_compiled["reader_result"]

        if uncertainty_results is None or relationship_result is None:
            raise R4ExperimentError("case reader results were not terminally assigned")
        final_fan_in = assemble_conversation_state_fan_in(
            source_registry=source["source_registry"],
            planned_readers=source["readers"],
            reader_results=sorted(
                [*source["existing"], *uncertainty_results, relationship_result],
                key=lambda row: row["reader_id"],
            ),
            source_bytes=source["source_bytes"],
            artifact_bytes_by_path=artifact_bytes,
        )
        _write(case_dir / "final-fan-in.json", final_fan_in)
        case_results.append(
            {
                "case_id": case_id,
                "provider_calls": sum(int(row.get("provider_calls", 0)) for row in case_calls),
                "provider_reported_cost_usd": round(case_cost, 12)
                if cost_custody_known
                else None,
                "cost_custody_known_after_case": cost_custody_known,
                "fan_in_status": final_fan_in["status"],
                "reader_state_counts": final_fan_in["fan_in"]["reader_state_counts"],
                "record_count": final_fan_in["fan_in"]["total_record_count"],
                "semantic_source_review": "required",
            }
        )
    result = {
        "schema_version": RESULT_SCHEMA,
        "status": "provider_calls_preserved_source_first_review_required",
        "run_id": contract["run_id"],
        "cases": case_results,
        "provider_calls": sum(int(row.get("provider_calls", 0)) for row in all_calls),
        "provider_reported_cost_usd": round(total_known_cost, 12)
        if cost_custody_known
        else None,
        "cost_custody_known": cost_custody_known,
        "cost_ceiling_met": cost_custody_known
        and total_known_cost
        <= contract["budget"]["maximum_provider_reported_cost_total_usd"],
        "automatic_retries": 0,
        "semantic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
        "source_first_review_status": "required",
        "runtime_or_graph_integration": False,
        "production_model_selected": False,
        "scalar_quality_score": None,
    }
    _write(output / "result.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    contract_path = args.contract.resolve()
    contract = _validate_contract(contract_path)
    if args.dry_run:
        print(
            json.dumps(
                {
                    "status": "frozen_experiment_contract_valid",
                    "provider_calls": 0,
                    "authorization_present": args.authorization is not None,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if args.authorization is None or args.env_file is None or args.output is None:
        raise R4ExperimentError("live execution requires authorization, env, and output")
    _validate_authorization(
        args.authorization.resolve(), contract=contract, contract_path=contract_path
    )
    output = args.output.resolve()
    if output.exists():
        raise R4ExperimentError("experiment output path already exists")
    output.mkdir(parents=True)
    _load_env(args.env_file.resolve())
    result = run(contract, output=output)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["cost_ceiling_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
