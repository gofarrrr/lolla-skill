from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/product/observatory-progressive-workspace-browser-review-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-progressive-workspace-browser-review-v0/review.json"
)


def test_browser_review_doc_records_visible_layers_and_progression() -> None:
    doc = DOC.read_text(encoding="utf-8")

    for phrase in [
        "Observatory Progressive Workspace Browser Review",
        "selected run",
        "what changed in the answer",
        "what reasoning move can I practice",
        "which models explain the move",
        "which relation teaches the pair",
        "what small map helps me navigate it",
        "what can I trust or inspect",
        "advanced telemetry only when needed",
        "First-Class, Expandable, And Advanced Data",
    ]:
        assert phrase in doc


def test_browser_review_doc_records_browser_clicked_scope() -> None:
    doc = DOC.read_text(encoding="utf-8")

    for phrase in [
        "Root workspace",
        "Learn tab",
        "Models tab",
        "Model detail",
        "Relations tab",
        "Relation detail",
        "Map search",
        "Map relation filter",
        "Map no-results",
        "Receipts tab",
        "Advanced Audit",
        "Extraction",
        "Usage",
        "Archive sample",
        "`first`",
        "`zzzz`",
    ]:
        assert phrase in doc


def test_browser_review_records_next_gate_and_risks() -> None:
    doc = DOC.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert "Add Observatory focused workspace narration" in doc
    assert (
        "proceed_to_observatory_focused_workspace_narration_slice" in doc
    )
    assert review["decision_gate"] == (
        "proceed_to_observatory_focused_workspace_narration_slice"
    )
    assert review["browser_grounded"] is True
    assert review["confirmed_working"]["relation_pages_story_first"] is True
    assert review["remaining_ux_risks"]["root_page_still_exposes_full_stack"] is True
    assert review["remaining_ux_risks"][
        "archive_outcome_markdown_heading_leaks"
    ] is True
    assert review["remaining_ux_risks"][
        "map_svg_labels_concatenate_model_type"
    ] is True
    assert review["recommended_next_pr"]["title"] == (
        "Add Observatory focused workspace narration"
    )


def test_browser_review_readme_and_review_json_are_wired() -> None:
    readme = README.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert "Observatory Progressive Workspace Browser Review" in readme
    assert "observatory-progressive-workspace-browser-review-v0.md" in readme

    for route in [
        "/",
        "/workspace?case_id=lolla-audit#learn",
        "/models/authority-bias?case_id=lolla-audit",
        "/workspace?case_id=lolla-audit#map",
        "/audit/extraction",
        "/usage",
    ]:
        assert route in review["browser_scope"]["routes_opened"]


def test_browser_review_boundaries_and_non_claims_are_explicit() -> None:
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


def test_browser_review_docs_are_clean_of_local_paths_and_positive_claims() -> None:
    text = DOC.read_text(encoding="utf-8") + REVIEW.read_text(encoding="utf-8")

    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "answer_correctness\": true" not in text
    assert "advice_correctness\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
    assert "action_authorized\": true" not in text
