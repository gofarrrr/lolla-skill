from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from engine.system_b.observatory_workspace_human_review_intake import (  # noqa: E402
    FORM_SCHEMA_VERSION,
    INTAKE_SCHEMA_VERSION,
    SURFACES,
    load_observatory_workspace_human_review_form,
    render_observatory_workspace_human_review_intake_json,
    validate_observatory_workspace_human_review_form,
    write_observatory_workspace_human_review_intake_result,
)


FORM_JSON = (
    REPO_ROOT
    / "docs/product/observatory-workspace-user-review-packet-v0/human-review-form.json"
)
DOC = REPO_ROOT / "docs/product/observatory-workspace-human-review-intake-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-workspace-human-review-intake-v0/review.json"
)


def _blank_form() -> dict:
    return json.loads(FORM_JSON.read_text(encoding="utf-8"))


def _completed_form(*, overall: str = "needs_first_screen_revision") -> dict:
    form = copy.deepcopy(_blank_form())
    form.update(
        {
            "status": "completed_human_review",
            "human_review_completed": True,
        }
    )
    form["workspace_reviewed"] = {
        "case_id": "lolla-audit",
        "run_id": "20260627T104146Z_7bfe79",
        "review_date": "2026-07-06",
        "reviewer": "human-reviewer",
    }
    form["overall_decision"]["selected"] = overall
    form["overall_decision"]["notes"] = "The first screen needs clearer framing."
    form["first_impression"] = {
        "page_purpose_in_first_ten_seconds": "A run learning workspace.",
        "wanted_next_click": "Learn.",
        "one_product_or_artifact_pile": "Mostly one product, but the first screen is dense.",
    }
    form["progression_review"]["selected"] = "adequate"
    form["progression_review"]["evidence"] = (
        "The flow from outcome into Learn and drilldowns is understandable."
    )
    for surface in SURFACES:
        form["surface_reviews"][surface]["selected"] = "adequate"
        form["surface_reviews"][surface]["what_worked"] = (
            f"{surface} has a recognizable job."
        )
        form["surface_reviews"][surface]["what_should_change"] = ""
    form["information_hierarchy"]["selected"] = "adequate"
    form["information_hierarchy"]["evidence"] = (
        "First read and drilldowns are separated."
    )
    form["non_claims_review"]["selected"] = "yes"
    form["non_claims_review"]["evidence"] = (
        "Receipts and copy avoid product-proof and action claims."
    )
    return form


def test_blank_review_form_stays_pending_and_does_not_authorize_downstream() -> None:
    intake = validate_observatory_workspace_human_review_form(
        _blank_form(),
        source_ref="docs/product/observatory-workspace-user-review-packet-v0/human-review-form.json",
        created_at="2026-07-06T00:00:00+00:00",
    )

    assert intake["schema_version"] == INTAKE_SCHEMA_VERSION
    assert intake["intake_status"] == "blocked_pending_human_review"
    assert intake["accepted_for_downstream"] is False
    assert intake["repair_required"] is True
    assert intake["blocker_reasons"] == ["human_review_not_completed"]
    assert intake["next_gate"] == "needs_human_review_before_observatory_expansion"
    assert intake["downstream_allowed"]["can_plan_revision"] is False
    assert all(
        value is False
        for key, value in intake["downstream_allowed"].items()
        if key != "can_plan_revision"
    )


def test_completed_review_form_maps_to_revision_gate_without_product_claims() -> None:
    intake = validate_observatory_workspace_human_review_form(
        _completed_form(),
        source_ref="reviews/human/observatory-workspace/review.json",
        created_at="2026-07-06T00:00:00+00:00",
    )

    assert intake["intake_status"] == "accepted"
    assert intake["accepted_for_downstream"] is True
    assert intake["repair_required"] is False
    assert intake["blocker_reasons"] == []
    assert intake["next_gate"] == "needs_first_screen_revision"
    assert intake["review_coverage"]["all_surfaces_reviewed"] is True
    assert intake["review_coverage"]["reviewed_surfaces"] == list(SURFACES)
    assert intake["downstream_allowed"]["can_plan_revision"] is True
    assert intake["downstream_allowed"]["can_expand_product"] is False
    assert intake["downstream_allowed"]["can_claim_human_validation"] is False
    assert intake["downstream_allowed"]["can_claim_product_proof"] is False
    assert intake["downstream_allowed"]["can_wire_runtime"] is False
    assert intake["downstream_allowed"]["can_authorize_action"] is False
    assert "intake_does_not_complete_human_review" in intake["non_claims"]
    assert "intake_is_not_product_proof" in intake["non_claims"]


def test_ready_with_caveats_still_allows_planning_not_expansion() -> None:
    intake = validate_observatory_workspace_human_review_form(
        _completed_form(overall="ready_to_continue_with_caveats"),
        created_at="2026-07-06T00:00:00+00:00",
    )

    assert intake["intake_status"] == "accepted"
    assert (
        intake["next_gate"]
        == "ready_to_plan_next_observatory_slice_with_human_caveats"
    )
    assert intake["downstream_allowed"]["can_plan_revision"] is True
    assert intake["downstream_allowed"]["can_expand_product"] is False


