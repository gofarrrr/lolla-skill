#!/usr/bin/env python3
"""Seal a failed R3 pressure attempt without making another provider call.

The frozen runner intentionally preserves the provider's exact error payload.
That payload can contain an account identifier, so this closeout validates the
private raw artifact and emits a separately hashed, safe-to-commit redaction
plus a vector result.  It never changes the frozen request contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.r3_fresh_consumer import (  # noqa: E402
    REVIEW_DIMENSIONS,
    value_sha256,
)


REDACTED_ERROR_SCHEMA = "lolla.r3_provider_error_redacted.v1"
FAILURE_CLOSEOUT_SCHEMA = "lolla.r3_fresh_consumer_failure_closeout.v1"
R3_RESULT_SCHEMA = "lolla.r3_fresh_consumer_result.v1"
ALLOWED_FAILURE_STATUSES = {
    "http_error_400_preserved",
    "transport_error_preserved",
}
PRIVATE_KEYS = frozenset(
    {
        "user_id",
        "account_id",
        "organization_id",
        "api_key",
        "authorization",
    }
)


class R3FailureCloseoutError(RuntimeError):
    """Raised when the preserved failure chain is incomplete or inconsistent."""


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R3FailureCloseoutError(f"expected JSON object: {path}")
    return value


def _write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_self_hash(value: Mapping[str, Any], field: str) -> None:
    observed = str(value.get(field, ""))
    unhashed = {key: item for key, item in value.items() if key != field}
    if not observed or observed != value_sha256(unhashed):
        raise R3FailureCloseoutError(f"invalid {field}")


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
                        "replacement": "[redacted-private-identifier]",
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


def _schema_keyword_counts(schema: Any) -> dict[str, int]:
    counts: dict[str, int] = {}

    def visit(value: Any) -> None:
        if isinstance(value, Mapping):
            for key, item in value.items():
                counts[str(key)] = counts.get(str(key), 0) + 1
                visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(schema)
    return dict(sorted(counts.items()))


def build_failure_closeout(
    *,
    call_result: Mapping[str, Any],
    call_started: Mapping[str, Any],
    provider_budget: Mapping[str, Any],
    provider_error_file: Mapping[str, Any],
    provider_error_file_sha256: str,
    bundle: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Validate and seal one preserved R3 request failure provider-free."""

    if call_result.get("status") not in ALLOWED_FAILURE_STATUSES:
        raise R3FailureCloseoutError("call result is not a closeable R3 failure")
    _validate_self_hash(call_result, "call_result_sha256")
    if call_result.get("provider_calls") != 1:
        raise R3FailureCloseoutError("R3 failure must preserve exactly one attempt")
    if call_result.get("source_review_required") is not False:
        raise R3FailureCloseoutError("failed pre-inference call cannot require source review")
    if call_result.get("quiet_control_authorized") is not False:
        raise R3FailureCloseoutError("failed pressure call cannot authorize quiet control")

    custody_fields = (
        "run_id",
        "case_id",
        "contract_sha256",
        "authorization_sha256",
        "bundle_sha256",
        "request_body_sha256",
        "budget_reservation_id",
    )
    for field in custody_fields:
        if call_started.get(field) != call_result.get(field):
            raise R3FailureCloseoutError(f"started/result custody drifted: {field}")
    if (
        call_started.get("status") != "started_before_network_transport"
        or call_started.get("provider_calls") != 1
        or call_started.get("automatic_retries") != 0
        or call_started.get("fallback_models") != 0
        or call_started.get("response_healing") is not False
    ):
        raise R3FailureCloseoutError("started-call policy custody is invalid")

    provider_error = provider_error_file.get("provider_error")
    if not isinstance(provider_error, Mapping):
        raise R3FailureCloseoutError("private provider error is missing")
    if value_sha256(provider_error) != call_result.get("provider_error_sha256"):
        raise R3FailureCloseoutError("private provider error hash drifted")

    reservations = provider_budget.get("reservations")
    reservation = reservations[0] if isinstance(reservations, list) and reservations else {}
    if (
        provider_budget.get("attempted_provider_calls") != 1
        or provider_budget.get("exact_cost_call_count") != 0
        or provider_budget.get("limits", {}).get("maximum_provider_calls") != 1
        or provider_budget.get("limits", {}).get("maximum_accounted_cost_usd") != 0.01
        or reservation.get("reservation_id") != call_result.get("budget_reservation_id")
        or reservation.get("status") != "finalized"
        or reservation.get("exact_cost_usd") is not None
        or reservation.get("accounting_basis")
        != "reserved_worst_case_unknown_charge"
    ):
        raise R3FailureCloseoutError("provider budget does not preserve the failed call")
    accounted_cost = float(provider_budget.get("accounted_cost_usd", -1))
    if not 0 <= accounted_cost <= 0.01:
        raise R3FailureCloseoutError("failed call escaped the one-cent budget")

    if bundle.get("bundle_sha256") != call_result.get("bundle_sha256"):
        raise R3FailureCloseoutError("failure bundle identity drifted")
    schema = bundle.get("response_schema")
    if not isinstance(schema, Mapping):
        raise R3FailureCloseoutError("failure bundle response schema is missing")
    keyword_counts = _schema_keyword_counts(schema)

    redactions: list[dict[str, str]] = []
    sanitized_error = _redact(
        provider_error_file,
        redactions=redactions,
    )
    redacted: dict[str, Any] = {
        "schema_version": REDACTED_ERROR_SCHEMA,
        "status": "safe_to_commit_redaction_of_privately_preserved_raw_error",
        "raw_provider_error_file_sha256": provider_error_file_sha256,
        "raw_provider_error_value_sha256": call_result["provider_error_sha256"],
        "redactions": redactions,
        "provider_error": sanitized_error["provider_error"],
        "raw_error_preserved_outside_git": True,
    }
    redacted["redacted_error_sha256"] = value_sha256(redacted)

    provider_name = (
        provider_error.get("error", {}).get("metadata", {}).get("provider_name", "")
        if isinstance(provider_error.get("error"), Mapping)
        else ""
    )
    dimensions = []
    for dimension in REVIEW_DIMENSIONS:
        if dimension == "exact_cost_and_failure_custody":
            dimensions.append(
                {
                    "dimension": dimension,
                    "verdict": "partial",
                    "why": (
                        "Failure custody, the one-call ceiling, no-retry policy, and "
                        "worst-case budget accounting passed; the provider returned no "
                        "generation identity or exact usage cost."
                    ),
                }
            )
        else:
            dimensions.append(
                {
                    "dimension": dimension,
                    "verdict": "not_evaluable_before_inference",
                    "why": "The provider rejected the request before returning a candidate.",
                }
            )

    closeout: dict[str, Any] = {
        "schema_version": FAILURE_CLOSEOUT_SCHEMA,
        "status": "r3_pressure_request_rejected_before_inference_preserved",
        "case_id": call_result["case_id"],
        "run_id": call_result["run_id"],
        "call_result_sha256": call_result["call_result_sha256"],
        "contract_sha256": call_result["contract_sha256"],
        "authorization_sha256": call_result["authorization_sha256"],
        "bundle_sha256": call_result["bundle_sha256"],
        "request_body_sha256": call_result["request_body_sha256"],
        "provider_error": {
            "http_status": call_result.get("http_status"),
            "provider_name": str(provider_name),
            "provider_error_value_sha256": call_result["provider_error_sha256"],
            "private_raw_file_sha256": provider_error_file_sha256,
            "checked_in_redacted_error_sha256": redacted["redacted_error_sha256"],
            "inference_reached": False,
        },
        "execution_contract_result": {
            "provider_calls_attempted": 1,
            "provider_calls_succeeded": 0,
            "automatic_retries": 0,
            "fallback_models": 0,
            "response_healing": False,
            "quiet_control_authorized": False,
            "quiet_control_calls": 0,
        },
        "cost_result": {
            "exact_provider_cost_status": "unavailable_no_usage_returned",
            "exact_provider_cost_usd": None,
            "conservative_accounted_cost_usd": accounted_cost,
            "accounting_basis": "reserved_worst_case_unknown_charge",
            "within_frozen_total_budget": accounted_cost <= 0.01,
        },
        "source_review": {
            "status": "not_run_candidate_absent",
            "dimensions": dimensions,
            "value_signal": "not_evaluable_candidate_absent",
            "scalar_quality_score": None,
        },
        "diagnosis": {
            "exact_root_cause": "unknown_from_generic_provider_400",
            "established_facts": [
                "OpenRouter routed the request to Google.",
                "Google rejected the request as INVALID_ARGUMENT before inference.",
                "Gemini 3.1 Flash-Lite and strict structured output worked in smaller repository probes.",
                "The frozen R3 schema contains 14 row properties and repeats string length constraints.",
            ],
            "probable_problem_class_not_single_cause": (
                "Google structured-output schema subset or complexity interoperability"
            ),
            "schema_keyword_counts": keyword_counts,
            "current_documentation_observation": (
                "Google documents enum/format for strings, not minLength/maxLength, and "
                "warns that large or deeply constrained schemas may be rejected."
            ),
            "why_not_proven": (
                "The response names no offending field, and prior smaller successful "
                "calls used some of the same constraints."
            ),
        },
        "decision": {
            "r3_semantic_exit_condition_met": False,
            "quiet_control_authorized": False,
            "additional_provider_call_authorized": False,
            "next_boundary": (
                "Return provider-free. Build a smaller documented-subset schema and local "
                "compatibility lint; any new attempt requires a new frozen authorization."
            ),
        },
    }
    closeout["failure_closeout_sha256"] = value_sha256(closeout)

    result: dict[str, Any] = {
        "schema_version": R3_RESULT_SCHEMA,
        "status": "complete_negative_operational_result",
        "case_id": call_result["case_id"],
        "r3_pressure_attempts": 1,
        "r3_pressure_successes": 0,
        "quiet_control_attempts": 0,
        "semantic_result": "not_evaluable_before_inference",
        "custody_result": "failure_preserved",
        "cost_result": "exact_cost_unavailable_worst_case_accounted_within_one_cent",
        "failure_closeout_sha256": closeout["failure_closeout_sha256"],
        "next_call_authorized": False,
    }
    result["r3_result_sha256"] = value_sha256(result)
    return redacted, closeout, result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--call-result", type=Path, required=True)
    parser.add_argument("--call-started", type=Path, required=True)
    parser.add_argument("--provider-budget", type=Path, required=True)
    parser.add_argument("--provider-error", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    provider_error_path = args.provider_error.resolve()
    redacted, closeout, result = build_failure_closeout(
        call_result=_load_object(args.call_result.resolve()),
        call_started=_load_object(args.call_started.resolve()),
        provider_budget=_load_object(args.provider_budget.resolve()),
        provider_error_file=_load_object(provider_error_path),
        provider_error_file_sha256=_file_sha(provider_error_path),
        bundle=_load_object(args.bundle.resolve()),
    )
    output = args.output.resolve()
    _write(output / "provider-error-redacted.json", redacted)
    _write(output / "failure-closeout.json", closeout)
    _write(output / "r3-result.json", result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
