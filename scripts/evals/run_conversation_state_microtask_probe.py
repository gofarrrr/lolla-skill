#!/usr/bin/env python3
"""Run one authorized conversation-state microtask call without writing files."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from urllib import error, request

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.system_b.conversation_state_candidate_pipeline import (  # noqa: E402
    build_candidate_ledger,
)
from engine.system_b.conversation_state_candidates import (  # noqa: E402
    ConstraintExtraction,
    PositionExtraction,
    ThreadExtraction,
    build_micro_contract,
    build_source_catalog,
    parse_typed,
    validate_extraction_state,
)
from engine.system_b.pricing import (  # noqa: E402
    PRICES_LAST_VERIFIED,
    estimate_chat_cost_usd,
    lookup_chat_price,
)
from scripts.evals.run_fixed_safe_holdout_pool import (  # noqa: E402
    _extract_json_object,
    _model_attribution,
)
from scripts.evals.run_fixed_safe_holdout_pool_v2 import (  # noqa: E402
    _provider_diagnostic,
)


CONTRACT_SCHEMA = "lolla.conversation_state_microtask_probe_contract.v1"
AUTHORIZATION_SCHEMA = "lolla.conversation_state_microtask_probe_authorization.v1"
RESULT_SCHEMA = "lolla.conversation_state_microtask_call_result.v1"
KINDS = ("positions", "threads", "constraints")
CLASSES = {
    "positions": PositionExtraction,
    "threads": ThreadExtraction,
    "constraints": ConstraintExtraction,
}


class MicrotaskProbeError(RuntimeError):
    pass


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise MicrotaskProbeError(f"expected JSON object: {path}")
    return value


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _json_sha(value: object) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _repo_path(raw: object, *, label: str) -> Path:
    path = Path(str(raw))
    if path.is_absolute():
        raise MicrotaskProbeError(f"{label} must be repo-relative")
    resolved = (REPO_ROOT / path).resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise MicrotaskProbeError(f"{label} escapes repository") from exc
    return resolved


def _load_env(path: Path) -> None:
    if not path.is_file():
        raise MicrotaskProbeError(f"env file missing: {path}")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        key, value = line.split("=", 1)
        if key.strip() and key.strip() not in os.environ:
            os.environ[key.strip()] = value.strip().strip("'\"")


def _catalog(contract: Mapping[str, Any]):
    case = contract["case"]
    source_path = _repo_path(case["source_path"], label="source")
    source_text = source_path.read_text(encoding="utf-8")
    return build_source_catalog(
        source_text=source_text, source_path=str(source_path.relative_to(REPO_ROOT))
    )


def expected_prompt_hashes(contract: Mapping[str, Any]) -> dict[str, Any]:
    catalog = _catalog(contract)
    result: dict[str, Any] = {}
    for kind in KINDS:
        micro = build_micro_contract(kind, catalog=catalog, provider="gemini")
        result[kind] = {
            "system_prompt_sha256": micro["system_prompt_sha256"],
            "user_prompt_sha256": micro["user_prompt_sha256"],
            "schema_sha256": micro["schema_sha256"],
            "schema_metrics": micro["schema_metrics"],
        }
    return result


def validate_contract(contract: Mapping[str, Any]) -> None:
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise MicrotaskProbeError("unexpected contract schema")
    if contract.get("status") != "frozen_before_calls":
        raise MicrotaskProbeError("contract is not frozen")
    if contract.get("microtask_order") != list(KINDS):
        raise MicrotaskProbeError("microtask order drifted")
    case = contract.get("case")
    if not isinstance(case, Mapping) or case.get("case_id") != "amb1-case02-nonprofit-scale":
        raise MicrotaskProbeError("Case 02 selection drifted")
    for key in ("source_path", "reviewed_packet_path"):
        path = _repo_path(case.get(key), label=key)
        hash_key = key.replace("_path", "_sha256")
        if not path.is_file() or _file_sha(path) != case.get(hash_key):
            raise MicrotaskProbeError(f"case lock mismatch: {key}")
    catalog = _catalog(contract)
    if catalog.message_count != 14 or catalog.source_sha256 != case.get("source_sha256"):
        raise MicrotaskProbeError("source catalog drifted")
    config = contract.get("call_configuration", {})
    expected = {
        "provider": "openrouter",
        "model": "google/gemini-3.1-flash-lite",
        "provider_projection": "gemini",
        "temperature": 0.0,
        "reasoning": {"enabled": False},
        "require_supported_parameters": True,
        "calls_per_microtask": 1,
        "automatic_retries": 0,
        "evaluator_calls": 0,
        "pipeline_calls": 0,
        "graph_calls": 0,
    }
    for key, value in expected.items():
        if config.get(key) != value:
            raise MicrotaskProbeError(f"call configuration drifted: {key}")
    if not 1 <= int(config.get("max_output_tokens", 0)) <= 5000:
        raise MicrotaskProbeError("output-token cap invalid")
    if not 1 <= float(config.get("provider_timeout_seconds", 0)) <= 120:
        raise MicrotaskProbeError("provider timeout invalid")
    budget = contract.get("call_budget", {})
    if budget.get("maximum_provider_calls") != 3:
        raise MicrotaskProbeError("call ceiling drifted")
    if budget.get("estimated_total_cost_ceiling_usd") != 0.02:
        raise MicrotaskProbeError("cost ceiling drifted")
    if budget.get("pricing_table_version") != PRICES_LAST_VERIFIED:
        raise MicrotaskProbeError("pricing version drifted")
    if lookup_chat_price("openrouter", str(config["model"])) is None:
        raise MicrotaskProbeError("model pricing unavailable")
    if contract.get("prompt_hashes") != expected_prompt_hashes(contract):
        raise MicrotaskProbeError("prompt or schema hashes drifted")
    roles: set[str] = set()
    for lock in contract.get("hash_locks", []):
        if not isinstance(lock, Mapping):
            raise MicrotaskProbeError("artifact lock invalid")
        path = _repo_path(lock.get("path"), label="artifact lock")
        if not path.is_file() or _file_sha(path) != lock.get("sha256"):
            raise MicrotaskProbeError(f"artifact lock mismatch: {lock.get('role')}")
        roles.add(str(lock.get("role")))
    required_roles = {
        "microtask_runner",
        "typed_candidates",
        "candidate_pipeline",
        "state_handoff",
        "pricing",
        "product_constitution",
        "structured_extraction_practices",
        "recovery_contract",
    }
    if not required_roles <= roles:
        raise MicrotaskProbeError("required artifact locks missing")
    if contract.get("stop_rules") != {
        "operational_failure_stops_remaining_calls": True,
        "valid_semantic_failure_is_preserved_and_does_not_trigger_retry": True,
        "hard_stop_before_second_case": True,
    }:
        raise MicrotaskProbeError("stop rules drifted")


def validate_authorization(
    authorization: Mapping[str, Any], *, contract: Mapping[str, Any], contract_path: Path
) -> None:
    if authorization.get("schema_version") != AUTHORIZATION_SCHEMA:
        raise MicrotaskProbeError("unexpected authorization schema")
    if authorization.get("status") != "authorized_once":
        raise MicrotaskProbeError("calls are not authorized")
    if authorization.get("contract_path") != str(contract_path.relative_to(REPO_ROOT)):
        raise MicrotaskProbeError("authorization contract path mismatch")
    if authorization.get("contract_sha256") != _file_sha(contract_path):
        raise MicrotaskProbeError("authorization contract hash mismatch")
    if authorization.get("run_id") != contract.get("run_id"):
        raise MicrotaskProbeError("authorization run mismatch")
    if authorization.get("maximum_provider_calls") != 3:
        raise MicrotaskProbeError("authorization call ceiling mismatch")
    if authorization.get("microtask_order") != list(KINDS):
        raise MicrotaskProbeError("authorization microtask order mismatch")
    if any(
        authorization.get(key) != 0
        for key in ("automatic_retries", "evaluator_calls", "pipeline_calls", "graph_calls")
    ):
        raise MicrotaskProbeError("authorization contains forbidden calls")


def _empty_extractions() -> dict[str, Any]:
    return {
        "positions": PositionExtraction(
            status="not_found", decision_summary=None, positions=()
        ),
        "threads": ThreadExtraction(status="not_found", threads=()),
        "constraints": ConstraintExtraction(status="not_found", constraints=()),
    }


def run_call(contract: Mapping[str, Any], *, kind: str) -> dict[str, Any]:
    validate_contract(contract)
    if kind not in KINDS:
        raise MicrotaskProbeError("unknown microtask")
    started = time.monotonic()
    config = contract["call_configuration"]
    catalog = _catalog(contract)
    micro = build_micro_contract(kind, catalog=catalog, provider="gemini")
    requested_model = str(config["model"])
    base = {
        "schema_version": RESULT_SCHEMA,
        "run_id": contract["run_id"],
        "case_id": contract["case"]["case_id"],
        "kind": kind,
        "call_attempted": True,
        "requested_model": requested_model,
        "provider_projection": "gemini",
        "system_prompt_sha256": micro["system_prompt_sha256"],
        "user_prompt_sha256": micro["user_prompt_sha256"],
        "schema_sha256": micro["schema_sha256"],
        "reasoning_configuration": config["reasoning"],
    }
    api_key = os.getenv("LOLLA_OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return {
            **base,
            "operational_status": "missing_api_key",
            "semantic_status": "not_observed",
            "validation_issues": ["OPENROUTER_API_KEY is missing"],
            "provider_calls": 0,
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    body = {
        "model": requested_model,
        "messages": [
            {"role": "system", "content": micro["system_prompt"]},
            {"role": "user", "content": micro["user_prompt"]},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": f"lolla_{kind}_candidates",
                "strict": True,
                "schema": micro["schema"],
            },
        },
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
        with request.urlopen(
            req, timeout=float(config["provider_timeout_seconds"])
        ) as response:
            provider_payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        try:
            error_payload = json.loads(text)
        except json.JSONDecodeError:
            error_payload = {"message": text[:1000]}
        return {
            **base,
            "operational_status": f"http_error_{exc.code}",
            "semantic_status": "not_observed",
            "validation_issues": [f"provider HTTP error {exc.code}"],
            "provider_diagnostic": _provider_diagnostic(error_payload, []),
            "provider_payload_sha256": _json_sha(error_payload),
            "provider_calls": 1,
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            **base,
            "operational_status": "provider_error",
            "semantic_status": "not_observed",
            "validation_issues": [type(exc).__name__],
            "provider_diagnostic": {"type": type(exc).__name__},
            "provider_calls": 1,
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    choices_raw = provider_payload.get("choices", [])
    choices = choices_raw if isinstance(choices_raw, list) else []
    choice = choices[0] if choices and isinstance(choices[0], Mapping) else {}
    message = choice.get("message", {}) if isinstance(choice, Mapping) else {}
    raw_content = str(message.get("content", "")) if isinstance(message, Mapping) else ""
    parsed = _extract_json_object(raw_content)
    typed, parse_issues = parse_typed(CLASSES[kind], parsed)
    issues = [issue.to_dict() for issue in parse_issues]
    if typed is not None and not parse_issues:
        issues.extend(issue.to_dict() for issue in validate_extraction_state(typed))
    ledger = None
    if typed is not None and not issues:
        extractions = _empty_extractions()
        extractions[kind] = typed
        ledger = build_candidate_ledger(
            case_id=str(contract["case"]["case_id"]),
            catalog=catalog,
            extractions=extractions,
        )
        for row in ledger["candidates"]:
            issues.extend(row["validation_issues"])
    finish_reason = str(choice.get("finish_reason", ""))
    if finish_reason.lower() == "error":
        issues.insert(0, {"code": "provider_finish_error", "path": "/"})
    usage = provider_payload.get("usage", {})
    usage_map = usage if isinstance(usage, Mapping) else {}
    prompt_tokens = usage_map.get("prompt_tokens")
    completion_tokens = usage_map.get("completion_tokens")
    total_tokens = usage_map.get("total_tokens")
    usage_complete = all(
        isinstance(value, int) and value > 0
        for value in (prompt_tokens, completion_tokens, total_tokens)
    )
    served_model = str(provider_payload.get("model", ""))
    attribution = _model_attribution(requested_model, served_model)
    operational_ok = (
        bool(choices)
        and finish_reason.lower() != "error"
        and usage_complete
        and attribution in {"matched", "served_version_alias"}
    )
    price = lookup_chat_price("openrouter", requested_model)
    cost = (
        estimate_chat_cost_usd(
            price=price,
            prompt_tokens=int(prompt_tokens),
            completion_tokens=int(completion_tokens),
        )
        if price is not None and usage_complete
        else None
    )
    semantic_status = "candidate_valid" if not issues else "candidate_quarantined"
    return {
        **base,
        "operational_status": "ok" if operational_ok else "operational_failure",
        "semantic_status": semantic_status if operational_ok else "not_observed",
        "candidate_payload": parsed,
        "candidate_payload_sha256": _json_sha(parsed),
        "candidate_ledger": ledger,
        "validation_issues": issues,
        "served_model": served_model,
        "model_attribution_status": attribution,
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
        "estimated_cost_usd": cost,
        "pricing_table_version": PRICES_LAST_VERIFIED,
        "response_sha256": hashlib.sha256(raw_content.encode("utf-8")).hexdigest(),
        "provider_payload_sha256": _json_sha(provider_payload),
        "provider_diagnostic": _provider_diagnostic(provider_payload, choices),
        "raw_provider_content_included": False,
        "provider_calls": 1,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "evaluator_calls": 0,
        "runtime_modified": False,
        "duration_seconds": round(time.monotonic() - started, 3),
        "non_claims": [
            "valid_shape_and_source_custody_are_not_semantic_correctness",
            "development_case_is_not_independent_gold",
            "microtask_result_is_not_graph_value",
            "microtask_result_is_not_runtime_authority",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--kind", choices=KINDS)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    contract_path = args.contract.resolve()
    contract = _load(contract_path)
    validate_contract(contract)
    if args.dry_run:
        print(
            json.dumps(
                {
                    "status": "dry_run_valid",
                    "run_id": contract["run_id"],
                    "case_id": contract["case"]["case_id"],
                    "microtask_order": list(KINDS),
                    "prompt_hashes": expected_prompt_hashes(contract),
                    "maximum_provider_calls": 3,
                    "automatic_retries": 0,
                    "provider_calls_made_by_dry_run": 0,
                    "graph_calls": 0,
                    "pipeline_calls": 0,
                    "evaluator_calls": 0,
                },
                indent=2,
            )
        )
        return 0
    if args.authorization is None or args.env_file is None or args.kind is None:
        raise MicrotaskProbeError(
            "--authorization, --env-file, and --kind are required for execution"
        )
    authorization = _load(args.authorization)
    validate_authorization(
        authorization, contract=contract, contract_path=contract_path
    )
    _load_env(args.env_file)
    print(json.dumps(run_call(contract, kind=args.kind), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
