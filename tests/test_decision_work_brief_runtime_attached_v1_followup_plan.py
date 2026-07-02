from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-runtime-attached-v1-followup-plan-v0.md"
)
REVIEW_JSON_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-brief-runtime-attached-v1-followup-plan-v0/review.json"
)
PACKAGE_MANIFEST_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-runtime-attached-v1-package-manifest-v0.json"
)
EXPECTED_SCHEMA = "lolla.decision_work_brief_runtime_attached_v1_followup_plan.v0"
EXPECTED_PRS = {f"PR{number}" for number in range(160, 168)}
APPROVED_NEXT_STEPS = {
    "product_surface_simplification",
    "safe_brief_supply_planning",
    "small_internal_demo_walkthrough",
    "runtime_fixture_expansion",
    "package_and_pause",
}
REQUIRED_FALSE_FIELDS = {
    "human_validated",
    "human_review_completed",
    "product_proof",
    "runtime_invoked",
    "skill_invoked",
    "archive_mutated",
    "prompt_changed",
    "skill_files_changed",
    "answer_quality_scored",
    "agent_action_authorized",
    "automatic_action_authorized",
    "customer_readiness_claimed",
    "default_on_runtime_behavior_claimed",
    "advice_correctness_claimed",
    "lolla_improvement_proof_claimed",
}
PRIVACY_MARKERS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)


def _review() -> dict[str, Any]:
    return json.loads(REVIEW_JSON_PATH.read_text(encoding="utf-8"))


def test_review_schema_and_reviewed_prs() -> None:
    review = _review()

    assert review["schema_version"] == EXPECTED_SCHEMA
    reviewed_prefixes = {item.split()[0] for item in review["reviewed_prs"]}
    assert reviewed_prefixes == EXPECTED_PRS
    assert len(review["reviewed_prs"]) == 8


def test_review_flags_are_conservative() -> None:
    review = _review()

    assert review["model_calls"] == 0
    for field in REQUIRED_FALSE_FIELDS:
        assert review[field] is False


def test_selected_next_step_and_recommendation_are_bounded() -> None:
    review = _review()

    assert review["selected_next_step"] in APPROVED_NEXT_STEPS
    assert review["selected_next_step"] == "safe_brief_supply_planning"
    assert review["recommended_next_pr"]
    assert "PR169" in review["recommended_next_pr"]
    selected = [
        option
        for option in review["options_considered"]
        if option["option"] == review["selected_next_step"]
    ]
    assert selected and selected[0]["selected"] is True


def test_review_records_mechanical_attachment_and_supply_limit() -> None:
    review = _review()

    hook = review["runtime_hook_read"]
    assert hook["state"] == "mechanically_attached_but_input_supply_limited"
    assert hook["default_off"] is True
    assert hook["post_archive_only"] is True
    assert hook["non_blocking"] is True
    assert hook["fail_closed"] is True
    assert "supply-limited" in review["strongest_unresolved_risk"]
    assert "runtime hinge" in review["strongest_useful_signal"]


def test_review_does_not_claim_customer_readiness_or_authority() -> None:
    rendered = REVIEW_JSON_PATH.read_text(encoding="utf-8")

    forbidden_fragments = (
        '"customer_readiness_claimed": true',
        '"default_on_runtime_behavior_claimed": true',
        '"advice_correctness_claimed": true',
        '"lolla_improvement_proof_claimed": true',
        '"human_validated": true',
        '"product_proof": true',
        '"answer_quality_scored": true',
        '"agent_action_authorized": true',
        '"automatic_action_authorized": true',
        "customer_ready",
        "default-on runtime behavior is implemented",
        "advice is correct",
        "Lolla improved the decision",
    )
    for fragment in forbidden_fragments:
        assert fragment not in rendered


def test_docs_and_review_have_no_private_markers() -> None:
    rendered = (
        DOC_PATH.read_text(encoding="utf-8")
        + "\n"
        + REVIEW_JSON_PATH.read_text(encoding="utf-8")
    )

    for marker in PRIVACY_MARKERS:
        assert marker not in rendered


def test_package_manifest_still_exists_for_followup_context() -> None:
    manifest = json.loads(PACKAGE_MANIFEST_PATH.read_text(encoding="utf-8"))

    assert manifest["schema_version"] == (
        "lolla.decision_work_brief_runtime_attached_v1_package_manifest.v0"
    )
    assert manifest["decision_gate"] == "runtime_attached_internal_v1_packaged"


def test_followup_docs_and_json_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths([DOC_PATH, REVIEW_JSON_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
