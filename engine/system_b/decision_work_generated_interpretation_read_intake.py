"""Generated Decision Work interpretation read intake validator.

PR182 validates externally supplied interpretation reads before later offline
Decision Work steps may consume them. It is deterministic and read-only: it
checks schema compatibility, source refs, uncertainty, privacy limits, custody
flags, and non-claims. It does not generate reads, call models, render briefs,
create triage, update resolver refs, mutate archives, update runtime sidecars,
score advice, or authorize action.
"""
from __future__ import annotations

import datetime as _dt
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any


INTAKE_SCHEMA_VERSION = (
    "lolla.decision_work_generated_interpretation_read_intake.v0"
)
CANONICAL_READ_SCHEMA_VERSION = (
    "lolla.decision_work_conversation_interpretation_read.v0"
)
SUPPORTED_READ_SCHEMA_VERSIONS = (
    CANONICAL_READ_SCHEMA_VERSION,
    "lolla.decision_work_conversation_interpretation_tiny_offline_read.v0",
    "lolla.decision_work_conversation_interpretation_second_tiny_offline_read.v0",
)
QUEUE_ITEM_SCHEMA_VERSION = "lolla.decision_work_offline_interpretation_queue_item.v0"
PROMPT_PACKET_SCHEMA_VERSION = (
    "lolla.decision_work_operator_codex_interpretation_prompt_packet.v0"
)
REPO_ROOT = Path(__file__).resolve().parents[2]

INTAKE_MODES = (
    "checked_in_safe",
    "local_private_operator",
)
ACCEPTED_STATUS = "accepted"
RAW_PRIVATE_MARKERS = (
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)
LOCAL_ABSOLUTE_PATH_MARKERS = (
    "/" + "Users" + "/",
    "/home/",
    "/private/",
)
REQUIRED_TOP_LEVEL_FIELDS = (
    "schema_version",
    "read_metadata",
    "custody_flags",
    "source_packet",
    "selected_case",
    "interpretation_scope",
    "interpreted_fields",
    "unresolved_fields",
    "source_limitations",
    "brief_implications",
    "overclaim_risk",
    "recommended_next_step",
    "non_claims",
)
REQUIRED_INTERPRETED_FIELD_FIELDS = (
    "field_group",
    "field_name",
    "status",
    "value",
    "uncertainty",
    "source_refs",
    "source_status",
    "interpretation_basis",
    "privacy_limit",
    "human_review_required",
    "could_feed_brief",
    "could_feed_agent_inspection",
    "must_not_be_used_as_quality_label",
)
ALLOWED_FIELD_STATUSES = {
    "interpreted_provisional",
    "partial_interpretation",
    "insufficient_context",
    "not_interpreted",
    "not_applicable",
}
ALLOWED_UNCERTAINTY = {"low", "medium", "high", "insufficient_context"}
REQUIRED_NON_CLAIMS = (
    "not_human_validated",
    "not_product_proof",
    "not_answer_quality_score",
    "not_agent_action_authorization",
    "not_correctness_proof",
)
FALSE_CUSTODY_FLAGS = (
    "human_validated",
    "product_proof",
    "archive_mutated",
    "runtime_invoked",
    "skill_invoked",
    "answer_quality_scored",
    "agent_action_authorized",
    "automatic_action_authorized",
    "raw_private_content_checked_in",
    "provider_text_checked_in",
    "local_absolute_paths_checked_in",
    "raw_private_content_included",
    "provider_text_included",
)
FALSE_SOURCE_LIMITATIONS = ()
TRUE_SOURCE_LIMITATIONS = (
    "raw_conversation_was_not_checked_in",
    "raw_revised_answer_was_not_checked_in",
    "raw_memo_was_not_checked_in",
    "provider_text_was_not_checked_in",
    "private_ledgers_were_not_checked_in",
    "human_validation_is_absent",
)
AUTHORITY_CLAIM_PATTERNS = (
    "advice_correctness_proven",
    "advice_is_correct",
    "safe_for_action",
    "safe_for_agent_action",
    "approved_for_action",
    "certified_advice",
    "product_proof_established",
    "lolla_improved_the_decision",
)
NON_CLAIMS = (
    "intake_is_structural_validation_only",
    "intake_does_not_generate_interpretation",
    "intake_does_not_modify_source_read",
    "intake_does_not_call_models",
    "intake_does_not_run_lolla",
    "intake_does_not_mutate_archives",
    "intake_does_not_render_briefs",
    "intake_does_not_generate_triage",
    "intake_does_not_update_runtime_sidecars",
    "intake_is_not_product_proof",
    "intake_is_not_human_validation",
    "intake_does_not_score_answer_quality",
    "intake_does_not_validate_advice_correctness",
    "intake_does_not_prove_lolla_improved_the_decision",
    "intake_does_not_authorize_agent_action",
    "intake_does_not_authorize_automatic_action",
)


