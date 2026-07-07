from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/product/observatory-review-guide-browser-audit-v0.md"
SUMMARY = REPO_ROOT / "docs/product/observatory-review-guide-browser-audit-v0.json"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-review-guide-browser-audit-v0/review.json"
)

SURFACES = [
    "Review Guide",
    "Outcome",
    "Learn",
    "Models",
    "Model detail",
    "Relations",
    "Relation detail",
    "Map",
    "Receipts",
    "Extraction audit",
    "Usage",
    "Advanced audit",
]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_browser_audit_is_indexed_and_records_post_review_guide_scope() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    summary = _load_json(SUMMARY)
    review = _load_json(REVIEW)

    assert "Observatory Review Guide Browser Audit" in readme
    assert "observatory-review-guide-browser-audit-v0.md" in readme
    assert "observatory-review-guide-browser-audit-v0.json" in readme
    assert summary["browser_grounded"] is True
    assert review["browser_grounded"] is True
    assert review["human_review_completed"] is False
    assert summary["decision_gate"] == "ready_for_human_hierarchy_review"
    assert review["decision_gate"] == "ready_for_human_hierarchy_review"

    for route in [
        "/review/observatory-workspace?case_id=launch-public-enterprise-beta",
        "/workspace?case_id=launch-public-enterprise-beta#outcome",
        "/workspace?case_id=launch-public-enterprise-beta#learn",
        "/workspace?case_id=launch-public-enterprise-beta#models",
        "/models/authority-bias?case_id=launch-public-enterprise-beta",
        "/workspace?case_id=launch-public-enterprise-beta#relations",
        "/relations/authority-bias__first-principles-thinking__antagonist?case_id=launch-public-enterprise-beta",
        "/workspace?case_id=launch-public-enterprise-beta#map",
        "/workspace?case_id=launch-public-enterprise-beta#receipts",
        "/audit/extraction",
        "/usage",
        "/audit",
    ]:
        assert route in summary["routes_checked"]
        assert route in review["routes_checked"]

    for phrase in [
        "Review Guide -> Outcome",
        "Outcome -> Learn",
        "Models -> model detail",
        "Relations -> relation detail",
        "Map search",
        "Map relation filter",
        "Map reset",
        "Receipts -> Extraction audit",
        "direct open of Advanced audit",
    ]:
        assert phrase in doc


def test_browser_audit_records_progression_hierarchy_and_interactions() -> None:
    doc = DOC.read_text(encoding="utf-8")
    summary = _load_json(SUMMARY)
    review = _load_json(REVIEW)

    assert summary["normal_progression"] == [
        "Outcome",
        "Learn",
        "Models",
        "Relations",
        "Map",
        "Receipts",
    ]
    assert summary["review_progression"] == [
        "Review Guide",
        "Outcome",
        "Learn",
        "Models",
        "Model detail",
        "Relations",
        "Relation detail",
        "Map",
        "Receipts",
        "Audit only if needed",
    ]
    assert summary["hierarchy"] == {
        "primary": ["Outcome", "Learn"],
        "supporting": ["Models", "Relations", "Map"],
        "inspection": ["Receipts", "Audit"],
    }

    for interaction in [
        "review_guide_open_workspace_at_outcome",
        "outcome_practice_lesson_link",
        "model_detail_link",
        "relation_detail_link",
        "map_search_models",
        "map_relation_filter",
        "map_reset",
        "receipts_technical_inspection_links",
    ]:
        assert interaction in summary["interactions_checked"]
        assert interaction in review["interactions_checked"]

    for phrase in [
        "Review Guide -> Outcome -> Learn -> Models -> Relations -> Map -> Receipts -> Audit only if needed",
        "Outcome -> Learn -> Models -> Relations -> Map -> Receipts",
        "`primary: Outcome and Learn`",
        "`supporting: Models, Relations, and Map`",
        "`inspection: Receipts and Audit`",
    ]:
        assert phrase in doc


