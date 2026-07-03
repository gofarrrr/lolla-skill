"""Offline sidecar update packet adapter for resolver-supply candidates.

PR202 prepares proposed sidecar update packets from PR198 resolver-supply
candidate packets. It never writes runtime sidecars, mutates archives, approves
resolver refs, wires runtime, calls models, scores answer quality, or
authorizes action.
"""
from __future__ import annotations

import datetime as _dt
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any


SIDECAR_UPDATE_PACKET_SCHEMA_VERSION = (
    "lolla.decision_work_resolver_candidate_sidecar_update_packet.v0"
)
RESOLVER_SUPPLY_SCHEMA_VERSION = (
    "lolla.decision_work_generated_read_resolver_supply.v0"
)
READY_RESOLVER_SUPPLY_STATUS = "ready_for_resolver_candidate_packet"
RUNTIME_BLOCK_RESOLVER_SUPPLY_STATUS = "candidate_packet_with_runtime_block"
READY_STATUS = "ready_for_sidecar_update_packet"
RUNTIME_BLOCK_STATUS = "packet_with_runtime_block"
REPO_ROOT = Path(__file__).resolve().parents[2]

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
RUNTIME_WRITE_FLAGS = (
    "actual_sidecar_write_performed",
    "archive_mutated",
    "archive_sidecar_written",
    "runtime_wiring_changed",
    "runtime_hook_changed",
    "runtime_sidecar_updated",
    "can_update_sidecar",
    "can_write_runtime_sidecar",
    "can_write_runtime_sidecar",
    "can_write_decision_work_directory",
    "candidate_packet_can_override_runtime_block",
)
AUTHORITY_FLAGS = (
    "resolver_refs_approved",
    "resolver_refs_marked_usable",
    "can_approve_resolver_refs",
    "can_mark_resolver_refs_usable",
    "product_proof",
    "human_validated",
    "answer_quality_scored",
    "advice_correctness_claimed",
    "agent_action_authorized",
    "automatic_action_authorized",
    "can_authorize_agent_action",
    "can_authorize_automatic_action",
    "can_be_used_as_quality_label",
    "customer_ready",
)
NON_CLAIMS = (
    "sidecar_update_packet_is_proposed_offline_packet_only",
    "sidecar_update_packet_does_not_write_decision_work_directory",
    "sidecar_update_packet_does_not_mutate_archives",
    "sidecar_update_packet_does_not_approve_resolver_refs",
    "sidecar_update_packet_does_not_mark_resolver_refs_usable",
    "sidecar_update_packet_does_not_wire_runtime",
    "sidecar_update_packet_does_not_call_models",
    "sidecar_update_packet_is_not_product_proof",
    "sidecar_update_packet_is_not_human_validation",
    "sidecar_update_packet_does_not_score_answer_quality",
    "sidecar_update_packet_does_not_validate_advice_correctness",
    "sidecar_update_packet_does_not_authorize_agent_action",
    "sidecar_update_packet_does_not_authorize_automatic_action",
)


class DecisionWorkResolverCandidateSidecarUpdatePacketError(ValueError):
    """Sanitized sidecar update packet input/output error."""


