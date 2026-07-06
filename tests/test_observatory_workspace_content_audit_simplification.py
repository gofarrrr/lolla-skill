from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/product/observatory-workspace-content-audit-and-simplification-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-workspace-content-audit-and-simplification-v0/review.json"
)


def test_content_audit_records_surface_progression_and_data_classes() -> None:
    doc = DOC.read_text(encoding="utf-8")

    for phrase in [
        "Outcome -> Learn -> Models -> Relations -> Map -> Receipts",
        "First-Class Product Data",
        "Second-Class Support Data",
        "Technical Inspection Data",
        "first read -> expandable support -> drill-down page -> receipts/audit",
        "Outcome is the case anchor.",
        "Learn is the reasoning move.",
        "Models are reusable concept pages.",
        "Relations are pair lessons.",
        "Map is navigation.",
        "Receipts are custody and missingness.",
    ]:
        assert phrase in doc


def test_content_audit_distinguishes_teacher_model_and_relation_information() -> None:
    doc = DOC.read_text(encoding="utf-8")

    for phrase in [
        "Teacher information differs from model information",
        "Teacher is case anchored",
        "Teacher is about a reasoning move",
        "Teacher asks the user to practice",
        "Model information differs from Teacher information",
        "model pages are reusable concepts",
        "Relation information differs from model information",
        "relation pages are about a pair, not a concept",
        "relation pages should explain the interaction",
    ]:
        assert phrase in doc


def test_content_audit_records_browser_checked_routes_and_next_gate() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert "Observatory Workspace Content Audit And Simplification" in readme
    assert "observatory-workspace-content-audit-and-simplification-v0.md" in readme
    assert review["decision_gate"] == (
        "proceed_to_observatory_model_relation_content_simplification"
    )
    assert review["browser_check"]["performed"] is True
    assert review["browser_check"]["default_visible_surface"] == "Outcome"
    assert review["browser_check"]["receipts_non_claims_seen"] is True
    assert review["teacher_model_relation_distinction"]["teacher"] == (
        "case anchored practice move"
    )

    for route in [
        "/workspace?case_id=lolla-audit",
        "/workspace?case_id=lolla-audit#learn",
        "/workspace?case_id=lolla-audit#models",
        "/workspace?case_id=lolla-audit#relations",
        "/workspace?case_id=lolla-audit#map",
        "/workspace?case_id=lolla-audit#receipts",
        "/models/authority-bias?case_id=lolla-audit",
        "/relations/authority-bias__first-principles-thinking__antagonist?case_id=lolla-audit",
    ]:
        assert route in review["browser_check"]["routes_checked"]

    for phrase in [
        "proceed_to_observatory_model_relation_content_simplification",
        "make the Models workspace surface a lighter model index",
        "keep Relations story-first",
        "preserve Receipts and Advanced Audit links",
    ]:
        assert phrase in doc


def test_content_audit_boundaries_and_non_claims() -> None:
    doc = DOC.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    for phrase in [
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not create new Lolla runs",
        "does not edit `observatory/build`",
        "does not touch `SKILL.md`",
        "does not touch `scripts/skill/*`",
        "does not touch `scripts/archive_run.py`",
        "does not claim product proof",
        "does not claim human validation",
        "does not claim answer correctness",
        "does not claim advice correctness",
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


def test_content_audit_docs_are_clean_of_local_paths_and_positive_claims() -> None:
    text = DOC.read_text(encoding="utf-8") + REVIEW.read_text(encoding="utf-8")

    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "answer_correctness\": true" not in text
    assert "advice_correctness\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
    assert "action_authorized\": true" not in text
