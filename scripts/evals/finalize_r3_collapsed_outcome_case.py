#!/usr/bin/env python3
"""Seal the single R3 collapsed-outcome result without semantic review."""

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

from engine.system_b.r3_fresh_consumer import value_sha256  # noqa: E402
from engine.system_b.r3_task_shape_counterfactual import (  # noqa: E402
    compile_collapsed_one_pass_response,
)
from scripts.evals.finalize_r3_repaired_pressure_failure import (  # noqa: E402
    _redact_payload,
)
from scripts.evals.run_r3_collapsed_outcome_case import (  # noqa: E402
    MODEL,
    validate_authorization,
    validate_execution_contract,
)


CONTRACT = ROOT / (
    "docs/evals/lolla-r3-collapsed-outcome-case-execution-contract-v1.json"
)
AUTHORIZATION = ROOT / (
    "docs/evals/lolla-r3-collapsed-outcome-case-authorization-v1.json"
)
RESULT_DIR = ROOT / (
    "research/lolla-r3-collapsed-outcome-case-2026-07-13/pressure-r1"
)
CALL_RESULT = RESULT_DIR / "pressure-call-result.json"
CALL_STARTED = RESULT_DIR / "pressure-call-started.json"
PROVIDER_BUDGET = RESULT_DIR / "provider-budget.json"
REDACTED_PAYLOAD = RESULT_DIR / "provider-payload-redacted.json"
CLOSEOUT = RESULT_DIR / "failure-closeout.json"
TERMINAL_RESULT = RESULT_DIR / "r3-terminal-result.json"

REDACTED_PAYLOAD_SCHEMA = "lolla.r3_collapsed_provider_payload_redacted.v1"
CLOSEOUT_SCHEMA = "lolla.r3_collapsed_outcome_failure_closeout.v1"
TERMINAL_SCHEMA = "lolla.r3_collapsed_outcome_terminal_result.v1"
SEMANTIC_DIMENSIONS = [
    "source_grounding",
    "disposition_quality",
    "non_forced_graph_contribution",
    "original_advice_preservation",
    "unsupported_claim_leakage",
    "private_over_absorption",
    "public_bloat_and_hedging",
]


