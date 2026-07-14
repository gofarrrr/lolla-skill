#!/usr/bin/env python3
"""Run the prospective R4 semantic-distinction holdout after authorization.

The historical R4 runner remains frozen.  This adapter reuses its deterministic
assembly while substituting the v2 prompts and strict, value-free reasoning
envelope inspection required by the prospective contract.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from urllib import error, request

from engine.system_b.r4_complementary_readers import (
    relationship_response_schema_v1,
    sha256_bytes,
    uncertainty_response_schema_v1,
    value_sha256,
)
from engine.system_b.r4_semantic_distinction import (
    SEMANTIC_DISTINCTION_PROMPT_CONTRACT,
    build_relationship_prompts_v2,
    inspect_r4_reasoning_exclusion_v1,
)
from scripts.evals import build_r4_complementary_reader_preflight as base_preflight
from scripts.evals import run_r4_complementary_reader_experiment as frozen
from scripts.evals.build_r4_semantic_distinction_contract import (
    MAX_RELATIONSHIP_PROMPT_UTF8_BYTES,
    TASK_LIMITS,
)


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_SCHEMA = "lolla.r4_semantic_distinction_contract.v1"
AUTH_SCHEMA = "lolla.r4_semantic_distinction_authorization.v1"
RESULT_SCHEMA = "lolla.r4_semantic_distinction_experiment_result.v1"
DEFAULT_CONTRACT = ROOT / "docs/evals/lolla-r4-semantic-distinction-contract-v1.json"
HOLDOUT_RELATIVE = "docs/evals/lolla-r4-semantic-distinction-holdout-target-v1.json"


class R4SemanticDistinctionRunError(RuntimeError):
    """Raised when the prospective contract, authorization, or custody drifts."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R4SemanticDistinctionRunError(f"expected JSON object: {path}")
    return value


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


