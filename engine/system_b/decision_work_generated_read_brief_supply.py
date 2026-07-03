"""Deterministic brief-supply adapter for accepted generated reads.

PR186 turns an accepted PR182 intake result plus its source read into a safe
brief-supply packet for later offline rendering. It validates, normalizes, and
copies allowed fields. It does not add semantic interpretation, render briefs,
enrich briefs, generate triage, approve resolver refs, update sidecars, call
models, score advice, or authorize action.
"""
from __future__ import annotations

import datetime as _dt
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any


SUPPLY_SCHEMA_VERSION = "lolla.decision_work_generated_read_brief_supply.v0"
INTAKE_SCHEMA_VERSION = "lolla.decision_work_generated_interpretation_read_intake.v0"
READ_SCHEMA_VERSION = "lolla.decision_work_conversation_interpretation_read.v0"
REPO_ROOT = Path(__file__).resolve().parents[2]

READY_STATUS = "ready_for_offline_brief_rendering"
REQUIRED_FIELDS = {
    "decision_question",
    "revised_direction_or_action_consequence",
    "what_the_final_answer_does_not_prove",
}
ALLOWED_BRIEF_FEED_FIELDS = {
    "decision_question",
    "likely_starting_direction",
    "revised_direction_or_action_consequence",
    "decision_thresholds",
    "evidence_gates",
    "useful_friction",
    "what_the_final_answer_does_not_prove",
}
EVIDENCE_ONLY_FIELDS = {
    "live_options",
    "abandoned_or_rejected_options",
    "noisy_friction",
    "lost_value",
    "assistant_influence_on_user_framing",
    "safe_for_agent_inspection_only",
}
SKIPPED_FIELD_STATUSES = {
    "insufficient_context",
    "not_interpreted",
    "not_applicable",
}
ALLOWED_UNCERTAINTY = {"low", "medium", "high", "insufficient_context"}
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
    "brief_supply_is_deterministic_copying_only",
    "brief_supply_does_not_generate_interpretation",
    "brief_supply_does_not_render_briefs",
    "brief_supply_does_not_enrich_briefs",
    "brief_supply_does_not_generate_triage",
    "brief_supply_does_not_update_resolver_refs",
    "brief_supply_does_not_update_runtime_sidecars",
    "brief_supply_is_not_product_proof",
    "brief_supply_is_not_human_validation",
    "brief_supply_does_not_score_answer_quality",
    "brief_supply_does_not_validate_advice_correctness",
    "brief_supply_does_not_authorize_agent_action",
    "brief_supply_does_not_authorize_automatic_action",
)


class DecisionWorkGeneratedReadBriefSupplyError(ValueError):
    """Sanitized generated-read brief-supply input/output error."""


