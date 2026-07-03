"""Deterministic resolver-supply adapter for generated-read artifacts.

PR198 prepares generated-read artifacts for future resolver inspection. It
validates and normalizes refs, status, routes, uncertainty, privacy, custody,
and non-claims. It does not approve resolver refs, update runtime sidecars,
wire runtime, call models, score advice, or authorize action.
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
from engine.system_b.decision_work_generated_read_triage_supply import (
    READY_STATUS as TRIAGE_SUPPLY_READY_STATUS,
    TRIAGE_SUPPLY_SCHEMA_VERSION,
)


RESOLVER_SUPPLY_SCHEMA_VERSION = (
    "lolla.decision_work_generated_read_resolver_supply.v0"
)
READ_SCHEMA_VERSION = "lolla.decision_work_conversation_interpretation_read.v0"
INTAKE_SCHEMA_VERSION = "lolla.decision_work_generated_interpretation_read_intake.v0"
TRIAGE_SCHEMA_VERSION = "lolla.decision_work_generated_read_triage.v0"
READY_STATUS = "ready_for_resolver_candidate_packet"
RUNTIME_BLOCK_STATUS = "candidate_packet_with_runtime_block"
REPO_ROOT = Path(__file__).resolve().parents[2]

RUNTIME_BLOCKING_ROUTES = {
    "runtime_attachment_blocked",
}
USER_SURFACE_BLOCKING_ROUTES = {
    "agent_inspection_only",
    "not_ready_for_user_surface",
}
HIGH_REVIEW_ROUTES = {
    "domain_review_recommended",
    "legal_or_compliance_review_recommended",
    "relationship_or_governance_sensitive",
}
FORBIDDEN_ROUTE_CATEGORIES = {
    "good_answer",
    "bad_answer",
    "approved",
    "certified",
    "safe_to_act",
    "safe_to_deploy",
    "correct_advice",
    "lolla_improved_decision",
    "human_validated",
    "product_proof",
    "agent_action_authorized",
    "automatic_action_authorized",
}
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
    "raw_private_content_included",
    "provider_text_included",
    "local_absolute_paths_included",
    "raw_private_content_checked_in",
    "provider_text_checked_in",
    "local_absolute_paths_checked_in",
    "resolver_refs_marked_usable",
    "resolver_refs_approved",
    "runtime_sidecar_updated",
)
NON_CLAIMS = (
    "resolver_supply_is_candidate_preparation_only",
    "resolver_supply_does_not_approve_resolver_refs",
    "resolver_supply_does_not_mark_resolver_refs_usable",
    "resolver_supply_does_not_update_runtime_sidecars",
    "resolver_supply_does_not_wire_runtime",
    "resolver_supply_does_not_generate_interpretation",
    "resolver_supply_does_not_generate_triage",
    "resolver_supply_is_not_product_proof",
    "resolver_supply_is_not_human_validation",
    "resolver_supply_does_not_score_answer_quality",
    "resolver_supply_does_not_validate_advice_correctness",
    "resolver_supply_does_not_authorize_agent_action",
    "resolver_supply_does_not_authorize_automatic_action",
)


class DecisionWorkGeneratedReadResolverSupplyError(ValueError):
    """Sanitized generated-read resolver-supply input/output error."""


def build_generated_read_resolver_supply(
    *,
    read_path: Path | str,
    intake_path: Path | str,
    brief_supply_path: Path | str,
    rendered_brief_path: Path | str,
    triage_supply_path: Path | str,
    triage_path: Path | str,
    queue_item_path: Path | str | None = None,
    prompt_packet_path: Path | str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build a deterministic generated-read resolver-supply candidate packet."""

    read_ref = _safe_ref(_resolve(read_path))
    intake_ref = _safe_ref(_resolve(intake_path))
    brief_supply_ref = _safe_ref(_resolve(brief_supply_path))
    rendered_brief_ref = _safe_ref(_resolve(rendered_brief_path))
    triage_supply_ref = _safe_ref(_resolve(triage_supply_path))
    triage_ref = _safe_ref(_resolve(triage_path))

    read_text, read_payload = _load_json_text(read_path, "generated read")
    intake_text, intake_payload = _load_json_text(intake_path, "intake result")
    brief_supply_text, brief_supply_payload, brief_supply_error = (
        _load_optional_json_text(brief_supply_path, "brief supply packet")
    )
    rendered_text, rendered_error = _load_optional_text(
        rendered_brief_path,
        "rendered brief",
    )
    triage_supply_text, triage_supply_payload, triage_supply_error = (
        _load_optional_json_text(triage_supply_path, "triage supply packet")
    )
    triage_text, triage_payload, triage_error = _load_optional_json_text(
        triage_path,
        "triage read",
    )

    blockers: list[str] = []
    input_texts = [
        read_text,
        intake_text,
        brief_supply_text,
        rendered_text,
        triage_supply_text,
        triage_text,
    ]
    if any(_contains_private_marker(text) for text in input_texts if text):
        blockers.append("privacy_marker_detected")
    if any(_contains_local_absolute_path_marker(text) for text in input_texts if text):
        blockers.append("local_absolute_path_detected")

    blockers.extend(_read_blockers(read_payload))
    blockers.extend(_intake_blockers(intake_payload, intake_ref, read_ref))
    blockers.extend(_brief_supply_blockers(brief_supply_payload, brief_supply_error))
    if rendered_error == "not_found":
        blockers.append("rendered_brief_missing")
    elif rendered_error:
        blockers.append(f"rendered_brief_unreadable:{rendered_error}")
    blockers.extend(_triage_supply_blockers(triage_supply_payload, triage_supply_error))
    blockers.extend(_triage_blockers(triage_payload, triage_error))

    route_summary = _route_summary(triage_payload)
    source_ref_summary = _source_ref_summary(
        read_payload=read_payload,
        triage_payload=triage_payload,
        brief_supply_payload=brief_supply_payload,
        triage_supply_payload=triage_supply_payload,
    )
    uncertainty_summary = _uncertainty_summary(read_payload, triage_payload)
    privacy_summary = _privacy_summary(input_texts)
    blockers.extend(route_summary["blocker_reasons"])
    blockers.extend(source_ref_summary["blocker_reasons"])
    blockers.extend(uncertainty_summary["blocker_reasons"])
    blockers.extend(privacy_summary["blocker_reasons"])

    blockers = _dedupe(blockers)
    resolver_supply_status = _resolver_supply_status(blockers, route_summary)
    candidate_ready = resolver_supply_status in {READY_STATUS, RUNTIME_BLOCK_STATUS}

    return {
        "schema_version": RESOLVER_SUPPLY_SCHEMA_VERSION,
        "resolver_supply_metadata": {
            "created_at": created_at or _utc_now(),
            "generated_by": "decision_work_generated_read_resolver_supply",
            "adapter_scope": "deterministic_resolver_candidate_preparation_only",
            "model_calls": 0,
            "runtime_invoked": False,
            "skill_invoked": False,
        },
        "source_case": _source_case(read_payload, triage_payload),
        "source_read_ref": read_ref,
        "source_intake_ref": intake_ref,
        "source_brief_supply_ref": brief_supply_ref,
        "source_rendered_brief_ref": rendered_brief_ref,
        "source_triage_supply_ref": triage_supply_ref,
        "source_triage_ref": triage_ref,
        "optional_queue_item_ref": _optional_ref(queue_item_path),
        "optional_prompt_packet_ref": _optional_ref(prompt_packet_path),
        "resolver_supply_status": resolver_supply_status,
        "blocker_reasons": blockers,
        "safe_ref_candidates": _safe_ref_candidates(
            ready=candidate_ready,
            read_ref=read_ref,
            intake_ref=intake_ref,
            intake_payload=intake_payload,
            brief_supply_ref=brief_supply_ref,
            brief_supply_payload=brief_supply_payload,
            rendered_brief_ref=rendered_brief_ref,
            triage_supply_ref=triage_supply_ref,
            triage_supply_payload=triage_supply_payload,
            triage_ref=triage_ref,
            triage_payload=triage_payload,
            route_summary=route_summary,
            source_ref_summary=source_ref_summary,
            uncertainty_summary=uncertainty_summary,
            privacy_summary=privacy_summary,
        ),
        "evidence_only_refs": _evidence_only_refs(
            read_ref=read_ref,
            rendered_brief_ref=rendered_brief_ref,
            triage_ref=triage_ref,
        ),
        "route_summary": route_summary,
        "runtime_use_status": _runtime_use_status(route_summary),
        "user_surface_status": _user_surface_status(route_summary),
        "agent_inspection_status": _agent_inspection_status(route_summary),
        "required_operator_review": _required_operator_review(route_summary),
        "required_source_refs": source_ref_summary,
        "uncertainty_summary": uncertainty_summary,
        "privacy_summary": privacy_summary,
        "custody_flags": _custody_flags(),
        "non_claims": list(NON_CLAIMS),
        "downstream_allowed": {
            "can_feed_future_resolver_review": candidate_ready,
            "resolver_refs_approved": False,
            "can_update_sidecar": False,
            "can_write_runtime_sidecar": False,
            "can_authorize_agent_action": False,
            "can_authorize_automatic_action": False,
            "can_be_used_as_quality_label": False,
            "product_proof": False,
            "human_validated": False,
            "answer_quality_scored": False,
            "advice_correctness_claimed": False,
        },
        "downstream_forbidden": [
            "approve_resolver_refs",
            "mark_resolver_refs_usable",
            "update_runtime_sidecar",
            "write_runtime_sidecar",
            "wire_runtime",
            "call_models_or_providers",
            "score_answer_quality",
            "claim_product_proof",
            "claim_human_validation",
            "claim_advice_correctness",
            "authorize_agent_or_automatic_action",
        ],
    }


