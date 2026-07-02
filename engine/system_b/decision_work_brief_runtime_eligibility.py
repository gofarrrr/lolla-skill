"""Deterministic eligibility and blocker gate for Decision Work Brief attachment.

The gate classifies runtime-attachment readiness from already available status
fields, parseability checks, custody flags, and explicit triage routes. It does
not infer conversation meaning, score advice, approve output, call models, run
Lolla, mutate archives, or authorize action.
"""
from __future__ import annotations

import datetime as _dt
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from engine.system_b.decision_work_brief_runtime_bundle import (
    ATTACHMENT_STATUS_SCHEMA_VERSION,
    DecisionWorkBriefRuntimeBundleInputError,
    REQUIRED_STRUCTURED_ARTIFACTS,
    REQUIRED_TEXT_ARTIFACTS,
    validate_output_dir,
)


ELIGIBILITY_SCHEMA_VERSION = "lolla.decision_work_brief_runtime_eligibility.v0"
TRIAGE_READ_SCHEMA_VERSION = "lolla.decision_work_automatic_triage_provisional_read.v0"
HARD_BLOCKER_VOCABULARY = (
    "incomplete_run_artifacts",
    "archive_not_finalized",
    "missing_revised_answer",
    "missing_required_structured_artifacts",
    "malformed_json",
    "failed_hygiene",
    "failed_boundary_lint",
    "unsafe_output_path",
    "source_refs_unresolved",
    "privacy_marker_or_raw_private_export_risk",
    "schema_validation_failure",
    "attempted_model_or_provider_invocation",
    "attempted_runtime_invocation",
    "attempted_archive_mutation",
    "attempted_answer_quality_scoring",
    "attempted_action_authorization",
)
SOFT_TRIAGE_BLOCKER_VOCABULARY = (
    "source_depth_too_thin",
    "high_overtrust_risk",
    "private_context_required",
    "legal_domain_compliance_or_safety_escalation",
    "relationship_or_political_sensitivity",
    "unresolved_lost_value_risk",
    "agent_inspection_only",
    "runtime_attachment_blocked",
)
RAW_PRIVATE_MARKERS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)
NON_CLAIMS = (
    "not_runtime_default",
    "not_customer_readiness",
    "not_human_validation",
    "not_product_proof",
    "not_answer_quality_scoring",
    "not_advice_correctness",
    "not_lolla_improvement_proof",
    "not_agent_action_authorization",
    "not_automatic_action_authorization",
    "triage_is_routing_not_scoring",
)