def validate_contract(path: Path = DEFAULT_CONTRACT) -> dict[str, Any]:
    """Rebuild and verify the exact provider-free package without transport."""

    contract = _load(path)
    if (
        contract.get("schema_version") != CONTRACT_SCHEMA
        or contract.get("status")
        != "frozen_provider_free_new_call_authorization_required"
        or contract.get("run_id") != "lolla-r4-semantic-distinction-holdout-a3"
    ):
        raise R4SemanticDistinctionRunError("semantic-distinction contract drifted")
    if path.resolve() != DEFAULT_CONTRACT.resolve():
        raise R4SemanticDistinctionRunError("only the frozen default contract is runnable")
    if contract.get("task_limits") != TASK_LIMITS:
        raise R4SemanticDistinctionRunError("task limits drifted")
    if contract.get("prompt_contract", {}).get("version") != (
        SEMANTIC_DISTINCTION_PROMPT_CONTRACT
    ):
        raise R4SemanticDistinctionRunError("prompt contract drifted")
    expected_cases = [
        "v1-case01-flood-infrastructure",
        "v1-case04-component-sourcing",
    ]
    if [row.get("case_id") for row in contract.get("cases", [])] != expected_cases:
        raise R4SemanticDistinctionRunError("holdout identity or order drifted")
    budget = contract.get("budget", {})
    if (
        budget.get("maximum_provider_calls") != 4
        or budget.get("maximum_calls_per_case") != 2
        or budget.get("maximum_provider_reported_cost_per_case_usd") != 0.015
        or budget.get("maximum_provider_reported_cost_total_usd") != 0.03
        or budget.get("automatic_retries") != 0
        or budget.get("semantic_retries") != 0
        or budget.get("fallback_models") != 0
        or budget.get("response_healing") is not False
    ):
        raise R4SemanticDistinctionRunError("budget boundary drifted")
    if (
        contract.get("decision_boundary", {}).get("provider_calls_authorized")
        is not False
        or contract.get("decision_boundary", {}).get("authorization_file_present")
        is not False
        or contract.get("execution_contract", {}).get(
            "strict_reasoning_shape_adapter_required"
        )
        is not True
        or contract.get("execution_contract", {}).get(
            "maximum_relationship_prompt_utf8_bytes"
        )
        != MAX_RELATIONSHIP_PROMPT_UTF8_BYTES
    ):
        raise R4SemanticDistinctionRunError("execution boundary drifted")
    if (
        value_sha256(uncertainty_response_schema_v1())
        != contract["schemas"]["uncertainty_sha256"]
        or value_sha256(relationship_response_schema_v1())
        != contract["schemas"]["relationship_sha256"]
    ):
        raise R4SemanticDistinctionRunError("response schema drifted")
    holdout_ref = contract.get("holdout_target", {})
    if (
        holdout_ref.get("path") != HOLDOUT_RELATIVE
        or not isinstance(holdout_ref.get("sha256"), str)
    ):
        raise R4SemanticDistinctionRunError("holdout reference drifted")
    for row in contract.get("frozen_inputs", []):
        if row.get("path") == HOLDOUT_RELATIVE:
            if row != holdout_ref:
                raise R4SemanticDistinctionRunError("holdout hash reference drifted")
            # The hidden target is review evidence, never runner input.  The
            # authorization freezes the contract that carries this reference.
            continue
        frozen_path = ROOT / row["path"]
        if not frozen_path.is_file() or _file_sha(frozen_path) != row["sha256"]:
            raise R4SemanticDistinctionRunError(f"frozen input drifted: {row['path']}")
    preflight_ref = contract.get("preflight", {})
    preflight_path = ROOT / preflight_ref["path"]
    manifest_path = ROOT / preflight_ref["manifest_path"]
    if (
        _file_sha(preflight_path) != preflight_ref.get("sha256")
        or _file_sha(manifest_path) != preflight_ref.get("manifest_sha256")
        or _load(preflight_path).get("status")
        != "provider_free_contract_ready_new_call_authorization_required"
    ):
        raise R4SemanticDistinctionRunError("preflight package drifted")
    for case in contract["cases"]:
        preview = _load(ROOT / case["uncertainty_request_preview_path"])
        if (
            preview.get("body_sha256") != case["uncertainty_request_body_sha256"]
            or preview.get("body", {}).get("seed") != case["seeds"]["uncertainty"]
            or case.get("relationship_seed") != case["seeds"]["relationship"]
        ):
            raise R4SemanticDistinctionRunError("request preview or seed drifted")
    return contract


