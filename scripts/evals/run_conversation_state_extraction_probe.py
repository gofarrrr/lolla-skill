#!/usr/bin/env python3
"""Freeze, dry-run, execute, and mechanically seal a two-case state probe."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib import error, request


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.system_b.conversation_state_handoff import (  # noqa: E402
    CLAIM_MODES,
    CONTRIBUTION_ROLES,
    CONSTRAINT_STATES,
    EVIDENCE_MODES,
    OWNERSHIP,
    POSITION_STATES,
    SCHEMA_VERSION as HANDOFF_SCHEMA,
    THREAD_DISPOSITIONS,
    THREAD_ENGAGEMENTS,
    validate_conversation_state_handoff,
)
from engine.system_b.pricing import (  # noqa: E402
    PRICES_LAST_VERIFIED,
    estimate_chat_cost_usd,
    lookup_chat_price,
)
from scripts.evals.run_fixed_safe_holdout_pool import (  # noqa: E402
    _extract_json_object,
    _hash_file,
    _hash_text,
    _model_attribution,
)
from scripts.evals.run_fixed_safe_holdout_pool_v2 import (  # noqa: E402
    _json_hash,
    _provider_diagnostic,
)


CONTRACT_SCHEMA = "lolla.conversation_state_extraction_probe_contract.v1"
RAW_OUTPUT_SCHEMA = "lolla.conversation_state_probe_raw.v1"
CUSTODY_SCHEMA = "lolla.conversation_state_extraction_probe_custody.v1"
SUMMARY_SCHEMA = "lolla.conversation_state_extraction_probe_summary.v1"
REVIEW_SHELL_SCHEMA = "lolla.conversation_state_extraction_probe_review_shell.v1"
REVIEW_RESULT_SCHEMA = "lolla.conversation_state_extraction_probe_review_result.v1"
AUTHORIZATION_SCHEMA = "lolla.conversation_state_extraction_probe_authorization.v1"
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


class ConversationStateProbeError(RuntimeError):
    pass


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ConversationStateProbeError(f"expected JSON object: {path}")
    return value


def _repo_path(raw: object, *, label: str) -> Path:
    path = Path(str(raw))
    if path.is_absolute():
        raise ConversationStateProbeError(f"{label} must be repo-relative")
    resolved = (REPO_ROOT / path).resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise ConversationStateProbeError(f"{label} must remain inside repository") from exc
    return resolved


def _write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def _load_env_file(path: Path) -> None:
    if not path.is_file():
        raise ConversationStateProbeError(f"env file missing: {path}")
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def _evidence_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "speaker": {"type": "string", "enum": ["user", "assistant"]},
            "turn_index": {"type": "integer", "minimum": 1},
            "quote": {"type": "string"},
        },
        "required": ["speaker", "turn_index", "quote"],
    }


def response_schema() -> dict[str, Any]:
    evidence = _evidence_schema()
    contribution = {
        **evidence,
        "properties": {
            **evidence["properties"],
            "role": {"type": "string", "enum": sorted(CONTRIBUTION_ROLES)},
        },
        "required": ["speaker", "turn_index", "quote", "role"],
    }
    response_item = {
        **evidence,
        "properties": {
            **evidence["properties"],
            "engagement": {"type": "string", "enum": sorted(THREAD_ENGAGEMENTS)},
        },
        "required": ["speaker", "turn_index", "quote", "engagement"],
    }
    return {
        "name": "conversation_state_extraction_probe",
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "schema_version": {"type": "string", "const": RAW_OUTPUT_SCHEMA},
                "decision_summary": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "text": {"type": "string"},
                        "evidence_mode": {"type": "string", "enum": sorted(EVIDENCE_MODES)},
                        "source_evidence": {"type": "array", "minItems": 1, "maxItems": 4, "items": evidence},
                    },
                    "required": ["text", "evidence_mode", "source_evidence"],
                },
                "positions": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 2,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "text": {"type": "string"},
                            "ownership": {"type": "string", "enum": sorted(OWNERSHIP)},
                            "state": {"type": "string", "enum": sorted(POSITION_STATES)},
                            "evidence_mode": {"type": "string", "enum": sorted(EVIDENCE_MODES)},
                            "contributions": {"type": "array", "minItems": 1, "maxItems": 6, "items": contribution},
                        },
                        "required": ["text", "ownership", "state", "evidence_mode", "contributions"],
                    },
                },
                "threads": {
                    "type": "array",
                    "minItems": 0,
                    "maxItems": 4,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "text": {"type": "string"},
                            "disposition": {"type": "string", "enum": sorted(THREAD_DISPOSITIONS)},
                            "introduced": evidence,
                            "responses": {"type": "array", "minItems": 0, "maxItems": 6, "items": response_item},
                            "latest_ref": evidence,
                            "superseded_by": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                            "evidence_mode": {"type": "string", "enum": sorted(EVIDENCE_MODES)},
                        },
                        "required": ["text", "disposition", "introduced", "responses", "latest_ref", "superseded_by", "evidence_mode"],
                    },
                },
                "constraints": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 12,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "text": {"type": "string"},
                            "state": {"type": "string", "enum": sorted(CONSTRAINT_STATES)},
                            "claim_mode": {"type": "string", "enum": sorted(CLAIM_MODES)},
                            "evidence_mode": {"type": "string", "enum": sorted(EVIDENCE_MODES)},
                            "source_evidence": {"type": "array", "minItems": 1, "maxItems": 4, "items": evidence},
                        },
                        "required": ["text", "state", "claim_mode", "evidence_mode", "source_evidence"],
                    },
                },
            },
            "required": ["schema_version", "decision_summary", "positions", "threads", "constraints"],
        },
    }


def build_prompts(contract: Mapping[str, Any], case: Mapping[str, Any]) -> dict[str, str]:
    source = _repo_path(case["source_path"], label="case source").read_text(encoding="utf-8")
    user_prompt = (
        str(contract["extraction_instruction"]).strip()
        + "\n\nSOURCE CONVERSATION\n\n"
        + source.strip()
        + "\n\nReturn only the object required by the response schema. "
        + f"Set schema_version to {RAW_OUTPUT_SCHEMA}."
    )
    return {
        "system_prompt": str(contract["system_prompt"]).strip(),
        "user_prompt": user_prompt,
    }


def prompt_hashes(contract: Mapping[str, Any]) -> dict[str, Any]:
    cases: dict[str, dict[str, str]] = {}
    for case in contract["cases"]:
        prompts = build_prompts(contract, case)
        cases[str(case["case_id"])] = {
            "system_prompt_sha256": _hash_text(prompts["system_prompt"]),
            "user_prompt_sha256": _hash_text(prompts["user_prompt"]),
        }
    return {
        "response_schema_sha256": _json_hash(response_schema()),
        "cases": cases,
    }


def _validate_raw_response(value: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, Mapping):
        return ["response_not_object"]
    required = {"schema_version", "decision_summary", "positions", "threads", "constraints"}
    if set(value) != required:
        errors.append("response_top_level_shape_invalid")
    if value.get("schema_version") != RAW_OUTPUT_SCHEMA:
        errors.append("response_schema_version_invalid")
    if not isinstance(value.get("decision_summary"), Mapping):
        errors.append("decision_summary_invalid")
    for field in ("positions", "threads", "constraints"):
        if not isinstance(value.get(field), list):
            errors.append(f"{field}_not_array")
    if isinstance(value.get("positions"), list) and not 1 <= len(value["positions"]) <= 2:
        errors.append("positions_count_invalid")
    if isinstance(value.get("threads"), list) and len(value["threads"]) > 4:
        errors.append("threads_count_invalid")
    if isinstance(value.get("constraints"), list) and not 1 <= len(value["constraints"]) <= 12:
        errors.append("constraints_count_invalid")
    return errors


def seal_raw_response(
    raw: Mapping[str, Any],
    *,
    case: Mapping[str, Any],
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    source_path = _repo_path(case["source_path"], label="case source")
    source_text = source_path.read_text(encoding="utf-8")
    packet = {
        "schema_version": HANDOFF_SCHEMA,
        "status": "model_probe_unreviewed",
        "case_id": case["case_id"],
        "source": {
            "path": case["source_path"],
            "sha256": case["source_sha256"],
            "message_count": case["message_count"],
        },
        "decision_summary": raw.get("decision_summary", {}),
        "positions": [
            {
                "position_id": f"position-{index:03d}",
                **dict(item),
                "graph_routing_eligible": False,
            }
            for index, item in enumerate(raw.get("positions", []), start=1)
            if isinstance(item, Mapping)
        ],
        "threads": [
            {
                "thread_id": f"thread-{index:03d}",
                **dict(item),
                "graph_routing_eligible": False,
            }
            for index, item in enumerate(raw.get("threads", []), start=1)
            if isinstance(item, Mapping)
        ],
        "constraints": [
            {
                "constraint_id": f"constraint-{index:03d}",
                **dict(item),
                "graph_routing_eligible": False,
            }
            for index, item in enumerate(raw.get("constraints", []), start=1)
            if isinstance(item, Mapping)
        ],
        "routing_boundary": {
            "contains_case_context": True,
            "direct_graph_routing_allowed": False,
            "reasoning_pattern_abstraction_required": True,
            "runtime_integration": False,
        },
        "non_claims": [
            "state_items_are_probabilistic_or_human_interpretations",
            "source_grounding_is_not_semantic_correctness",
            "conversation_state_is_not_reasoning_pattern",
            "facts_cannot_seed_graph_directly",
            "not_runtime_integration_authority",
        ],
    }
    violations = validate_conversation_state_handoff(packet, source_text=source_text)
    return packet, violations


def validate_contract(contract: Mapping[str, Any]) -> None:
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise ConversationStateProbeError("unexpected probe contract schema")
    if contract.get("status") != "frozen_before_calls":
        raise ConversationStateProbeError("probe contract is not frozen")
    if not RUN_ID_PATTERN.fullmatch(str(contract.get("run_id", ""))):
        raise ConversationStateProbeError("run_id is invalid")
    cases = contract.get("cases")
    if not isinstance(cases, list) or len(cases) != 2:
        raise ConversationStateProbeError("exactly two cases are required")
    expected_roles = ["resolved_thread", "addressed_unresolved_material_propagation"]
    if [case.get("selection_role") for case in cases] != expected_roles:
        raise ConversationStateProbeError("case diversity roles drifted")
    if [case.get("case_id") for case in cases] != contract.get("selection", {}).get("selected_case_ids"):
        raise ConversationStateProbeError("selected case order drifted")
    for case in cases:
        if set(case) != {
            "case_id", "selection_role", "source_path", "source_sha256",
            "message_count", "reviewed_packet_path", "reviewed_packet_sha256",
            "expected_position_ownership", "expected_thread_disposition",
            "reviewed_constraint_count",
        }:
            raise ConversationStateProbeError("case row shape invalid")
        source = _repo_path(case["source_path"], label="case source")
        reviewed = _repo_path(case["reviewed_packet_path"], label="reviewed packet")
        if not source.is_file() or _hash_file(source) != case["source_sha256"]:
            raise ConversationStateProbeError("case source hash mismatch")
        if not reviewed.is_file() or _hash_file(reviewed) != case["reviewed_packet_sha256"]:
            raise ConversationStateProbeError("reviewed packet hash mismatch")
        reviewed_payload = _load_object(reviewed)
        if reviewed_payload.get("case_id") != case["case_id"]:
            raise ConversationStateProbeError("reviewed packet case mismatch")
        if [item["ownership"] for item in reviewed_payload["positions"]] != [case["expected_position_ownership"]]:
            raise ConversationStateProbeError("expected ownership differs from reviewed packet")
        if [item["disposition"] for item in reviewed_payload["threads"]] != [case["expected_thread_disposition"]]:
            raise ConversationStateProbeError("expected disposition differs from reviewed packet")
        if len(reviewed_payload["constraints"]) != int(case["reviewed_constraint_count"]):
            raise ConversationStateProbeError("reviewed constraint count mismatch")
    selection = contract.get("selection", {})
    if selection.get("rule") != "unique_resolved_case_plus_unique_material_downstream_propagation_case":
        raise ConversationStateProbeError("selection rule drifted")
    if selection.get("selected_for_likely_success") is not False:
        raise ConversationStateProbeError("selection must not optimize for likely success")

    config = contract.get("call_configuration", {})
    expected_config = {
        "provider": "openrouter",
        "model": "google/gemini-3.1-flash-lite",
        "temperature": 0.0,
        "reasoning": {"enabled": False},
        "strict_structured_output": True,
        "require_supported_parameters": True,
        "calls_per_case": 1,
        "automatic_retries": 0,
        "evaluator_calls": 0,
        "pipeline_calls": 0,
        "graph_calls": 0,
    }
    for key, expected in expected_config.items():
        if config.get(key) != expected:
            raise ConversationStateProbeError(f"call configuration drifted: {key}")
    if not 1 <= int(config.get("max_output_tokens", 0)) <= 8000:
        raise ConversationStateProbeError("output-token cap invalid")
    if not 1 <= float(config.get("provider_timeout_seconds", 0)) <= 120:
        raise ConversationStateProbeError("provider timeout invalid")
    if not float(config["provider_timeout_seconds"]) < float(config.get("wall_clock_timeout_seconds", 0)) <= 300:
        raise ConversationStateProbeError("wall timeout invalid")
    if lookup_chat_price("openrouter", str(config["model"])) is None:
        raise ConversationStateProbeError("model missing from pricing table")
    budget = contract.get("call_budget", {})
    if budget.get("pricing_table_version") != PRICES_LAST_VERIFIED:
        raise ConversationStateProbeError("pricing table version drifted")
    if not 0 < float(budget.get("estimated_total_cost_ceiling_usd", 0)) <= 0.03:
        raise ConversationStateProbeError("cost ceiling invalid")

    scoring = contract.get("scoring_contract", {})
    if scoring.get("composite_score") is not None:
        raise ConversationStateProbeError("composite score is forbidden")
    required_axes = {
        "position_ownership", "thread_disposition", "source_strength",
        "constraint_coverage", "exact_quote_grounding", "late_turn_trajectory",
    }
    if set(scoring.get("axes", {})) != required_axes:
        raise ConversationStateProbeError("scoring axes drifted")
    if scoring.get("source_first_human_review_required") is not True:
        raise ConversationStateProbeError("source-first review is required")

    locks = contract.get("hash_locks", [])
    roles: set[str] = set()
    for lock in locks:
        if not isinstance(lock, Mapping) or set(lock) != {"role", "path", "sha256"}:
            raise ConversationStateProbeError("hash lock shape invalid")
        role = str(lock["role"])
        if role in roles:
            raise ConversationStateProbeError("hash lock roles must be unique")
        roles.add(role)
        path = _repo_path(lock["path"], label=f"hash lock {role}")
        if not path.is_file() or _hash_file(path) != lock["sha256"]:
            raise ConversationStateProbeError(f"hash lock mismatch: {role}")
    if not {"probe_runner", "state_handoff", "pricing", "provider_custody_helper", "evaluation_doctrine"} <= roles:
        raise ConversationStateProbeError("required hash lock roles missing")
    if prompt_hashes(contract) != contract.get("prompt_hashes"):
        raise ConversationStateProbeError("prompt or response-schema hashes drifted")

    artifacts = contract.get("artifacts", {})
    output_dir = _repo_path(artifacts.get("output_dir", ""), label="output directory")
    expected_files = {
        "call_custody_path": output_dir / "call-custody.json",
        "mechanical_summary_path": output_dir / "mechanical-summary.json",
        "source_review_shell_path": output_dir / "source-review-shell.json",
        "source_review_result_path": output_dir / "source-review-result.json",
    }
    for key, expected in expected_files.items():
        if _repo_path(artifacts.get(key, ""), label=key) != expected:
            raise ConversationStateProbeError(f"invalid artifact path: {key}")
    if artifacts.get("require_output_dir_absent_before_run") is not True:
        raise ConversationStateProbeError("output directory absence precondition required")
    if contract.get("experiment_stop_rule") != "stop_after_first_nonpassing_call_without_retry":
        raise ConversationStateProbeError("stop rule drifted")


def validate_authorization(
    authorization: Mapping[str, Any],
    *,
    contract_path: Path,
    contract: Mapping[str, Any],
) -> None:
    if authorization.get("schema_version") != AUTHORIZATION_SCHEMA:
        raise ConversationStateProbeError("unexpected authorization schema")
    if authorization.get("status") != "authorized_once":
        raise ConversationStateProbeError("provider calls are not authorized")
    if authorization.get("contract_path") != str(contract_path.relative_to(REPO_ROOT)):
        raise ConversationStateProbeError("authorization contract path mismatch")
    if authorization.get("contract_sha256") != _hash_file(contract_path):
        raise ConversationStateProbeError("authorization contract hash mismatch")
    if authorization.get("run_id") != contract.get("run_id"):
        raise ConversationStateProbeError("authorization run_id mismatch")
    if authorization.get("maximum_provider_calls") != 2:
        raise ConversationStateProbeError("authorization call ceiling mismatch")
    if authorization.get("automatic_retries") != 0:
        raise ConversationStateProbeError("authorization retries must be zero")
    if authorization.get("pipeline_calls") != 0 or authorization.get("graph_calls") != 0:
        raise ConversationStateProbeError("authorization must exclude pipeline and graph")


def _call_openrouter(
    contract: Mapping[str, Any],
    case: Mapping[str, Any],
) -> dict[str, Any]:
    started = time.monotonic()
    config = contract["call_configuration"]
    prompts = build_prompts(contract, case)
    requested_model = str(config["model"])
    base = {
        "case_id": case["case_id"],
        "call_attempted": True,
        "requested_model": requested_model,
        "system_prompt_sha256": _hash_text(prompts["system_prompt"]),
        "user_prompt_sha256": _hash_text(prompts["user_prompt"]),
        "response_schema_sha256": _json_hash(response_schema()),
        "reasoning_configuration": config["reasoning"],
    }
    api_key = os.getenv("LOLLA_OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return {
            **base,
            "status": "missing_api_key",
            "response": {},
            "validation_errors": ["OPENROUTER_API_KEY is missing"],
            "served_model": "",
            "model_attribution_status": "not_observed",
            "finish_reason": "",
            "usage_evidence_state": "unknown",
            "provider_diagnostic": {},
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    body = {
        "model": requested_model,
        "messages": [
            {"role": "system", "content": prompts["system_prompt"]},
            {"role": "user", "content": prompts["user_prompt"]},
        ],
        "response_format": {"type": "json_schema", "json_schema": response_schema()},
        "provider": {"require_parameters": True},
        "temperature": config["temperature"],
        "max_tokens": config["max_output_tokens"],
        "reasoning": config["reasoning"],
    }
    req = request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=float(config["provider_timeout_seconds"])) as response:
            provider_payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")
        try:
            error_payload = json.loads(body_text)
        except json.JSONDecodeError:
            error_payload = {"message": body_text[:1000]}
        return {
            **base,
            "status": f"http_error_{exc.code}",
            "response": {},
            "validation_errors": [f"provider HTTP error {exc.code}"],
            "served_model": "",
            "model_attribution_status": "not_observed",
            "finish_reason": "",
            "usage_evidence_state": "unknown",
            "provider_diagnostic": _provider_diagnostic(error_payload, []),
            "provider_payload_sha256": _json_hash(error_payload),
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            **base,
            "status": "provider_error",
            "response": {},
            "validation_errors": [type(exc).__name__],
            "served_model": "",
            "model_attribution_status": "not_observed",
            "finish_reason": "",
            "usage_evidence_state": "unknown",
            "provider_diagnostic": {"type": type(exc).__name__},
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    choices_raw = provider_payload.get("choices", [])
    choices = choices_raw if isinstance(choices_raw, list) else []
    choice = choices[0] if choices and isinstance(choices[0], Mapping) else {}
    message = choice.get("message", {}) if isinstance(choice, Mapping) else {}
    raw_content = str(message.get("content", "")) if isinstance(message, Mapping) else ""
    parsed = _extract_json_object(raw_content)
    errors = _validate_raw_response(parsed)
    finish_reason = str(choice.get("finish_reason", ""))
    if finish_reason.strip().lower() == "error":
        errors.insert(0, "provider returned finish_reason=error")
    packet: dict[str, Any] = {}
    custody_violations: list[dict[str, str]] = []
    if not errors:
        packet, custody_violations = seal_raw_response(parsed, case=case)
        errors.extend(item["code"] for item in custody_violations)
    usage = provider_payload.get("usage", {})
    usage_map = usage if isinstance(usage, Mapping) else {}
    prompt_tokens = usage_map.get("prompt_tokens")
    completion_tokens = usage_map.get("completion_tokens")
    total_tokens = usage_map.get("total_tokens")
    usage_complete = all(isinstance(value, int) and value > 0 for value in (prompt_tokens, completion_tokens, total_tokens))
    served_model = str(provider_payload.get("model", ""))
    status = "provider_finish_error" if finish_reason.strip().lower() == "error" else (
        "ok" if not errors else "invalid_contract"
    )
    return {
        **base,
        "status": status,
        "response": parsed,
        "sealed_packet": packet,
        "validation_errors": errors,
        "custody_violation_count": len(custody_violations),
        "served_model": served_model,
        "model_attribution_status": _model_attribution(requested_model, served_model),
        "finish_reason": finish_reason,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "reasoning_tokens": (
            usage_map.get("completion_tokens_details", {}).get("reasoning_tokens", 0)
            if isinstance(usage_map.get("completion_tokens_details", {}), Mapping)
            else 0
        ),
        "usage_evidence_state": "complete" if usage_complete else "unknown",
        "response_sha256": _hash_text(raw_content),
        "provider_payload_sha256": _json_hash(provider_payload),
        "provider_diagnostic": _provider_diagnostic(provider_payload, choices),
        "raw_provider_content_included": False,
        "duration_seconds": round(time.monotonic() - started, 3),
    }


def run_probe(
    contract: Mapping[str, Any],
    *,
    call_fn: Callable[[Mapping[str, Any], Mapping[str, Any]], dict[str, Any]] = _call_openrouter,
) -> tuple[dict[str, Any], dict[str, Any]]:
    validate_contract(contract)
    output_dir = _repo_path(contract["artifacts"]["output_dir"], label="output directory")
    if output_dir.exists():
        raise ConversationStateProbeError("frozen output directory already exists")
    output_dir.mkdir(parents=True)
    calls: list[dict[str, Any]] = []
    case_results: list[dict[str, Any]] = []
    stopped_early = False
    started = time.monotonic()
    for case in contract["cases"]:
        call = call_fn(contract, case)
        calls.append(call)
        safe_call = {key: value for key, value in call.items() if key != "response"}
        if "sealed_packet" in safe_call:
            packet_path = output_dir / f"{case['case_id']}-unreviewed-state.json"
            _write_json_atomic(packet_path, safe_call.pop("sealed_packet"))
            safe_call["sealed_packet_path"] = str(packet_path.relative_to(REPO_ROOT))
            safe_call["sealed_packet_sha256"] = _hash_file(packet_path)
        case_results.append(safe_call)
        _write_json_atomic(
            _repo_path(contract["artifacts"]["call_custody_path"], label="call custody"),
            {
                "schema_version": CUSTODY_SCHEMA,
                "run_id": contract["run_id"],
                "recorded_call_count": len(case_results),
                "calls": case_results,
                "raw_provider_content_included": False,
            },
        )
        if call.get("status") != "ok":
            stopped_early = True
            break
    wall_time = time.monotonic() - started
    price = lookup_chat_price("openrouter", contract["call_configuration"]["model"])
    complete_calls = [call for call in calls if call.get("usage_evidence_state") == "complete"]
    cost = (
        sum(
            estimate_chat_cost_usd(
                price=price,
                prompt_tokens=int(call.get("prompt_tokens") or 0),
                completion_tokens=int(call.get("completion_tokens") or 0),
            )
            for call in complete_calls
        )
        if price is not None and len(complete_calls) == len(calls)
        else None
    )
    expected_calls = len(contract["cases"])
    gates = {
        "contract_valid": True,
        "call_count_exact": len(calls) == expected_calls,
        "all_calls_ok": len(calls) == expected_calls and all(call.get("status") == "ok" for call in calls),
        "no_automatic_retries": True,
        "typed_packets_valid": len(calls) == expected_calls and all(not call.get("validation_errors") for call in calls),
        "usage_complete": len(complete_calls) == expected_calls,
        "model_attribution_acceptable": len(calls) == expected_calls and all(call.get("model_attribution_status") in {"matched", "served_version_alias"} for call in calls),
        "finish_reasons_not_error": len(calls) == expected_calls and all(str(call.get("finish_reason", "")).lower() != "error" for call in calls),
        "reasoning_tokens_zero": len(calls) == expected_calls and all(int(call.get("reasoning_tokens", 0) or 0) == 0 for call in calls),
        "cost_estimate_complete": cost is not None,
        "cost_ceiling_met": cost is not None and cost <= float(contract["call_budget"]["estimated_total_cost_ceiling_usd"]),
        "wall_clock_ceiling_met": wall_time <= float(contract["call_configuration"]["wall_clock_timeout_seconds"]),
        "pipeline_graph_evaluator_calls_zero": True,
    }
    failed = [key for key, passed in gates.items() if not passed]
    summary = {
        "schema_version": SUMMARY_SCHEMA,
        "status": "mechanically_passed_pending_source_review" if not failed else "failed",
        "run_id": contract["run_id"],
        "contract_sha256": _hash_text(json.dumps(contract, sort_keys=True, separators=(",", ":"))),
        "recorded_call_count": len(calls),
        "stopped_early": stopped_early,
        "wall_time_seconds": round(wall_time, 3),
        "prompt_tokens": sum(int(call.get("prompt_tokens", 0) or 0) for call in complete_calls) if complete_calls else None,
        "completion_tokens": sum(int(call.get("completion_tokens", 0) or 0) for call in complete_calls) if complete_calls else None,
        "estimated_cost_usd": cost,
        "pricing_table_version": PRICES_LAST_VERIFIED,
        "gates": gates,
        "failed_gates": failed,
        "source_first_review_status": "pending" if not failed else "not_authorized",
        "full_pipeline_authorized": False,
        "graph_calls": 0,
        "evaluator_calls": 0,
        "runtime_integration_authorized": False,
        "non_claims": contract["non_claims"],
    }
    _write_json_atomic(
        _repo_path(contract["artifacts"]["mechanical_summary_path"], label="mechanical summary"),
        summary,
    )
    _write_json_atomic(
        _repo_path(
            contract["artifacts"]["source_review_shell_path"],
            label="source review shell",
        ),
        build_source_review_shell(contract, case_results=case_results),
    )
    return summary, {
        "schema_version": CUSTODY_SCHEMA,
        "run_id": contract["run_id"],
        "recorded_call_count": len(case_results),
        "calls": case_results,
        "raw_provider_content_included": False,
    }


def build_source_review_shell(
    contract: Mapping[str, Any],
    *,
    case_results: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    by_case = {str(item.get("case_id")): item for item in case_results}
    cases: list[dict[str, Any]] = []
    for case in contract["cases"]:
        result = by_case.get(str(case["case_id"]), {})
        cases.append(
            {
                "case_id": case["case_id"],
                "source_path": case["source_path"],
                "reviewed_packet_path": case["reviewed_packet_path"],
                "observed_packet_path": result.get("sealed_packet_path"),
                "mechanical_call_status": result.get("status", "not_run"),
                "axes": {
                    "position_ownership": {
                        "status": "pending",
                        "expected": case["expected_position_ownership"],
                        "observed": None,
                        "reason": "",
                    },
                    "thread_disposition": {
                        "status": "pending",
                        "expected": case["expected_thread_disposition"],
                        "observed": None,
                        "reason": "",
                    },
                    "source_strength": {
                        "status": "pending",
                        "material_strengthening_breaches": None,
                        "reason": "",
                    },
                    "constraint_coverage": {
                        "status": "pending",
                        "reviewed_constraint_count": case["reviewed_constraint_count"],
                        "matched_constraint_count": None,
                        "precision": None,
                        "recall": None,
                        "reason": "",
                    },
                    "exact_quote_grounding": {
                        "status": "mechanical_gate",
                        "violations": result.get("custody_violation_count"),
                    },
                    "late_turn_trajectory": {
                        "status": "pending",
                        "user_turn_7_represented": None,
                        "assistant_turn_7_represented": None,
                        "reason": "",
                    },
                },
            }
        )
    return {
        "schema_version": REVIEW_SHELL_SCHEMA,
        "status": "pending_source_first_review",
        "run_id": contract["run_id"],
        "review_order": "source_then_reviewed_packet_then_observed_packet",
        "review_sequence_attestation": {
            "source_opened_first": False,
            "reviewed_packet_opened_second": False,
            "observed_packet_opened_third": False,
            "review_completed_without_evaluator_call": False,
        },
        "composite_score": None,
        "cases": cases,
        "aggregate_decision": {
            "status": "pending",
            "probe_passed": None,
            "failed_axes": [],
            "full_pipeline_authorized": False,
            "graph_calls_authorized": False,
        },
        "evaluator_calls": 0,
        "non_claims": [
            "pending_is_not_pass",
            "mechanical_grounding_is_not_semantic_correctness",
            "no_composite_quality_score",
            "not_full_pipeline_authority",
        ],
    }


def seal_source_review(
    contract: Mapping[str, Any],
    review: Mapping[str, Any],
) -> dict[str, Any]:
    """Seal an axis-by-axis human review without manufacturing a quality score."""

    validate_contract(contract)
    if review.get("schema_version") != REVIEW_SHELL_SCHEMA:
        raise ConversationStateProbeError("unexpected source-review schema")
    if review.get("status") != "completed_source_first_review":
        raise ConversationStateProbeError("source review is not complete")
    if review.get("run_id") != contract.get("run_id"):
        raise ConversationStateProbeError("source-review run_id mismatch")
    if review.get("review_order") != "source_then_reviewed_packet_then_observed_packet":
        raise ConversationStateProbeError("source-first review order drifted")
    if review.get("composite_score") is not None:
        raise ConversationStateProbeError("composite source-review score is forbidden")
    attestations = review.get("review_sequence_attestation")
    required_attestations = {
        "source_opened_first",
        "reviewed_packet_opened_second",
        "observed_packet_opened_third",
        "review_completed_without_evaluator_call",
    }
    if not isinstance(attestations, Mapping) or set(attestations) != required_attestations:
        raise ConversationStateProbeError("source-review attestation shape invalid")
    if not all(attestations[key] is True for key in required_attestations):
        raise ConversationStateProbeError("source-first review sequence not attested")
    if review.get("evaluator_calls") != 0:
        raise ConversationStateProbeError("source review must not use evaluator calls")

    reviewed_cases = review.get("cases")
    if not isinstance(reviewed_cases, list):
        raise ConversationStateProbeError("source-review cases missing")
    by_case = {
        str(item.get("case_id")): item
        for item in reviewed_cases
        if isinstance(item, Mapping)
    }
    expected_ids = [str(case["case_id"]) for case in contract["cases"]]
    if list(by_case) != expected_ids or len(reviewed_cases) != len(expected_ids):
        raise ConversationStateProbeError("source-review case order or identity drifted")

    sealed_cases: list[dict[str, Any]] = []
    aggregate_failed: set[str] = set()
    for case in contract["cases"]:
        case_id = str(case["case_id"])
        row = by_case[case_id]
        axes = row.get("axes")
        if not isinstance(axes, Mapping):
            raise ConversationStateProbeError(f"source-review axes missing: {case_id}")
        required_axes = {
            "position_ownership",
            "thread_disposition",
            "source_strength",
            "constraint_coverage",
            "exact_quote_grounding",
            "late_turn_trajectory",
        }
        if set(axes) != required_axes:
            raise ConversationStateProbeError(f"source-review axes drifted: {case_id}")

        ownership = axes["position_ownership"]
        disposition = axes["thread_disposition"]
        strength = axes["source_strength"]
        coverage = axes["constraint_coverage"]
        grounding = axes["exact_quote_grounding"]
        trajectory = axes["late_turn_trajectory"]
        for axis_name, axis in axes.items():
            if not isinstance(axis, Mapping):
                raise ConversationStateProbeError(
                    f"source-review axis is not an object: {case_id}/{axis_name}"
                )
        try:
            precision = float(coverage.get("precision"))
            recall = float(coverage.get("recall"))
            strengthening_breaches = int(strength.get("material_strengthening_breaches"))
            quote_violations = int(grounding.get("violations"))
        except (TypeError, ValueError) as exc:
            raise ConversationStateProbeError(
                f"source-review numeric value invalid: {case_id}"
            ) from exc
        if not 0.0 <= precision <= 1.0 or not 0.0 <= recall <= 1.0:
            raise ConversationStateProbeError(f"source-review coverage out of range: {case_id}")
        if strengthening_breaches < 0 or quote_violations < 0:
            raise ConversationStateProbeError(f"source-review violation count invalid: {case_id}")

        axis_passes = {
            "position_ownership": (
                ownership.get("status") == "reviewed"
                and ownership.get("expected") == case["expected_position_ownership"]
                and ownership.get("observed") == case["expected_position_ownership"]
            ),
            "thread_disposition": (
                disposition.get("status") == "reviewed"
                and disposition.get("expected") == case["expected_thread_disposition"]
                and disposition.get("observed") == case["expected_thread_disposition"]
                and disposition.get("observed") != "genuinely_dropped"
            ),
            "source_strength": (
                strength.get("status") == "reviewed"
                and strengthening_breaches == 0
            ),
            "constraint_coverage": (
                coverage.get("status") == "reviewed"
                and precision >= 0.80
                and recall >= 0.75
            ),
            "exact_quote_grounding": (
                grounding.get("status") in {"mechanical_gate", "reviewed"}
                and quote_violations == 0
            ),
            "late_turn_trajectory": (
                trajectory.get("status") == "reviewed"
                and trajectory.get("user_turn_7_represented") is True
                and trajectory.get("assistant_turn_7_represented") is True
            ),
        }
        failed_axes = [name for name, passed in axis_passes.items() if not passed]
        aggregate_failed.update(failed_axes)
        sealed_cases.append(
            {
                "case_id": case_id,
                "passed": not failed_axes,
                "axis_passes": axis_passes,
                "failed_axes": failed_axes,
                "review_notes": {
                    name: str(axis.get("reason", ""))
                    for name, axis in axes.items()
                    if str(axis.get("reason", "")).strip()
                },
            }
        )

    probe_passed = not aggregate_failed
    return {
        "schema_version": REVIEW_RESULT_SCHEMA,
        "status": "passed" if probe_passed else "failed",
        "run_id": contract["run_id"],
        "contract_sha256": _hash_text(
            json.dumps(contract, sort_keys=True, separators=(",", ":"))
        ),
        "review_order_attested": True,
        "composite_score": None,
        "cases": sealed_cases,
        "aggregate_decision": {
            "probe_passed": probe_passed,
            "failed_axes": sorted(aggregate_failed),
            "full_pipeline_authorized": False,
            "graph_calls_authorized": False,
            "runtime_integration_authorized": False,
        },
        "evaluator_calls": 0,
        "non_claims": [
            "probe_pass_is_not_answer_improvement",
            "probe_pass_is_not_graph_value",
            "no_composite_quality_score",
            "not_full_pipeline_authority",
        ],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--seal-review", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    contract = _load_object(args.contract)
    validate_contract(contract)
    if args.seal_review is not None:
        result = seal_source_review(contract, _load_object(args.seal_review))
        result_path = _repo_path(
            contract["artifacts"]["source_review_result_path"],
            label="source review result",
        )
        _write_json_atomic(result_path, result)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["status"] == "passed" else 1
    if args.dry_run:
        output_dir = _repo_path(contract["artifacts"]["output_dir"], label="output directory")
        if output_dir.exists():
            raise ConversationStateProbeError("frozen output directory must be absent")
        print(
            json.dumps(
                {
                    "status": "dry_run_valid",
                    "run_id": contract["run_id"],
                    "selected_case_ids": [case["case_id"] for case in contract["cases"]],
                    "prompt_hashes": contract["prompt_hashes"],
                    "response_schema_sha256": _json_hash(response_schema()),
                    "maximum_provider_calls": 2,
                    "automatic_retries": 0,
                    "pipeline_calls": 0,
                    "graph_calls": 0,
                    "evaluator_calls": 0,
                    "provider_calls_made_by_dry_run": 0,
                },
                indent=2,
            )
        )
        return 0
    if args.env_file is None:
        raise ConversationStateProbeError("--env-file required for execution")
    if args.authorization is None:
        raise ConversationStateProbeError("--authorization required for execution")
    authorization = _load_object(args.authorization)
    validate_authorization(
        authorization,
        contract_path=args.contract.resolve(),
        contract=contract,
    )
    _load_env_file(args.env_file)
    summary, _custody = run_probe(contract)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if not summary["failed_gates"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
