#!/usr/bin/env python3
"""Validate or execute the one frozen R3 collapsed-outcome case call."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib import error, request


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.provider_budget import (  # noqa: E402
    finalize_provider_call,
    reserve_provider_call,
)
from engine.system_b.r3_fresh_consumer import value_sha256  # noqa: E402
from engine.system_b.r3_task_shape_counterfactual import (  # noqa: E402
    compile_collapsed_one_pass_response,
)
from scripts.evals import (  # noqa: E402
    build_r3_collapsed_outcome_case_selection as selection,
)


EXECUTION_CONTRACT_SCHEMA = "lolla.r3_collapsed_outcome_execution_contract.v1"
AUTHORIZATION_SCHEMA = "lolla.r3_collapsed_outcome_authorization.v1"
CALL_RESULT_SCHEMA = "lolla.r3_collapsed_outcome_call_result.v1"
CASE_ID = "v2-case01-anchor-contract"
RUN_ID = "lolla-r3-collapsed-outcome-v2-case01-pressure-r1"
MODEL = "google/gemini-3.1-flash-lite"
MAX_PROVIDER_CALLS = 1
MAX_PROVIDER_COST_USD = 0.01
REVIEW = ROOT / (
    "research/lolla-r3-collapsed-outcome-case-2026-07-13/review/"
    "protected-review-contract.json"
)
PRIVATE_KEYS = frozenset(
    {"user_id", "account_id", "organization_id", "api_key", "authorization"}
)


class R3CollapsedRunError(RuntimeError):
    """Raised before transport when collapsed-outcome custody is invalid."""


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R3CollapsedRunError(f"expected JSON object: {path}")
    return value


def _write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def _load_env_file(path: Path | None) -> None:
    if path is None:
        return
    if not path.is_file():
        raise R3CollapsedRunError(f"env file missing: {path}")
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
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key.strip(), value)


def _result_with_hash(value: dict[str, Any]) -> dict[str, Any]:
    value["call_result_sha256"] = value_sha256(value)
    return value


def _exact_json_object(content: str) -> dict[str, Any]:
    try:
        value = json.loads(content)
    except json.JSONDecodeError as exc:
        raise R3CollapsedRunError("provider content is not exact JSON") from exc
    if not isinstance(value, dict):
        raise R3CollapsedRunError("provider content is not a JSON object")
    return value


def _redact(
    value: Any,
    *,
    path: tuple[str, ...] = (),
    redactions: list[dict[str, str]],
) -> Any:
    if isinstance(value, Mapping):
        result: dict[str, Any] = {}
        for key, item in value.items():
            next_path = (*path, str(key))
            if str(key).lower() in PRIVATE_KEYS:
                result[str(key)] = "[redacted-private-identifier]"
                redactions.append(
                    {
                        "json_pointer": "/" + "/".join(next_path),
                        "reason": "private account or credential field",
                    }
                )
            else:
                result[str(key)] = _redact(
                    item,
                    path=next_path,
                    redactions=redactions,
                )
        return result
    if isinstance(value, list):
        return [
            _redact(item, path=(*path, str(index)), redactions=redactions)
            for index, item in enumerate(value)
        ]
    return value


def _validate_review(review: Mapping[str, Any], runtime: Mapping[str, Any]) -> None:
    if (
        review.get("schema_version")
        != "lolla.r3_collapsed_outcome_protected_review.v1"
        or review.get("status")
        != "frozen_after_source_and_pressure_selection_before_provider_execution"
        or review.get("case_id") != CASE_ID
    ):
        raise R3CollapsedRunError("protected review contract drifted")
    source = review.get("source", {})
    pressure_selection = review.get("pressure_selection", {})
    for item in (source, pressure_selection):
        path = ROOT / str(item.get("path", ""))
        if not path.is_file() or _file_sha(path) != item.get("sha256"):
            raise R3CollapsedRunError("protected review source custody drifted")
    separation = review.get("separation", {})
    if (
        separation.get("supplied_to_provider") is not False
        or separation.get("embedded_in_prompt_or_schema") is not False
        or separation.get("reviewed_only_after_mechanical_pass") is not True
        or separation.get("independent_human_gold") is not False
    ):
        raise R3CollapsedRunError("protected review separation drifted")
    active = runtime["packet"]["constitutional_graph_survival"][
        "active_pressure_items"
    ]
    expected_ids = [item["model_id"] for item in active]
    boundaries = review.get("candidate_review_boundaries")
    if (
        not isinstance(boundaries, list)
        or [item.get("model_id") for item in boundaries] != expected_ids
    ):
        raise R3CollapsedRunError("protected review candidate coverage drifted")
    if len(review.get("protected_opportunities", [])) != 3:
        raise R3CollapsedRunError("protected review opportunity coverage drifted")
    if len(review.get("strengths_to_preserve", [])) != 5:
        raise R3CollapsedRunError("protected review preservation coverage drifted")
    if review.get("review_dimensions") != [
        "source_grounding",
        "disposition_quality",
        "non_forced_graph_contribution",
        "original_advice_preservation",
        "unsupported_claim_leakage",
        "private_over_absorption",
        "public_bloat_and_hedging",
        "exact_cost_and_failure_custody",
    ]:
        raise R3CollapsedRunError("protected review dimensions drifted")
    request_text = json.dumps(runtime["request_body"], ensure_ascii=False).lower()
    protected_markers = (
        "t01_endogenous_customer_base_evidence",
        "t02_duration_and_recommitment_cliff",
        "t03_delegated_commercial_authority",
        "mixed_pressure_opportunity_with_required_restraint",
    )
    if any(marker.lower() in request_text for marker in protected_markers):
        raise R3CollapsedRunError("protected review leaked into provider request")


def validate_execution_contract(
    contract_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    contract = _load_object(contract_path)
    if (
        contract.get("schema_version") != EXECUTION_CONTRACT_SCHEMA
        or contract.get("status") != "frozen_awaiting_founder_authorization"
        or contract.get("case_id") != CASE_ID
        or contract.get("run_id") != RUN_ID
    ):
        raise R3CollapsedRunError("collapsed-outcome execution contract is not frozen")
    for item in contract.get("frozen_inputs", []):
        path = ROOT / str(item.get("path", ""))
        if not path.is_file() or _file_sha(path) != item.get("sha256"):
            raise R3CollapsedRunError(f"frozen input drifted: {item.get('path')}")
    selection.validate(selection.SELECTION.parent)
    artifacts = selection.construct(include_runtime=True)
    bundle = artifacts[selection.BUNDLE_NAME]
    runtime = artifacts["_runtime_material"]
    review = _load_object(REVIEW)
    _validate_review(review, runtime)
    if contract.get("protected_review") != {
        "path": _relative(REVIEW),
        "sha256": _file_sha(REVIEW),
        "supplied_to_provider": False,
        "review_only_after_mechanical_pass": True,
        "not_an_answer_key": True,
        "independent_human_gold": False,
    }:
        raise R3CollapsedRunError("protected review attestation drifted")
    expected_attestation = {
        **bundle["hashes"],
        "bundle_sha256": bundle["bundle_sha256"],
        "packet_sha256": bundle["packet_sha256"],
    }
    if contract.get("request_attestation") != expected_attestation:
        raise R3CollapsedRunError("collapsed request attestation drifted")
    request_contract = runtime["request_contract"]
    if contract.get("operator") != {
        "provider": "openrouter",
        "endpoint": request_contract["endpoint"],
        "model": MODEL,
        "provider_order": ["google-vertex/global"],
        "provider_only": ["google-vertex"],
        "allow_fallbacks": False,
        "require_parameters": True,
        "data_collection": "deny",
        "zdr_claimed": False,
        "wire_mode": "strict_json_schema",
        "reasoning_effort": "low",
        "reasoning_content_excluded": True,
        "seed": 3101,
        "maximum_output_tokens": 4000,
    }:
        raise R3CollapsedRunError("collapsed-outcome operator drifted")
    if contract.get("budget") != {
        "maximum_provider_calls": MAX_PROVIDER_CALLS,
        "maximum_provider_reported_cost_usd": MAX_PROVIDER_COST_USD,
        "maximum_estimated_call_cost_usd": request_contract[
            "maximum_estimated_call_cost_usd"
        ],
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "premium_models": 0,
        "quiet_control_calls": 0,
    }:
        raise R3CollapsedRunError("collapsed-outcome budget drifted")
    decision = contract.get("decision_state", {})
    if (
        decision.get("provider_calls_authorized_now") != 0
        or decision.get("founder_decision") != "pending"
        or decision.get("execution_requires_separate_authorization") is not True
    ):
        raise R3CollapsedRunError("collapsed-outcome decision state drifted")
    return contract, {"bundle": bundle, **runtime}


def validate_authorization(
    *, contract: Mapping[str, Any], contract_path: Path, authorization_path: Path
) -> dict[str, Any]:
    if (
        contract.get("status") != "frozen_awaiting_founder_authorization"
        or contract.get("run_id") != RUN_ID
    ):
        raise R3CollapsedRunError("authorization references an invalid contract")
    authorization = _load_object(authorization_path)
    expected = {
        "schema_version": AUTHORIZATION_SCHEMA,
        "status": "authorized_once_by_founder_for_collapsed_outcome_case",
        "founder_decision": "authorize_one_call",
        "authorization_basis": authorization.get("authorization_basis"),
        "contract_path": _relative(contract_path),
        "contract_sha256": _file_sha(contract_path),
        "authorized_run_id": RUN_ID,
        "authorized_case_id": CASE_ID,
        "maximum_provider_calls": 1,
        "maximum_provider_reported_cost_usd": 0.01,
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "premium_models_authorized": False,
        "quiet_control_authorized": False,
        "model_switch_authorized": False,
        "llm_judge_authorized": False,
    }
    if (
        not isinstance(authorization.get("authorization_basis"), str)
        or not authorization["authorization_basis"].strip()
        or authorization != expected
    ):
        raise R3CollapsedRunError("collapsed-outcome authorization drifted")
    return authorization


def _preserve_provider_error(
    *, private_output: Path, public_output: Path, provider_error: Any
) -> dict[str, Any]:
    private_path = private_output / "provider-error.json"
    _write(private_path, {"provider_error": provider_error})
    redactions: list[dict[str, str]] = []
    redacted_value = _redact(provider_error, redactions=redactions)
    public = {
        "schema_version": "lolla.r3_collapsed_provider_error_redacted.v1",
        "status": "safe_to_commit_redaction_of_privately_preserved_raw_error",
        "raw_provider_error_file_sha256": _file_sha(private_path),
        "raw_provider_error_value_sha256": value_sha256(provider_error),
        "redactions": redactions,
        "provider_error": redacted_value,
        "raw_error_preserved_outside_git": True,
    }
    public["redacted_error_sha256"] = value_sha256(public)
    _write(public_output / "provider-error-redacted.json", public)
    return public


def run_once(
    *,
    contract: Mapping[str, Any],
    material: Mapping[str, Any],
    contract_path: Path,
    authorization_path: Path,
    output: Path,
    private_output: Path,
) -> dict[str, Any]:
    if output.exists() and any(output.iterdir()):
        raise R3CollapsedRunError("public output directory must be empty")
    if private_output.exists() and any(private_output.iterdir()):
        raise R3CollapsedRunError("private output directory must be empty")
    output.mkdir(parents=True, exist_ok=True)
    private_output.mkdir(parents=True, exist_ok=True)
    api_key = os.getenv("LOLLA_OPENROUTER_API_KEY") or os.getenv(
        "OPENROUTER_API_KEY"
    )
    bundle = material["bundle"]
    base = {
        "schema_version": CALL_RESULT_SCHEMA,
        "run_id": RUN_ID,
        "case_id": CASE_ID,
        "contract_path": _relative(contract_path),
        "contract_sha256": _file_sha(contract_path),
        "authorization_path": _relative(authorization_path),
        "authorization_sha256": _file_sha(authorization_path),
        "bundle_sha256": bundle["bundle_sha256"],
        "requested_model": MODEL,
        "request_body_sha256": bundle["hashes"]["request_body_sha256"],
        "maximum_provider_calls": 1,
        "maximum_provider_reported_cost_usd": 0.01,
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "provider_calls": 0,
        "quiet_control_authorized": False,
    }
    if not api_key:
        result = _result_with_hash(
            {
                **base,
                "status": "missing_api_key_no_call",
                "provider_attempted": False,
                "source_review_required": False,
            }
        )
        _write(output / "pressure-call-result.json", result)
        return result

    budget_path = output / "provider-budget.json"
    os.environ["LOLLA_PROVIDER_BUDGET_STATE"] = str(budget_path)
    maximum_estimated = float(
        bundle["request_contract"]["maximum_estimated_call_cost_usd"]
    )
    reservation_id, _ = reserve_provider_call(
        run_id=RUN_ID,
        stage="r3_collapsed_outcome_fresh_consumer_pressure",
        requested_model=MODEL,
        maximum_call_cost_usd=maximum_estimated,
        maximum_calls=1,
        maximum_run_cost_usd=0.01,
    )
    started = {
        **base,
        "status": "started_before_network_transport",
        "provider_attempted": True,
        "provider_calls": 1,
        "budget_reservation_id": reservation_id,
        "started_at_unix": time.time(),
        "request_contract": bundle["request_contract"],
    }
    _write(output / "pressure-call-started.json", started)
    req = request.Request(
        bundle["request_contract"]["endpoint"],
        data=json.dumps(material["request_body"], ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    monotonic_started = time.monotonic()
    try:
        with request.urlopen(req, timeout=90.0) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            provider_error: Any = json.loads(raw)
        except json.JSONDecodeError:
            provider_error = {"message": raw[:6000]}
        redacted = _preserve_provider_error(
            private_output=private_output,
            public_output=output,
            provider_error=provider_error,
        )
        finalize_provider_call(
            run_id=RUN_ID,
            reservation_id=reservation_id,
            status=f"http_error_{exc.code}",
            response_id="",
            exact_cost_usd=None,
            estimated_cost_usd=None,
            maximum_calls=1,
            maximum_run_cost_usd=0.01,
        )
        result = _result_with_hash(
            {
                **base,
                "status": f"http_error_{exc.code}_preserved",
                "provider_attempted": True,
                "provider_calls": 1,
                "budget_reservation_id": reservation_id,
                "http_status": exc.code,
                "provider_error_sha256": value_sha256(provider_error),
                "redacted_error_sha256": redacted["redacted_error_sha256"],
                "duration_seconds": round(time.monotonic() - monotonic_started, 3),
                "source_review_required": False,
            }
        )
        _write(output / "pressure-call-result.json", result)
        return result
    except Exception as exc:  # noqa: BLE001
        finalize_provider_call(
            run_id=RUN_ID,
            reservation_id=reservation_id,
            status="transport_error",
            response_id="",
            exact_cost_usd=None,
            estimated_cost_usd=None,
            maximum_calls=1,
            maximum_run_cost_usd=0.01,
        )
        result = _result_with_hash(
            {
                **base,
                "status": "transport_error_preserved",
                "provider_attempted": True,
                "provider_calls": 1,
                "budget_reservation_id": reservation_id,
                "error_type": type(exc).__name__,
                "error_message": str(exc)[:1500],
                "duration_seconds": round(time.monotonic() - monotonic_started, 3),
                "source_review_required": False,
            }
        )
        _write(output / "pressure-call-result.json", result)
        return result

    if not isinstance(payload, Mapping):
        payload = {"invalid_provider_payload": payload}
    _write(private_output / "provider-payload.json", dict(payload))
    choices = payload.get("choices") if isinstance(payload.get("choices"), list) else []
    choice = choices[0] if choices and isinstance(choices[0], Mapping) else {}
    message = choice.get("message") if isinstance(choice.get("message"), Mapping) else {}
    content = str(message.get("content", ""))
    candidate: dict[str, Any] | None = None
    compiled: dict[str, Any] | None = None
    validation_error = ""
    try:
        candidate = _exact_json_object(content)
        compiled = compile_collapsed_one_pass_response(
            response=candidate,
            packet=material["packet"],
        )
    except Exception as exc:  # noqa: BLE001
        validation_error = f"{type(exc).__name__}: {exc}"
    usage = payload.get("usage") if isinstance(payload.get("usage"), Mapping) else {}
    exact_cost_raw = usage.get("cost")
    try:
        exact_cost = float(exact_cost_raw) if exact_cost_raw is not None else None
    except (TypeError, ValueError):
        exact_cost = None
    try:
        prompt_tokens = int(usage.get("prompt_tokens", 0) or 0)
        completion_tokens = int(usage.get("completion_tokens", 0) or 0)
        estimated_cost = round(
            prompt_tokens * 0.25 / 1_000_000
            + completion_tokens * 1.50 / 1_000_000,
            9,
        )
    except (TypeError, ValueError):
        estimated_cost = None
    response_id = str(payload.get("id", ""))
    served_model = str(payload.get("model", ""))
    served_provider = str(payload.get("provider", ""))
    operator_identity_valid = served_model.startswith(MODEL) and (
        served_provider == "Google"
    )
    reasoning_returned = bool(message.get("reasoning") or message.get("reasoning_details"))
    finalize_provider_call(
        run_id=RUN_ID,
        reservation_id=reservation_id,
        status="ok" if compiled is not None else "local_validation_failed",
        response_id=response_id,
        exact_cost_usd=exact_cost,
        estimated_cost_usd=estimated_cost,
        maximum_calls=1,
        maximum_run_cost_usd=0.01,
    )
    exact_cost_present = exact_cost is not None
    exact_cost_within_budget = exact_cost_present and exact_cost <= 0.01
    mechanical_contract_valid = bool(
        compiled is not None
        and operator_identity_valid
        and not reasoning_returned
        and exact_cost_within_budget
        and response_id
    )
    if compiled is None:
        status = "pressure_response_invalid_preserved"
    elif not operator_identity_valid:
        status = "pressure_response_valid_operator_identity_drifted"
    elif reasoning_returned:
        status = "pressure_response_valid_reasoning_exclusion_breached"
    elif not exact_cost_present:
        status = "pressure_response_valid_exact_cost_missing"
    elif not exact_cost_within_budget:
        status = "pressure_response_valid_cost_contract_breached"
    elif not response_id:
        status = "pressure_response_valid_generation_identity_missing"
    else:
        status = "pressure_response_mechanically_valid_source_review_required"
    result = _result_with_hash(
        {
            **base,
            "status": status,
            "provider_attempted": True,
            "provider_calls": 1,
            "budget_reservation_id": reservation_id,
            "served_model": served_model,
            "served_provider": served_provider,
            "operator_identity_valid": operator_identity_valid,
            "generation_id": response_id,
            "finish_reason": str(choice.get("finish_reason", "")),
            "usage": dict(usage),
            "provider_reported_cost_usd": exact_cost,
            "local_estimated_cost_usd": estimated_cost,
            "exact_cost_present": exact_cost_present,
            "exact_cost_within_budget": exact_cost_within_budget,
            "raw_content": content,
            "raw_content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            "candidate": candidate,
            "compiled": compiled,
            "validation_error": validation_error,
            "provider_payload_sha256": value_sha256(payload),
            "raw_provider_payload_preserved_outside_git": True,
            "reasoning_content_returned": reasoning_returned,
            "mechanical_contract_valid": mechanical_contract_valid,
            "duration_seconds": round(time.monotonic() - monotonic_started, 3),
            "source_review_required": mechanical_contract_valid,
        }
    )
    _write(output / "pressure-call-result.json", result)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--private-output", type=Path)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execute-pressure", action="store_true")
    args = parser.parse_args(argv)
    contract_path = args.contract.resolve()
    contract, material = validate_execution_contract(contract_path)
    if args.dry_run:
        print(
            json.dumps(
                {
                    "status": "collapsed_outcome_contract_valid_not_authorized",
                    "provider_calls": 0,
                    "request_body_sha256": material["bundle"]["hashes"][
                        "request_body_sha256"
                    ],
                    "maximum_estimated_call_cost_usd": material["bundle"]
                    ["request_contract"]["maximum_estimated_call_cost_usd"],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if not args.execute_pressure:
        raise R3CollapsedRunError("network execution requires --execute-pressure")
    if not args.authorization or not args.output or not args.private_output:
        raise R3CollapsedRunError("execution requires authorization and output paths")
    authorization_path = args.authorization.resolve()
    validate_authorization(
        contract=contract,
        contract_path=contract_path,
        authorization_path=authorization_path,
    )
    _load_env_file(args.env_file.resolve() if args.env_file else None)
    result = run_once(
        contract=contract,
        material=material,
        contract_path=contract_path,
        authorization_path=authorization_path,
        output=args.output.resolve(),
        private_output=args.private_output.resolve(),
    )
    print(
        json.dumps(
            {
                key: result.get(key)
                for key in (
                    "status",
                    "provider_calls",
                    "served_model",
                    "served_provider",
                    "provider_reported_cost_usd",
                    "validation_error",
                    "call_result_sha256",
                )
            },
            indent=2,
            sort_keys=True,
        )
    )
    return (
        0
        if result["status"]
        == "pressure_response_mechanically_valid_source_review_required"
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
