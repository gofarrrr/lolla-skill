"""Deterministic triage-supply adapter for generated-read artifacts.

PR192 prepares generated-read artifacts for a future offline triage generation
step. It validates and normalizes refs, status, source, uncertainty, privacy,
custody, and non-claims. It does not generate triage, create a triage read,
mark resolver refs usable, update sidecars, call models, score advice, or
authorize action.
"""
from __future__ import annotations

import datetime as _dt
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from engine.system_b.decision_work_generated_read_brief_supply import (
    READY_STATUS as BRIEF_SUPPLY_READY_STATUS,
    SUPPLY_SCHEMA_VERSION,
)


TRIAGE_SUPPLY_SCHEMA_VERSION = "lolla.decision_work_generated_read_triage_supply.v0"
INTAKE_SCHEMA_VERSION = "lolla.decision_work_generated_interpretation_read_intake.v0"
READ_SCHEMA_VERSION = "lolla.decision_work_conversation_interpretation_read.v0"
READY_STATUS = "ready_for_offline_triage_generation"
REPO_ROOT = Path(__file__).resolve().parents[2]

ALLOWED_ROUTING_FIELD_NAMES = (
    "decision_question",
    "revised_direction_or_action_consequence",
    "evidence_gates",
    "what_the_final_answer_does_not_prove",
)
EVIDENCE_ONLY_FIELDS = (
    "lost_value",
    "noisy_friction",
    "useful_friction",
    "live_options",
    "abandoned_or_rejected_options",
    "assistant_influence_on_user_framing",
    "stakeholder_obligations",
    "user_values_or_priorities",
    "safe_for_agent_inspection_only",
    "safe_to_show_user",
)
ROUTE_CATEGORIES_ALLOWED = (
    "source_depth_insufficient",
    "private_context_required",
    "high_overtrust_risk",
    "domain_review_recommended",
    "legal_or_compliance_review_recommended",
    "relationship_or_governance_sensitive",
    "lost_value_risk_unresolved",
    "agent_inspection_only",
    "not_ready_for_user_surface",
    "runtime_attachment_blocked",
)
ROUTE_CATEGORIES_FORBIDDEN = (
    "good_answer",
    "bad_answer",
    "approved",
    "certified",
    "safe_to_act",
    "correct_advice",
    "lolla_improved_decision",
    "human_validated",
    "product_proof",
    "agent_action_authorized",
    "automatic_action_authorized",
)
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
AUTHORITY_CUSTODY_FLAGS = (
    "product_proof",
    "human_validated",
    "answer_quality_scored",
    "agent_action_authorized",
    "automatic_action_authorized",
    "raw_private_content_checked_in",
    "provider_text_checked_in",
    "local_absolute_paths_checked_in",
)
NON_CLAIMS = (
    "triage_supply_is_deterministic_preparation_only",
    "triage_supply_does_not_generate_triage",
    "triage_supply_does_not_create_triage_read",
    "triage_supply_does_not_generate_interpretation",
    "triage_supply_does_not_render_or_modify_briefs",
    "triage_supply_does_not_mark_resolver_refs_usable",
    "triage_supply_does_not_update_runtime_sidecars",
    "triage_supply_is_not_product_proof",
    "triage_supply_is_not_human_validation",
    "triage_supply_does_not_score_answer_quality",
    "triage_supply_does_not_validate_advice_correctness",
    "triage_supply_does_not_authorize_agent_action",
    "triage_supply_does_not_authorize_automatic_action",
)


class DecisionWorkGeneratedReadTriageSupplyError(ValueError):
    """Sanitized generated-read triage-supply input/output error."""