def validate_authorization(
    authorization_path: Path, *, contract: Mapping[str, Any], contract_path: Path
) -> None:
    expected = {
        "schema_version": AUTH_SCHEMA,
        "status": "authorized_once_after_semantic_distinction_preflight",
        "contract_path": _relative(contract_path),
        "contract_sha256": _file_sha(contract_path),
        "run_id": contract["run_id"],
        "authorized_case_ids": [row["case_id"] for row in contract["cases"]],
        "maximum_provider_calls": 4,
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
    if _load(authorization_path) != expected:
        raise R4SemanticDistinctionRunError("authorization drifted")


def _provider_call(
    *,
    output: Path,
    ordinal: int,
    case_id: str,
    task: str,
    preview: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    """Make one bounded call while preserving only value-free reasoning custody."""

    body = preview["body"]
    prefix = f"call-{ordinal:02d}-{task}"
    started_path = output / f"{prefix}-started.json"
    result_path = output / f"{prefix}-result.json"
    if started_path.exists() or result_path.exists():
        raise R4SemanticDistinctionRunError(f"call artifact already exists: {prefix}")
    prompt_bytes = sum(
        len(message["content"].encode("utf-8")) for message in body["messages"]
    )
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
        "prompt_utf8_bytes": prompt_bytes,
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
    if task == "relationship" and prompt_bytes > MAX_RELATIONSHIP_PROMPT_UTF8_BYTES:
        result = {
            **base,
            "operational_status": "relationship_prompt_size_preflight_failed",
            "provider_calls": 0,
            "maximum_prompt_utf8_bytes": MAX_RELATIONSHIP_PROMPT_UTF8_BYTES,
        }
        _write(result_path, result)
        return result
    _write(
        started_path,
        {
            **base,
            "status": "started_before_network_transport",
            "started_at_unix": time.time(),
        },
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
    custody = inspect_r4_reasoning_exclusion_v1(message)
    content = message.get("content", "")
    if not isinstance(content, str):
        content = json.dumps(content, ensure_ascii=False)
    candidate = None
    parse_error = ""
    try:
        candidate = json.loads(content)
        if not isinstance(candidate, dict):
            raise R4SemanticDistinctionRunError("provider content is not a JSON object")
    except Exception as exc:  # noqa: BLE001
        parse_error = f"{type(exc).__name__}: {exc}"
    usage = payload.get("usage") if isinstance(payload.get("usage"), Mapping) else {}
    served_model = str(payload.get("model", ""))
    served_provider = str(payload.get("provider", ""))
    attribution_ok = (
        served_model in contract["operator"]["allowed_served_model_ids"]
        and served_provider in contract["operator"]["allowed_served_provider_names"]
    )
    status = (
        "reasoning_custody_failed"
        if not custody["exclusion_satisfied"]
        else "candidate_parsed"
        if candidate is not None and attribution_ok
        else "operator_attribution_failed"
        if candidate is not None
        else "candidate_parse_failed"
    )
    result = {
        **base,
        "operational_status": status,
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
        "reasoning_custody": custody,
        "reasoning_values_preserved": False,
        "duration_seconds": round(time.monotonic() - started, 3),
    }
    _write(result_path, result)
    return result


def run(contract: Mapping[str, Any], *, output: Path) -> dict[str, Any]:
    """Reuse frozen assembly with prospective prompts and custody, then restore it."""

    previous_tasks = copy.deepcopy(base_preflight.TASKS)
    previous_provider_call = frozen._provider_call
    previous_relationship_prompts = frozen.build_relationship_prompts_v1
    try:
        base_preflight.TASKS.clear()
        base_preflight.TASKS.update(copy.deepcopy(TASK_LIMITS))
        frozen._provider_call = _provider_call
        frozen.build_relationship_prompts_v1 = build_relationship_prompts_v2
        result = frozen.run(contract, output=output)
    finally:
        frozen._provider_call = previous_provider_call
        frozen.build_relationship_prompts_v1 = previous_relationship_prompts
        base_preflight.TASKS.clear()
        base_preflight.TASKS.update(previous_tasks)
    result["schema_version"] = RESULT_SCHEMA
    result["prompt_contract_version"] = SEMANTIC_DISTINCTION_PROMPT_CONTRACT
    result["strict_reasoning_shape_adapter_used"] = True
    result["historical_r4_result_reclassified"] = False
    _write(output / "result.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    contract_path = args.contract.resolve()
    contract = validate_contract(contract_path)
    if args.dry_run:
        print(
            json.dumps(
                {
                    "status": "frozen_semantic_distinction_contract_valid",
                    "provider_calls": 0,
                    "authorization_present": args.authorization is not None,
                    "conservative_estimated_total_cost_usd": contract["budget"][
                        "conservative_estimated_total_cost_usd"
                    ],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if args.authorization is None or args.env_file is None or args.output is None:
        raise R4SemanticDistinctionRunError(
            "live execution requires new authorization, env, and output"
        )
    validate_authorization(
        args.authorization.resolve(), contract=contract, contract_path=contract_path
    )
    output = args.output.resolve()
    if output.exists():
        raise R4SemanticDistinctionRunError("experiment output path already exists")
    output.mkdir(parents=True)
    frozen._load_env(args.env_file.resolve())
    result = run(contract, output=output)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["cost_ceiling_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
