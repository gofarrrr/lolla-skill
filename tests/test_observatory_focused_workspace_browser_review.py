from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/product/observatory-focused-workspace-browser-review-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-focused-workspace-browser-review-v0/review.json"
)


def test_focused_browser_review_records_product_progression() -> None:
    doc = DOC.read_text(encoding="utf-8")

    for phrase in [
        "Observatory Focused Workspace Browser Review",
        "Did the focused workspace make Observatory feel like a guided product path",
        "Root First Read",
        "Surface Switching",
        "Outcome Cleanup",
        "Relations",
        "Map",
        "Mobile Layout",
        "start with the selected run",
        "open Advanced Audit only for technical inspection",
    ]:
        assert phrase in doc


def test_focused_browser_review_records_clicked_scope() -> None:
    doc = DOC.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    for phrase in [
        "Root workspace",
        "Learn surface",
        "Models surface",
        "Model detail",
        "Relations surface",
        "Map search",
        "Map relation filter",
        "Receipts surface",
        "Mobile viewport",
        "`first`",
        "`antagonist`",
    ]:
        assert phrase in doc

    for route in [
        "/",
        "/workspace?case_id=lolla-audit#learn",
        "/workspace?case_id=lolla-audit#models",
        "/models/authority-bias?case_id=lolla-audit",
        "/workspace?case_id=lolla-audit#map",
        "/workspace?case_id=lolla-audit#receipts",
    ]:
        assert route in review["browser_scope"]["routes_opened"]


def test_focused_browser_review_records_working_signals_and_remaining_risks() -> None:
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert review["decision_gate"] == (
        "proceed_to_observatory_model_page_readability_slice"
    )
    assert review["browser_grounded"] is True
    assert review["confirmed_working"]["root_shows_start_here_path"] is True
    assert review["confirmed_working"][
        "browser_focus_mode_hides_inactive_sections"
    ] is True
    assert review["confirmed_working"]["map_relation_filter_selects_edge"] is True
    assert review["confirmed_working"][
        "archive_outcome_markdown_heading_cleanup"
    ] is True
    assert review["remaining_ux_risks"][
        "model_detail_page_leads_with_boundary_copy"
    ] is True
    assert review["remaining_ux_risks"][
        "receipts_source_refs_are_dense_when_expanded"
    ] is True
    assert review["recommended_next_pr"]["title"] == (
        "Add Observatory model page readability slice"
    )


def test_focused_browser_review_readme_and_review_json_are_wired() -> None:
    readme = README.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert "Observatory Focused Workspace Browser Review" in readme
    assert "observatory-focused-workspace-browser-review-v0.md" in readme
    assert review["recommended_next_pr"]["gate"] == (
        "proceed_to_observatory_model_page_readability_slice"
    )


def test_focused_browser_review_boundaries_and_non_claims_are_explicit() -> None:
    doc = DOC.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    for phrase in [
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not create new Lolla runs",
        "does not wire runtime behavior",
        "does not edit `observatory/build`",
        "does not touch `SKILL.md`",
        "does not touch `scripts/skill/*`",
        "does not touch `scripts/archive_run.py`",
        "does not claim product proof",
        "does not claim human validation",
        "does not claim answer correctness",
        "does not claim advice correctness",
        "does not authorize action",
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


def test_focused_browser_review_docs_are_clean_of_local_paths_and_positive_claims() -> None:
    text = DOC.read_text(encoding="utf-8") + REVIEW.read_text(encoding="utf-8")

    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "answer_correctness\": true" not in text
    assert "advice_correctness\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
    assert "action_authorized\": true" not in text