def evaluate_runtime_attachment_eligibility(
    *,
    run_dir: Path | str,
    requested: bool = True,
    output_dir: Path | str | None = None,
    attachment_status: Mapping[str, Any] | None = None,
    triage_read: Mapping[str, Any] | None = None,
    case_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Return a deterministic attachment eligibility result."""

    run_path = Path(run_dir).expanduser()
    hard_blockers: list[str] = []
    run_artifact_status = _inspect_run_artifacts(run_path, hard_blockers)

    if output_dir is not None and run_path.exists():
        try:
            validate_output_dir(output_dir=output_dir, run_dir=run_path)
        except DecisionWorkBriefRuntimeBundleInputError:
            hard_blockers.append("unsafe_output_path")

    normalized_status = _normalize_attachment_status(
        attachment_status=attachment_status,
        hard_blockers=hard_blockers,
    )
    triage_route_status = _normalize_triage_route(
        triage_read=triage_read,
        case_id=case_id,
        hard_blockers=hard_blockers,
    )
    soft_triage_blockers = _soft_triage_blockers(triage_route_status)
    attachment_state = _decide_attachment_state(
        requested=requested,
        hard_blockers=hard_blockers,
        attachment_status_state=normalized_status["attachment_state"],
        soft_triage_blockers=soft_triage_blockers,
        triage_route_status=triage_route_status,
    )

    agent_only = attachment_state == "generated_agent_only"
    return {
        "schema_version": ELIGIBILITY_SCHEMA_VERSION,
        "eligibility_metadata": {
            "created_at": created_at or _utc_now(),
            "evaluator": "engine.system_b.decision_work_brief_runtime_eligibility",
            "deterministic_only": True,
            "post_archive_only": True,
            "default_off_assumed": True,
        },
        "requested": requested,
        "attachment_state": attachment_state,
        "eligible_for_generation": attachment_state in {
            "generated",
            "generated_agent_only",
        },
        "eligible_for_user_surface": attachment_state == "generated" and not agent_only,
        "agent_inspection_only": agent_only,
        "hard_blockers": _dedupe(hard_blockers),
        "soft_triage_blockers": soft_triage_blockers,
        "run_artifact_status": run_artifact_status,
        "attachment_status_read": normalized_status,
        "triage_route_status": triage_route_status,
        "custody_flags": _custody_flags(),
        "non_claims": list(NON_CLAIMS),
    }


def _inspect_run_artifacts(run_path: Path, hard_blockers: list[str]) -> dict[str, Any]:
    if not run_path.exists() or not run_path.is_dir():
        hard_blockers.extend(["archive_not_finalized", "incomplete_run_artifacts"])
        return {
            "source_run_ref": _run_ref(run_path),
            "archive_finalized": False,
            "required_artifacts": {},
        }

    artifacts: dict[str, dict[str, Any]] = {}
    for artifact in REQUIRED_STRUCTURED_ARTIFACTS:
        path = run_path / artifact
        if not path.exists():
            artifacts[artifact] = {"status": "missing"}
            hard_blockers.extend(
                ["incomplete_run_artifacts", "missing_required_structured_artifacts"]
            )
            continue
        try:
            text = path.read_text(encoding="utf-8")
            json.loads(text)
        except json.JSONDecodeError:
            artifacts[artifact] = {"status": "malformed"}
            hard_blockers.append("malformed_json")
        except (OSError, UnicodeDecodeError):
            artifacts[artifact] = {"status": "unreadable"}
            hard_blockers.append("incomplete_run_artifacts")
        else:
            if _contains_private_marker(text):
                artifacts[artifact] = {"status": "privacy_marker_detected"}
                hard_blockers.append("privacy_marker_or_raw_private_export_risk")
            else:
                artifacts[artifact] = {"status": "present_parseable"}

    for artifact in REQUIRED_TEXT_ARTIFACTS:
        path = run_path / artifact
        if not path.exists():
            artifacts[artifact] = {"status": "missing"}
            hard_blockers.extend(["missing_revised_answer", "incomplete_run_artifacts"])
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            artifacts[artifact] = {"status": "unreadable"}
            hard_blockers.append("incomplete_run_artifacts")
            continue
        if _contains_private_marker(text):
            artifacts[artifact] = {"status": "privacy_marker_detected"}
            hard_blockers.append("privacy_marker_or_raw_private_export_risk")
        else:
            artifacts[artifact] = {"status": "present_not_exported"}

    return {
        "source_run_ref": _run_ref(run_path),
        "archive_finalized": not any(
            blocker
            in {
                "archive_not_finalized",
                "incomplete_run_artifacts",
                "missing_revised_answer",
                "missing_required_structured_artifacts",
                "malformed_json",
            }
            for blocker in hard_blockers
        ),
        "required_artifacts": artifacts,
    }


def _normalize_attachment_status(
    *,
    attachment_status: Mapping[str, Any] | None,
    hard_blockers: list[str],
) -> dict[str, Any]:
    if attachment_status is None:
        return {
            "available": False,
            "attachment_state": "deferred",
            "status_ref": None,
            "generated_artifacts": {},
            "blocked_reasons": ["attachment_status_not_supplied"],
            "deferred_reasons": ["attachment_status_not_supplied"],
        }
    if attachment_status.get("schema_version") != ATTACHMENT_STATUS_SCHEMA_VERSION:
        hard_blockers.append("schema_validation_failure")
    custody = _mapping(attachment_status.get("custody_flags"))
    _custody_blockers(custody, hard_blockers)
    generated_artifacts = _mapping(attachment_status.get("generated_artifacts"))
    blocked_reasons = _string_list(attachment_status.get("blocked_reasons"))
    deferred_reasons = _string_list(attachment_status.get("deferred_reasons"))
    if _contains_unresolved_source_ref(attachment_status):
        hard_blockers.append("source_refs_unresolved")
    return {
        "available": True,
        "attachment_state": _text(
            attachment_status.get("attachment_state"),
            fallback="deferred",
        ),
        "status_ref": generated_artifacts.get("attachment_status"),
        "generated_artifacts": dict(generated_artifacts),
        "blocked_reasons": blocked_reasons,
        "deferred_reasons": deferred_reasons,
    }


def _normalize_triage_route(
    *,
    triage_read: Mapping[str, Any] | None,
    case_id: str | None,
    hard_blockers: list[str],
) -> dict[str, Any]:
    if triage_read is None:
        return {
            "available": False,
            "case_id": case_id,
            "triage_categories": [],
            "user_surface_route": "not_evaluated",
            "agent_inspection_route": "not_evaluated",
            "human_calibration_route": "not_evaluated",
            "domain_review_route": "not_evaluated",
            "runtime_attachment_route": "not_evaluated",
        }
    if triage_read.get("schema_version") != TRIAGE_READ_SCHEMA_VERSION:
        hard_blockers.append("schema_validation_failure")
        return {"available": False, "case_id": case_id, "triage_categories": []}

    custody = {
        key: triage_read.get(key)
        for key in (
            "product_proof",
            "runtime_invoked",
            "skill_invoked",
            "archive_mutated",
            "answer_quality_scored",
            "agent_action_authorized",
            "automatic_action_authorized",
        )
    }
    _custody_blockers(custody, hard_blockers)
    cases = triage_read.get("case_triage_reads")
    if not isinstance(cases, list):
        hard_blockers.append("schema_validation_failure")
        return {"available": False, "case_id": case_id, "triage_categories": []}
    selected = _select_case(cases, case_id)
    if selected is None:
        hard_blockers.append("source_refs_unresolved")
        return {"available": False, "case_id": case_id, "triage_categories": []}
    return {
        "available": True,
        "case_id": selected.get("case_id"),
        "triage_categories": _string_list(selected.get("triage_categories")),
        "user_surface_route": _text(selected.get("user_surface_route"), "not_evaluated"),
        "agent_inspection_route": _text(
            selected.get("agent_inspection_route"),
            "not_evaluated",
        ),
        "human_calibration_route": _text(
            selected.get("human_calibration_route"),
            "not_evaluated",
        ),
        "domain_review_route": _text(
            selected.get("domain_review_route"),
            "not_evaluated",
        ),
        "runtime_attachment_route": _text(
            selected.get("runtime_attachment_route"),
            "not_evaluated",
        ),
        "must_not_be_used_as_quality_label": selected.get(
            "must_not_be_used_as_quality_label"
        )
        is True,
    }


def _soft_triage_blockers(triage_route_status: Mapping[str, Any]) -> list[str]:
    categories = set(_string_list(triage_route_status.get("triage_categories")))
    routes = {
        "user_surface_route": triage_route_status.get("user_surface_route"),
        "agent_inspection_route": triage_route_status.get("agent_inspection_route"),
        "human_calibration_route": triage_route_status.get("human_calibration_route"),
        "domain_review_route": triage_route_status.get("domain_review_route"),
        "runtime_attachment_route": triage_route_status.get("runtime_attachment_route"),
    }
    blockers: list[str] = []
    if "source_depth_insufficient" in categories:
        blockers.append("source_depth_too_thin")
    if "high_overtrust_risk" in categories:
        blockers.append("high_overtrust_risk")
    if "private_context_required" in categories:
        blockers.append("private_context_required")
    if categories & {
        "domain_review_recommended",
        "legal_or_compliance_review_recommended",
    }:
        blockers.append("legal_domain_compliance_or_safety_escalation")
    if "relationship_or_political_risk" in categories:
        blockers.append("relationship_or_political_sensitivity")
    if "lost_value_risk" in categories:
        blockers.append("unresolved_lost_value_risk")
    if "agent_inspection_only" in categories or routes["agent_inspection_route"] == (
        "agent_only"
    ):
        blockers.append("agent_inspection_only")
    if "runtime_attachment_blocked" in categories or routes[
        "runtime_attachment_route"
    ] == "blocked_runtime":
        blockers.append("runtime_attachment_blocked")
    if routes["user_surface_route"] in {
        "agent_only",
        "requires_human_calibration",
        "requires_domain_review",
        "blocked_source_depth",
        "blocked_overtrust_risk",
        "not_ready",
    }:
        blockers.append("agent_inspection_only")
    return _dedupe(blockers)


def _decide_attachment_state(
    *,
    requested: bool,
    hard_blockers: Sequence[str],
    attachment_status_state: str,
    soft_triage_blockers: Sequence[str],
    triage_route_status: Mapping[str, Any],
) -> str:
    if not requested:
        return "not_requested"
    if hard_blockers:
        return "blocked"
    if attachment_status_state in {"blocked", "failed_closed"}:
        return attachment_status_state
    if attachment_status_state in {"deferred", "not_requested", "not_eligible"}:
        return "deferred"
    if attachment_status_state == "generated_agent_only":
        return "generated_agent_only"
    if attachment_status_state == "generated":
        if "agent_inspection_only" in soft_triage_blockers:
            return "generated_agent_only"
        if triage_route_status.get("runtime_attachment_route") == "blocked_runtime":
            return "generated_agent_only"
        return "generated"
    return "deferred"


def _custody_blockers(custody: Mapping[str, Any], hard_blockers: list[str]) -> None:
    if custody.get("model_calls") not in {None, 0}:
        hard_blockers.append("attempted_model_or_provider_invocation")
    if custody.get("runtime_invoked") is True or custody.get("skill_invoked") is True:
        hard_blockers.append("attempted_runtime_invocation")
    if custody.get("archive_mutated") is True:
        hard_blockers.append("attempted_archive_mutation")
    if custody.get("answer_quality_scored") is True:
        hard_blockers.append("attempted_answer_quality_scoring")
    if custody.get("agent_action_authorized") is True:
        hard_blockers.append("attempted_action_authorization")
    if custody.get("automatic_action_authorized") is True:
        hard_blockers.append("attempted_action_authorization")


def _contains_unresolved_source_ref(value: Any) -> bool:
    if isinstance(value, str):
        return value in {"missing", "unresolved", "source_not_found"}
    if isinstance(value, list):
        return any(_contains_unresolved_source_ref(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_unresolved_source_ref(item) for item in value.values())
    return False


def _select_case(cases: Sequence[Any], case_id: str | None) -> Mapping[str, Any] | None:
    if case_id is None and len(cases) == 1 and isinstance(cases[0], Mapping):
        return cases[0]
    for case in cases:
        if isinstance(case, Mapping) and case.get("case_id") == case_id:
            return case
    return None


def _custody_flags() -> dict[str, Any]:
    return {
        "human_validated": False,
        "human_review_completed": False,
        "product_proof": False,
        "model_calls": 0,
        "runtime_invoked": False,
        "skill_invoked": False,
        "archive_mutated": False,
        "answer_quality_scored": False,
        "agent_action_authorized": False,
        "automatic_action_authorized": False,
        "raw_private_content_included": False,
        "provider_text_included": False,
        "local_absolute_paths_included": False,
    }


def _run_ref(run_path: Path) -> str:
    parts = [part for part in run_path.parts if part]
    if len(parts) >= 2:
        return f"{parts[-2]}/{parts[-1]}"
    return run_path.name or "unknown"


def _contains_private_marker(text: str) -> bool:
    return any(marker in text for marker in RAW_PRIVATE_MARKERS)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _text(value: Any, fallback: str = "") -> str:
    return value if isinstance(value, str) and value else fallback


def _dedupe(values: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _utc_now() -> str:
    return _dt.datetime.now(tz=_dt.UTC).replace(microsecond=0).isoformat().replace(
        "+00:00",
        "Z",
    )
