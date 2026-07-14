#!/usr/bin/env python3
"""Run the frozen matched R4 v2 experiment only after exact founder authorization."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib import error, request

from engine.system_b.r4_complementary_readers import (
    canonical_json_bytes,
    compile_uncertainty_response_v1,
    planned_readers_v1,
    uncertainty_response_schema_v1,
    value_sha256,
)
from engine.system_b.r4_residual_task import (
    compile_residual_response_v1,
    residual_response_schema_v1,
)
from engine.system_b.r4_semantic_distinction import inspect_r4_reasoning_exclusion_v1


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTRACT = ROOT / "docs/evals/lolla-r4-matched-holdout-v2-contract.json"
CONTRACT_SCHEMA = "lolla.r4_matched_residual_holdout_contract.v2"
AUTH_SCHEMA = "lolla.r4_matched_residual_holdout_authorization.v2"


class R4MatchedHoldoutV2RunError(RuntimeError):
    """Raised when frozen execution, authorization, or custody drifts."""


class R4ProviderTransportError(RuntimeError):
    """Carry exact terminal HTTP bytes across the injected transport boundary."""

    def __init__(
        self,
        message: str,
        *,
        raw_response: bytes | None = None,
        http_status: int | None = None,
    ) -> None:
        super().__init__(message)
        self.raw_response = raw_response
        self.http_status = http_status


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R4MatchedHoldoutV2RunError(f"expected JSON object: {path}")
    return value


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def validate_contract(path: Path = DEFAULT_CONTRACT) -> dict[str, Any]:
    """Validate only immutable execution-visible inputs."""

    path = path.resolve()
    if path != DEFAULT_CONTRACT.resolve():
        raise R4MatchedHoldoutV2RunError("only the frozen default contract is runnable")
    contract = _load(path)
    if (
        contract.get("schema_version") != CONTRACT_SCHEMA
        or contract.get("status")
        != "provider_free_matched_holdout_v2_frozen_no_authorization"
        or contract.get("run_id") != "lolla-r4-matched-residual-holdout-v2"
    ):
        raise R4MatchedHoldoutV2RunError("matched holdout contract drifted")
    boundary = contract.get("decision_boundary", {})
    if (
        boundary.get("provider_calls_authorized") is not False
        or boundary.get("authorization_file_present") is not False
        or boundary.get("package_grants_authorization") is not False
        or boundary.get("package_requests_authorization") is not False
    ):
        raise R4MatchedHoldoutV2RunError("decision boundary drifted")
    budget = contract.get("budget", {})
    expected_budget = {
        "maximum_provider_calls": 8,
        "hard_provider_reported_cost_per_case_usd": 0.03,
        "hard_provider_reported_cost_total_usd": 0.12,
        "automatic_retries": 0,
        "semantic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "relationship_calls": 0,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
    }
    if any(budget.get(key) != value for key, value in expected_budget.items()):
        raise R4MatchedHoldoutV2RunError("execution budget drifted")
    if contract.get("operator") != {
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "model": "google/gemini-3.1-flash-lite",
        "allowed_served_model_ids": [
            "google/gemini-3.1-flash-lite",
            "google/gemini-3.1-flash-lite-20260507",
        ],
        "provider_slug": "google-vertex",
        "allowed_served_provider_names": ["Google"],
        "provider_order": ["google-vertex"],
        "provider_only": ["google-vertex"],
        "allow_fallbacks": False,
        "require_parameters": True,
        "data_collection": "deny",
        "zdr": True,
        "maximum_price_usd_per_million_tokens": {
            "prompt": 0.25,
            "completion": 1.5,
        },
        "seed_policy": "one fixed seed per case, byte-identical between arms",
        "maximum_output_tokens": 1600,
        "reasoning": {"effort": "minimal", "exclude": True},
        "stream": False,
        "strict_json_schema": True,
    }:
        raise R4MatchedHoldoutV2RunError("operator boundary drifted")
    call_plan = contract.get("call_plan")
    if (
        not isinstance(call_plan, list)
        or len(call_plan) != 8
        or [row.get("ordinal") for row in call_plan] != list(range(1, 9))
        or sum(row.get("arm", "").startswith("A_") for row in call_plan) != 4
        or sum(row.get("arm", "").startswith("B_") for row in call_plan) != 4
    ):
        raise R4MatchedHoldoutV2RunError("eight-call plan drifted")
    execution = contract.get("execution_envelope", {})
    manifest_path = ROOT / str(execution.get("execution_manifest_path", ""))
    if (
        not manifest_path.is_file()
        or _file_sha(manifest_path) != execution.get("execution_manifest_sha256")
    ):
        raise R4MatchedHoldoutV2RunError("execution manifest drifted")
    manifest = _load(manifest_path)
    if (
        manifest.get("status") != "frozen_runner_visible_inputs_no_authorization"
        or manifest.get("protected_review_reference_present") is not False
    ):
        raise R4MatchedHoldoutV2RunError("execution-visible boundary drifted")
    for row in manifest.get("files", []):
        artifact = ROOT / row["path"]
        if (
            not artifact.is_file()
            or _file_sha(artifact) != row.get("sha256")
            or len(artifact.read_bytes()) != row.get("utf8_bytes")
        ):
            raise R4MatchedHoldoutV2RunError(
                f"execution artifact drifted: {row['path']}"
            )
    for case in contract.get("cases", []):
        for prefix in ("source", "prior"):
            artifact = ROOT / case[f"{prefix}_path"]
            if (
                not artifact.is_file()
                or _file_sha(artifact) != case[f"{prefix}_sha256"]
            ):
                raise R4MatchedHoldoutV2RunError(
                    f"{prefix} artifact drifted: {case.get('case_id')}"
                )
    history = contract.get("frozen_history", {})
    current = {
        "v1_module_sha256": _file_sha(
            ROOT / "engine/system_b/r4_complementary_readers.py"
        ),
        "v2_module_sha256": _file_sha(
            ROOT / "engine/system_b/r4_semantic_distinction.py"
        ),
        "residual_module_sha256": _file_sha(
            ROOT / "engine/system_b/r4_residual_task.py"
        ),
        "v2_schema_sha256": value_sha256(uncertainty_response_schema_v1()),
        "residual_schema_sha256": value_sha256(residual_response_schema_v1()),
    }
    if any(history.get(key) != value for key, value in current.items()):
        raise R4MatchedHoldoutV2RunError("historical prompt or schema drifted")
    frozen_runner = contract.get("future_runner", {})
    if (
        frozen_runner.get("path") != _relative(Path(__file__))
        or frozen_runner.get("sha256") != _file_sha(Path(__file__))
        or frozen_runner.get("network_transport_created_only_after_authorization")
        is not True
    ):
        raise R4MatchedHoldoutV2RunError("future runner drifted")
    for row in call_plan:
        preview = _load(ROOT / row["request_preview_path"])
        if preview.get("body_sha256") != row.get("request_body_sha256"):
            raise R4MatchedHoldoutV2RunError("request preview drifted")
    return contract


def expected_authorization(*, contract: Mapping[str, Any]) -> dict[str, Any]:
    """Return the exact object a separate founder action would have to match."""

    return {
        "schema_version": AUTH_SCHEMA,
        "status": "authorized_once_after_founder_review",
        "contract_path": _relative(DEFAULT_CONTRACT),
        "contract_sha256": _file_sha(DEFAULT_CONTRACT),
        "run_id": contract["run_id"],
        "authorized_call_plan": [
            {
                "ordinal": row["ordinal"],
                "case_id": row["case_id"],
                "arm": row["arm"],
                "request_body_sha256": row["request_body_sha256"],
            }
            for row in contract["call_plan"]
        ],
        "maximum_provider_calls": 8,
        "hard_provider_reported_cost_per_case_usd": 0.03,
        "hard_provider_reported_cost_total_usd": 0.12,
        "automatic_retries": 0,
        "semantic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "relationship_calls": 0,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
    }


def validate_authorization(
    authorization_path: Path, *, contract: Mapping[str, Any]
) -> None:
    if _load(authorization_path.resolve()) != expected_authorization(
        contract=contract
    ):
        raise R4MatchedHoldoutV2RunError("authorization drifted")


def _render(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _write(path: Path, value: Any) -> bytes:
    raw = _render(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return raw


def _load_env(path: Path) -> None:
    if not path.is_file():
        raise R4MatchedHoldoutV2RunError("environment file does not exist")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key.strip(), value)


def _openrouter_transport(*, endpoint: str) -> Callable[[dict[str, Any]], bytes]:
    """Create the one-attempt HTTP boundary after exact authorization."""

    api_key = os.getenv("LOLLA_OPENROUTER_API_KEY") or os.getenv(
        "OPENROUTER_API_KEY"
    )
    if not api_key:
        raise R4MatchedHoldoutV2RunError("OpenRouter API key is absent")

    def send(body: dict[str, Any]) -> bytes:
        provider_request = request.Request(
            endpoint,
            data=canonical_json_bytes(body),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(provider_request, timeout=180) as response:
                return response.read()
        except error.HTTPError as exc:
            raw_response = exc.read()
            raise R4ProviderTransportError(
                f"HTTP {exc.code}",
                raw_response=raw_response,
                http_status=exc.code,
            ) from exc

    return send


def _terminal_failure(
    *,
    ordinal: int,
    case_id: str,
    arm: str,
    request_body_sha256: str,
    status: str,
    provider_calls: int,
    detail: str,
) -> dict[str, Any]:
    return {
        "ordinal": ordinal,
        "case_id": case_id,
        "arm": arm,
        "operational_status": status,
        "provider_calls": provider_calls,
        "request_body_sha256": request_body_sha256,
        "failure_detail": detail[:1000],
        "terminal": True,
    }


def execute(
    *,
    contract: Mapping[str, Any],
    authorization_path: Path,
    output: Path,
    transport: Callable[[dict[str, Any]], bytes],
) -> dict[str, Any]:
    """Execute once in fixed order through an injected provider boundary."""

    frozen = validate_contract()
    if dict(contract) != frozen:
        raise R4MatchedHoldoutV2RunError("in-memory contract drifted")
    validate_authorization(authorization_path, contract=frozen)
    output = output.resolve()
    if output.exists():
        raise R4MatchedHoldoutV2RunError("execution output path already exists")
    output.mkdir(parents=True)
    case_by_id = {row["case_id"]: row for row in frozen["cases"]}
    provider_calls = 0
    total_cost = 0.0
    case_costs = {case_id: 0.0 for case_id in case_by_id}
    call_results: list[dict[str, Any]] = []

    for plan in frozen["call_plan"]:
        ordinal = int(plan["ordinal"])
        case_id = str(plan["case_id"])
        arm = str(plan["arm"])
        preview = _load(ROOT / plan["request_preview_path"])
        body = preview["body"]
        request_raw = canonical_json_bytes(body)
        request_sha = hashlib.sha256(request_raw).hexdigest()
        if request_sha != plan["request_body_sha256"]:
            raise R4MatchedHoldoutV2RunError("request body changed after validation")
        if provider_calls >= frozen["budget"]["maximum_provider_calls"]:
            failure = _terminal_failure(
                ordinal=ordinal,
                case_id=case_id,
                arm=arm,
                request_body_sha256=request_sha,
                status="call_ceiling_preflight_failed",
                provider_calls=0,
                detail="eight-call maximum reached before transport",
            )
            call_results.append(failure)
            _write(output / f"call-{ordinal:02d}-result.json", failure)
            break
        _write(
            output / f"call-{ordinal:02d}-started.json",
            {
                "status": "started_before_transport",
                "ordinal": ordinal,
                "case_id": case_id,
                "arm": arm,
                "request_body_sha256": request_sha,
                "provider_calls_before": provider_calls,
                "automatic_retries": 0,
                "semantic_retries": 0,
                "fallback_models": 0,
                "response_healing": False,
            },
        )
        try:
            raw_response = transport(body)
            provider_calls += 1
            if not isinstance(raw_response, bytes):
                raise TypeError("transport must return exact response bytes")
        except Exception as exc:  # noqa: BLE001
            if not isinstance(exc, TypeError) or "exact response bytes" not in str(exc):
                provider_calls += 1
            failure = _terminal_failure(
                ordinal=ordinal,
                case_id=case_id,
                arm=arm,
                request_body_sha256=request_sha,
                status="transport_failure",
                provider_calls=1,
                detail=f"{type(exc).__name__}: {exc}",
            )
            terminal_raw = getattr(exc, "raw_response", None)
            if isinstance(terminal_raw, bytes):
                raw_path = output / f"call-{ordinal:02d}-raw-response.bin"
                raw_path.write_bytes(terminal_raw)
                failure.update(
                    {
                        "raw_response_path": raw_path.name,
                        "raw_response_sha256": hashlib.sha256(
                            terminal_raw
                        ).hexdigest(),
                        "raw_response_utf8_bytes": len(terminal_raw),
                        "first_terminal_provider_result_preserved_exactly": True,
                    }
                )
            http_status = getattr(exc, "http_status", None)
            if isinstance(http_status, int):
                failure["http_status"] = http_status
            call_results.append(failure)
            _write(output / f"call-{ordinal:02d}-result.json", failure)
            break

        raw_path = output / f"call-{ordinal:02d}-raw-response.bin"
        raw_path.write_bytes(raw_response)
        base = {
            "ordinal": ordinal,
            "case_id": case_id,
            "arm": arm,
            "provider_calls": 1,
            "request_body_sha256": request_sha,
            "raw_response_path": raw_path.name,
            "raw_response_sha256": hashlib.sha256(raw_response).hexdigest(),
            "raw_response_utf8_bytes": len(raw_response),
            "first_terminal_provider_result_preserved_exactly": True,
        }
        try:
            payload = json.loads(raw_response.decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("provider payload must be an object")
        except Exception as exc:  # noqa: BLE001
            failure = {
                **base,
                "operational_status": "provider_payload_parse_failure",
                "failure_detail": f"{type(exc).__name__}: {exc}"[:1000],
                "terminal": True,
            }
            call_results.append(failure)
            _write(output / f"call-{ordinal:02d}-result.json", failure)
            break

        choices = payload.get("choices")
        choice = choices[0] if isinstance(choices, list) and choices else {}
        message = choice.get("message") if isinstance(choice, Mapping) else {}
        if not isinstance(message, Mapping):
            message = {}
        served_model = str(payload.get("model", ""))
        served_provider = str(payload.get("provider", ""))
        generation_id = str(payload.get("id", ""))
        attribution_ok = (
            served_model in frozen["operator"]["allowed_served_model_ids"]
            and served_provider
            in frozen["operator"]["allowed_served_provider_names"]
            and bool(generation_id)
        )
        usage = payload.get("usage")
        if not isinstance(usage, Mapping):
            usage = {}
        reported_cost = usage.get("cost")
        token_usage_ok = all(
            isinstance(usage.get(field), int)
            and not isinstance(usage.get(field), bool)
            and usage[field] >= 0
            for field in ("prompt_tokens", "completion_tokens", "total_tokens")
        )
        cost_ok = (
            token_usage_ok
            and isinstance(reported_cost, (int, float))
            and not isinstance(reported_cost, bool)
            and float(reported_cost) >= 0
        )
        custody = inspect_r4_reasoning_exclusion_v1(message)
        content = message.get("content", "")
        finish_reason = (
            str(choice.get("finish_reason", ""))
            if isinstance(choice, Mapping)
            else ""
        )
        operational_status = "candidate_ready_for_admission"
        failure_detail = ""
        candidate: dict[str, Any] | None = None
        compiled: dict[str, Any] | None = None
        if not attribution_ok:
            operational_status = "operator_attribution_failure"
            failure_detail = "served model, provider, or generation identity did not match"
        elif not cost_ok:
            operational_status = "budget_custody_failure"
            failure_detail = "provider-reported cost is absent or invalid"
        elif not custody["exclusion_satisfied"]:
            operational_status = "reasoning_custody_failure"
            failure_detail = custody["status"]
        elif finish_reason != "stop":
            operational_status = "provider_terminal_status_failure"
            failure_detail = f"finish_reason={finish_reason}"
        elif not isinstance(content, str):
            operational_status = "candidate_parse_failure"
            failure_detail = "provider message content is not text"
        else:
            try:
                parsed = json.loads(content)
                if not isinstance(parsed, dict):
                    raise ValueError("candidate must be a JSON object")
                candidate = parsed
            except Exception as exc:  # noqa: BLE001
                operational_status = "candidate_parse_failure"
                failure_detail = f"{type(exc).__name__}: {exc}"

        if operational_status == "candidate_ready_for_admission" and candidate is not None:
            case = case_by_id[case_id]
            packet = _load(ROOT / case["packet_path"])
            registry = _load(ROOT / case["source_registry_path"])
            readers = planned_readers_v1(
                case_id=case_id,
                existing_producer_id="frozen-fallible-prior-context",
                complementary_producer_id=frozen["operator"]["model"],
            )
            candidate_raw = canonical_json_bytes(candidate)
            try:
                if arm.startswith("A_"):
                    compiled = compile_uncertainty_response_v1(
                        response=candidate,
                        packet=packet,
                        source_registry=registry,
                        planned_readers=readers,
                        artifact_path=f"call-{ordinal:02d}-candidate.json",
                        artifact_bytes=candidate_raw,
                    )
                elif arm.startswith("B_"):
                    compiled = compile_residual_response_v1(
                        response=candidate,
                        packet=packet,
                        source_registry=registry,
                        planned_readers=readers,
                        artifact_path=f"call-{ordinal:02d}-candidate.json",
                        artifact_bytes=candidate_raw,
                    )
                else:
                    raise R4MatchedHoldoutV2RunError("undeclared arm")
                operational_status = "completed"
            except Exception as exc:  # noqa: BLE001
                operational_status = "schema_or_local_admission_failure"
                failure_detail = f"{type(exc).__name__}: {exc}"

        if cost_ok:
            call_cost = float(reported_cost)
            total_cost = round(total_cost + call_cost, 12)
            case_costs[case_id] = round(case_costs[case_id] + call_cost, 12)
            if (
                case_costs[case_id]
                > frozen["budget"]["hard_provider_reported_cost_per_case_usd"]
                or total_cost
                > frozen["budget"]["hard_provider_reported_cost_total_usd"]
            ):
                operational_status = "provider_reported_budget_failure"
                failure_detail = "provider-reported hard cost ceiling exceeded"

        call_result = {
            **base,
            "operational_status": operational_status,
            "served_model": served_model,
            "served_provider": served_provider,
            "generation_id": generation_id,
            "operator_attribution_ok": attribution_ok,
            "finish_reason": finish_reason,
            "usage": dict(usage),
            "usage_sha256": value_sha256(dict(usage)),
            "provider_reported_cost_usd": reported_cost,
            "reasoning_custody": custody,
            "reasoning_values_copied_to_result": False,
            "candidate_sha256": (
                value_sha256(candidate) if candidate is not None else None
            ),
            "local_admission_status": "passed" if compiled is not None else "failed",
            "compiled": compiled,
            "failure_detail": failure_detail[:1000],
            "terminal": True,
        }
        call_results.append(call_result)
        _write(output / f"call-{ordinal:02d}-result.json", call_result)
        if operational_status != "completed":
            break

    complete = len(call_results) == 8 and all(
        row["operational_status"] == "completed" for row in call_results
    )
    result = {
        "schema_version": "lolla.r4_matched_residual_execution_result.v2",
        "status": "matched_execution_complete" if complete else "stopped_on_first_failure",
        "run_id": frozen["run_id"],
        "provider_calls": provider_calls,
        "provider_reported_cost_usd": total_cost,
        "case_costs_usd": case_costs,
        "call_ordinals": [row["ordinal"] for row in call_results],
        "calls": call_results,
        "maximum_provider_calls": 8,
        "automatic_retries": 0,
        "semantic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "relationship_calls": 0,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
        "first_failure_stopped_further_transport": not complete,
    }
    _write(output / "result.json", result)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    contract = validate_contract(args.contract.resolve())
    if args.dry_run:
        print(
            json.dumps(
                {
                    "status": "frozen_matched_residual_v2_contract_valid",
                    "provider_calls": 0,
                    "provider_cost_usd": 0.0,
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
        raise R4MatchedHoldoutV2RunError(
            "execution requires separate exact authorization, env, and output"
        )
    validate_authorization(args.authorization.resolve(), contract=contract)
    _load_env(args.env_file.resolve())
    transport = _openrouter_transport(endpoint=contract["operator"]["endpoint"])
    result = execute(
        contract=contract,
        authorization_path=args.authorization.resolve(),
        output=args.output.resolve(),
        transport=transport,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "matched_execution_complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
