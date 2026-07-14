#!/usr/bin/env python3
"""Seal the mechanically invalid repaired R3 response without healing it."""

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

from engine.system_b.r3_fresh_consumer import REVIEW_DIMENSIONS, value_sha256  # noqa: E402
from engine.system_b.r3_google_schema_projection import (  # noqa: E402
    BOUNDARY_TEXT_MAX,
    CHANGE_SUMMARY_MAX,
    EFFECT_TEXT_MAX,
    RECONSIDERED_ANSWER_MAX,
    REQUIRED_ROW_TEXT_MAX,
    ROW_FIELDS,
    compile_projected_pressure_response,
)
from scripts.evals.run_r3_repaired_pressure import (  # noqa: E402
    validate_execution_contract,
)


REDACTED_PAYLOAD_SCHEMA = "lolla.r3_repaired_provider_payload_redacted.v1"
CLOSEOUT_SCHEMA = "lolla.r3_repaired_pressure_failure_closeout.v1"
RESULT_SCHEMA = "lolla.r3_repaired_pressure_terminal_result.v1"


class R3RepairedFailureCloseoutError(RuntimeError):
    """Raised when the repaired call failure chain is inconsistent."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R3RepairedFailureCloseoutError(f"expected JSON object: {path}")
    return value


def _write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _without(value: Mapping[str, Any], *fields: str) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key not in fields}


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _text_length_error(value: Any, *, allow_empty: bool, maximum: int) -> str:
    if not isinstance(value, str):
        return "not_text"
    if not allow_empty and not value.strip():
        return "empty_required_text"
    if len(value) > maximum:
        return "exceeds_local_length_boundary"
    return ""


def collect_mechanical_findings(
    *, candidate: Mapping[str, Any], packet: Mapping[str, Any]
) -> list[dict[str, Any]]:
    """Enumerate explicit contract violations without modifying the candidate."""

    findings: list[dict[str, Any]] = []

    def add(path: str, code: str, observed: Any, expected: str) -> None:
        findings.append(
            {
                "path": path,
                "code": code,
                "observed": observed,
                "expected": expected,
            }
        )

    top_fields = {
        "candidate_dispositions",
        "reconsidered_answer",
        "change_summary",
        "original_answer_preservation",
    }
    if set(candidate) != top_fields:
        add("/", "top_level_shape", sorted(candidate), "exact projected top fields")
    active = packet["constitutional_graph_survival"]["active_pressure_items"]
    rows = candidate.get("candidate_dispositions")
    if not isinstance(rows, list):
        add(
            "/candidate_dispositions",
            "not_array",
            type(rows).__name__,
            f"array of {len(active)} rows",
        )
        rows = []
    elif len(rows) != len(active):
        add(
            "/candidate_dispositions",
            "wrong_row_count",
            len(rows),
            str(len(active)),
        )
    valid_turns = set(packet["source_turn_numbers"])
    effects = {
        "reframe",
        "new_condition",
        "new_alternative",
        "uncertainty_change",
        "reversal_rule",
        "reinforces_existing",
        "no_material_effect",
    }
    dispositions = {"apply", "reject", "park"}
    text_limits = {
        "strongest_plausible_application": (False, REQUIRED_ROW_TEXT_MAX),
        "attempted_application_condition": (False, REQUIRED_ROW_TEXT_MAX),
        "why": (False, REQUIRED_ROW_TEXT_MAX),
        "disposition_boundary": (False, BOUNDARY_TEXT_MAX),
        "visible_effect": (True, EFFECT_TEXT_MAX),
        "private_guardrail": (True, EFFECT_TEXT_MAX),
    }
    for index, expected in enumerate(active):
        if index >= len(rows):
            break
        row = rows[index]
        prefix = f"/candidate_dispositions/{index}"
        if not isinstance(row, Mapping):
            add(prefix, "row_not_object", type(row).__name__, "object")
            continue
        if set(row) != set(ROW_FIELDS):
            add(prefix, "row_shape", sorted(row), "exact projected row fields")
        if row.get("pressure_id") != expected["pressure_id"]:
            add(
                f"{prefix}/pressure_id",
                "pressure_identity_or_order",
                row.get("pressure_id"),
                expected["pressure_id"],
            )
        disposition = row.get("disposition")
        effect = row.get("effect")
        if disposition not in dispositions:
            add(f"{prefix}/disposition", "invalid_disposition", disposition, "apply|reject|park")
        if effect not in effects:
            add(f"{prefix}/effect", "invalid_effect", effect, "allowed effect vocabulary")
        turns = row.get("source_turn_numbers")
        if (
            not isinstance(turns, list)
            or not turns
            or len(turns) > 6
            or any(not isinstance(turn, int) or isinstance(turn, bool) for turn in turns)
            or len(turns) != len(set(turns))
            or (isinstance(turns, list) and set(turns) - valid_turns)
        ):
            add(
                f"{prefix}/source_turn_numbers",
                "invalid_source_turn_custody",
                turns,
                "1-6 unique supplied integer turns",
            )
        for field, (allow_empty, maximum) in text_limits.items():
            code = _text_length_error(
                row.get(field), allow_empty=allow_empty, maximum=maximum
            )
            if code:
                add(
                    f"{prefix}/{field}",
                    code,
                    row.get(field),
                    f"text <= {maximum} chars; allow_empty={allow_empty}",
                )
        visible = row.get("visible_effect")
        private = row.get("private_guardrail")
        boundary = row.get("disposition_boundary")
        if disposition == "apply" and (
            effect == "no_material_effect"
            or not (_nonempty_text(visible) or _nonempty_text(private))
            or not _nonempty_text(boundary)
        ):
            add(
                prefix,
                "apply_contract_violation",
                {"effect": effect, "visible_effect": visible, "private_guardrail": private},
                "material effect, public/private custody, and reopen boundary",
            )
        if disposition == "reject" and (
            effect != "no_material_effect"
            or _nonempty_text(visible)
            or _nonempty_text(private)
            or not _nonempty_text(boundary)
        ):
            add(
                prefix,
                "reject_contract_violation",
                {"effect": effect, "visible_effect": visible, "private_guardrail": private},
                "no material effect, empty effects, and failed condition",
            )
        if disposition == "park" and (
            effect != "no_material_effect"
            or _nonempty_text(visible)
            or _nonempty_text(private)
            or not _nonempty_text(boundary)
        ):
            add(
                prefix,
                "park_contract_violation",
                {"effect": effect, "visible_effect": visible, "private_guardrail": private},
                "no material effect, empty effects, and reopen condition",
            )
    for field, maximum in (
        ("reconsidered_answer", RECONSIDERED_ANSWER_MAX),
        ("change_summary", CHANGE_SUMMARY_MAX),
    ):
        code = _text_length_error(candidate.get(field), allow_empty=False, maximum=maximum)
        if code:
            add(f"/{field}", code, candidate.get(field), f"required text <= {maximum}")
    if candidate.get("original_answer_preservation") not in {
        "preserved",
        "partially_changed",
        "replaced",
    }:
        add(
            "/original_answer_preservation",
            "invalid_preservation_value",
            candidate.get("original_answer_preservation"),
            "preserved|partially_changed|replaced",
        )
    return findings


def _redact_payload(payload: Mapping[str, Any]) -> tuple[dict[str, Any], list[dict[str, str]]]:
    redacted = json.loads(json.dumps(payload))
    redactions: list[dict[str, str]] = []
    choices = redacted.get("choices")
    if isinstance(choices, list):
        for choice_index, choice in enumerate(choices):
            message = choice.get("message") if isinstance(choice, Mapping) else None
            details = message.get("reasoning_details") if isinstance(message, Mapping) else None
            if not isinstance(details, list):
                continue
            for detail_index, detail in enumerate(details):
                if isinstance(detail, dict) and detail.get("signature"):
                    detail["signature"] = "[redacted-opaque-reasoning-signature]"
                    redactions.append(
                        {
                            "json_pointer": (
                                f"/choices/{choice_index}/message/reasoning_details/"
                                f"{detail_index}/signature"
                            ),
                            "reason": "opaque provider reasoning-continuation metadata",
                        }
                    )
    return redacted, redactions


def build_closeout(
    *,
    contract: Mapping[str, Any],
    bundle: Mapping[str, Any],
    call_result: Mapping[str, Any],
    call_started: Mapping[str, Any],
    provider_budget: Mapping[str, Any],
    provider_payload: Mapping[str, Any],
    provider_payload_file_sha256: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if call_result.get("status") != "pressure_response_invalid_preserved":
        raise R3RepairedFailureCloseoutError("call is not the preserved invalid response")
    if call_result.get("call_result_sha256") != value_sha256(
        _without(call_result, "call_result_sha256")
    ):
        raise R3RepairedFailureCloseoutError("call result self-hash is invalid")
    if (
        call_result.get("provider_calls") != 1
        or call_result.get("mechanical_contract_valid") is not False
        or call_result.get("source_review_required") is not False
        or call_result.get("quiet_control_authorized") is not False
    ):
        raise R3RepairedFailureCloseoutError("invalid response gates drifted")
    for field in (
        "run_id",
        "case_id",
        "contract_sha256",
        "authorization_sha256",
        "bundle_sha256",
        "request_body_sha256",
        "budget_reservation_id",
    ):
        if call_started.get(field) != call_result.get(field):
            raise R3RepairedFailureCloseoutError(f"started/result drifted: {field}")
    if call_result.get("bundle_sha256") != bundle["bundle_sha256"]:
        raise R3RepairedFailureCloseoutError("call bundle identity drifted")
    if value_sha256(provider_payload) != call_result.get("provider_payload_sha256"):
        raise R3RepairedFailureCloseoutError("provider payload value hash drifted")
    choices = provider_payload.get("choices")
    choice = choices[0] if isinstance(choices, list) and choices else {}
    message = choice.get("message") if isinstance(choice, Mapping) else {}
    content = str(message.get("content", ""))
    if hashlib.sha256(content.encode("utf-8")).hexdigest() != call_result.get(
        "raw_content_sha256"
    ):
        raise R3RepairedFailureCloseoutError("provider content hash drifted")
    candidate = json.loads(content)
    if candidate != call_result.get("candidate"):
        raise R3RepairedFailureCloseoutError("candidate drifted from exact provider content")
    findings = collect_mechanical_findings(candidate=candidate, packet=bundle["packet"])
    if not findings:
        raise R3RepairedFailureCloseoutError("invalid result has no reproducible finding")
    try:
        compile_projected_pressure_response(response=candidate, packet=bundle["packet"])
    except Exception as exc:  # noqa: BLE001
        reproduced_error = f"{type(exc).__name__}: {exc}"
    else:
        raise R3RepairedFailureCloseoutError("canonical compiler unexpectedly accepted response")
    if reproduced_error != call_result.get("validation_error"):
        raise R3RepairedFailureCloseoutError("compiler failure did not reproduce")
    reservations = provider_budget.get("reservations")
    reservation = reservations[0] if isinstance(reservations, list) and reservations else {}
    exact_cost = call_result.get("provider_reported_cost_usd")
    if (
        provider_budget.get("attempted_provider_calls") != 1
        or provider_budget.get("exact_cost_call_count") != 1
        or provider_budget.get("provider_reported_cost_usd") != exact_cost
        or reservation.get("reservation_id") != call_result.get("budget_reservation_id")
        or reservation.get("exact_cost_usd") != exact_cost
        or reservation.get("accounting_basis") != "provider_reported_exact"
        or not isinstance(exact_cost, (int, float))
        or exact_cost > 0.01
    ):
        raise R3RepairedFailureCloseoutError("exact cost or budget custody drifted")

    redacted_payload_value, redactions = _redact_payload(provider_payload)
    redacted_payload: dict[str, Any] = {
        "schema_version": REDACTED_PAYLOAD_SCHEMA,
        "status": "safe_to_commit_redaction_of_privately_preserved_raw_payload",
        "raw_provider_payload_file_sha256": provider_payload_file_sha256,
        "raw_provider_payload_value_sha256": call_result["provider_payload_sha256"],
        "redactions": redactions,
        "provider_payload": redacted_payload_value,
        "raw_payload_preserved_outside_git": True,
    }
    redacted_payload["redacted_payload_sha256"] = value_sha256(redacted_payload)

    details = message.get("reasoning_details") if isinstance(message, Mapping) else None
    detail_texts = [
        str(item.get("text", ""))
        for item in details or []
        if isinstance(item, Mapping)
    ]
    signature_count = sum(
        1
        for item in details or []
        if isinstance(item, Mapping) and item.get("signature")
    )
    dimensions = [
        {
            "dimension": dimension,
            "verdict": (
                "pass"
                if dimension == "exact_cost_and_failure_custody"
                else "not_evaluable_mechanical_contract_failed"
            ),
            "why": (
                "Exact provider cost, response identity, raw payload hash, candidate, "
                "budget, and failure custody are complete."
                if dimension == "exact_cost_and_failure_custody"
                else "Source-first semantic review was prohibited after mechanical failure."
            ),
        }
        for dimension in REVIEW_DIMENSIONS
    ]
    closeout: dict[str, Any] = {
        "schema_version": CLOSEOUT_SCHEMA,
        "status": "repaired_transport_passed_response_contract_failed_preserved",
        "run_id": call_result["run_id"],
        "case_id": call_result["case_id"],
        "contract_sha256": call_result["contract_sha256"],
        "authorization_sha256": call_result["authorization_sha256"],
        "bundle_sha256": call_result["bundle_sha256"],
        "call_result_sha256": call_result["call_result_sha256"],
        "execution_result": {
            "provider_calls_attempted": 1,
            "provider_calls_succeeded": 1,
            "served_model": call_result.get("served_model"),
            "served_provider": call_result.get("served_provider"),
            "operator_identity_valid": call_result.get("operator_identity_valid"),
            "generation_id": call_result.get("generation_id"),
            "exact_cost_usd": exact_cost,
            "within_one_cent": exact_cost <= 0.01,
            "automatic_retries": 0,
            "fallback_models": 0,
            "response_healing": False,
        },
        "mechanical_result": {
            "schema_transport_accepted": True,
            "strict_json_object_returned": True,
            "canonical_compiler_accepted": False,
            "first_compiler_error": reproduced_error,
            "finding_count": len(findings),
            "findings": findings,
            "candidate_modified_or_healed": False,
        },
        "reasoning_metadata": {
            "runner_conservative_reasoning_details_flag": call_result.get(
                "reasoning_content_returned"
            ),
            "reasoning_text_returned": bool(
                str(message.get("reasoning", "")).strip()
                or any(text.strip() for text in detail_texts)
            ),
            "opaque_signature_count": signature_count,
            "interpretation": (
                "The provider returned opaque reasoning-continuation signature metadata "
                "but no reasoning text. The frozen runner conservatively flagged any "
                "reasoning_details presence; this closeout does not rewrite that result."
            ),
        },
        "source_review": {
            "status": "not_run_mechanical_contract_failed",
            "dimensions": dimensions,
            "scalar_quality_score": None,
            "value_signal": "not_evaluable",
        },
        "privacy_custody": {
            "private_raw_payload_file_sha256": provider_payload_file_sha256,
            "checked_in_redacted_payload_sha256": redacted_payload[
                "redacted_payload_sha256"
            ],
            "opaque_reasoning_signature_redacted_from_git": signature_count > 0,
        },
        "decision": {
            "r3_semantic_exit_condition_met": False,
            "quiet_control_authorized": False,
            "quiet_control_calls": 0,
            "additional_provider_call_authorized": False,
            "r3_status": "closed_after_repaired_attempt_mechanical_failure",
            "next_boundary": (
                "No retry or model shopping. Reassess the final-consumer task shape "
                "provider-free before deciding whether R3 should be redesigned, deferred, "
                "or stopped."
            ),
        },
    }
    closeout["closeout_sha256"] = value_sha256(closeout)
    terminal: dict[str, Any] = {
        "schema_version": RESULT_SCHEMA,
        "status": "r3_closed_repaired_transport_pass_mechanical_response_fail",
        "case_id": call_result["case_id"],
        "repaired_pressure_calls": 1,
        "repaired_pressure_cost_usd": exact_cost,
        "quiet_control_calls": 0,
        "semantic_result": "not_evaluable_mechanical_contract_failed",
        "transport_result": "repaired_schema_accepted",
        "custody_result": "complete",
        "closeout_sha256": closeout["closeout_sha256"],
        "next_call_authorized": False,
    }
    terminal["result_sha256"] = value_sha256(terminal)
    return redacted_payload, closeout, terminal


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--call-result", type=Path, required=True)
    parser.add_argument("--call-started", type=Path, required=True)
    parser.add_argument("--provider-budget", type=Path, required=True)
    parser.add_argument("--provider-payload", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    contract, bundle = validate_execution_contract(
        contract_path=args.contract.resolve(),
        authorization_path=args.authorization.resolve(),
    )
    payload_path = args.provider_payload.resolve()
    redacted, closeout, terminal = build_closeout(
        contract=contract,
        bundle=bundle,
        call_result=_load(args.call_result.resolve()),
        call_started=_load(args.call_started.resolve()),
        provider_budget=_load(args.provider_budget.resolve()),
        provider_payload=_load(payload_path),
        provider_payload_file_sha256=_file_sha(payload_path),
    )
    output = args.output.resolve()
    _write(output / "provider-payload-redacted.json", redacted)
    _write(output / "failure-closeout.json", closeout)
    _write(output / "r3-terminal-result.json", terminal)
    print(json.dumps(terminal, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