class DecisionWorkGeneratedInterpretationReadIntakeError(ValueError):
    """Sanitized generated interpretation read intake input/output error."""


def validate_generated_interpretation_read(
    *,
    read_path: Path | str,
    queue_item_path: Path | str | None = None,
    prompt_packet_path: Path | str | None = None,
    mode: str = "checked_in_safe",
    created_at: str | None = None,
) -> dict[str, Any]:
    """Validate a candidate interpretation read and return an intake result."""

    if mode not in INTAKE_MODES:
        raise DecisionWorkGeneratedInterpretationReadIntakeError(
            "unsupported intake mode"
        )

    source_read = _load_candidate_read(read_path)
    queue_ref = _optional_schema_ref(
        queue_item_path,
        expected_schema=QUEUE_ITEM_SCHEMA_VERSION,
        description="queue item JSON",
    )
    prompt_ref = _optional_schema_ref(
        prompt_packet_path,
        expected_schema=PROMPT_PACKET_SCHEMA_VERSION,
        description="prompt packet JSON",
    )

    payload = source_read.get("payload")
    blockers: list[str] = []
    repair_reasons: list[str] = []

    if source_read["local_absolute_path_detected"]:
        blockers.append("local_absolute_path_detected")
    if source_read["privacy_marker_detected"]:
        blockers.append("privacy_marker_detected")
    if source_read["json_status"] != "valid_json_object":
        blockers.append(source_read["json_status"])

    if isinstance(payload, Mapping):
        blockers.extend(_schema_blockers(payload))
        blockers.extend(_custody_blockers(payload))
        field_summary = _field_validation_summary(payload)
        source_validation = _source_ref_validation(payload)
        uncertainty_validation = _uncertainty_validation(payload)
        privacy_validation = _privacy_validation(payload)
        non_claim_validation = _non_claim_validation(payload)
        semantic_limits = _semantic_limits(payload)
        repair_reasons.extend(non_claim_validation["missing_non_claims"])
        repair_reasons.extend(privacy_validation["missing_privacy_limit_fields"])
        blockers.extend(source_validation["blocker_reasons"])
        blockers.extend(uncertainty_validation["blocker_reasons"])
        blockers.extend(field_summary["quality_label_blockers"])
        blockers.extend(privacy_validation["blocker_reasons"])
        blockers.extend(non_claim_validation["blocker_reasons"])
    else:
        field_summary = _empty_field_validation_summary()
        source_validation = _empty_source_ref_validation()
        uncertainty_validation = _empty_uncertainty_validation()
        privacy_validation = _empty_privacy_validation()
        non_claim_validation = _empty_non_claim_validation()
        semantic_limits = list(NON_CLAIMS)

    if queue_ref["status"] == "blocked_privacy_risk":
        blockers.append("queue_item_privacy_marker_detected")
    elif queue_ref["status"] == "blocked_schema_invalid":
        blockers.append("queue_item_schema_invalid")
    if prompt_ref["status"] == "blocked_privacy_risk":
        blockers.append("prompt_packet_privacy_marker_detected")
    elif prompt_ref["status"] == "blocked_schema_invalid":
        blockers.append("prompt_packet_schema_invalid")

    blockers = _dedupe(blockers)
    repair_reasons = _dedupe(repair_reasons)
    intake_status = _intake_status(blockers, repair_reasons)
    accepted = intake_status == ACCEPTED_STATUS

    return {
        "schema_version": INTAKE_SCHEMA_VERSION,
        "intake_metadata": {
            "created_at": created_at or _utc_now(),
            "generated_by": "decision_work_generated_interpretation_read_intake",
            "mode": mode,
            "validator_scope": "structure_source_privacy_custody_non_claims_only",
            "model_calls": 0,
            "runtime_invoked": False,
            "skill_invoked": False,
        },
        "source_read_ref": source_read["ref"],
        "source_queue_item_ref": queue_ref,
        "source_prompt_packet_ref": prompt_ref,
        "read_schema_detected": source_read.get("schema_version"),
        "intake_status": intake_status,
        "blocker_reasons": blockers,
        "repair_required": intake_status == "requires_operator_repair",
        "repair_reasons": repair_reasons,
        "accepted_for_downstream": accepted,
        "downstream_allowed": {
            "can_feed_brief": accepted,
            "can_feed_enrichment": accepted,
            "can_feed_triage_packet": accepted,
            "can_feed_resolver": accepted,
            "can_update_sidecar": False,
            "can_authorize_agent_action": False,
            "can_be_used_as_quality_label": False,
        },
        "field_validation_summary": field_summary,
        "source_ref_validation": source_validation,
        "uncertainty_validation": uncertainty_validation,
        "privacy_validation": privacy_validation,
        "custody_validation": _custody_validation(payload),
        "non_claim_validation": non_claim_validation,
        "semantic_limits": semantic_limits,
        "output_refs": {
            "intake_result_ref": None,
            "source_read_content_modified": False,
            "brief_generated": False,
            "enriched_brief_generated": False,
            "triage_generated": False,
            "resolver_refs_updated": False,
            "runtime_sidecar_updated": False,
        },
        "non_claims": list(NON_CLAIMS),
    }


