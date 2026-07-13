#!/usr/bin/env python3
"""Generate one frozen pool of realistic ambiguous multi-turn conversations."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import re
import time
from typing import Any, Callable, Mapping, Sequence
from urllib import error, request

from engine.system_b.pricing import (
    PRICES_LAST_VERIFIED,
    estimate_chat_cost_usd,
    lookup_chat_price,
)
from scripts.evals import run_fixed_safe_holdout_pool as shared
from scripts.evals import run_fixed_safe_holdout_pool_v2 as custody_v2


CONTRACT_SCHEMA = "lolla.designed_ambiguous_pool_contract.v1"
PAYLOAD_SCHEMA = "lolla.designed_ambiguous_pool_payload.v1"
POOL_SCHEMA = "lolla.designed_ambiguous_pool.v1"
CUSTODY_SCHEMA = "lolla.designed_ambiguous_pool_call_custody.v1"
SUMMARY_SCHEMA = "lolla.designed_ambiguous_pool_run_summary.v1"
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


class DesignedPoolError(RuntimeError):
    pass


def _selection_order(seed: str, case_ids: Sequence[str]) -> list[str]:
    return sorted(case_ids, key=lambda item: shared._hash_text(f"{seed}:{item}"))


def _response_schema(contract: Mapping[str, Any]) -> dict[str, Any]:
    message_count = int(contract["case_specs"][0]["required_message_count"])
    return {
        "name": "designed_ambiguous_conversation_pool",
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "schema_version": {"type": "string"},
                "cases": {
                    "type": "array",
                    "minItems": 5,
                    "maxItems": 5,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "case_id": {"type": "string"},
                            "title": {"type": "string"},
                            "stratum": {"type": "string"},
                            "messages": {
                                "type": "array",
                                "minItems": message_count,
                                "maxItems": message_count,
                                "items": {
                                    "type": "object",
                                    "additionalProperties": False,
                                    "properties": {
                                        "role": {
                                            "type": "string",
                                            "enum": ["user", "assistant"],
                                        },
                                        "content": {"type": "string"},
                                    },
                                    "required": ["role", "content"],
                                },
                            },
                        },
                        "required": ["case_id", "title", "stratum", "messages"],
                    },
                },
            },
            "required": ["schema_version", "cases"],
        },
    }


def build_prompts(contract: Mapping[str, Any]) -> dict[str, str]:
    specs = [
        {
            "case_id": row["case_id"],
            "title": row["title"],
            "stratum": row["stratum"],
            "scenario_brief": row["scenario_brief"],
            "required_message_count": row["required_message_count"],
        }
        for row in contract["case_specs"]
    ]
    user = (
        str(contract["authoring_instruction"]).strip()
        + "\n\nCASE SPECIFICATIONS\n"
        + json.dumps(specs, indent=2, ensure_ascii=False)
        + "\n\nOUTPUT\nReturn only the structured object required by the response schema. "
        + f"Set schema_version to {PAYLOAD_SCHEMA}. Preserve the case order above."
    )
    return {
        "system_prompt": str(contract["system_prompt"]).strip(),
        "user_prompt": user,
    }


def _prompt_hashes(contract: Mapping[str, Any]) -> dict[str, str]:
    prompts = build_prompts(contract)
    return {
        "system_prompt_sha256": shared._hash_text(prompts["system_prompt"]),
        "user_prompt_sha256": shared._hash_text(prompts["user_prompt"]),
        "response_schema_sha256": custody_v2._json_hash(_response_schema(contract)),
    }


def validate_contract(contract: Mapping[str, Any]) -> None:
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise DesignedPoolError("unexpected designed-pool contract schema")
    if contract.get("status") != "frozen_before_call":
        raise DesignedPoolError("contract must be frozen_before_call")
    if not RUN_ID_PATTERN.fullmatch(str(contract.get("run_id", ""))):
        raise DesignedPoolError("invalid run_id")
    specs = contract.get("case_specs")
    if not isinstance(specs, list) or len(specs) != 5:
        raise DesignedPoolError("exactly five case specs required")
    case_ids: list[str] = []
    strata: list[str] = []
    for row in specs:
        if not isinstance(row, Mapping) or set(row) != {
            "case_id",
            "title",
            "stratum",
            "scenario_brief",
            "required_message_count",
        }:
            raise DesignedPoolError("case spec shape invalid")
        if int(row["required_message_count"]) != 14:
            raise DesignedPoolError("every case must require fourteen messages")
        if not all(str(row[key]).strip() for key in ("case_id", "title", "stratum", "scenario_brief")):
            raise DesignedPoolError("case spec text missing")
        case_ids.append(str(row["case_id"]))
        strata.append(str(row["stratum"]))
    if len(case_ids) != len(set(case_ids)) or len(strata) != len(set(strata)):
        raise DesignedPoolError("case IDs and strata must be unique")

    selection = contract.get("selection_contract", {})
    expected_order = _selection_order(str(selection.get("public_seed", "")), case_ids)
    if selection.get("algorithm") != "sha256_seed_colon_case_id_ascending":
        raise DesignedPoolError("selection algorithm drifted")
    if selection.get("ranked_case_ids") != expected_order:
        raise DesignedPoolError("selection order drifted")
    if selection.get("generator_receives_selection_order") is not False:
        raise DesignedPoolError("selection order must be withheld")
    prompts = build_prompts(contract)
    if str(selection["public_seed"]) in prompts["user_prompt"]:
        raise DesignedPoolError("selection seed leaked to generator")
    if json.dumps(expected_order) in prompts["user_prompt"]:
        raise DesignedPoolError("selection rank leaked to generator")

    config = contract.get("call_configuration", {})
    expected_config = {
        "provider": "openrouter",
        "model": "moonshotai/kimi-k2.6",
        "generation_calls": 1,
        "automatic_retries": 0,
        "evaluator_calls": 0,
        "reasoning_parameter_sent": False,
        "strict_structured_output": True,
        "require_supported_parameters": True,
    }
    for key, value in expected_config.items():
        if config.get(key) != value:
            raise DesignedPoolError(f"call configuration drifted: {key}")
    if config.get("downstream_model") == config.get("model"):
        raise DesignedPoolError("source and downstream model families must differ")
    if not 0 <= float(config.get("temperature", -1)) <= 1:
        raise DesignedPoolError("temperature invalid")
    if not 1 <= int(config.get("max_output_tokens", 0)) <= 16000:
        raise DesignedPoolError("max output tokens invalid")
    if not isinstance(config.get("seed"), int):
        raise DesignedPoolError("generation seed missing")
    if not 1 <= float(config.get("provider_timeout_seconds", 0)) <= 120:
        raise DesignedPoolError("provider timeout invalid")
    if not 1 <= float(config.get("wall_clock_timeout_seconds", 0)) <= 180:
        raise DesignedPoolError("wall timeout invalid")
    if lookup_chat_price("openrouter", str(config["model"])) is None:
        raise DesignedPoolError("model missing from pricing table")
    budget = contract.get("call_budget", {})
    if budget.get("pricing_table_version") != PRICES_LAST_VERIFIED:
        raise DesignedPoolError("pricing version drifted")
    if not 0 < float(budget.get("estimated_cost_ceiling_usd", 0)) <= 0.10:
        raise DesignedPoolError("cost ceiling invalid")

    roles: set[str] = set()
    for row in contract.get("hash_locks", []):
        if not isinstance(row, Mapping) or set(row) != {"role", "path", "sha256"}:
            raise DesignedPoolError("hash lock shape invalid")
        role = str(row["role"])
        if role in roles:
            raise DesignedPoolError("hash lock roles must be unique")
        roles.add(role)
        path = shared._repo_path(row["path"], label=f"hash lock {role}")
        if not path.is_file() or shared._hash_file(path) != row["sha256"]:
            raise DesignedPoolError(f"hash lock mismatch: {role}")
    if not {"pool_runner", "pricing", "ambiguity_protocol", "evaluation_doctrine"} <= roles:
        raise DesignedPoolError("required hash locks missing")
    if contract.get("prompt_hashes") != _prompt_hashes(contract):
        raise DesignedPoolError("prompt hashes drifted")

    artifacts = contract.get("artifacts", {})
    output_dir = shared._repo_path(artifacts.get("output_dir", ""), label="output dir")
    for key in ("pool_path", "call_custody_path", "run_summary_path"):
        path = shared._repo_path(artifacts.get(key, ""), label=key)
        if path.parent != output_dir:
            raise DesignedPoolError(f"{key} must be inside output dir")
    case_dir = shared._repo_path(artifacts.get("case_dir", ""), label="case dir")
    if case_dir.parent != output_dir:
        raise DesignedPoolError("case_dir must be inside output dir")
    if contract.get("post_call_review", {}).get("scope") != (
        "safety_realism_and_ambiguity_only_not_lolla_or_graph_favorability"
    ):
        raise DesignedPoolError("review scope drifted")


def _validate_payload(payload: Mapping[str, Any], contract: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if set(payload) != {"schema_version", "cases"}:
        errors.append("payload top-level shape invalid")
    if payload.get("schema_version") != PAYLOAD_SCHEMA:
        errors.append("payload schema invalid")
    cases = payload.get("cases")
    if not isinstance(cases, list) or len(cases) != len(contract["case_specs"]):
        return errors + ["payload case count invalid"]
    for index, (case, spec) in enumerate(zip(cases, contract["case_specs"], strict=True)):
        label = f"case[{index}]"
        if not isinstance(case, Mapping) or set(case) != {
            "case_id",
            "title",
            "stratum",
            "messages",
        }:
            errors.append(f"{label} shape invalid")
            continue
        for key in ("case_id", "title", "stratum"):
            if case.get(key) != spec[key]:
                errors.append(f"{label} {key} drifted")
        messages = case.get("messages")
        required = int(spec["required_message_count"])
        if not isinstance(messages, list) or len(messages) != required:
            errors.append(f"{label} message count invalid")
            continue
        total_chars = 0
        for message_index, message in enumerate(messages, start=1):
            message_label = f"{label}.messages[{message_index - 1}]"
            if not isinstance(message, Mapping) or set(message) != {"role", "content"}:
                errors.append(f"{message_label} shape invalid")
                continue
            expected_role = "user" if message_index % 2 else "assistant"
            content = message.get("content")
            if message.get("role") != expected_role:
                errors.append(f"{message_label} role invalid")
            if not isinstance(content, str) or not content.strip() or len(content) > 2600:
                errors.append(f"{message_label} content invalid")
            elif content != content.strip():
                errors.append(f"{message_label} content must be trimmed")
            else:
                total_chars += len(content)
        if total_chars < 3200 or total_chars > 18000:
            errors.append(f"{label} conversation length outside contract")
    return errors


def _call_openrouter(contract: Mapping[str, Any]) -> dict[str, Any]:
    started = time.monotonic()
    config = contract["call_configuration"]
    prompts = build_prompts(contract)
    requested_model = str(config["model"])
    base = {
        "call_attempted": True,
        "requested_model": requested_model,
        "system_prompt_sha256": shared._hash_text(prompts["system_prompt"]),
        "user_prompt_sha256": shared._hash_text(prompts["user_prompt"]),
        "response_schema_sha256": custody_v2._json_hash(_response_schema(contract)),
        "reasoning_parameter_sent": False,
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
        "response_format": {"type": "json_schema", "json_schema": _response_schema(contract)},
        "provider": {"require_parameters": True},
        "temperature": config["temperature"],
        "seed": config["seed"],
        "max_tokens": config["max_output_tokens"],
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
            "usage_evidence_state": "unknown",
            "provider_diagnostic": custody_v2._provider_diagnostic(error_payload, []),
            "provider_payload_sha256": custody_v2._json_hash(error_payload),
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    except Exception as exc:
        return {
            **base,
            "status": "provider_error",
            "response": {},
            "validation_errors": [type(exc).__name__],
            "served_model": "",
            "model_attribution_status": "not_observed",
            "usage_evidence_state": "unknown",
            "provider_diagnostic": {"type": type(exc).__name__},
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    choices_raw = provider_payload.get("choices", [])
    choices = choices_raw if isinstance(choices_raw, list) else []
    choice = choices[0] if choices and isinstance(choices[0], Mapping) else {}
    message = choice.get("message", {}) if isinstance(choice, Mapping) else {}
    raw = str(message.get("content", "")) if isinstance(message, Mapping) else ""
    parsed = shared._extract_json_object(raw)
    validation_errors = _validate_payload(parsed, contract)
    finish_reason = str(choice.get("finish_reason", ""))
    if finish_reason == "error":
        validation_errors.insert(0, "provider returned finish_reason=error")
    usage = provider_payload.get("usage", {})
    prompt_tokens = usage.get("prompt_tokens") if isinstance(usage, Mapping) else None
    completion_tokens = usage.get("completion_tokens") if isinstance(usage, Mapping) else None
    total_tokens = usage.get("total_tokens") if isinstance(usage, Mapping) else None
    usage_complete = all(
        isinstance(value, int) and value > 0
        for value in (prompt_tokens, completion_tokens, total_tokens)
    )
    served_model = str(provider_payload.get("model", ""))
    return {
        **base,
        "status": "ok" if not validation_errors else "invalid_contract",
        "response": parsed,
        "validation_errors": validation_errors,
        "served_model": served_model,
        "model_attribution_status": shared._model_attribution(requested_model, served_model),
        "finish_reason": finish_reason,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "reasoning_tokens": (
            usage.get("completion_tokens_details", {}).get("reasoning_tokens", 0)
            if isinstance(usage, Mapping)
            and isinstance(usage.get("completion_tokens_details", {}), Mapping)
            else 0
        ),
        "usage_evidence_state": "complete" if usage_complete else "unknown",
        "response_sha256": shared._hash_text(raw),
        "provider_payload_sha256": custody_v2._json_hash(provider_payload),
        "provider_diagnostic": custody_v2._provider_diagnostic(provider_payload, choices),
        "raw_provider_content_included": False,
        "duration_seconds": round(time.monotonic() - started, 3),
    }


def _render_conversation(case: Mapping[str, Any]) -> str:
    lines = [
        f"# {case['title']}",
        "",
        f"Case ID: {case['case_id']}",
        f"Stratum: {case['stratum']}",
        "Designed synthetic evaluation fixture; not a real person's conversation.",
        "",
    ]
    turn = 0
    for message in case["messages"]:
        if message["role"] == "user":
            turn += 1
        lines.extend(
            [
                f"[Turn {turn}] {str(message['role']).upper()}:",
                str(message["content"]),
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _build_pool(contract: Mapping[str, Any], call: Mapping[str, Any]) -> dict[str, Any]:
    cases = []
    for raw_case in call.get("response", {}).get("cases", []):
        case = deepcopy(raw_case)
        for index, message in enumerate(case["messages"], start=1):
            message["message_id"] = f"{case['case_id']}-m{index:02d}"
        conversation = _render_conversation(case)
        cases.append(
            {
                **case,
                "message_count": len(case["messages"]),
                "conversation_sha256": shared._hash_text(conversation),
                "conversation_path": (
                    f"{contract['artifacts']['case_dir']}/{case['case_id']}.txt"
                ),
            }
        )
    return {
        "schema_version": POOL_SCHEMA,
        "pool_id": contract["pool_id"],
        "status": "frozen_unreviewed" if call.get("status") == "ok" else "generation_failed",
        "provenance": {
            "kind": "founder_directed_independent_model_synthetic",
            "real_person_data": False,
            "requested_model": call.get("requested_model", ""),
            "served_model": call.get("served_model", ""),
            "generation_contract_sha256": contract.get("contract_sha256_at_execution", ""),
            "canonical_message_id_owner": "deterministic_runner",
        },
        "selection_contract": contract["selection_contract"],
        "selected_case_id": None,
        "selection_review_status": "pending_safety_realism_and_ambiguity_review",
        "cases": cases,
        "non_claims": contract["non_claims"],
    }


def run_generation(
    contract: Mapping[str, Any],
    *,
    call_fn: Callable[[Mapping[str, Any]], dict[str, Any]] = _call_openrouter,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    validate_contract(contract)
    started = time.monotonic()
    call = call_fn(contract)
    wall_time = time.monotonic() - started
    pool = _build_pool(contract, call)
    custody = {
        "schema_version": CUSTODY_SCHEMA,
        "run_id": contract["run_id"],
        "recorded_call_count": 1,
        "call": call,
        "raw_provider_content_included": False,
    }
    usage_complete = call.get("usage_evidence_state") == "complete"
    price = lookup_chat_price("openrouter", contract["call_configuration"]["model"])
    estimated_cost = (
        estimate_chat_cost_usd(
            price=price,
            prompt_tokens=int(call.get("prompt_tokens") or 0),
            completion_tokens=int(call.get("completion_tokens") or 0),
        )
        if price is not None and usage_complete
        else None
    )
    gates = {
        "exactly_one_call_recorded": True,
        "call_status_ok": call.get("status") == "ok",
        "typed_pool_valid": not call.get("validation_errors"),
        "five_cases_preserved": len(pool["cases"]) == 5,
        "fourteen_messages_each": bool(pool["cases"])
        and all(case["message_count"] == 14 for case in pool["cases"]),
        "canonical_ids_assigned_deterministically": bool(pool["cases"])
        and all(
            message["message_id"] == f"{case['case_id']}-m{index:02d}"
            for case in pool["cases"]
            for index, message in enumerate(case["messages"], start=1)
        ),
        "usage_evidence_complete": usage_complete,
        "served_model_attribution_complete": call.get("model_attribution_status")
        in {"matched", "served_version_alias"},
        "wall_clock_ceiling_met": wall_time
        <= float(contract["call_configuration"]["wall_clock_timeout_seconds"]),
        "cost_estimate_complete": estimated_cost is not None,
        "cost_ceiling_met": estimated_cost is not None
        and estimated_cost <= float(contract["call_budget"]["estimated_cost_ceiling_usd"]),
        "automatic_retries_zero": True,
        "evaluator_calls_zero": True,
    }
    summary = {
        "schema_version": SUMMARY_SCHEMA,
        "run_id": contract["run_id"],
        "status": "passed" if all(gates.values()) else "failed",
        "contract_sha256": contract.get("contract_sha256_at_execution", ""),
        "call_count": 1,
        "prompt_tokens": call.get("prompt_tokens") if usage_complete else None,
        "completion_tokens": call.get("completion_tokens") if usage_complete else None,
        "total_tokens": call.get("total_tokens") if usage_complete else None,
        "estimated_cost_usd": estimated_cost,
        "pricing_table_version": PRICES_LAST_VERIFIED,
        "wall_time_seconds": round(wall_time, 3),
        "gates": gates,
        "failed_gates": [name for name, passed in gates.items() if not passed],
        "automatic_retries": 0,
        "evaluator_calls": 0,
        "semantic_or_graph_selection_performed": False,
        "runtime_change_authorized": False,
    }
    return pool, custody, summary


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    contract = shared._load_object(args.contract)
    validate_contract(contract)
    if args.dry_run:
        print(
            json.dumps(
                {
                    "status": "dry_run_valid",
                    "run_id": contract["run_id"],
                    "call_count": 1,
                    "prompt_hashes": contract["prompt_hashes"],
                    "source_model": contract["call_configuration"]["model"],
                    "reasoning_parameter_sent": False,
                    "message_id_owner": "deterministic_runner",
                    "ranked_case_ids": contract["selection_contract"]["ranked_case_ids"],
                    "provider_calls": 0,
                },
                indent=2,
            )
        )
        return 0
    if args.env_file is None:
        raise DesignedPoolError("--env-file is required for execution")
    contract = dict(contract)
    contract["contract_sha256_at_execution"] = shared._hash_file(args.contract)
    shared._load_env_file(args.env_file)
    output_dir = shared._repo_path(contract["artifacts"]["output_dir"], label="output dir")
    if output_dir.exists():
        raise DesignedPoolError("designed-pool output directory already exists")
    output_dir.mkdir(parents=True)
    pool, custody, summary = run_generation(contract)
    summary["gates"]["output_directory_absent_before_run"] = True
    summary["failed_gates"] = [name for name, passed in summary["gates"].items() if not passed]
    summary["status"] = "passed" if not summary["failed_gates"] else "failed"
    for case in pool["cases"]:
        shared._write_text_atomic(
            shared._repo_path(case["conversation_path"], label="conversation path"),
            _render_conversation(case),
        )
    shared._write_json_atomic(
        shared._repo_path(contract["artifacts"]["pool_path"], label="pool path"), pool
    )
    shared._write_json_atomic(
        shared._repo_path(contract["artifacts"]["call_custody_path"], label="call custody path"),
        custody,
    )
    shared._write_json_atomic(
        shared._repo_path(contract["artifacts"]["run_summary_path"], label="run summary path"),
        summary,
    )
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