def render_generated_read_resolver_supply_json(
    result: Mapping[str, Any],
    *,
    pretty: bool = False,
) -> str:
    """Render a generated-read resolver-supply packet as stable JSON."""

    if pretty:
        return json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return json.dumps(result, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"


def write_generated_read_resolver_supply(path: Path | str, payload: str) -> None:
    """Write a generated-read resolver-supply packet."""

    output = Path(path).expanduser()
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    except OSError as exc:
        raise DecisionWorkGeneratedReadResolverSupplyError(
            f"output could not be written:{type(exc).__name__}"
        ) from exc


def _read_blockers(read: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if read.get("schema_version") != READ_SCHEMA_VERSION:
        blockers.append("read_schema_invalid")
    blockers.extend(_custody_blockers(read))
    return blockers


def _intake_blockers(
    intake: Mapping[str, Any],
    intake_ref: str,
    read_ref: str,
) -> list[str]:
    blockers: list[str] = []
    if intake.get("schema_version") != INTAKE_SCHEMA_VERSION:
        blockers.append("intake_schema_invalid")
    intake_status = _text(intake.get("intake_status"))
    if intake_status != "accepted" or intake.get("accepted_for_downstream") is not True:
        if intake.get("repair_required") is True:
            blockers.append("requires_operator_repair")
        blockers.append(f"intake_not_accepted:{intake_status or 'missing'}")
    if _text(intake.get("source_read_ref")) != read_ref:
        blockers.append("source_read_ref_mismatch")
    downstream = _mapping(intake.get("downstream_allowed"))
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
    supply: Mapping[str, Any] | None,
    supply_error: str | None,
) -> list[str]:
    if supply_error == "not_found":
        return ["brief_supply_missing"]
    if supply_error:
        return [f"brief_supply_unreadable:{supply_error}"]
    if not isinstance(supply, Mapping):
        return ["brief_supply_missing"]
    blockers: list[str] = []
    if supply.get("schema_version") != SUPPLY_SCHEMA_VERSION:
        blockers.append("brief_supply_schema_invalid")
    if supply.get("supply_status") != BRIEF_SUPPLY_READY_STATUS:
        blockers.append(
            f"brief_supply_not_ready:{_text(supply.get('supply_status'), 'missing')}"
        )
    if supply.get("blocker_reasons") not in ([], None):
        blockers.append("brief_supply_has_blockers")
    downstream = _mapping(supply.get("downstream_allowed"))
    if downstream.get("can_update_sidecar") is not False:
        blockers.append("sidecar_update_allowed_by_brief_supply")
    if downstream.get("can_authorize_agent_action") is not False:
        blockers.append("agent_action_allowed_by_brief_supply")
    if downstream.get("can_be_used_as_quality_label") is not False:
        blockers.append("quality_label_allowed_by_brief_supply")
    blockers.extend(_custody_blockers(supply, suffix="_by_brief_supply"))
    return blockers


def _triage_supply_blockers(
    supply: Mapping[str, Any] | None,
    supply_error: str | None,
) -> list[str]:
    if supply_error == "not_found":
        return ["triage_supply_missing"]
    if supply_error:
        return [f"triage_supply_unreadable:{supply_error}"]
    if not isinstance(supply, Mapping):
        return ["triage_supply_missing"]
    blockers: list[str] = []
    if supply.get("schema_version") != TRIAGE_SUPPLY_SCHEMA_VERSION:
        blockers.append("triage_supply_schema_invalid")
    if supply.get("triage_supply_status") != TRIAGE_SUPPLY_READY_STATUS:
        blockers.append(
            "triage_supply_not_ready:"
            f"{_text(supply.get('triage_supply_status'), 'missing')}"
        )
    if supply.get("blocker_reasons") not in ([], None):
        blockers.append("triage_supply_has_blockers")
    downstream = _mapping(supply.get("downstream_allowed"))
    if downstream.get("can_update_sidecar") is not False:
        blockers.append("sidecar_update_allowed_by_triage_supply")
    if downstream.get("can_approve_resolver_refs") is not False:
        blockers.append("resolver_approval_allowed_by_triage_supply")
    if downstream.get("can_be_used_as_quality_label") is not False:
        blockers.append("quality_label_allowed_by_triage_supply")
    blockers.extend(_custody_blockers(supply, suffix="_by_triage_supply"))
    return blockers


def _triage_blockers(
    triage: Mapping[str, Any] | None,
    triage_error: str | None,
) -> list[str]:
    if triage_error == "not_found":
        return ["triage_missing"]
    if triage_error:
        return [f"triage_unreadable:{triage_error}"]
    if not isinstance(triage, Mapping):
        return ["triage_missing"]
    blockers: list[str] = []
    if triage.get("schema_version") != TRIAGE_SCHEMA_VERSION:
        blockers.append("triage_schema_invalid")
    if _text(triage.get("triage_status")) != "generated_provisional_checked_in_safe":
        blockers.append(f"triage_not_ready:{_text(triage.get('triage_status'), 'missing')}")
    if _text(triage.get("source_triage_supply_status")) != TRIAGE_SUPPLY_READY_STATUS:
        blockers.append("triage_source_supply_not_ready")
    if triage.get("forbidden_route_concepts_absent") is not True:
        blockers.append("forbidden_route_concepts_not_absent")
    routes = [item for item in triage.get("route_categories", []) if isinstance(item, str)]
    if not routes:
        blockers.append("triage_routes_missing")
    if FORBIDDEN_ROUTE_CATEGORIES.intersection(routes):
        blockers.append("forbidden_route_category_selected")
    explanations = _list_of_mappings(triage.get("route_explanations"))
    explanation_routes = {_text(item.get("route_category")) for item in explanations}
    for route in routes:
        if route not in explanation_routes:
            blockers.append("triage_route_explanation_missing")
    for explanation in explanations:
        route = _text(explanation.get("route_category"), "unknown")
        refs = explanation.get("source_refs")
        if not isinstance(refs, list) or not refs:
            blockers.append(f"triage_route_source_refs_missing:{route}")
        if not _text(explanation.get("uncertainty")):
            blockers.append(f"triage_route_uncertainty_missing:{route}")
        if explanation.get("must_not_be_used_as_quality_label") is not True:
            blockers.append(f"triage_route_quality_label_allowed:{route}")
    blockers.extend(_custody_blockers(triage, suffix="_by_triage"))
    return blockers


def _source_ref_summary(
    *,
    read_payload: Mapping[str, Any],
    triage_payload: Mapping[str, Any] | None,
    brief_supply_payload: Mapping[str, Any] | None,
    triage_supply_payload: Mapping[str, Any] | None,
) -> dict[str, Any]:
    missing: list[str] = []
    local_path: list[str] = []
    checked = 0
    fields = _list_of_mappings(read_payload.get("interpreted_fields"))
    for index, field in enumerate(fields):
        if _text(field.get("status")) in {
            "insufficient_context",
            "not_interpreted",
            "not_applicable",
        }:
            continue
        refs = field.get("source_refs")
        name = _text(field.get("field_name"), f"field_{index}")
        if not isinstance(refs, list) or not refs:
            missing.append(name)
            continue
        for ref in refs:
            if not isinstance(ref, Mapping) or not _text(ref.get("artifact")):
                missing.append(name)
                continue
            checked += 1
            if _looks_like_local_absolute_path(_text(ref.get("artifact"))):
                local_path.append(name)
    triage_routes_missing_refs: list[str] = []
    for explanation in _list_of_mappings(_mapping(triage_payload).get("route_explanations")):
        route = _text(explanation.get("route_category"), "unknown")
        refs = explanation.get("source_refs")
        if not isinstance(refs, list) or not refs:
            triage_routes_missing_refs.append(route)
            continue
        checked += len([ref for ref in refs if isinstance(ref, str)])
        for ref in refs:
            if isinstance(ref, str) and _looks_like_local_absolute_path(ref):
                local_path.append(route)
    blockers: list[str] = []
    if missing or triage_routes_missing_refs:
        blockers.append("missing_source_refs")
    if local_path:
        blockers.append("local_absolute_path_in_source_ref")
    for payload, label, summary_key in (
        (brief_supply_payload, "brief_supply", "source_ref_summary"),
        (triage_supply_payload, "triage_supply", "required_source_refs"),
    ):
        summary = _mapping(_mapping(payload).get(summary_key))
        if summary and summary.get("status") != "passed":
            blockers.append(f"{label}_source_ref_summary_not_passed")
    return {
        "status": "passed" if not blockers else "blocked",
        "checked_source_ref_count": checked,
        "missing_source_ref_fields": _dedupe(missing),
        "triage_routes_missing_source_refs": _dedupe(triage_routes_missing_refs),
        "local_absolute_path_fields": _dedupe(local_path),
        "source_refs_preserved": True,
        "blocker_reasons": blockers,
    }


def _uncertainty_summary(
    read_payload: Mapping[str, Any],
    triage_payload: Mapping[str, Any] | None,
) -> dict[str, Any]:
    missing: list[str] = []
    invalid: list[str] = []
    allowed = {"low", "medium", "high", "insufficient_context"}
    for index, field in enumerate(_list_of_mappings(read_payload.get("interpreted_fields"))):
        if _text(field.get("status")) in {
            "insufficient_context",
            "not_interpreted",
            "not_applicable",
        }:
            continue
        name = _text(field.get("field_name"), f"field_{index}")
        uncertainty = _text(field.get("uncertainty"))
        if not uncertainty:
            missing.append(name)
        elif uncertainty not in allowed:
            invalid.append(name)
    triage_missing: list[str] = []
    for explanation in _list_of_mappings(_mapping(triage_payload).get("route_explanations")):
        route = _text(explanation.get("route_category"), "unknown")
        uncertainty = _text(explanation.get("uncertainty"))
        if not uncertainty:
            triage_missing.append(route)
        elif uncertainty not in allowed:
            invalid.append(route)
    blockers: list[str] = []
    if missing or triage_missing:
        blockers.append("missing_uncertainty")
    if invalid:
        blockers.append("invalid_uncertainty")
    return {
        "status": "passed" if not blockers else "blocked",
        "missing_uncertainty_fields": _dedupe(missing),
        "triage_routes_missing_uncertainty": _dedupe(triage_missing),
        "invalid_uncertainty_fields": _dedupe(invalid),
        "uncertainty_preserved": True,
        "blocker_reasons": blockers,
    }


def _privacy_summary(input_texts: list[str]) -> dict[str, Any]:
    private_marker = any(_contains_private_marker(text) for text in input_texts if text)
    local_path = any(
        _contains_local_absolute_path_marker(text) for text in input_texts if text
    )
    blockers: list[str] = []
    if private_marker:
        blockers.append("privacy_marker_detected")
    if local_path:
        blockers.append("local_absolute_path_detected")
    return {
        "status": "passed" if not blockers else "blocked",
        "privacy_marker_detected": private_marker,
        "local_absolute_path_detected": local_path,
        "raw_private_content_included": False,
        "provider_text_included": False,
        "blocker_reasons": blockers,
    }


def _route_summary(triage: Mapping[str, Any] | None) -> dict[str, Any]:
    routes = [item for item in _mapping(triage).get("route_categories", []) if isinstance(item, str)]
    forbidden = sorted(FORBIDDEN_ROUTE_CATEGORIES.intersection(routes))
    blockers = ["forbidden_route_category_selected"] if forbidden else []
    explanations = _list_of_mappings(_mapping(triage).get("route_explanations"))
    return {
        "route_categories": routes,
        "forbidden_route_categories_present": forbidden,
        "ordinary_caveated_offline_candidate": (
            "ordinary_caveated_offline_brief_candidate" in routes
        ),
        "runtime_blocking_routes": sorted(
            set(routes).intersection(RUNTIME_BLOCKING_ROUTES)
        ),
        "user_surface_blocking_routes": sorted(
            set(routes).intersection(USER_SURFACE_BLOCKING_ROUTES)
        ),
        "high_review_routes": sorted(set(routes).intersection(HIGH_REVIEW_ROUTES)),
        "route_explanation_count": len(explanations),
        "must_not_be_used_as_quality_label": all(
            item.get("must_not_be_used_as_quality_label") is True
            for item in explanations
        )
        if explanations
        else False,
        "blocker_reasons": blockers,
    }


def _resolver_supply_status(
    blockers: list[str],
    route_summary: Mapping[str, Any],
) -> str:
    if blockers:
        blocker_set = set(blockers)
        if blocker_set.intersection(
            {
                "privacy_marker_detected",
                "local_absolute_path_detected",
                "local_absolute_path_in_source_ref",
                "raw_private_content_included_claimed",
                "provider_text_included_claimed",
                "local_absolute_paths_included_claimed",
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
                "resolver_refs_marked_usable_claimed",
                "resolver_refs_approved_claimed",
                "runtime_sidecar_updated_claimed",
                "resolver_refs_marked_usable_claimed_by_triage",
                "resolver_refs_approved_claimed_by_triage",
                "runtime_sidecar_updated_claimed_by_triage",
                "model_calls_claimed",
                "sidecar_update_allowed_by_intake",
                "agent_action_allowed_by_intake",
                "quality_label_allowed_by_intake",
                "sidecar_update_allowed_by_brief_supply",
                "agent_action_allowed_by_brief_supply",
                "quality_label_allowed_by_brief_supply",
                "sidecar_update_allowed_by_triage_supply",
                "resolver_approval_allowed_by_triage_supply",
                "quality_label_allowed_by_triage_supply",
                "forbidden_route_category_selected",
            )
        ):
            return "blocked_authority_claim"
        if "requires_operator_repair" in blocker_set:
            return "requires_operator_repair"
        if any(blocker.startswith("intake_not_accepted") for blocker in blockers):
            return "blocked_intake_not_accepted"
        if blocker_set.intersection(
            {
                "missing_source_refs",
                "brief_supply_source_ref_summary_not_passed",
                "triage_supply_source_ref_summary_not_passed",
            }
        ):
            return "requires_operator_repair"
        if blocker_set.intersection({"missing_uncertainty", "invalid_uncertainty"}):
            return "requires_operator_repair"
        if "triage_missing" in blocker_set:
            return "deferred_missing_triage"
        if any(blocker.startswith("triage_") for blocker in blockers):
            return "blocked_triage_missing"
        if "rendered_brief_missing" in blocker_set:
            return "deferred_missing_rendered_brief"
        if "brief_supply_missing" in blocker_set:
            return "deferred_missing_brief_supply"
        if any(blocker.startswith("brief_supply") for blocker in blockers):
            return "deferred_missing_brief_supply"
        return "requires_operator_repair"
    if route_summary.get("user_surface_blocking_routes") or route_summary.get(
        "high_review_routes"
    ):
        return RUNTIME_BLOCK_STATUS
    return READY_STATUS


def _safe_ref_candidates(
    *,
    ready: bool,
    read_ref: str,
    intake_ref: str,
    intake_payload: Mapping[str, Any],
    brief_supply_ref: str,
    brief_supply_payload: Mapping[str, Any] | None,
    rendered_brief_ref: str,
    triage_supply_ref: str,
    triage_supply_payload: Mapping[str, Any] | None,
    triage_ref: str,
    triage_payload: Mapping[str, Any] | None,
    route_summary: Mapping[str, Any],
    source_ref_summary: Mapping[str, Any],
    uncertainty_summary: Mapping[str, Any],
    privacy_summary: Mapping[str, Any],
) -> list[dict[str, Any]]:
    if not ready:
        return []
    return [
        {
            "candidate_kind": "generated_read",
            "ref": read_ref,
            "status": "present",
            "content_included": False,
        },
        {
            "candidate_kind": "intake_result",
            "ref": intake_ref,
            "status": _text(intake_payload.get("intake_status"), "unknown"),
            "content_included": False,
        },
        {
            "candidate_kind": "brief_supply",
            "ref": brief_supply_ref,
            "status": _text(_mapping(brief_supply_payload).get("supply_status"), "unknown"),
            "content_included": False,
        },
        {
            "candidate_kind": "rendered_brief",
            "ref": rendered_brief_ref,
            "status": "present",
            "content_included": False,
        },
        {
            "candidate_kind": "triage_supply",
            "ref": triage_supply_ref,
            "status": _text(
                _mapping(triage_supply_payload).get("triage_supply_status"),
                "unknown",
            ),
            "content_included": False,
        },
        {
            "candidate_kind": "generated_triage",
            "ref": triage_ref,
            "status": _text(_mapping(triage_payload).get("triage_status"), "unknown"),
            "content_included": False,
        },
        {
            "candidate_kind": "route_summary",
            "ref": triage_ref,
            "status": "present",
            "route_categories": list(route_summary.get("route_categories", [])),
            "content_included": False,
        },
        {
            "candidate_kind": "validation_summaries",
            "ref": intake_ref,
            "status": "present",
            "source_ref_status": source_ref_summary.get("status"),
            "uncertainty_status": uncertainty_summary.get("status"),
            "privacy_status": privacy_summary.get("status"),
            "content_included": False,
        },
    ]


def _evidence_only_refs(
    *,
    read_ref: str,
    rendered_brief_ref: str,
    triage_ref: str,
) -> list[dict[str, Any]]:
    return [
        {
            "evidence_kind": "generated_read_semantic_fields",
            "ref": read_ref,
            "reason": "interpreted fields remain evidence, not resolver approval",
            "content_included": False,
        },
        {
            "evidence_kind": "rendered_brief_reader_surface",
            "ref": rendered_brief_ref,
            "reason": "rendered prose can aid inspection but is not proof or approval",
            "content_included": False,
        },
        {
            "evidence_kind": "generated_triage_routes",
            "ref": triage_ref,
            "reason": "routes attention and blockers, not answer quality",
            "content_included": False,
        },
    ]


def _runtime_use_status(route_summary: Mapping[str, Any]) -> dict[str, Any]:
    routes = list(route_summary.get("runtime_blocking_routes", []))
    return {
        "status": "blocked" if routes else "not_approved",
        "blocking_routes": routes,
        "can_update_sidecar": False,
        "can_write_runtime_sidecar": False,
        "candidate_packet_can_override_runtime_block": False,
    }


def _user_surface_status(route_summary: Mapping[str, Any]) -> dict[str, Any]:
    routes = list(route_summary.get("user_surface_blocking_routes", []))
    return {
        "status": "blocked" if routes else "not_established",
        "blocking_routes": routes,
        "customer_ready": False,
        "product_proof": False,
    }


def _agent_inspection_status(route_summary: Mapping[str, Any]) -> dict[str, Any]:
    routes = list(route_summary.get("route_categories", []))
    return {
        "status": "inspection_only" if "agent_inspection_only" in routes else "inspection_candidate",
        "agent_action_authorized": False,
        "automatic_action_authorized": False,
    }


def _required_operator_review(route_summary: Mapping[str, Any]) -> dict[str, Any]:
    routes = list(route_summary.get("route_categories", []))
    return {
        "required_before_runtime_use": True,
        "required_before_user_surface": True,
        "domain_review_required": bool(set(routes).intersection(HIGH_REVIEW_ROUTES)),
        "private_context_required": "private_context_required" in routes,
    }


def _source_case(
    read_payload: Mapping[str, Any],
    triage_payload: Mapping[str, Any] | None,
) -> dict[str, str]:
    triage_case = _mapping(_mapping(triage_payload).get("source_case"))
    read_case = _mapping(read_payload.get("selected_case"))
    return {
        "case_id": _text(
            triage_case.get("case_id"),
            _text(read_case.get("case_id"), "unknown"),
        ),
        "run_ref": _text(
            triage_case.get("run_ref"),
            _text(read_case.get("run_ref")),
        ),
        "decision_family": _text(
            triage_case.get("decision_family"),
            _text(read_case.get("decision_family"), "unknown"),
        ),
    }


def _custody_blockers(payload: Mapping[str, Any], *, suffix: str = "") -> list[str]:
    custody = payload.get("custody_flags")
    if not isinstance(custody, Mapping):
        return [f"custody_flags_missing{suffix}"]
    blockers: list[str] = []
    for flag in AUTHORITY_CUSTODY_FLAGS:
        if custody.get(flag) is True:
            blockers.append(f"{flag}_claimed{suffix}")
    if _safe_int(custody.get("model_calls")) != 0:
        blockers.append(f"model_calls_claimed{suffix}")
    return blockers


def _custody_flags() -> dict[str, Any]:
    return {
        "model_calls": 0,
        "runtime_invoked": False,
        "skill_invoked": False,
        "archive_mutated": False,
        "runtime_behavior_changed": False,
        "resolver_refs_approved": False,
        "resolver_refs_marked_usable": False,
        "runtime_sidecar_updated": False,
        "runtime_wired": False,
        "can_update_sidecar": False,
        "can_write_runtime_sidecar": False,
        "can_authorize_agent_action": False,
        "can_authorize_automatic_action": False,
        "can_be_used_as_quality_label": False,
        "product_proof": False,
        "human_validated": False,
        "answer_quality_scored": False,
        "advice_correctness_claimed": False,
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
        raise DecisionWorkGeneratedReadResolverSupplyError(
            f"{description} was not found"
        ) from exc
    except json.JSONDecodeError as exc:
        raise DecisionWorkGeneratedReadResolverSupplyError(
            f"{description} was not valid JSON"
        ) from exc
    except UnicodeDecodeError as exc:
        raise DecisionWorkGeneratedReadResolverSupplyError(
            f"{description} was not valid UTF-8"
        ) from exc
    except OSError as exc:
        raise DecisionWorkGeneratedReadResolverSupplyError(
            f"{description} could not be read:{type(exc).__name__}"
        ) from exc
    if not isinstance(payload, dict):
        raise DecisionWorkGeneratedReadResolverSupplyError(
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
