from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/product/observatory-workspace-product-flow-audit-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-workspace-product-flow-audit-v0/review.json"
)


def test_product_flow_audit_records_browser_scope_and_current_surfaces() -> None:
    doc = DOC.read_text(encoding="utf-8")

    for phrase in [
        "Browser Audit Scope",
        "Root workspace",
        "Workspace tabs",
        "Model pages",
        "Relation page",
        "Map controls",
        "Receipts",
        "Advanced Audit",
        "Archive sample",
    ]:
        assert phrase in doc

    for surface in [
        "Workspace Shell",
        "Outcome",
        "Learn",
        "Models",
        "Relations",
        "Map",
        "Receipts",
        "Advanced Audit",
    ]:
        assert f"### {surface}" in doc


def test_product_flow_audit_defines_progression_and_information_tiers() -> None:
    doc = DOC.read_text(encoding="utf-8")

    for phrase in [
        "First-Class, Second-Class, And Internal Data",
        "Desired Product Progression",
        "The first screen should not try to show all seven layers",
        "Read the outcome",
        "Practice the lesson",
        "Open the model cards",
        "Explore the map",
        "Check receipts",
    ]:
        assert phrase in doc


def test_product_flow_audit_names_critical_findings_and_next_gate() -> None:
    doc = DOC.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    for phrase in [
        "The Route Family Is Right",
        "The Page Is Still Too Dense For A Normal User",
        "Teacher Needs A More Guided First Read",
        "Model Pages Need A Library Card Shape",
        "Relations Are The Best Current Product Signal",
        "Receipts Are Correct But Too Loud",
        "Advanced Audit Must Be Visually Demoted",
        "Map Interaction Has One Immediate UX Bug",
        "Add Observatory progressive workspace UX hierarchy",
    ]:
        assert phrase in doc

    assert review["decision_gate"] == (
        "proceed_to_observatory_progressive_workspace_ux_slice"
    )
    assert review["findings"]["page_is_too_dense_for_normal_user"] is True
    assert review["findings"]["map_selection_can_stay_stale_after_filter"] is True
    assert review["recommended_next_slice"]["add_first_read_cards"] is True
    assert review["recommended_next_slice"]["move_support_data_behind_disclosure"] is True


def test_product_flow_audit_is_registered_and_preserves_boundaries() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert "Observatory Workspace Product Flow Audit" in readme
    assert "observatory-workspace-product-flow-audit-v0.md" in readme

    for phrase in [
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not edit `observatory/build`",
        "does not claim product proof",
        "does not claim human validation",
        "does not claim answer correctness",
        "does not claim advice correctness",
        "does not authorize action",
        "does not treat graph edges as proof",
    ]:
        assert phrase in doc

    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["invokes_lolla_skill"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["compiled_spa_bundle_changed"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False
    assert review["non_claims"]["action_authorized"] is False


def test_product_flow_audit_docs_and_review_are_clean() -> None:
    text = DOC.read_text(encoding="utf-8") + REVIEW.read_text(encoding="utf-8")

    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "answer_correctness\": true" not in text
    assert "advice_correctness\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
    assert "action_authorized\": true" not in text
