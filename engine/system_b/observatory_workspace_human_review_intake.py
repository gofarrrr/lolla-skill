"""Observatory workspace human-review intake validator.

This module validates a completed Observatory workspace human review form after
the reviewer fills it. It is deterministic and read-only. It does not perform
human review, run Lolla, call providers, mutate archives, update runtime
sidecars, claim product proof, claim answer/advice correctness, or authorize
action.
"""
from __future__ import annotations

import datetime as _dt
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any


FORM_SCHEMA_VERSION = "lolla.observatory_workspace_human_review_form.v0"
INTAKE_SCHEMA_VERSION = "lolla.observatory_workspace_human_review_intake.v0"

SURFACES = ("Outcome", "Learn", "Models", "Relations", "Map", "Receipts")
ALLOWED_RATINGS = {"strong", "adequate", "weak", "cannot_judge"}
COMPLETED_STATUSES = {"completed_human_review", "human_review_completed"}
ALLOWED_OVERALL_DECISIONS = {
    "ready_to_continue_with_caveats",
    "needs_first_screen_revision",
    "needs_learn_revision",
    "needs_model_page_revision",
    "needs_relation_page_revision",
    "needs_graph_map_ux_revision",
    "needs_receipts_audit_revision",
    "cannot_judge_from_packet",
}
DECISION_TO_GATE = {
    "ready_to_continue_with_caveats": (
        "ready_to_plan_next_observatory_slice_with_human_caveats"
    ),
    "needs_first_screen_revision": "needs_first_screen_revision",
    "needs_learn_revision": "needs_learn_revision",
    "needs_model_page_revision": "needs_model_page_revision",
    "needs_relation_page_revision": "needs_relation_page_revision",
    "needs_graph_map_ux_revision": "needs_graph_map_ux_revision",
    "needs_receipts_audit_revision": "needs_receipts_audit_revision",
    "cannot_judge_from_packet": "needs_review_packet_revision",
}
FALSE_TOP_LEVEL_FLAGS = (
    "prefilled_positive",
    "human_validated",
    "product_proof",
)
FALSE_NON_CLAIM_FLAGS = (
    "product_proof",
    "human_validated",
    "answer_correctness",
    "advice_correctness",
    "runtime_integration_authorized",
    "action_authorized",
    "graph_edges_are_proof",
    "relation_confidence_is_certification",
)
RAW_PRIVATE_MARKERS = (
    "SEC" + "RET",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
    "raw_message" + "_content",
)
LOCAL_ABSOLUTE_PATH_MARKERS = ("/" + "Users" + "/", "/home/", "/private/")
NON_CLAIMS = (
    "intake_validates_review_shape_only",
    "intake_does_not_complete_human_review",
    "intake_does_not_run_lolla",
    "intake_does_not_call_providers_or_models",
    "intake_does_not_create_runs",
    "intake_does_not_mutate_archives",
    "intake_does_not_write_sidecars",
    "intake_does_not_wire_runtime_behavior",
    "intake_is_not_product_proof",
    "intake_is_not_answer_correctness",
    "intake_is_not_advice_correctness",
    "intake_does_not_authorize_action",
)


class ObservatoryWorkspaceHumanReviewIntakeError(ValueError):
    """Sanitized Observatory workspace human-review intake error."""