def build_resolver_candidate_sidecar_update_packet(
    *,
    resolver_supply_path: Path | str,
    source_resolver_supply_ref: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build a proposed offline sidecar update packet from resolver supply."""

    resolver_supply_ref = source_resolver_supply_ref or _safe_ref(
        _resolve(resolver_supply_path)
    )
    resolver_text, resolver_supply, resolver_error = _load_optional_json_text(
        resolver_supply_path,
        "resolver supply packet",
    )
    blockers: list[str] = []
    if resolver_error == "not_found":
        blockers.append("resolver_supply_missing")
    elif resolver_error:
        blockers.append(f"resolver_supply_unreadable:{resolver_error}")
    if resolver_text and _contains_private_marker(resolver_text):
        blockers.append("privacy_marker_detected")
    if resolver_text and _contains_local_absolute_path_marker(resolver_text):
        blockers.append("local_absolute_path_detected")

    resolver_mapping = _mapping(resolver_supply)
    blockers.extend(_resolver_supply_blockers(resolver_mapping))
    blockers = _dedupe(blockers)
    packet_status = _packet_status(blockers, resolver_mapping)
    packet_ready = packet_status in {READY_STATUS, RUNTIME_BLOCK_STATUS}

    return {
        "schema_version": SIDECAR_UPDATE_PACKET_SCHEMA_VERSION,
        "sidecar_update_packet_metadata": {
            "created_at": created_at or _utc_now(),
            "generated_by": "decision_work_resolver_candidate_sidecar_update_packet",
            "adapter_scope": "offline_proposed_sidecar_update_packet_only",
            "model_calls": 0,
            "runtime_invoked": False,
            "skill_invoked": False,
            "archive_mutated": False,
            "actual_sidecar_write_performed": False,
            "runtime_wiring_changed": False,
        },
        "source_case": dict(_mapping(resolver_mapping.get("source_case"))),
        "source_resolver_supply_ref": resolver_supply_ref,
        "sidecar_update_packet_status": packet_status,
        "blocker_reasons": blockers,
        "proposed_sidecar_state": _proposed_sidecar_state(
            packet_status=packet_status,
            resolver_supply=resolver_mapping,
        ),
        "proposed_receipt_state": _proposed_receipt_state(
            packet_status=packet_status,
            resolver_supply=resolver_mapping,
        ),
        "proposed_agent_handoff_state": _proposed_agent_handoff_state(
            packet_status=packet_status,
            resolver_supply=resolver_mapping,
        ),
        "runtime_use_status": dict(_mapping(resolver_mapping.get("runtime_use_status"))),
        "user_surface_status": dict(_mapping(resolver_mapping.get("user_surface_status"))),
        "agent_inspection_status": dict(
            _mapping(resolver_mapping.get("agent_inspection_status"))
        ),
        "resolver_refs_approved": False,
        "actual_sidecar_write_performed": False,
        "archive_mutated": False,
        "runtime_wiring_changed": False,
        "source_refs": _source_refs(resolver_mapping, resolver_supply_ref),
        "uncertainty_summary": dict(
            _mapping(resolver_mapping.get("uncertainty_summary"))
        ),
        "privacy_summary": dict(_mapping(resolver_mapping.get("privacy_summary"))),
        "custody_flags": _custody_flags(),
        "non_claims": list(NON_CLAIMS),
        "downstream_allowed": {
            "can_feed_sidecar_update_packet_review": packet_ready,
            "resolver_refs_approved": False,
            "resolver_refs_marked_usable": False,
            "can_update_sidecar": False,
            "can_write_decision_work_directory": False,
            "can_mutate_archive": False,
            "can_wire_runtime": False,
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
            "write_decision_work_sidecar",
            "mutate_archives",
            "wire_runtime",
            "make_runtime_default_on",
            "call_models_or_providers",
            "score_answer_quality",
            "claim_product_proof",
            "claim_human_validation",
            "claim_advice_correctness",
            "authorize_agent_or_automatic_action",
        ],
    }


def render_resolver_candidate_sidecar_update_packet_json(
    result: Mapping[str, Any],
    *,
    pretty: bool = False,
) -> str:
    """Render a sidecar update packet as stable JSON."""

    if pretty:
        return json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return json.dumps(result, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"


def write_resolver_candidate_sidecar_update_packet(path: Path | str, payload: str) -> None:
    """Write an offline sidecar update packet, never a runtime sidecar."""

    output = Path(path).expanduser()
    if "decision_work" in output.parts:
        raise DecisionWorkResolverCandidateSidecarUpdatePacketError(
            "output path must not target a decision_work sidecar directory"
        )
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    except OSError as exc:
        raise DecisionWorkResolverCandidateSidecarUpdatePacketError(
            f"output could not be written:{type(exc).__name__}"
        ) from exc


def _resolver_supply_blockers(resolver_supply: Mapping[str, Any]) -> list[str]:
    if not resolver_supply:
        return []
    blockers: list[str] = []
    if resolver_supply.get("schema_version") != RESOLVER_SUPPLY_SCHEMA_VERSION:
        blockers.append("resolver_supply_schema_invalid")
    status = _text(resolver_supply.get("resolver_supply_status"))
    if status not in {
        READY_RESOLVER_SUPPLY_STATUS,
        RUNTIME_BLOCK_RESOLVER_SUPPLY_STATUS,
    }:
        if status == "requires_operator_repair":
            blockers.append("requires_operator_repair")
        else:
            blockers.append(f"resolver_supply_not_candidate:{status or 'missing'}")
    if resolver_supply.get("blocker_reasons") not in ([], None):
        blockers.append("resolver_supply_has_blockers")
    if _any_true_flag(resolver_supply, RUNTIME_WRITE_FLAGS):
        blockers.append("runtime_write_attempt_detected")
    if _any_true_flag(resolver_supply, AUTHORITY_FLAGS):
        blockers.append("authority_claim_detected")
    downstream = _mapping(resolver_supply.get("downstream_allowed"))
    if downstream.get("resolver_refs_approved") is not False:
        blockers.append("resolver_refs_approval_not_false")
    if downstream.get("can_update_sidecar") is not False:
        blockers.append("sidecar_update_not_false")
    if downstream.get("can_write_runtime_sidecar") is not False:
        blockers.append("runtime_sidecar_write_not_false")
    if downstream.get("can_be_used_as_quality_label") is not False:
        blockers.append("quality_label_not_false")
    if downstream.get("can_authorize_agent_action") is not False:
        blockers.append("agent_action_not_false")
    if downstream.get("can_authorize_automatic_action") is not False:
        blockers.append("automatic_action_not_false")
    privacy_summary = _mapping(resolver_supply.get("privacy_summary"))
    if privacy_summary.get("privacy_marker_detected") is True:
        blockers.append("privacy_marker_detected")
    if privacy_summary.get("local_absolute_path_detected") is True:
        blockers.append("local_absolute_path_detected")
    source_refs = _source_refs(resolver_supply, _text(resolver_supply.get("source_ref")))
    if not source_refs.get("source_generated_read_ref"):
        blockers.append("source_generated_read_ref_missing")
    if not source_refs.get("source_intake_ref"):
        blockers.append("source_intake_ref_missing")
    if not source_refs.get("source_brief_supply_ref"):
        blockers.append("source_brief_supply_ref_missing")
    if not source_refs.get("source_rendered_brief_ref"):
        blockers.append("source_rendered_brief_ref_missing")
    if not source_refs.get("source_triage_supply_ref"):
        blockers.append("source_triage_supply_ref_missing")
    if not source_refs.get("source_triage_ref"):
        blockers.append("source_triage_ref_missing")
    return blockers


def _packet_status(
    blockers: list[str],
    resolver_supply: Mapping[str, Any],
) -> str:
    if blockers:
        blocker_set = set(blockers)
        if "resolver_supply_missing" in blocker_set:
            return "deferred_missing_resolver_supply"
        if blocker_set.intersection(
            {
                "privacy_marker_detected",
                "local_absolute_path_detected",
            }
        ):
            return "blocked_privacy_risk"
        if "runtime_write_attempt_detected" in blocker_set or blocker_set.intersection(
            {
                "sidecar_update_not_false",
                "runtime_sidecar_write_not_false",
            }
        ):
            return "blocked_runtime_write_attempt"
        if blocker_set.intersection(
            {
                "authority_claim_detected",
                "resolver_refs_approval_not_false",
                "quality_label_not_false",
                "agent_action_not_false",
                "automatic_action_not_false",
            }
        ):
            return "blocked_authority_claim"
        if "requires_operator_repair" in blocker_set:
            return "requires_operator_repair"
        return "blocked_resolver_supply_not_candidate"
    status = _text(resolver_supply.get("resolver_supply_status"))
    if status == RUNTIME_BLOCK_RESOLVER_SUPPLY_STATUS:
        return RUNTIME_BLOCK_STATUS
    return READY_STATUS


def _proposed_sidecar_state(
    *,
    packet_status: str,
    resolver_supply: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "state_kind": "proposed_sidecar_update_packet_only",
        "status": packet_status,
        "source_resolver_supply_status": _text(
            resolver_supply.get("resolver_supply_status"),
            "missing",
        ),
        "would_write_decision_work_directory": False,
        "actual_sidecar_write_performed": False,
        "archive_mutated": False,
        "runtime_wiring_changed": False,
        "resolver_refs_approved": False,
        "candidate_refs_count": len(
            [item for item in resolver_supply.get("safe_ref_candidates", []) if isinstance(item, Mapping)]
        )
        if isinstance(resolver_supply.get("safe_ref_candidates"), list)
        else 0,
        "content_included": False,
    }


def _proposed_receipt_state(
    *,
    packet_status: str,
    resolver_supply: Mapping[str, Any],
) -> dict[str, Any]:
    user_surface = _mapping(resolver_supply.get("user_surface_status"))
    if packet_status == RUNTIME_BLOCK_STATUS:
        receipt_state = "blocked_for_runtime_use"
    elif packet_status == READY_STATUS:
        receipt_state = "candidate_packet_available_for_review"
    elif packet_status == "deferred_missing_resolver_supply":
        receipt_state = "deferred"
    else:
        receipt_state = "blocked_or_repair_required"
    return {
        "state_kind": "proposed_receipt_state_only",
        "receipt_state": receipt_state,
        "customer_ready": False,
        "product_proof": False,
        "user_surface_status": _text(user_surface.get("status"), "not_established"),
        "content_included": False,
    }


def _proposed_agent_handoff_state(
    *,
    packet_status: str,
    resolver_supply: Mapping[str, Any],
) -> dict[str, Any]:
    agent_status = _mapping(resolver_supply.get("agent_inspection_status"))
    return {
        "state_kind": "proposed_agent_handoff_state_only",
        "handoff_candidate": packet_status in {READY_STATUS, RUNTIME_BLOCK_STATUS},
        "agent_inspection_status": _text(agent_status.get("status"), "not_established"),
        "agent_action_authorized": False,
        "automatic_action_authorized": False,
        "content_included": False,
    }


def _source_refs(
    resolver_supply: Mapping[str, Any],
    resolver_supply_ref: str | None,
) -> dict[str, Any]:
    return {
        "source_resolver_supply_ref": resolver_supply_ref,
        "source_generated_read_ref": _text(resolver_supply.get("source_read_ref")),
        "source_intake_ref": _text(resolver_supply.get("source_intake_ref")),
        "source_brief_supply_ref": _text(
            resolver_supply.get("source_brief_supply_ref")
        ),
        "source_rendered_brief_ref": _text(
            resolver_supply.get("source_rendered_brief_ref")
        ),
        "source_triage_supply_ref": _text(
            resolver_supply.get("source_triage_supply_ref")
        ),
        "source_triage_ref": _text(resolver_supply.get("source_triage_ref")),
        "raw_content_included": False,
    }


def _custody_flags() -> dict[str, Any]:
    return {
        "model_calls": 0,
        "runtime_invoked": False,
        "skill_invoked": False,
        "archive_mutated": False,
        "actual_sidecar_write_performed": False,
        "runtime_wiring_changed": False,
        "resolver_refs_approved": False,
        "resolver_refs_marked_usable": False,
        "product_proof": False,
        "human_validated": False,
        "answer_quality_scored": False,
        "advice_correctness_claimed": False,
        "agent_action_authorized": False,
        "automatic_action_authorized": False,
    }


def _load_optional_json_text(
    path: Path | str,
    description: str,
) -> tuple[str, Mapping[str, Any] | None, str | None]:
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
    if not isinstance(payload, Mapping):
        return text, None, "not_object"
    return text, payload, None


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


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _text(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        return value
    return default


def _contains_private_marker(text: str) -> bool:
    return any(marker in text for marker in RAW_PRIVATE_MARKERS)


def _contains_local_absolute_path_marker(text: str) -> bool:
    return any(marker in text for marker in LOCAL_ABSOLUTE_PATH_MARKERS)


def _any_true_flag(value: Any, flag_names: tuple[str, ...]) -> bool:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if key in flag_names and item is True:
                return True
            if _any_true_flag(item, flag_names):
                return True
    elif isinstance(value, list):
        return any(_any_true_flag(item, flag_names) for item in value)
    return False


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