def test_surface_audit_records_every_visible_surface_and_overload_risk() -> None:
    doc = DOC.read_text(encoding="utf-8")
    summary = _load_json(SUMMARY)
    review = _load_json(REVIEW)

    assert [item["surface"] for item in summary["surface_audit"]] == SURFACES
    assert review["surfaces_audited"] == SURFACES

    by_surface = {item["surface"]: item for item in summary["surface_audit"]}
    assert by_surface["Review Guide"]["layer"] == "supporting_review"
    assert "cold_user_hierarchy_check" in by_surface["Review Guide"]["visible_data"]
    assert by_surface["Outcome"]["layer"] == "primary"
    assert "missing_outcome_state" in by_surface["Outcome"]["visible_data"]
    assert by_surface["Learn"]["progression_role"] == "primary_teaching_value"
    assert "thinking_move" in by_surface["Learn"]["visible_data"]
    assert "role_cues" in by_surface["Models"]["visible_data"]
    assert "library_view" in by_surface["Model detail"]["visible_data"]
    assert "run_context" in by_surface["Model detail"]["visible_data"]
    assert by_surface["Relations"]["progression_role"] == "supporting_relation_story"
    assert by_surface["Relation detail"]["overload_risk"] == (
        "low_current_risk_because_page_is_focused_and_story_first"
    )
    assert "non_proof_copy" in by_surface["Map"]["visible_data"]
    assert by_surface["Receipts"]["layer"] == "inspection"
    assert by_surface["Advanced audit"]["overload_risk"] == (
        "highest_overload_risk_and_should_remain_behind_receipts_or_explicit_audit_entry"
    )

    for phrase in [
        "missingness can still feel like absence",
        "selection reason is still mostly implicit",
        "supporting model detail",
        "receipts, and audit routes as equal",
        "Advanced audit is not the main user journey",
    ]:
        assert phrase in doc


def test_browser_audit_states_useful_signal_risk_and_next_gate() -> None:
    doc = DOC.read_text(encoding="utf-8")
    summary = _load_json(SUMMARY)
    review = _load_json(REVIEW)

    assert summary["strongest_useful_signal"] == review["strongest_useful_signal"]
    assert summary["strongest_unresolved_risk"] == (
        review["strongest_unresolved_risk"]
    )
    assert summary["recommended_next_pr"] == review["recommended_next_pr"]

    for phrase in [
        "The strongest useful signal is that the current Observatory surface now has a testable hierarchy.",
        "The strongest unresolved risk is still cognitive overload.",
        "ready_for_human_hierarchy_review",
        "The audit can confirm these cues exist. It cannot confirm that they work for a human learner.",
        "collect the first human hierarchy review using the blank form",
    ]:
        assert phrase in doc

    assert review["implemented"]["browser_grounded_audit_doc"] is True
    assert review["implemented"]["machine_readable_audit_summary"] is True
    assert review["implemented"]["post_review_guide_hierarchy_prompt_check"] is True
    assert review["implemented"]["runtime_behavior_changed"] is False
    assert review["implemented"]["compiled_spa_bundle_changed"] is False


def test_browser_audit_boundary_non_claims_links_and_privacy_are_clean() -> None:
    summary = _load_json(SUMMARY)
    review = _load_json(REVIEW)

    for payload in [summary, review]:
        assert payload["boundary"]["runs_lolla"] is False
        assert payload["boundary"]["invokes_lolla_skill"] is False
        assert payload["boundary"]["calls_provider_or_model"] is False
        assert payload["boundary"]["creates_new_run"] is False
        assert payload["boundary"]["generates_sidecars"] is False
        assert payload["boundary"]["wires_skill_runtime_behavior"] is False
        assert payload["boundary"]["mutates_archives"] is False
        assert payload["boundary"]["compiled_spa_bundle_changed"] is False
        assert payload["boundary"]["touches_skill_md"] is False
        assert payload["boundary"]["touches_scripts_skill"] is False
        assert payload["boundary"]["touches_archive_run"] is False
        assert payload["non_claims"]["product_proof"] is False
        assert payload["non_claims"]["human_validated"] is False
        assert payload["non_claims"]["answer_correctness"] is False
        assert payload["non_claims"]["advice_correctness"] is False
        assert payload["non_claims"]["action_authorized"] is False
        assert payload["non_claims"]["graph_edges_are_proof"] is False
        assert payload["non_claims"]["relation_confidence_is_certification"] is False

    missing = []
    for path in [DOC, README]:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith("#") or re.match(r"^[a-z]+:", target):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                missing.append(f"{path}: {target}")

    text = "\n".join(
        path.read_text(encoding="utf-8") for path in [DOC, SUMMARY, REVIEW]
    )

    assert missing == []
    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "answer_correctness\": true" not in text
    assert "advice_correctness\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
    assert "action_authorized\": true" not in text