def validate_observatory_workspace_human_review_form(
    form: Mapping[str, Any],
    *,
    source_ref: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Validate a completed human-review form and return an intake result."""

    if not isinstance(form, Mapping):
        raise ObservatoryWorkspaceHumanReviewIntakeError(
            "review form must be a JSON object"
        )

    blocker_reasons: list[str] = []
    warning_reasons: list[str] = []

    rendered = _safe_json_dumps(form)
    if _contains_any(rendered, LOCAL_ABSOLUTE_PATH_MARKERS):
        blocker_reasons.append("local_absolute_path_detected")
    if _contains_any(rendered, RAW_PRIVATE_MARKERS):
        blocker_reasons.append("privacy_marker_detected")

    if _text(form.get("schema_version")) != FORM_SCHEMA_VERSION:
        blocker_reasons.append("unsupported_schema_version")

    for field in FALSE_TOP_LEVEL_FLAGS:
        if form.get(field) is True:
            blocker_reasons.append(f"{field}_claim_not_allowed")

    completed = (
        form.get("human_review_completed") is True
        and _text(form.get("status")) in COMPLETED_STATUSES
    )
    if not completed:
        blocker_reasons.append("human_review_not_completed")

    _validate_false_flags(
        _mapping(form.get("boundary_acknowledgement")),
        prefix="boundary_acknowledgement",
        blockers=blocker_reasons,
    )
    _validate_false_flags(
        _mapping(form.get("non_claims")),
        prefix="non_claims",
        blockers=blocker_reasons,
        expected_fields=FALSE_NON_CLAIM_FLAGS,
    )

    if completed:
        _validate_completed_form(form, blocker_reasons, warning_reasons)

    blocker_reasons = _dedupe(blocker_reasons)
    warning_reasons = _dedupe(warning_reasons)
    intake_status = _intake_status(blocker_reasons)
    accepted = intake_status == "accepted"

    overall_decision = _selected(_mapping(form.get("overall_decision")))
    non_claims_selection = _selected(_mapping(form.get("non_claims_review")))
    next_gate = _next_gate(
        intake_status=intake_status,
        overall_decision=overall_decision,
        non_claims_selection=non_claims_selection,
    )

    return {
        "schema_version": INTAKE_SCHEMA_VERSION,
        "intake_metadata": {
            "created_at": created_at or _utc_now(),
            "generated_by": "observatory_workspace_human_review_intake",
            "source_ref": _safe_source_ref(source_ref),
        },
        "intake_status": intake_status,
        "accepted_for_downstream": accepted,
        "repair_required": not accepted,
        "blocker_reasons": blocker_reasons,
        "warning_reasons": warning_reasons,
        "source_review": {
            "schema_version": _text(form.get("schema_version")),
            "status": _text(form.get("status")),
            "human_review_completed": form.get("human_review_completed") is True,
            "overall_decision": overall_decision,
            "non_claims_review": non_claims_selection,
        },
        "review_coverage": _review_coverage(form),
        "next_gate": next_gate,
        "downstream_allowed": {
            "can_plan_revision": accepted,
            "can_expand_product": False,
            "can_claim_human_validation": False,
            "can_claim_product_proof": False,
            "can_claim_answer_correctness": False,
            "can_claim_advice_correctness": False,
            "can_wire_runtime": False,
            "can_authorize_action": False,
        },
        "boundary": {
            "runs_lolla": False,
            "invokes_lolla_skill": False,
            "calls_provider_or_model": False,
            "creates_new_lolla_run": False,
            "wires_runtime_behavior": False,
            "mutates_archives": False,
            "writes_sidecars": False,
            "compiled_spa_bundle_changed": False,
        },
        "non_claims": list(NON_CLAIMS),
    }


def load_observatory_workspace_human_review_form(path: Path | str) -> dict[str, Any]:
    """Load a human-review form JSON object without leaking local path details."""

    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ObservatoryWorkspaceHumanReviewIntakeError(
            "review form is not valid JSON"
        ) from exc
    except OSError as exc:
        raise ObservatoryWorkspaceHumanReviewIntakeError(
            "review form could not be read"
        ) from exc
    if not isinstance(payload, dict):
        raise ObservatoryWorkspaceHumanReviewIntakeError(
            "review form must be a JSON object"
        )
    return payload


def render_observatory_workspace_human_review_intake_json(
    intake: Mapping[str, Any],
) -> str:
    """Render an intake result as stable JSON."""

    return json.dumps(intake, indent=2, sort_keys=True) + "\n"


def write_observatory_workspace_human_review_intake_result(
    path: Path | str,
    intake: Mapping[str, Any],
) -> Path:
    """Write a validated intake result JSON."""

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        render_observatory_workspace_human_review_intake_json(intake),
        encoding="utf-8",
    )
    return out


def _validate_completed_form(
    form: Mapping[str, Any],
    blockers: list[str],
    warnings: list[str],
) -> None:
    workspace = _mapping(form.get("workspace_reviewed"))
    for field in ("case_id", "run_id", "review_date", "reviewer"):
        if not _text(workspace.get(field)):
            blockers.append(f"workspace_reviewed.{field}_missing")

    overall = _selected(_mapping(form.get("overall_decision")))
    if overall not in ALLOWED_OVERALL_DECISIONS:
        blockers.append("overall_decision_missing_or_invalid")

    first = _mapping(form.get("first_impression"))
    for field in (
        "page_purpose_in_first_ten_seconds",
        "wanted_next_click",
        "one_product_or_artifact_pile",
    ):
        if not _text(first.get(field)):
            blockers.append(f"first_impression.{field}_missing")

    progression = _mapping(form.get("progression_review"))
    if list(progression.get("progression") or []) != list(SURFACES):
        blockers.append("progression_review.progression_mismatch")
    _validate_rating(
        progression,
        "progression_review",
        blockers,
        require_evidence=True,
    )

    surface_reviews = _mapping(form.get("surface_reviews"))
    for surface in SURFACES:
        review = _mapping(surface_reviews.get(surface))
        if not review:
            blockers.append(f"surface_reviews.{surface}_missing")
            continue
        _validate_rating(review, f"surface_reviews.{surface}", blockers)
        if not _text(review.get("what_worked")) and not _text(
            review.get("what_should_change")
        ):
            blockers.append(f"surface_reviews.{surface}.evidence_missing")
    for extra in surface_reviews:
        if extra not in SURFACES:
            warnings.append(f"surface_reviews.{extra}_ignored")

    _validate_rating(
        _mapping(form.get("information_hierarchy")),
        "information_hierarchy",
        blockers,
        require_evidence=True,
    )
    non_claims = _mapping(form.get("non_claims_review"))
    selected = _selected(non_claims)
    if selected not in {"yes", "no", "cannot_judge"}:
        blockers.append("non_claims_review.selected_missing_or_invalid")
    if not _text(non_claims.get("evidence")):
        blockers.append("non_claims_review.evidence_missing")


def _validate_rating(
    value: Mapping[str, Any],
    label: str,
    blockers: list[str],
    *,
    require_evidence: bool = False,
) -> None:
    if _selected(value) not in ALLOWED_RATINGS:
        blockers.append(f"{label}.selected_missing_or_invalid")
    if require_evidence and not _text(value.get("evidence")):
        blockers.append(f"{label}.evidence_missing")


def _validate_false_flags(
    value: Mapping[str, Any],
    *,
    prefix: str,
    blockers: list[str],
    expected_fields: tuple[str, ...] | None = None,
) -> None:
    if expected_fields is not None:
        for field in expected_fields:
            if field not in value:
                blockers.append(f"{prefix}.{field}_missing")
    for field, flag in value.items():
        if flag is True:
            blockers.append(f"{prefix}.{field}_must_remain_false")


def _review_coverage(form: Mapping[str, Any]) -> dict[str, Any]:
    surface_reviews = _mapping(form.get("surface_reviews"))
    reviewed_surfaces = [
        surface
        for surface in SURFACES
        if _selected(_mapping(surface_reviews.get(surface))) in ALLOWED_RATINGS
    ]
    return {
        "expected_surfaces": list(SURFACES),
        "reviewed_surfaces": reviewed_surfaces,
        "all_surfaces_reviewed": len(reviewed_surfaces) == len(SURFACES),
        "progression_reviewed": _selected(
            _mapping(form.get("progression_review"))
        )
        in ALLOWED_RATINGS,
        "information_hierarchy_reviewed": _selected(
            _mapping(form.get("information_hierarchy"))
        )
        in ALLOWED_RATINGS,
        "non_claims_reviewed": _selected(_mapping(form.get("non_claims_review")))
        in {"yes", "no", "cannot_judge"},
    }


def _next_gate(
    *,
    intake_status: str,
    overall_decision: str,
    non_claims_selection: str,
) -> str:
    if intake_status == "blocked_pending_human_review":
        return "needs_human_review_before_observatory_expansion"
    if intake_status != "accepted":
        return "needs_human_review_form_repair"
    if non_claims_selection == "no":
        return "needs_non_claims_revision_before_expansion"
    return DECISION_TO_GATE.get(overall_decision, "needs_human_review_form_repair")


def _intake_status(blockers: list[str]) -> str:
    if any(
        item in blockers
        for item in ("local_absolute_path_detected", "privacy_marker_detected")
    ):
        return "blocked_privacy_risk"
    if any(
        item.endswith("_claim_not_allowed") or item.endswith("_must_remain_false")
        for item in blockers
    ):
        return "rejected_boundary_claim"
    if blockers == ["human_review_not_completed"]:
        return "blocked_pending_human_review"
    if "human_review_not_completed" in blockers:
        return "blocked_pending_human_review"
    if blockers:
        return "rejected_invalid_review_form"
    return "accepted"


def _safe_json_dumps(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)


def _safe_source_ref(value: str | None) -> str | None:
    text = _text(value)
    if not text:
        return None
    if _contains_any(text, LOCAL_ABSOLUTE_PATH_MARKERS) or _contains_any(
        text,
        RAW_PRIVATE_MARKERS,
    ):
        return "redacted_unsafe_source_ref"
    return text


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(marker.lower() in lowered for marker in markers)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _selected(value: Mapping[str, Any]) -> str:
    return _text(value.get("selected"))


def _text(value: Any) -> str:
    return str(value or "").strip()


def _dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(item for item in items if item))


def _utc_now() -> str:
    return _dt.datetime.now(_dt.UTC).replace(microsecond=0).isoformat()