def render_generated_interpretation_read_intake_json(
    result: Mapping[str, Any],
    *,
    pretty: bool = False,
) -> str:
    """Render an intake result as stable JSON."""

    if pretty:
        return json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return json.dumps(
        result,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ) + "\n"


def write_generated_interpretation_read_intake_result(
    path: Path | str,
    payload: str,
) -> None:
    """Write a generated interpretation read intake result JSON file."""

    output = Path(path).expanduser()
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    except OSError as exc:
        raise DecisionWorkGeneratedInterpretationReadIntakeError(
            f"output could not be written:{type(exc).__name__}"
        ) from exc


def _load_candidate_read(path: Path | str) -> dict[str, Any]:
    candidate = _resolve(path)
    ref = _safe_ref(candidate)
    try:
        text = candidate.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return _candidate_status(
            ref=ref,
            json_status="read_not_utf8",
            text="",
            payload=None,
        )
    except OSError as exc:
        raise DecisionWorkGeneratedInterpretationReadIntakeError(
            "interpretation read could not be read"
        ) from exc

    if _contains_local_absolute_path_marker(text):
        local_path = True
    else:
        local_path = False
    privacy = _contains_private_marker(text)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return _candidate_status(
            ref=ref,
            json_status="json_invalid",
            text=text,
            payload=None,
            local_absolute_path_detected=local_path,
            privacy_marker_detected=privacy,
        )
    if not isinstance(payload, dict):
        return _candidate_status(
            ref=ref,
            json_status="json_not_object",
            text=text,
            payload=None,
            local_absolute_path_detected=local_path,
            privacy_marker_detected=privacy,
        )
    return _candidate_status(
        ref=ref,
        json_status="valid_json_object",
        text=text,
        payload=payload,
        local_absolute_path_detected=local_path,
        privacy_marker_detected=privacy,
    )


def _candidate_status(
    *,
    ref: str | None,
    json_status: str,
    text: str,
    payload: Mapping[str, Any] | None,
    local_absolute_path_detected: bool | None = None,
    privacy_marker_detected: bool | None = None,
) -> dict[str, Any]:
    return {
        "ref": ref,
        "json_status": json_status,
        "schema_version": (
            _text(payload.get("schema_version")) if isinstance(payload, Mapping) else None
        ),
        "payload": payload,
        "local_absolute_path_detected": (
            _contains_local_absolute_path_marker(text)
            if local_absolute_path_detected is None
            else local_absolute_path_detected
        ),
        "privacy_marker_detected": (
            _contains_private_marker(text)
            if privacy_marker_detected is None
            else privacy_marker_detected
        ),
    }