def build_generated_read_brief_supply(
    *,
    read_path: Path | str,
    intake_path: Path | str,
    queue_item_path: Path | str | None = None,
    prompt_packet_path: Path | str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build a deterministic generated-read brief-supply packet."""

    read_ref = _safe_ref(_resolve(read_path))
    intake_ref = _safe_ref(_resolve(intake_path))
    read_text, read_payload = _load_json_text(read_path, "generated read")
    intake_text, intake_payload = _load_json_text(intake_path, "intake result")

    blockers: list[str] = []
    if _contains_private_marker(read_text) or _contains_private_marker(intake_text):
        blockers.append("privacy_marker_detected")
    if _contains_local_absolute_path_marker(read_text) or _contains_local_absolute_path_marker(
        intake_text
    ):
        blockers.append("local_absolute_path_detected")

    intake_status = _text(intake_payload.get("intake_status"))
    if intake_payload.get("schema_version") != INTAKE_SCHEMA_VERSION:
        blockers.append("intake_schema_invalid")
    if intake_status != "accepted" or intake_payload.get("accepted_for_downstream") is not True:
        blockers.append(f"intake_not_accepted:{intake_status or 'missing'}")
    if _text(intake_payload.get("source_read_ref")) != read_ref:
        blockers.append("source_read_ref_mismatch")

    downstream = intake_payload.get("downstream_allowed")
    if not isinstance(downstream, Mapping):
        blockers.append("intake_downstream_allowed_missing")
    else:
        if downstream.get("can_update_sidecar") is not False:
            blockers.append("sidecar_update_allowed_by_intake")
        if downstream.get("can_authorize_agent_action") is not False:
            blockers.append("agent_action_allowed_by_intake")
        if downstream.get("can_be_used_as_quality_label") is not False:
            blockers.append("quality_label_allowed_by_intake")

    if read_payload.get("schema_version") != READ_SCHEMA_VERSION:
        blockers.append("read_schema_invalid")
    blockers.extend(_custody_blockers(read_payload))

    fields = _list_of_mappings(read_payload.get("interpreted_fields"))
    allowed_feed, evidence_only_seen = _classify_fields(fields)
    source_summary = _source_ref_summary(fields)
    uncertainty_summary = _uncertainty_summary(fields)
    privacy_summary = _privacy_summary(read_text, intake_text, fields)
    blockers.extend(source_summary["blocker_reasons"])
    blockers.extend(uncertainty_summary["blocker_reasons"])
    blockers.extend(privacy_summary["blocker_reasons"])

    missing_required = sorted(REQUIRED_FIELDS - {item["field_name"] for item in allowed_feed})
    if missing_required:
        blockers.append("missing_required_fields")

    blockers = _dedupe(blockers)
    supply_status = _supply_status(blockers)
    ready = supply_status == READY_STATUS

    return {
        "schema_version": SUPPLY_SCHEMA_VERSION,
        "supply_metadata": {
            "created_at": created_at or _utc_now(),
            "generated_by": "decision_work_generated_read_brief_supply",
            "adapter_scope": "deterministic_field_copying_and_validation_only",
            "model_calls": 0,
            "runtime_invoked": False,
            "skill_invoked": False,
        },
        "source_read_ref": read_ref,
        "intake_ref": intake_ref,
        "queue_item_ref": _optional_ref(queue_item_path),
        "prompt_packet_ref": _optional_ref(prompt_packet_path),
        "supply_status": supply_status,
        "blocker_reasons": blockers,
        "allowed_brief_feed": allowed_feed if ready else [],
        "evidence_only_fields": sorted(set(evidence_only_seen) | EVIDENCE_ONLY_FIELDS),
        "missing_required_fields": missing_required,
        "source_ref_summary": source_summary,
        "uncertainty_summary": uncertainty_summary,
        "privacy_summary": privacy_summary,
        "custody_flags": _custody_flags(),
        "downstream_allowed": {
            "can_render_offline_brief": ready,
            "can_feed_enrichment": ready,
            "can_feed_triage_packet": ready,
            "can_feed_resolver": ready,
            "can_update_sidecar": False,
            "can_authorize_agent_action": False,
            "can_be_used_as_quality_label": False,
        },
        "non_claims": list(NON_CLAIMS),
    }


def render_generated_read_brief_supply_json(
    result: Mapping[str, Any],
    *,
    pretty: bool = False,
) -> str:
    """Render a generated-read brief-supply packet as stable JSON."""

    if pretty:
        return json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return json.dumps(result, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"


def write_generated_read_brief_supply(path: Path | str, payload: str) -> None:
    """Write a generated-read brief-supply packet."""

    output = Path(path).expanduser()
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    except OSError as exc:
        raise DecisionWorkGeneratedReadBriefSupplyError(
            f"output could not be written:{type(exc).__name__}"
        ) from exc


def _load_json_text(path: Path | str, description: str) -> tuple[str, dict[str, Any]]:
    candidate = _resolve(path)
    try:
        text = candidate.read_text(encoding="utf-8")
        payload = json.loads(text)
    except FileNotFoundError as exc:
        raise DecisionWorkGeneratedReadBriefSupplyError(
            f"{description} was not found"
        ) from exc
    except json.JSONDecodeError as exc:
        raise DecisionWorkGeneratedReadBriefSupplyError(
            f"{description} was not valid JSON"
        ) from exc
    except UnicodeDecodeError as exc:
        raise DecisionWorkGeneratedReadBriefSupplyError(
            f"{description} was not valid UTF-8"
        ) from exc
    except OSError as exc:
        raise DecisionWorkGeneratedReadBriefSupplyError(
            f"{description} could not be read:{type(exc).__name__}"
        ) from exc
    if not isinstance(payload, dict):
        raise DecisionWorkGeneratedReadBriefSupplyError(
            f"{description} JSON root was not an object"
        )
    return text, payload


def _classify_fields(fields: list[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    allowed: list[dict[str, Any]] = []
    evidence_only: list[str] = []
    for field in fields:
        name = _text(field.get("field_name"))
        status = _text(field.get("status"))
        if name in EVIDENCE_ONLY_FIELDS:
            evidence_only.append(name)
            continue
        if name not in ALLOWED_BRIEF_FEED_FIELDS:
            continue
        if status in SKIPPED_FIELD_STATUSES:
            continue
        if field.get("must_not_be_used_as_quality_label") is not True:
            continue
        allowed.append(
            {
                "field_name": name,
                "field_group": _text(field.get("field_group")),
                "status": status,
                "value": field.get("value"),
                "uncertainty": _text(field.get("uncertainty")),
                "source_refs": field.get("source_refs") if isinstance(field.get("source_refs"), list) else [],
                "source_status": _text(field.get("source_status")),
                "interpretation_basis": _text(field.get("interpretation_basis")),
                "privacy_limit": _text(field.get("privacy_limit")),
                "human_review_required": field.get("human_review_required") is True,
                "could_feed_brief": field.get("could_feed_brief") is True,
                "must_not_be_used_as_quality_label": True,
            }
        )
    return allowed, evidence_only


def _source_ref_summary(fields: list[Mapping[str, Any]]) -> dict[str, Any]:
    missing: list[str] = []
    local_path: list[str] = []
    malformed: list[str] = []
    checked = 0
    for index, field in enumerate(fields):
        name = _field_name(field, index)
        if _text(field.get("field_name")) not in ALLOWED_BRIEF_FEED_FIELDS:
            continue
        if _text(field.get("status")) in SKIPPED_FIELD_STATUSES:
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


def _uncertainty_summary(fields: list[Mapping[str, Any]]) -> dict[str, Any]:
    missing: list[str] = []
    invalid: list[str] = []
    for index, field in enumerate(fields):
        name = _field_name(field, index)
        if _text(field.get("field_name")) not in ALLOWED_BRIEF_FEED_FIELDS:
            continue
        if _text(field.get("status")) in SKIPPED_FIELD_STATUSES:
            continue
        uncertainty = _text(field.get("uncertainty"))
        if not uncertainty:
            missing.append(name)
        elif uncertainty not in ALLOWED_UNCERTAINTY:
            invalid.append(name)
    blockers: list[str] = []
    if missing:
        blockers.append("missing_uncertainty")
    if invalid:
        blockers.append("invalid_uncertainty")
    return {
        "status": "passed" if not blockers else "blocked",
        "missing_uncertainty_fields": missing,
        "invalid_uncertainty_fields": invalid,
        "blocker_reasons": blockers,
    }


def _privacy_summary(
    read_text: str,
    intake_text: str,
    fields: list[Mapping[str, Any]],
) -> dict[str, Any]:
    missing_privacy: list[str] = []
    for index, field in enumerate(fields):
        name = _field_name(field, index)
        if _text(field.get("field_name")) not in ALLOWED_BRIEF_FEED_FIELDS:
            continue
        if _text(field.get("status")) in SKIPPED_FIELD_STATUSES:
            continue
        if not _text(field.get("privacy_limit")):
            missing_privacy.append(name)
    private_marker = _contains_private_marker(read_text) or _contains_private_marker(intake_text)
    local_path = _contains_local_absolute_path_marker(read_text) or _contains_local_absolute_path_marker(intake_text)
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
        "missing_privacy_limit_fields": missing_privacy,
        "raw_private_content_included": False,
        "provider_text_included": False,
        "blocker_reasons": blockers,
    }


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


def _supply_status(blockers: list[str]) -> str:
    if not blockers:
        return READY_STATUS
    blocker_set = set(blockers)
    if "missing_required_fields" in blocker_set:
        return "deferred_missing_required_fields"
    if any(blocker.startswith("intake_not_accepted") for blocker in blockers):
        if any("requires_operator_repair" in blocker for blocker in blockers):
            return "requires_operator_repair"
        return "blocked_intake_not_accepted"
    if blocker_set.intersection({"missing_source_refs", "malformed_source_refs"}):
        return "blocked_missing_source_refs"
    if blocker_set.intersection({"missing_uncertainty", "invalid_uncertainty"}):
        return "blocked_missing_uncertainty"
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
        )
    ):
        return "blocked_authority_claim"
    if "source_read_ref_mismatch" in blocker_set:
        return "blocked_intake_not_accepted"
    return "requires_operator_repair"


def _custody_flags() -> dict[str, Any]:
    return {
        "model_calls": 0,
        "runtime_invoked": False,
        "skill_invoked": False,
        "archive_mutated": False,
        "runtime_behavior_changed": False,
        "product_proof": False,
        "human_validated": False,
        "answer_quality_scored": False,
        "agent_action_authorized": False,
        "automatic_action_authorized": False,
        "raw_private_content_included": False,
        "provider_text_included": False,
        "local_absolute_paths_included": False,
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


def _optional_ref(path: Path | str | None) -> dict[str, Any]:
    if path is None:
        return {"input_ref": None, "status": "not_supplied", "content_included": False}
    return {
        "input_ref": _safe_ref(_resolve(path)),
        "status": "supplied",
        "content_included": False,
    }


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