def test_non_claim_problem_overrides_ready_gate_to_revision() -> None:
    form = _completed_form(overall="ready_to_continue_with_caveats")
    form["non_claims_review"]["selected"] = "no"
    form["non_claims_review"]["evidence"] = "The map looked like proof."

    intake = validate_observatory_workspace_human_review_form(
        form,
        created_at="2026-07-06T00:00:00+00:00",
    )

    assert intake["intake_status"] == "accepted"
    assert intake["next_gate"] == "needs_non_claims_revision_before_expansion"
    assert intake["downstream_allowed"]["can_expand_product"] is False


def test_boundary_claims_are_rejected_even_when_form_is_completed() -> None:
    form = _completed_form()
    form["human_validated"] = True
    form["non_claims"]["product_proof"] = True

    intake = validate_observatory_workspace_human_review_form(
        form,
        created_at="2026-07-06T00:00:00+00:00",
    )

    assert intake["intake_status"] == "rejected_boundary_claim"
    assert intake["accepted_for_downstream"] is False
    assert "human_validated_claim_not_allowed" in intake["blocker_reasons"]
    assert "non_claims.product_proof_must_remain_false" in intake["blocker_reasons"]
    assert intake["next_gate"] == "needs_human_review_form_repair"


def test_missing_surface_review_rejects_completed_form() -> None:
    form = _completed_form()
    del form["surface_reviews"]["Map"]

    intake = validate_observatory_workspace_human_review_form(
        form,
        created_at="2026-07-06T00:00:00+00:00",
    )

    assert intake["intake_status"] == "rejected_invalid_review_form"
    assert "surface_reviews.Map_missing" in intake["blocker_reasons"]
    assert intake["review_coverage"]["all_surfaces_reviewed"] is False


def test_privacy_markers_block_form_without_leaking_source_ref() -> None:
    form = _completed_form()
    form["overall_decision"]["notes"] = "private " + "api" + "_key marker"

    intake = validate_observatory_workspace_human_review_form(
        form,
        source_ref="/" + "Users/example/private-review.json",
        created_at="2026-07-06T00:00:00+00:00",
    )

    rendered = render_observatory_workspace_human_review_intake_json(intake)

    assert intake["intake_status"] == "blocked_privacy_risk"
    assert intake["accepted_for_downstream"] is False
    assert "privacy_marker_detected" in intake["blocker_reasons"]
    assert intake["intake_metadata"]["source_ref"] == "redacted_unsafe_source_ref"
    assert "/" + "Users/" not in rendered
    assert "api" + "_key" not in rendered


def test_load_render_and_write_intake_round_trip(tmp_path: Path) -> None:
    form_path = tmp_path / "review.json"
    form_path.write_text(json.dumps(_completed_form()), encoding="utf-8")

    form = load_observatory_workspace_human_review_form(form_path)
    intake = validate_observatory_workspace_human_review_form(
        form,
        source_ref="reviews/human/observatory-workspace/review.json",
        created_at="2026-07-06T00:00:00+00:00",
    )
    out = write_observatory_workspace_human_review_intake_result(
        tmp_path / "intake.json",
        intake,
    )
    loaded = json.loads(out.read_text(encoding="utf-8"))

    assert loaded == intake
    assert render_observatory_workspace_human_review_intake_json(intake).endswith("\n")


def test_intake_docs_review_and_readme_capture_gate_and_boundaries() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert "Observatory Workspace Human Review Intake" in readme
    assert "observatory-workspace-human-review-intake-v0.md" in readme

    for phrase in [
        "deterministic intake validator",
        "blank forms remain blocked",
        "completed forms may plan revision work",
        "does not complete human review",
        "does not run Lolla",
        "does not call providers or model APIs",
        "does not wire runtime behavior",
        "needs_human_review_form_repair",
        "needs_non_claims_revision_before_expansion",
    ]:
        assert phrase in doc

    assert review["decision_gate"] == "ready_to_validate_human_review_response"
    assert review["implemented"]["deterministic_intake_validator"] is True
    assert review["implemented"]["runtime_behavior_changed"] is False
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["invokes_lolla_skill"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["compiled_spa_bundle_changed"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False
    assert review["non_claims"]["action_authorized"] is False


def test_markdown_links_and_packet_artifacts_are_clean() -> None:
    missing = []
    for path in [DOC, README]:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith("#") or re.match(r"^[a-z]+:", target):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                missing.append(f"{path}: {target}")
    assert missing == []

    rendered = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [DOC, REVIEW, REPO_ROOT / "engine/system_b/observatory_workspace_human_review_intake.py"]
    )
    assert "/" + "Users/" not in rendered
    assert "Desktop/" + "Apps" not in rendered
    assert "product_proof\": true" not in rendered
    assert "human_validated\": true" not in rendered
    assert "answer_correctness\": true" not in rendered
    assert "advice_correctness\": true" not in rendered
    assert "runtime_integration_authorized\": true" not in rendered
    assert "action_authorized\": true" not in rendered