def _optional_schema_ref(
    path: Path | str | None,
    *,
    expected_schema: str,
    description: str,
) -> dict[str, Any]:
    if path is None:
        return {
            "input_ref": None,
            "status": "not_supplied",
            "schema_version": None,
            "expected_schema": expected_schema,
            "content_included": False,
        }
    candidate = _resolve(path)
    ref = _safe_ref(candidate)
    try:
        text = candidate.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {
            "input_ref": ref,
            "status": "blocked_schema_invalid",
            "schema_version": None,
            "expected_schema": expected_schema,
            "reason": f"{description} could not be read",
            "content_included": False,
        }
    if _contains_private_marker(text) or _contains_local_absolute_path_marker(text):
        return {
            "input_ref": ref,
            "status": "blocked_privacy_risk",
            "schema_version": None,
            "expected_schema": expected_schema,
            "reason": "privacy_or_local_path_marker_detected",
            "content_included": False,
        }
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {
            "input_ref": ref,
            "status": "blocked_schema_invalid",
            "schema_version": None,
            "expected_schema": expected_schema,
            "reason": f"{description} was not valid JSON",
            "content_included": False,
        }
    if not isinstance(payload, dict):
        schema = None
    else:
        schema = _text(payload.get("schema_version"))
    return {
        "input_ref": ref,
        "status": "available" if schema == expected_schema else "blocked_schema_invalid",
        "schema_version": schema or None,
        "expected_schema": expected_schema,
        "content_included": False,
    }