def build_generated_read_triage_supply(
    *,
    read_path: Path | str,
    intake_path: Path | str,
    brief_supply_path: Path | str,
    rendered_brief_path: Path | str,
    queue_item_path: Path | str | None = None,
    prompt_packet_path: Path | str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build a deterministic generated-read triage-supply packet."""

    read_ref = _safe_ref(_resolve(read_path))
    intake_ref = _safe_ref(_resolve(intake_path))
    brief_supply_ref = _safe_ref(_resolve(brief_supply_path))
    rendered_brief_ref = _safe_ref(_resolve(rendered_brief_path))

    read_text, read_payload = _load_json_text(read_path, "generated read")
    intake_text, intake_payload = _load_json_text(intake_path, "intake result")
    supply_text, supply_payload, supply_error = _load_optional_json_text(
        brief_supply_path,
        "brief supply packet",
    )
    rendered_text, rendered_error = _load_optional_text(
        rendered_brief_path,
        "rendered brief",
    )

    fields = _list_of_mappings(read_payload.get("interpreted_fields"))
    case = _mapping(read_payload.get("selected_case"))
    source_case = {
        "case_id": _text(case.get("case_id"), "unknown"),
        "run_ref": _text(case.get("run_ref")),
        "decision_family": _text(case.get("decision_family"), "unknown"),
    }

    blockers: list[str] = []
    private_texts = [read_text, intake_text, supply_text, rendered_text]
    if any(_contains_private_marker(text) for text in private_texts if text):
        blockers.append("privacy_marker_detected")
    if any(_contains_local_absolute_path_marker(text) for text in private_texts if text):
        blockers.append("local_absolute_path_detected")

    if read_payload.get("schema_version") != READ_SCHEMA_VERSION:
        blockers.append("read_schema_invalid")
    blockers.extend(_custody_blockers(read_payload))

    blockers.extend(
        _intake_blockers(
            intake_payload=intake_payload,
            intake_ref=intake_ref,
            read_ref=read_ref,
        )
    )
    blockers.extend(
        _brief_supply_blockers(
            supply_payload=supply_payload,
            supply_error=supply_error,
        )
    )
    if rendered_error == "not_found":
        blockers.append("rendered_brief_missing")
    elif rendered_error:
        blockers.append(f"rendered_brief_unreadable:{rendered_error}")

    source_summary = _source_ref_summary(fields, supply_payload)
    uncertainty_summary = _uncertainty_summary(fields, supply_payload)
    privacy_summary = _privacy_summary(
        input_texts=private_texts,
        fields=fields,
    )
    blockers.extend(source_summary["blocker_reasons"])
    blockers.extend(uncertainty_summary["blocker_reasons"])
    blockers.extend(privacy_summary["blocker_reasons"])

    blockers = _dedupe(blockers)
    triage_supply_status = _triage_supply_status(blockers)
    ready = triage_supply_status == READY_STATUS

    return {
        "schema_version": TRIAGE_SUPPLY_SCHEMA_VERSION,
        "triage_supply_metadata": {
            "created_at": created_at or _utc_now(),
            "generated_by": "decision_work_generated_read_triage_supply",
            "adapter_scope": "deterministic_triage_supply_preparation_only",
            "model_calls": 0,
            "runtime_invoked": False,
            "skill_invoked": False,
        },
        "source_case": source_case,
        "source_read_ref": read_ref,
        "source_intake_ref": intake_ref,
        "source_brief_supply_ref": brief_supply_ref,
        "source_rendered_brief_ref": rendered_brief_ref,
        "optional_queue_item_ref": _optional_ref(queue_item_path),
        "optional_prompt_packet_ref": _optional_ref(prompt_packet_path),
        "triage_supply_status": triage_supply_status,
        "blocker_reasons": blockers,
        "allowed_routing_inputs": _allowed_routing_inputs(
            read_fields=fields,
            supply=supply_payload,
            rendered_brief_available=rendered_error is None,
            ready=ready,
        ),
        "evidence_only_inputs": _evidence_only_inputs(supply_payload),
        "forbidden_route_claims": list(ROUTE_CATEGORIES_FORBIDDEN),
        "required_source_refs": source_summary,
        "uncertainty_summary": uncertainty_summary,
        "privacy_summary": privacy_summary,
        "custody_flags": _custody_flags(),
        "non_claims": list(NON_CLAIMS),
        "downstream_allowed": {
            "can_generate_offline_triage": ready,
            "can_update_sidecar": False,
            "can_approve_resolver_refs": False,
            "can_authorize_agent_action": False,
            "can_authorize_automatic_action": False,
            "can_be_used_as_quality_label": False,
        },
        "downstream_forbidden": [
            "generate_triage_read_in_adapter",
            "mark_resolver_refs_usable",
            "update_runtime_sidecar",
            "call_models_or_providers",
            "score_answer_quality",
            "claim_product_proof",
            "claim_human_validation",
            "authorize_agent_or_automatic_action",
        ],
        "route_categories_allowed": list(ROUTE_CATEGORIES_ALLOWED),
        "route_categories_forbidden": list(ROUTE_CATEGORIES_FORBIDDEN),
    }


def render_generated_read_triage_supply_json(
    result: Mapping[str, Any],
    *,
    pretty: bool = False,
) -> str:
    """Render a generated-read triage-supply packet as stable JSON."""

    if pretty:
        return json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return json.dumps(result, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"


def write_generated_read_triage_supply(path: Path | str, payload: str) -> None:
    """Write a generated-read triage-supply packet."""

    output = Path(path).expanduser()
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    except OSError as exc:
        raise DecisionWorkGeneratedReadTriageSupplyError(
            f"output could not be written:{type(exc).__name__}"
        ) from exc


def _intake_blockers(
    *,
    intake_payload: Mapping[str, Any],
    intake_ref: str,
    read_ref: str,
) -> list[str]:
    blockers: list[str] = []
    if intake_payload.get("schema_version") != INTAKE_SCHEMA_VERSION:
        blockers.append("intake_schema_invalid")
    intake_status = _text(intake_payload.get("intake_status"))
    if intake_status != "accepted" or intake_payload.get("accepted_for_downstream") is not True:
        if intake_payload.get("repair_required") is True:
            blockers.append("requires_operator_repair")
        blockers.append(f"intake_not_accepted:{intake_status or 'missing'}")
    if _text(intake_payload.get("source_read_ref")) != read_ref:
        blockers.append("source_read_ref_mismatch")
    downstream = _mapping(intake_payload.get("downstream_allowed"))
    if downstream.get("can_update_sidecar") is not False:
        blockers.append("sidecar_update_allowed_by_intake")
    if downstream.get("can_authorize_agent_action") is not False:
        blockers.append("agent_action_allowed_by_intake")
    if downstream.get("can_be_used_as_quality_label") is not False:
        blockers.append("quality_label_allowed_by_intake")
    if not intake_ref:
        blockers.append("intake_ref_missing")
    return blockers


def _brief_supply_blockers(
    *,
    supply_payload: Mapping[str, Any] | None,
    supply_error: str | None,
) -> list[str]:
    if supply_error == "not_found":
        return ["brief_supply_missing"]
    if supply_error:
        return [f"brief_supply_unreadable:{supply_error}"]
    if not isinstance(supply_payload, Mapping):
        return ["brief_supply_missing"]
    blockers: list[str] = []
    if supply_payload.get("schema_version") != SUPPLY_SCHEMA_VERSION:
        blockers.append("brief_supply_schema_invalid")
    if supply_payload.get("supply_status") != BRIEF_SUPPLY_READY_STATUS:
        blockers.append(
            f"brief_supply_not_ready:{_text(supply_payload.get('supply_status'), 'missing')}"
        )
    if supply_payload.get("blocker_reasons") not in ([], None):
        blockers.append("brief_supply_has_blockers")
    downstream = _mapping(supply_payload.get("downstream_allowed"))
    if downstream.get("can_update_sidecar") is not False:
        blockers.append("sidecar_update_allowed_by_brief_supply")
    if downstream.get("can_authorize_agent_action") is not False:
        blockers.append("agent_action_allowed_by_brief_supply")
    if downstream.get("can_be_used_as_quality_label") is not False:
        blockers.append("quality_label_allowed_by_brief_supply")
    custody = _mapping(supply_payload.get("custody_flags"))
    for key in (
        "product_proof",
        "human_validated",
        "answer_quality_scored",
        "agent_action_authorized",
        "automatic_action_authorized",
    ):
        if custody.get(key) is True:
            blockers.append(f"{key}_claimed_by_brief_supply")
    if _safe_int(custody.get("model_calls")) != 0:
        blockers.append("model_calls_claimed_by_brief_supply")
    return blockers


def _source_ref_summary(
    fields: list[Mapping[str, Any]],
    supply_payload: Mapping[str, Any] | None,
) -> dict[str, Any]:
    missing: list[str] = []
    malformed: list[str] = []
    local_path: list[str] = []
    checked = 0
    for index, field in enumerate(fields):
        name = _field_name(field, index)
        if _text(field.get("field_name")) not in ALLOWED_ROUTING_FIELD_NAMES:
            continue
        if _text(field.get("status")) in {"insufficient_context", "not_interpreted", "not_applicable"}:
            continue
        refs = field.get("source_refs")
        if not isinstance(refs, list) or not refs:
            missing.append(name)
            continue
        for ref in refs:
            if not isinstance(ref, Mapping):
                malformed.append(name)
                continue
            checked += 1
            artifact = _text(ref.get("artifact"))
            if not artifact:
                malformed.append(name)
            elif _looks_like_local_absolute_path(artifact):
                local_path.append(name)
    supply_source_status = _text(
        _mapping(supply_payload).get("source_ref_summary", {}).get("status")
        if isinstance(_mapping(supply_payload).get("source_ref_summary"), Mapping)
        else ""
    )
    if supply_payload and supply_source_status and supply_source_status != "passed":
        malformed.append("brief_supply_source_ref_summary")
    blockers: list[str] = []
    if missing:
        blockers.append("missing_source_refs")
    if malformed:
        blockers.append("malformed_source_refs")
    if local_path:
        blockers.append("local_absolute_path_in_source_ref")
    return {
        "status": "passed" if not blockers else "blocked",
        "checked_source_ref_count": checked,
        "missing_source_ref_fields": _dedupe(missing),
        "malformed_source_ref_fields": _dedupe(malformed),
        "local_absolute_path_fields": _dedupe(local_path),
        "source_refs_preserved": True,
        "blocker_reasons": blockers,
    }


def _uncertainty_summary(
    fields: list[Mapping[str, Any]],
    supply_payload: Mapping[str, Any] | None,
) -> dict[str, Any]:
    missing: list[str] = []
    invalid: list[str] = []
    allowed = {"low", "medium", "high", "insufficient_context"}
    for index, field in enumerate(fields):
        name = _field_name(field, index)
        if _text(field.get("field_name")) not in ALLOWED_ROUTING_FIELD_NAMES:
            continue
        if _text(field.get("status")) in {"insufficient_context", "not_interpreted", "not_applicable"}:
            continue
        uncertainty = _text(field.get("uncertainty"))
        if not uncertainty:
            missing.append(name)
        elif uncertainty not in allowed:
            invalid.append(name)
    supply_uncertainty = _mapping(supply_payload).get("uncertainty_summary")
    if isinstance(supply_uncertainty, Mapping) and supply_uncertainty.get("status") != "passed":
        invalid.append("brief_supply_uncertainty_summary")
    blockers: list[str] = []
    if missing:
        blockers.append("missing_uncertainty")
    if invalid:
        blockers.append("invalid_uncertainty")
    return {
        "status": "passed" if not blockers else "blocked",
        "missing_uncertainty_fields": _dedupe(missing),
        "invalid_uncertainty_fields": _dedupe(invalid),
        "uncertainty_preserved": True,
        "blocker_reasons": blockers,
    }


def _privacy_summary(
    *,
    input_texts: list[str],
    fields: list[Mapping[str, Any]],
) -> dict[str, Any]:
    missing_privacy: list[str] = []
    for index, field in enumerate(fields):
        name = _field_name(field, index)
        if _text(field.get("field_name")) not in ALLOWED_ROUTING_FIELD_NAMES:
            continue
        if _text(field.get("status")) in {"insufficient_context", "not_interpreted", "not_applicable"}:
            continue
        if not _text(field.get("privacy_limit")):
            missing_privacy.append(name)
    private_marker = any(_contains_private_marker(text) for text in input_texts if text)
    local_path = any(
        _contains_local_absolute_path_marker(text) for text in input_texts if text
    )
    blockers: list[str] = []
    if private_marker:
        blockers.append("privacy_marker_detected")
    if local_path:
        blockers.append("local_absolute_path_detected")
    if missing_privacy:
        blockers.append("missing_privacy_limit")
    return {
        "status": "passed" if not blockers else "blocked",
        "privacy_marker_detected": private_marker,
        "local_absolute_path_detected": local_path,
        "missing_privacy_limit_fields": _dedupe(missing_privacy),
        "raw_private_content_included": False,
        "provider_text_included": False,
        "blocker_reasons": blockers,
    }


def _allowed_routing_inputs(
    *,
    read_fields: list[Mapping[str, Any]],
    supply: Mapping[str, Any] | None,
    rendered_brief_available: bool,
    ready: bool,
) -> list[dict[str, Any]]:
    if not ready:
        return []
    supply_fields = _list_of_mappings(_mapping(supply).get("allowed_brief_feed"))
    if supply_fields:
        fields = supply_fields
    else:
        fields = read_fields
    result: list[dict[str, Any]] = []
    for field in fields:
        name = _text(field.get("field_name"))
        if name not in ALLOWED_ROUTING_FIELD_NAMES:
            continue
        result.append(
            {
                "field_name": name,
                "status": _text(field.get("status")),
                "value": field.get("value"),
                "source_refs": field.get("source_refs") if isinstance(field.get("source_refs"), list) else [],
                "source_status": _text(field.get("source_status")),
                "uncertainty": _text(field.get("uncertainty")),
                "interpretation_basis": _text(field.get("interpretation_basis")),
                "privacy_limit": _text(field.get("privacy_limit")),
                "rendered_brief_available": rendered_brief_available,
                "must_not_be_used_as_quality_label": True,
            }
        )
    return result


def _evidence_only_inputs(supply: Mapping[str, Any] | None) -> list[str]:
    values = list(EVIDENCE_ONLY_FIELDS)
    if isinstance(supply, Mapping):
        supplied = supply.get("evidence_only_fields")
        if isinstance(supplied, list):
            values.extend(str(item) for item in supplied if isinstance(item, str))
    return sorted(set(values))


def _triage_supply_status(blockers: list[str]) -> str:
    if not blockers:
        return READY_STATUS
    blocker_set = set(blockers)
    if blocker_set.intersection(
        {
            "privacy_marker_detected",
            "local_absolute_path_detected",
            "local_absolute_path_in_source_ref",
            "missing_privacy_limit",
            "raw_private_content_checked_in_claimed",
            "provider_text_checked_in_claimed",
            "local_absolute_paths_checked_in_claimed",
        }
    ):
        return "blocked_privacy_risk"
    if any(
        blocker in blocker_set
        for blocker in (
            "product_proof_claimed",
            "human_validated_claimed",
            "answer_quality_scored_claimed",
            "agent_action_authorized_claimed",
            "automatic_action_authorized_claimed",
            "model_calls_claimed",
            "sidecar_update_allowed_by_intake",
            "agent_action_allowed_by_intake",
            "quality_label_allowed_by_intake",
            "sidecar_update_allowed_by_brief_supply",
            "agent_action_allowed_by_brief_supply",
            "quality_label_allowed_by_brief_supply",
            "product_proof_claimed_by_brief_supply",
            "human_validated_claimed_by_brief_supply",
            "answer_quality_scored_claimed_by_brief_supply",
            "agent_action_authorized_claimed_by_brief_supply",
            "automatic_action_authorized_claimed_by_brief_supply",
            "model_calls_claimed_by_brief_supply",
        )
    ):
        return "blocked_authority_claim"
    if "requires_operator_repair" in blocker_set:
        return "requires_operator_repair"
    if any(blocker.startswith("intake_not_accepted") for blocker in blockers):
        return "blocked_intake_not_accepted"
    if "brief_supply_missing" in blocker_set:
        return "deferred_missing_brief_supply"
    if any(blocker.startswith("brief_supply") for blocker in blockers):
        return "blocked_brief_supply_not_ready"
    if "rendered_brief_missing" in blocker_set:
        return "deferred_missing_rendered_brief"
    if blocker_set.intersection({"missing_source_refs", "malformed_source_refs"}):
        return "blocked_missing_source_refs"
    if blocker_set.intersection({"missing_uncertainty", "invalid_uncertainty"}):
        return "blocked_missing_uncertainty"
    return "requires_operator_repair"


def _custody_blockers(read: Mapping[str, Any]) -> list[str]:
    custody = read.get("custody_flags")
    if not isinstance(custody, Mapping):
        return ["custody_flags_missing"]
    blockers: list[str] = []
    for flag in AUTHORITY_CUSTODY_FLAGS:
        if custody.get(flag) is True:
            blockers.append(f"{flag}_claimed")
    if _safe_int(custody.get("model_calls")) != 0:
        blockers.append("model_calls_claimed")
    if custody.get("semantic_read_is_provisional") is not True:
        blockers.append("semantic_read_not_provisional")
    return blockers


def _custody_flags() -> dict[str, Any]:
    return {
        "model_calls": 0,
        "runtime_invoked": False,
        "skill_invoked": False,
        "archive_mutated": False,
        "runtime_behavior_changed": False,
        "triage_generated": False,
        "triage_read_created": False,
        "resolver_refs_marked_usable": False,
        "runtime_sidecar_updated": False,
        "product_proof": False,
        "human_validated": False,
        "answer_quality_scored": False,
        "agent_action_authorized": False,
        "automatic_action_authorized": False,
        "raw_private_content_included": False,
        "provider_text_included": False,
        "local_absolute_paths_included": False,
    }


def _load_json_text(path: Path | str, description: str) -> tuple[str, dict[str, Any]]:
    candidate = _resolve(path)
    try:
        text = candidate.read_text(encoding="utf-8")
        payload = json.loads(text)
    except FileNotFoundError as exc:
        raise DecisionWorkGeneratedReadTriageSupplyError(
            f"{description} was not found"
        ) from exc
    except json.JSONDecodeError as exc:
        raise DecisionWorkGeneratedReadTriageSupplyError(
            f"{description} was not valid JSON"
        ) from exc
    except UnicodeDecodeError as exc:
        raise DecisionWorkGeneratedReadTriageSupplyError(
            f"{description} was not valid UTF-8"
        ) from exc
    except OSError as exc:
        raise DecisionWorkGeneratedReadTriageSupplyError(
            f"{description} could not be read:{type(exc).__name__}"
        ) from exc
    if not isinstance(payload, dict):
        raise DecisionWorkGeneratedReadTriageSupplyError(
            f"{description} JSON root was not an object"
        )
    return text, payload


def _load_optional_json_text(
    path: Path | str,
    description: str,
) -> tuple[str, dict[str, Any] | None, str | None]:
    candidate = _resolve(path)
    try:
        text = candidate.read_text(encoding="utf-8")
        payload = json.loads(text)
    except FileNotFoundError:
        return "", None, "not_found"
    except json.JSONDecodeError:
        return "", None, "invalid_json"
    except UnicodeDecodeError:
        return "", None, "invalid_utf8"
    except OSError as exc:
        return "", None, type(exc).__name__
    if not isinstance(payload, dict):
        return text, None, "not_object"
    return text, payload, None


def _load_optional_text(path: Path | str, description: str) -> tuple[str, str | None]:
    candidate = _resolve(path)
    try:
        return candidate.read_text(encoding="utf-8"), None
    except FileNotFoundError:
        return "", "not_found"
    except UnicodeDecodeError:
        return "", "invalid_utf8"
    except OSError as exc:
        return "", type(exc).__name__


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


def _optional_ref(path: Path | str | None) -> dict[str, Any]:
    if path is None:
        return {"input_ref": None, "status": "not_supplied", "content_included": False}
    return {
        "input_ref": _safe_ref(_resolve(path)),
        "status": "supplied",
        "content_included": False,
    }


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


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


def _contains_private_marker(text: str) -> bool:
    return any(marker in text for marker in RAW_PRIVATE_MARKERS)


def _contains_local_absolute_path_marker(text: str) -> bool:
    return any(marker in text for marker in LOCAL_ABSOLUTE_PATH_MARKERS)


def _looks_like_local_absolute_path(value: str) -> bool:
    if Path(value).is_absolute():
        return True
    return bool(re.search(r"(^|\\s)/(Users|home|private)/", value))


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