class R3CollapsedCloseoutError(RuntimeError):
    """Raised when the one-call evidence chain is inconsistent."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R3CollapsedCloseoutError(f"expected JSON object: {path}")
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


def _reasoning_observation(payload: Mapping[str, Any]) -> dict[str, Any]:
    choices = payload.get("choices")
    choice = choices[0] if isinstance(choices, list) and choices else {}
    message = choice.get("message") if isinstance(choice, Mapping) else {}
    if not isinstance(message, Mapping):
        raise R3CollapsedCloseoutError("provider message is missing")
    details = message.get("reasoning_details")
    if not isinstance(details, list) or len(details) != 1:
        raise R3CollapsedCloseoutError("unexpected reasoning detail shape")
    detail = details[0]
    if not isinstance(detail, Mapping):
        raise R3CollapsedCloseoutError("reasoning detail must be an object")
    expected_keys = {"format", "index", "signature", "type"}
    if (
        set(detail) != expected_keys
        or detail.get("type") != "reasoning.text"
        or detail.get("format") != "google-gemini-v1"
        or not detail.get("signature")
    ):
        raise R3CollapsedCloseoutError("reasoning signature metadata drifted")
    plaintext = message.get("reasoning")
    return {
        "message_reasoning_field_present": "reasoning" in message,
        "message_reasoning_text_nonempty": bool(
            isinstance(plaintext, str) and plaintext.strip()
        ),
        "reasoning_details_count": 1,
        "detail_type": detail["type"],
        "detail_format": detail["format"],
        "detail_keys": sorted(detail),
        "detail_text_field_present": "text" in detail,
        "detail_summary_field_present": "summary" in detail,
        "detail_data_field_present": "data" in detail,
        "detail_signature_present": True,
        "returned_plaintext_or_summary_reasoning": False,
        "returned_signature_only_metadata": True,
    }


def _validate_evidence(
    *, private_payload: Mapping[str, Any] | None
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    contract, material = validate_execution_contract(CONTRACT)
    validate_authorization(
        contract=contract,
        contract_path=CONTRACT,
        authorization_path=AUTHORIZATION,
    )
    call_result = _load(CALL_RESULT)
    call_started = _load(CALL_STARTED)
    provider_budget = _load(PROVIDER_BUDGET)
    if call_result.get("call_result_sha256") != value_sha256(
        _without(call_result, "call_result_sha256")
    ):
        raise R3CollapsedCloseoutError("call result self-hash drifted")
    if (
        call_result.get("status")
        != "pressure_response_valid_reasoning_exclusion_breached"
        or call_result.get("provider_calls") != 1
        or call_result.get("served_model") != MODEL
        or call_result.get("served_provider") != "Google"
        or call_result.get("operator_identity_valid") is not True
        or call_result.get("mechanical_contract_valid") is not False
        or call_result.get("source_review_required") is not False
        or call_result.get("reasoning_content_returned") is not True
        or call_result.get("quiet_control_authorized") is not False
        or call_result.get("validation_error") != ""
    ):
        raise R3CollapsedCloseoutError("frozen failure status drifted")
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
            raise R3CollapsedCloseoutError(f"started/result drifted: {field}")
    if call_result.get("contract_sha256") != _file_sha(CONTRACT):
        raise R3CollapsedCloseoutError("execution contract hash drifted")
    if call_result.get("authorization_sha256") != _file_sha(AUTHORIZATION):
        raise R3CollapsedCloseoutError("authorization hash drifted")
    bundle = material["bundle"]
    if (
        call_result.get("bundle_sha256") != bundle["bundle_sha256"]
        or call_result.get("request_body_sha256")
        != bundle["hashes"]["request_body_sha256"]
    ):
        raise R3CollapsedCloseoutError("request or bundle custody drifted")
    candidate = call_result.get("candidate")
    compiled = call_result.get("compiled")
    if not isinstance(candidate, Mapping) or not isinstance(compiled, Mapping):
        raise R3CollapsedCloseoutError("compiled provider candidate is missing")
    reproduced = compile_collapsed_one_pass_response(
        response=candidate,
        packet=material["packet"],
    )
    if reproduced != compiled:
        raise R3CollapsedCloseoutError("collapsed compiler result drifted")
    if (
        compiled.get("all_active_candidates_accounted_for") is not True
        or len(compiled.get("candidate_dispositions", [])) != 9
    ):
        raise R3CollapsedCloseoutError("nine-pressure compilation drifted")
    reservations = provider_budget.get("reservations")
    reservation = (
        reservations[0] if isinstance(reservations, list) and reservations else {}
    )
    exact_cost = call_result.get("provider_reported_cost_usd")
    if (
        provider_budget.get("attempted_provider_calls") != 1
        or provider_budget.get("exact_cost_call_count") != 1
        or provider_budget.get("provider_reported_cost_usd") != exact_cost
        or reservation.get("reservation_id")
        != call_result.get("budget_reservation_id")
        or reservation.get("exact_cost_usd") != exact_cost
        or reservation.get("accounting_basis") != "provider_reported_exact"
        or not isinstance(exact_cost, (int, float))
        or exact_cost > 0.01
    ):
        raise R3CollapsedCloseoutError("provider budget custody drifted")
    if private_payload is not None:
        if value_sha256(private_payload) != call_result.get("provider_payload_sha256"):
            raise R3CollapsedCloseoutError("private provider payload hash drifted")
        choices = private_payload.get("choices")
        choice = choices[0] if isinstance(choices, list) and choices else {}
        message = choice.get("message") if isinstance(choice, Mapping) else {}
        content = str(message.get("content", ""))
        if hashlib.sha256(content.encode("utf-8")).hexdigest() != call_result.get(
            "raw_content_sha256"
        ):
            raise R3CollapsedCloseoutError("provider content hash drifted")
        if json.loads(content) != candidate:
            raise R3CollapsedCloseoutError("provider candidate content drifted")
        observation = _reasoning_observation(private_payload)
    else:
        redacted = _load(REDACTED_PAYLOAD)
        payload = redacted.get("provider_payload")
        if not isinstance(payload, Mapping):
            raise R3CollapsedCloseoutError("redacted provider payload is missing")
        if (
            redacted.get("raw_provider_payload_value_sha256")
            != call_result.get("provider_payload_sha256")
            or redacted.get("redactions")
            != [
                {
                    "json_pointer": (
                        "/choices/0/message/reasoning_details/0/signature"
                    ),
                    "reason": "opaque provider reasoning-continuation metadata",
                }
            ]
        ):
            raise R3CollapsedCloseoutError("redacted payload custody drifted")
        choices = payload.get("choices")
        choice = choices[0] if isinstance(choices, list) and choices else {}
        message = choice.get("message") if isinstance(choice, Mapping) else {}
        content = str(message.get("content", ""))
        usage = payload.get("usage")
        if (
            hashlib.sha256(content.encode("utf-8")).hexdigest()
            != call_result.get("raw_content_sha256")
            or json.loads(content) != candidate
            or payload.get("id") != call_result.get("generation_id")
            or payload.get("model") != call_result.get("served_model")
            or payload.get("provider") != call_result.get("served_provider")
            or not isinstance(usage, Mapping)
            or usage.get("cost") != exact_cost
        ):
            raise R3CollapsedCloseoutError("redacted provider evidence drifted")
        observation = _reasoning_observation(payload)
    return contract, material, call_result, {
        "provider_budget": provider_budget,
        "reasoning_observation": observation,
    }


def build(private_payload_path: Path) -> dict[str, Any]:
    private_payload = _load(private_payload_path)
    contract, _material, call_result, evidence = _validate_evidence(
        private_payload=private_payload
    )
    redacted_value, redactions = _redact_payload(private_payload)
    redacted_payload: dict[str, Any] = {
        "schema_version": REDACTED_PAYLOAD_SCHEMA,
        "status": "safe_to_commit_redaction_of_privately_preserved_raw_payload",
        "raw_provider_payload_file_sha256": _file_sha(private_payload_path),
        "raw_provider_payload_value_sha256": call_result["provider_payload_sha256"],
        "redactions": redactions,
        "provider_payload": redacted_value,
        "raw_payload_preserved_outside_git": True,
    }
    redacted_payload["redacted_payload_sha256"] = value_sha256(redacted_payload)
    _write(REDACTED_PAYLOAD, redacted_payload)
    reasoning = evidence["reasoning_observation"]
    dimensions = [
        {
            "dimension": dimension,
            "verdict": "not_evaluable_frozen_mechanical_gate_failed",
            "why": (
                "The frozen runner prohibited source-first review after its "
                "reasoning-exclusion gate returned false."
            ),
        }
        for dimension in SEMANTIC_DIMENSIONS
    ]
    dimensions.append(
        {
            "dimension": "exact_cost_and_failure_custody",
            "verdict": "pass",
            "why": (
                "The exact provider cost, generation identity, raw payload hash, "
                "compiled candidate, and one-call budget are preserved."
            ),
        }
    )
    closeout: dict[str, Any] = {
        "schema_version": CLOSEOUT_SCHEMA,
        "status": "collapsed_response_compiled_frozen_reasoning_gate_failed",
        "run_id": call_result["run_id"],
        "case_id": call_result["case_id"],
        "contract_sha256": call_result["contract_sha256"],
        "authorization_sha256": call_result["authorization_sha256"],
        "call_result_sha256": call_result["call_result_sha256"],
        "execution_result": {
            "provider_calls_attempted": 1,
            "provider_calls_succeeded": 1,
            "served_model": call_result["served_model"],
            "served_provider": call_result["served_provider"],
            "generation_id": call_result["generation_id"],
            "exact_cost_usd": call_result["provider_reported_cost_usd"],
            "within_one_cent": True,
            "automatic_retries": 0,
            "fallback_models": 0,
            "response_healing": False,
        },
        "wire_and_compiler_result": {
            "provider_accepted_strict_schema": True,
            "exact_json_object_returned": True,
            "collapsed_compiler_accepted": True,
            "all_nine_pressures_accounted_for": True,
            "candidate_modified_or_healed": False,
            "semantic_review_performed": False,
        },
        "reasoning_exclusion_result": {
            "request_exclude_true": True,
            "frozen_runner_classification": "reasoning_content_returned",
            "frozen_runner_mechanical_contract_valid": False,
            "frozen_runner_tested_any_reasoning_details_as_content": True,
            "provider_observation": reasoning,
            "causal_classification": (
                "frozen_validator_conflated_signature_only_metadata_with_"
                "returned_reasoning_content"
            ),
            "current_practice_interpretation": (
                "OpenRouter documents excluded reasoning tokens in the message "
                "reasoning field and separately documents reasoning_details as a "
                "structured preservation surface. The observed response has no "
                "reasoning text, summary, or encrypted data, only a signature."
            ),
            "frozen_result_reclassified_as_pass": False,
            "response_repaired": False,
        },
        "source_review": {
            "status": "not_run_frozen_mechanical_gate_failed",
            "dimensions": dimensions,
            "value_signal": "not_evaluable",
            "scalar_quality_score": None,
        },
        "decision": {
            "experiment_closed": True,
            "r3_semantic_exit_condition_met": False,
            "r3_semantic_hypothesis_status": "unresolved",
            "additional_provider_call_authorized": False,
            "quiet_control_authorized": False,
            "next_boundary": (
                "Correct reasoning-exclusion validation provider-free so only "
                "actual returned reasoning content fails. Do not retry this case. "
                "Then decide whether to defer R3 or freeze a different prospective "
                "case before any further empirical call."
            ),
            "r4_recommendation": (
                "Do not begin provider-backed R4 work. A narrow provider-free "
                "validator correction may proceed before R4 corpus work; R3 remains "
                "semantically unresolved unless explicitly deferred."
            ),
        },
        "current_practice": {
            "checked_on": "2026-07-13",
            "source": (
                "https://openrouter.ai/docs/guides/best-practices/"
                "reasoning-tokens"
            ),
        },
        "claims_not_made": [
            "the_frozen_call_passed_its_mechanical_contract",
            "the_candidate_was_semantically_useful_or_correct",
            "the_collapsed_outcome_hypothesis_was_validated",
            "the_deterministic_graph_contributed_value",
            "the_model_is_reliable_for_this_task",
            "the_product_is_reliable_or_ready_for_integration",
        ],
    }
    closeout["closeout_sha256"] = value_sha256(closeout)
    _write(CLOSEOUT, closeout)
    terminal: dict[str, Any] = {
        "schema_version": TERMINAL_SCHEMA,
        "status": "r3_collapsed_attempt_closed_semantic_review_not_evaluable",
        "run_id": call_result["run_id"],
        "case_id": call_result["case_id"],
        "contract_sha256": _file_sha(CONTRACT),
        "authorization_sha256": _file_sha(AUTHORIZATION),
        "call_result_sha256": call_result["call_result_sha256"],
        "redacted_payload_sha256": redacted_payload["redacted_payload_sha256"],
        "closeout_sha256": closeout["closeout_sha256"],
        "provider_calls": 1,
        "provider_reported_cost_usd": call_result["provider_reported_cost_usd"],
        "collapsed_compiler_accepted": True,
        "frozen_mechanical_contract_valid": False,
        "semantic_review_performed": False,
        "r3_semantic_exit_condition_met": False,
        "next_call_authorized": False,
        "runtime_integration_authorized": False,
        "quiet_control_authorized": False,
        "result_kind": "honest_negative_experiment_validator_boundary_exposed",
        "stop_rule_honored": contract["stop_rule"],
    }
    terminal["result_sha256"] = value_sha256(terminal)
    _write(TERMINAL_RESULT, terminal)
    validate()
    return terminal


def validate() -> dict[str, Any]:
    _validate_evidence(private_payload=None)
    redacted = _load(REDACTED_PAYLOAD)
    closeout = _load(CLOSEOUT)
    terminal = _load(TERMINAL_RESULT)
    if redacted.get("redacted_payload_sha256") != value_sha256(
        _without(redacted, "redacted_payload_sha256")
    ):
        raise R3CollapsedCloseoutError("redacted payload self-hash drifted")
    if closeout.get("closeout_sha256") != value_sha256(
        _without(closeout, "closeout_sha256")
    ):
        raise R3CollapsedCloseoutError("closeout self-hash drifted")
    if terminal.get("result_sha256") != value_sha256(
        _without(terminal, "result_sha256")
    ):
        raise R3CollapsedCloseoutError("terminal result self-hash drifted")
    if (
        terminal.get("call_result_sha256")
        != _load(CALL_RESULT)["call_result_sha256"]
        or terminal.get("redacted_payload_sha256")
        != redacted["redacted_payload_sha256"]
        or terminal.get("closeout_sha256") != closeout["closeout_sha256"]
        or terminal.get("next_call_authorized") is not False
        or terminal.get("semantic_review_performed") is not False
        or closeout.get("source_review", {}).get("status")
        != "not_run_frozen_mechanical_gate_failed"
    ):
        raise R3CollapsedCloseoutError("terminal evidence chain drifted")
    return terminal


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-payload", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    if args.validate_only:
        terminal = validate()
    else:
        if args.private_payload is None:
            raise R3CollapsedCloseoutError("build requires --private-payload")
        terminal = build(args.private_payload.resolve())
    print(
        json.dumps(
            {
                key: terminal.get(key)
                for key in (
                    "status",
                    "provider_calls",
                    "provider_reported_cost_usd",
                    "collapsed_compiler_accepted",
                    "frozen_mechanical_contract_valid",
                    "semantic_review_performed",
                    "next_call_authorized",
                    "result_sha256",
                )
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
