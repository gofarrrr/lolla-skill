#!/usr/bin/env python3
"""Prospective v3 pool runner with deterministic message-ID ownership."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from scripts.evals import run_fixed_safe_holdout_pool as v1
from scripts.evals import run_fixed_safe_holdout_pool_v2 as v2


CONTRACT_SCHEMA = "lolla.fixed_safe_holdout_pool_generation_contract.v3"


def _expand_contract(contract: Mapping[str, Any]) -> dict[str, Any]:
    if "case_specs" in contract:
        return deepcopy(dict(contract))
    base_ref = contract.get("base_contract", {})
    base_path = v1._repo_path(base_ref.get("path", ""), label="base contract")
    if not base_path.is_file() or v1._hash_file(base_path) != base_ref.get("sha256"):
        raise v1.HoldoutPoolError("v3 base contract hash mismatch")
    expanded = deepcopy(v1._load_object(base_path))
    for key in (
        "schema_version",
        "status",
        "date",
        "run_id",
        "purpose",
        "deterministic_id_repair",
        "hash_locks",
        "prompt_hashes",
        "artifacts",
        "stop_rules",
        "non_claims",
    ):
        if key not in contract:
            raise v1.HoldoutPoolError(f"v3 overlay missing field: {key}")
        expanded[key] = deepcopy(contract[key])
    return expanded


def _shadow_v1_contract(contract: Mapping[str, Any]) -> dict[str, Any]:
    shadow = dict(contract)
    shadow["schema_version"] = v1.CONTRACT_SCHEMA
    config = dict(contract["call_configuration"])
    config["reasoning_effort"] = "none"
    shadow["call_configuration"] = config
    shadow["prompt_hashes"] = v1._prompt_hashes(shadow)
    return shadow


def validate_contract(contract: Mapping[str, Any]) -> None:
    contract = _expand_contract(contract)
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise v1.HoldoutPoolError("unexpected v3 pool contract schema")
    config = contract.get("call_configuration", {})
    if config.get("model") != "google/gemini-3.1-flash-lite":
        raise v1.HoldoutPoolError("v3 repair is scoped to the frozen Gemini model")
    if config.get("reasoning_effort") != "minimal":
        raise v1.HoldoutPoolError("v3 Gemini reasoning effort must be minimal")
    repair = contract.get("deterministic_id_repair", {})
    expected = {
        "semantic_prompt_changed": False,
        "case_specs_changed": False,
        "selection_contract_changed": False,
        "model_message_ids_authoritative": False,
        "canonical_ids_assigned_by_deterministic_code": True,
        "automatic_retry_of_v2": False,
    }
    for key, value in expected.items():
        if repair.get(key) is not value:
            raise v1.HoldoutPoolError(f"v3 ID repair drifted: {key}")
    v1.validate_contract(_shadow_v1_contract(contract))
    if contract.get("prompt_hashes") != v1._prompt_hashes(contract):
        raise v1.HoldoutPoolError("v3 prompt hashes drifted")


def _canonicalize_payload(
    payload: Mapping[str, Any], contract: Mapping[str, Any]
) -> tuple[dict[str, Any], list[str], dict[str, Any]]:
    errors: list[str] = []
    if set(payload) != {"schema_version", "cases"}:
        return {}, ["payload top-level shape invalid"], {}
    cases = payload.get("cases")
    if not isinstance(cases, list) or len(cases) != len(contract["case_specs"]):
        return {}, ["payload case count invalid"], {}
    canonical = deepcopy(dict(payload))
    normalized = 0
    original_ids_by_case: dict[str, list[str]] = {}
    for index, (case, spec) in enumerate(zip(cases, contract["case_specs"], strict=True)):
        label = f"case[{index}]"
        if not isinstance(case, Mapping):
            errors.append(f"{label} shape invalid")
            continue
        messages = case.get("messages")
        if not isinstance(messages, list):
            errors.append(f"{label} messages invalid")
            continue
        observed_ids: list[str] = []
        for message_index, message in enumerate(messages, start=1):
            message_label = f"{label}.messages[{message_index - 1}]"
            if not isinstance(message, Mapping) or set(message) != {
                "message_id",
                "role",
                "content",
            }:
                errors.append(f"{message_label} shape invalid")
                continue
            raw_id = message.get("message_id")
            if not isinstance(raw_id, (str, int)) or not str(raw_id).strip():
                errors.append(f"{message_label} model message ID invalid")
                continue
            observed_ids.append(str(raw_id).strip())
            canonical["cases"][index]["messages"][message_index - 1][
                "message_id"
            ] = f"{spec['case_id']}-m{message_index:02d}"
            normalized += 1
        if len(observed_ids) != len(set(observed_ids)):
            errors.append(f"{label} model message IDs must be unique")
        original_ids_by_case[str(spec["case_id"])] = observed_ids
    if not errors:
        errors.extend(v1._validate_payload(canonical, contract))
    normalization = {
        "rule": "case_id_plus_one_based_message_index",
        "model_message_ids_authoritative": False,
        "normalized_message_count": normalized,
        "original_ids_by_case": original_ids_by_case,
    }
    return canonical, errors, normalization


def _call_openrouter(contract: Mapping[str, Any]) -> dict[str, Any]:
    call = v2._call_openrouter(contract)
    previous_errors = list(call.get("validation_errors", []))
    if call.get("finish_reason") == "stop" and isinstance(call.get("response"), Mapping):
        _, errors, normalization = _canonicalize_payload(call["response"], contract)
        call["pre_v3_validation_errors"] = previous_errors
        call["validation_errors"] = errors
        call["status"] = "ok" if not errors else "invalid_contract"
        call["message_id_normalization"] = normalization
    return call


def run_pool_generation(
    contract: Mapping[str, Any],
    *,
    call_fn: Callable[[Mapping[str, Any]], dict[str, Any]] = _call_openrouter,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    contract = _expand_contract(contract)
    validate_contract(contract)
    raw_call = call_fn(contract)
    canonical, errors, normalization = _canonicalize_payload(
        raw_call.get("response", {}), contract
    )
    if raw_call.get("status") == "ok" and errors:
        raw_call = dict(raw_call)
        raw_call["status"] = "invalid_contract"
        raw_call["validation_errors"] = errors
    canonical_call = dict(raw_call)
    canonical_call["response"] = canonical
    canonical_call["validation_errors"] = errors
    canonical_call["status"] = "ok" if not errors and raw_call.get("status") == "ok" else raw_call.get("status")
    pool, custody, summary = v1.run_pool_generation(
        _shadow_v1_contract(contract), call_fn=lambda _: canonical_call
    )
    custody["call"] = raw_call
    custody["message_id_normalization"] = normalization
    summary["message_ids_assigned_deterministically"] = not errors
    summary["model_message_ids_authoritative"] = False
    return pool, custody, summary


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    contract = _expand_contract(v1._load_object(args.contract))
    validate_contract(contract)
    if args.dry_run:
        print(
            json.dumps(
                {
                    "status": "dry_run_valid",
                    "run_id": contract["run_id"],
                    "call_count": 1,
                    "prompt_hashes": contract["prompt_hashes"],
                    "reasoning_effort": contract["call_configuration"][
                        "reasoning_effort"
                    ],
                    "message_id_owner": "deterministic_runner",
                    "ranked_case_ids": contract["selection_contract"][
                        "ranked_case_ids"
                    ],
                    "provider_calls": 0,
                },
                indent=2,
            )
        )
        return 0
    if args.env_file is None:
        raise v1.HoldoutPoolError("--env-file is required for execution")
    contract = dict(contract)
    contract["contract_sha256_at_execution"] = v1._hash_file(args.contract)
    v1._load_env_file(args.env_file)
    output_dir = v1._repo_path(
        contract["artifacts"]["output_dir"], label="output dir"
    )
    if output_dir.exists():
        raise v1.HoldoutPoolError("pool output directory already exists")
    output_dir.mkdir(parents=True)
    pool, custody, summary = run_pool_generation(contract)
    summary["gates"]["output_directory_absent_before_run"] = True
    summary["failed_gates"] = [
        name for name, passed in summary["gates"].items() if not passed
    ]
    summary["status"] = "passed" if not summary["failed_gates"] else "failed"
    for case in pool["cases"]:
        v1._write_text_atomic(
            v1._repo_path(case["conversation_path"], label="conversation path"),
            v1._render_conversation(case),
        )
    v1._write_json_atomic(
        v1._repo_path(contract["artifacts"]["pool_path"], label="pool path"), pool
    )
    v1._write_json_atomic(
        v1._repo_path(
            contract["artifacts"]["call_custody_path"], label="call custody path"
        ),
        custody,
    )
    v1._write_json_atomic(
        v1._repo_path(contract["artifacts"]["run_summary_path"], label="run summary path"),
        summary,
    )
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