def _schema_blockers(payload: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    schema = _text(payload.get("schema_version"))
    if not schema:
        blockers.append("schema_version_missing")
    elif schema not in SUPPORTED_READ_SCHEMA_VERSIONS:
        blockers.append("unsupported_schema")
    missing = [field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in payload]
    if missing:
        blockers.append("required_top_level_fields_missing")
    if not isinstance(payload.get("interpreted_fields"), list):
        blockers.append("interpreted_fields_not_array")
    return blockers


def _field_validation_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    fields = _list_of_mappings(payload.get("interpreted_fields"))
    missing_required: list[str] = []
    quality_label_blockers: list[str] = []
    invalid_status_fields: list[str] = []
    feedable_fields: list[str] = []
    for index, field in enumerate(fields):
        name = _field_name(field, index)
        missing = [key for key in REQUIRED_INTERPRETED_FIELD_FIELDS if key not in field]
        if missing:
            missing_required.append(name)
        if field.get("must_not_be_used_as_quality_label") is not True:
            quality_label_blockers.append(f"quality_label_allowed:{name}")
        if _text(field.get("status")) not in ALLOWED_FIELD_STATUSES:
            invalid_status_fields.append(name)
        if field.get("could_feed_brief") is True:
            feedable_fields.append(name)
    return {
        "field_count": len(fields),
        "feedable_field_count": len(feedable_fields),
        "feedable_fields": feedable_fields,
        "missing_required_field_names": missing_required,
        "invalid_status_fields": invalid_status_fields,
        "quality_label_blockers": quality_label_blockers,
    }


def _source_ref_validation(payload: Mapping[str, Any]) -> dict[str, Any]:
    fields = _list_of_mappings(payload.get("interpreted_fields"))
    missing_source_ref_fields: list[str] = []
    local_absolute_path_fields: list[str] = []
    malformed_source_ref_fields: list[str] = []
    checked_refs = 0
    for index, field in enumerate(fields):
        name = _field_name(field, index)
        refs = field.get("source_refs")
        if not isinstance(refs, list) or not refs:
            missing_source_ref_fields.append(name)
            continue
        for ref in refs:
            if not isinstance(ref, Mapping):
                malformed_source_ref_fields.append(name)
                continue
            checked_refs += 1
            artifact = _text(ref.get("artifact"))
            if not artifact:
                malformed_source_ref_fields.append(name)
            elif _looks_like_local_absolute_path(artifact):
                local_absolute_path_fields.append(name)
    blockers: list[str] = []
    if missing_source_ref_fields:
        blockers.append("missing_source_refs")
    if malformed_source_ref_fields:
        blockers.append("malformed_source_refs")
    if local_absolute_path_fields:
        blockers.append("local_absolute_path_in_source_ref")
    return {
        "status": "passed" if not blockers else "blocked",
        "checked_source_ref_count": checked_refs,
        "missing_source_ref_fields": _dedupe(missing_source_ref_fields),
        "malformed_source_ref_fields": _dedupe(malformed_source_ref_fields),
        "local_absolute_path_fields": _dedupe(local_absolute_path_fields),
        "blocker_reasons": blockers,
    }


def _uncertainty_validation(payload: Mapping[str, Any]) -> dict[str, Any]:
    fields = _list_of_mappings(payload.get("interpreted_fields"))
    missing_fields: list[str] = []
    invalid_fields: list[str] = []
    for index, field in enumerate(fields):
        name = _field_name(field, index)
        uncertainty = _text(field.get("uncertainty"))
        if not uncertainty:
            missing_fields.append(name)
        elif uncertainty not in ALLOWED_UNCERTAINTY:
            invalid_fields.append(name)
    blockers: list[str] = []
    if missing_fields:
        blockers.append("missing_uncertainty")
    if invalid_fields:
        blockers.append("invalid_uncertainty")
    return {
        "status": "passed" if not blockers else "blocked",
        "missing_uncertainty_fields": missing_fields,
        "invalid_uncertainty_fields": invalid_fields,
        "blocker_reasons": blockers,
    }


def _privacy_validation(payload: Mapping[str, Any]) -> dict[str, Any]:
    fields = _list_of_mappings(payload.get("interpreted_fields"))
    missing_privacy_limit_fields: list[str] = []
    for index, field in enumerate(fields):
        if not _text(field.get("privacy_limit")):
            missing_privacy_limit_fields.append(_field_name(field, index))

    source_limitations = payload.get("source_limitations")
    missing_limitations: list[str] = []
    wrong_limitations: list[str] = []
    if not isinstance(source_limitations, Mapping):
        missing_limitations.extend(TRUE_SOURCE_LIMITATIONS)
    else:
        for key in TRUE_SOURCE_LIMITATIONS:
            if key not in source_limitations:
                missing_limitations.append(key)
            elif source_limitations.get(key) is not True:
                wrong_limitations.append(key)
        for key in FALSE_SOURCE_LIMITATIONS:
            if source_limitations.get(key) is not False:
                wrong_limitations.append(key)

    blockers: list[str] = []
    if wrong_limitations:
        blockers.append("privacy_limit_claim_invalid")
    return {
        "status": (
            "passed"
            if not missing_privacy_limit_fields and not missing_limitations and not wrong_limitations
            else "requires_repair"
        ),
        "missing_privacy_limit_fields": missing_privacy_limit_fields,
        "missing_source_limitations": missing_limitations,
        "invalid_source_limitations": wrong_limitations,
        "blocker_reasons": blockers,
    }


def _custody_blockers(payload: Mapping[str, Any]) -> list[str]:
    custody = payload.get("custody_flags")
    if not isinstance(custody, Mapping):
        return ["custody_flags_missing"]
    blockers: list[str] = []
    if custody.get("product_proof") is True:
        blockers.append("product_proof_claimed")
    if custody.get("human_validated") is True:
        blockers.append("human_validation_claimed")
    if custody.get("answer_quality_scored") is True:
        blockers.append("answer_quality_scored")
    if custody.get("agent_action_authorized") is True:
        blockers.append("agent_action_authorized")
    if custody.get("automatic_action_authorized") is True:
        blockers.append("automatic_action_authorized")
    if custody.get("local_absolute_paths_checked_in") is True:
        blockers.append("local_absolute_path_claimed")
    if custody.get("raw_private_content_checked_in") is True:
        blockers.append("raw_private_content_claimed")
    if custody.get("provider_text_checked_in") is True:
        blockers.append("provider_text_claimed")
    if _safe_int(custody.get("model_calls")) != 0:
        blockers.append("model_calls_claimed")
    if custody.get("semantic_read_is_provisional") is False:
        blockers.append("semantic_read_not_provisional")
    return blockers


def _custody_validation(payload: Mapping[str, Any] | None) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        return {
            "status": "blocked",
            "model_calls": 0,
            "human_validated": False,
            "product_proof": False,
            "answer_quality_scored": False,
            "agent_action_authorized": False,
            "automatic_action_authorized": False,
            "blocker_reasons": ["read_payload_missing"],
        }
    custody = payload.get("custody_flags")
    if not isinstance(custody, Mapping):
        return {
            "status": "blocked",
            "model_calls": 0,
            "human_validated": False,
            "product_proof": False,
            "answer_quality_scored": False,
            "agent_action_authorized": False,
            "automatic_action_authorized": False,
            "blocker_reasons": ["custody_flags_missing"],
        }
    blockers = _custody_blockers(payload)
    return {
        "status": "passed" if not blockers else "blocked",
        "model_calls": _safe_int(custody.get("model_calls")),
        "human_validated": bool(custody.get("human_validated", False)),
        "product_proof": bool(custody.get("product_proof", False)),
        "answer_quality_scored": bool(custody.get("answer_quality_scored", False)),
        "agent_action_authorized": bool(
            custody.get("agent_action_authorized", False)
        ),
        "automatic_action_authorized": bool(
            custody.get("automatic_action_authorized", False)
        ),
        "semantic_read_is_provisional": bool(
            custody.get("semantic_read_is_provisional", False)
        ),
        "blocker_reasons": blockers,
    }


def _non_claim_validation(payload: Mapping[str, Any]) -> dict[str, Any]:
    non_claims = payload.get("non_claims")
    if not isinstance(non_claims, list) or not all(
        isinstance(item, str) for item in non_claims
    ):
        return {
            "status": "requires_repair",
            "missing_non_claims": list(REQUIRED_NON_CLAIMS),
            "blocker_reasons": [],
        }
    missing = [claim for claim in REQUIRED_NON_CLAIMS if claim not in non_claims]
    authority_hits = _authority_claim_hits(payload)
    return {
        "status": "passed" if not missing and not authority_hits else "blocked",
        "missing_non_claims": missing,
        "authority_claim_hits": authority_hits,
        "blocker_reasons": (
            ["authority_claim_detected"] if authority_hits else []
        ),
    }


def _authority_claim_hits(payload: Mapping[str, Any]) -> list[str]:
    text = json.dumps(payload, ensure_ascii=False).lower()
    return [pattern for pattern in AUTHORITY_CLAIM_PATTERNS if pattern in text]


def _semantic_limits(payload: Mapping[str, Any] | None) -> list[str]:
    limits = [
        "intake_validates_structure_not_semantic_truth",
        "accepted_read_still_requires_later_offline_brief_generation",
        "accepted_read_cannot_update_runtime_sidecars_in_pr182",
        "accepted_read_cannot_authorize_agent_action",
        "accepted_read_cannot_be_used_as_quality_label",
    ]
    if isinstance(payload, Mapping):
        case = payload.get("selected_case")
        if isinstance(case, Mapping):
            family = _text(case.get("decision_family"))
            if any(
                fragment in family.lower()
                for fragment in (
                    "legal",
                    "governance",
                    "medical",
                    "employment",
                    "safety",
                    "relationship",
                    "healthcare",
                    "compliance",
                )
            ):
                limits.append("high_risk_case_requires_visible_caveats")
    return limits


def _intake_status(blockers: list[str], repair_reasons: list[str]) -> str:
    if not blockers and not repair_reasons:
        return ACCEPTED_STATUS
    blocker_set = set(blockers)
    if "unsupported_schema" in blocker_set:
        return "unsupported_schema"
    if blocker_set.intersection(
        {
            "schema_version_missing",
            "required_top_level_fields_missing",
            "interpreted_fields_not_array",
            "json_invalid",
            "json_not_object",
            "read_not_utf8",
            "custody_flags_missing",
            "queue_item_schema_invalid",
            "prompt_packet_schema_invalid",
        }
    ):
        return "rejected_schema_invalid"
    if blocker_set.intersection(
        {
            "local_absolute_path_detected",
            "local_absolute_path_in_source_ref",
            "local_absolute_path_claimed",
        }
    ):
        return "rejected_local_absolute_path"
    if blocker_set.intersection(
        {
            "privacy_marker_detected",
            "raw_private_content_claimed",
            "provider_text_claimed",
            "privacy_limit_claim_invalid",
            "queue_item_privacy_marker_detected",
            "prompt_packet_privacy_marker_detected",
        }
    ):
        return "rejected_privacy_risk"
    if "human_validation_claimed" in blocker_set:
        return "rejected_human_validation_claim"
    if "product_proof_claimed" in blocker_set:
        return "rejected_product_proof_claim"
    if "answer_quality_scored" in blocker_set or any(
        blocker.startswith("quality_label_allowed:") for blocker in blockers
    ):
        return "rejected_quality_label"
    if blocker_set.intersection(
        {"agent_action_authorized", "automatic_action_authorized"}
    ):
        return "rejected_action_authorization"
    if "missing_source_refs" in blocker_set:
        return "rejected_missing_source_refs"
    if "missing_uncertainty" in blocker_set:
        return "rejected_missing_uncertainty"
    if blocker_set.intersection({"authority_claim_detected", "model_calls_claimed"}):
        return "rejected_authority_claim"
    if repair_reasons:
        return "requires_operator_repair"
    return "requires_operator_repair"


def _empty_field_validation_summary() -> dict[str, Any]:
    return {
        "field_count": 0,
        "feedable_field_count": 0,
        "feedable_fields": [],
        "missing_required_field_names": [],
        "invalid_status_fields": [],
        "quality_label_blockers": [],
    }


def _empty_source_ref_validation() -> dict[str, Any]:
    return {
        "status": "blocked",
        "checked_source_ref_count": 0,
        "missing_source_ref_fields": [],
        "malformed_source_ref_fields": [],
        "local_absolute_path_fields": [],
        "blocker_reasons": ["read_payload_missing"],
    }


def _empty_uncertainty_validation() -> dict[str, Any]:
    return {
        "status": "blocked",
        "missing_uncertainty_fields": [],
        "invalid_uncertainty_fields": [],
        "blocker_reasons": ["read_payload_missing"],
    }


def _empty_privacy_validation() -> dict[str, Any]:
    return {
        "status": "blocked",
        "missing_privacy_limit_fields": [],
        "missing_source_limitations": [],
        "invalid_source_limitations": [],
        "blocker_reasons": ["read_payload_missing"],
    }


def _empty_non_claim_validation() -> dict[str, Any]:
    return {
        "status": "blocked",
        "missing_non_claims": [],
        "authority_claim_hits": [],
        "blocker_reasons": ["read_payload_missing"],
    }


def _resolve(path: Path | str) -> Path:
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    return candidate


def _safe_ref(path: Path | str | None) -> str | None:
    if path is None:
        return None
    candidate = Path(path).expanduser()
    try:
        return str(candidate.resolve(strict=False).relative_to(REPO_ROOT))
    except ValueError:
        return candidate.name


def _contains_private_marker(text: str) -> bool:
    return any(marker in text for marker in RAW_PRIVATE_MARKERS)


def _contains_local_absolute_path_marker(text: str) -> bool:
    return any(marker in text for marker in LOCAL_ABSOLUTE_PATH_MARKERS)


def _looks_like_local_absolute_path(value: str) -> bool:
    if Path(value).is_absolute():
        return True
    return bool(re.search(r"(^|\\s)/(Users|home|private)/", value))


def _list_of_mappings(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _field_name(field: Mapping[str, Any], index: int) -> str:
    return _text(field.get("field_name"), f"field_{index}")


def _text(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        return value
    return default


def _safe_int(value: Any) -> int:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return 0


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _utc_now() -> str:
    return (
        _dt.datetime.now(tz=_dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
