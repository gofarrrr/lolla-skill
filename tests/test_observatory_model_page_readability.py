from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = (
    REPO_ROOT
    / "docs/product/observatory-model-page-readability-and-visible-surface-audit-v0.md"
)
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-model-page-readability-v0/review.json"
)


def _install_launch_case(monkeypatch) -> None:
    monkeypatch.setattr(
        serve_result,
        "_RESULT",
        {
            "usage_summary": {"run_id": "20260627T104146Z_7bfe79"},
            "extraction": {
                "decision_situation": (
                    "A public enterprise beta launch is being reviewed."
                )
            },
            "run_health": {"overall": "healthy", "issues": []},
            "revised_answer": (
                "Launch in stages after the support risk is made explicit. "
                "Keep the first cohort narrow and treat the beta as a learning gate."
            ),
            "delta_card": {
                "top_findings": [
                    {
                        "description": (
                            "Authority pressure was doing too much work in the launch plan."
                        )
                    }
                ]
            },
        },
    )
    monkeypatch.setattr(serve_result, "_RESULT_PATH", None)
    monkeypatch.setattr(serve_result, "_CASE_ID", "lolla-audit")
    monkeypatch.setattr(serve_result, "_CASE_NAME", "Lolla Audit")


def test_model_detail_page_starts_with_learning_value(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_model_detail_html(
        "authority-bias",
        "lolla-audit",
    )

    assert "A selected-run mental model page" not in html
    assert (
        "Learn what this model helps you notice, when to use it, "
        "where it can mislead, and one practice rep for this selected run."
    ) in html
    assert "What This Model Helps You See" in html
    assert "Practice this" in html
    assert "When it misleads" in html
    assert "Source, status, and boundaries" in html
    assert html.index("What This Model Helps You See") < html.index(
        "Source, status, and boundaries"
    )


def test_workspace_model_cards_are_progressive_but_still_complete(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert "What This Model Helps You See" in html
    assert "Use when" in html
    assert "When it misleads" in html
    assert "Practice this" in html
    assert "Use, avoid, and source-backed details" in html
    assert "Helps notice" in html
    assert "Avoid when" in html
    assert "Practice and failure detail" in html
    assert "Open model page" in html
    assert "canonical_model_markdown" in html


def test_workspace_sidebar_collapses_run_switching(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert "<h3>Run Context</h3>" in html
    assert "<summary>Switch run</summary>" in html
    assert "<h3>Recent Runs</h3>" not in html
    assert "Surface Homes" in html


def test_relation_detail_lede_reads_like_a_lesson(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_relation_detail_html(
        "authority-bias__first-principles-thinking__antagonist",
        "lolla-audit",
    )

    assert "A selected-run relation page" not in html
    assert (
        "Read the model relationship as a lesson: the story, why it "
        "matters, where it can be misread, and one practice rep."
    ) in html
    assert html.index("Plain Language Story") < html.index(
        "Taxonomy, confidence, and custody"
    )


def test_visible_surface_audit_records_data_hierarchy_and_next_gate() -> None:
    doc = DOC.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    readme = README.read_text(encoding="utf-8")

    assert "Observatory Model Page Readability And Visible Surface Audit" in readme
    assert "observatory-model-page-readability-and-visible-surface-audit-v0.md" in readme
    assert review["decision_gate"] == (
        "proceed_to_observatory_teacher_route_consolidation_slice"
    )
    assert review["browser_grounded"] is True
    assert review["implemented_changes"]["model_detail_learning_first_lede"] is True
    assert review["implemented_changes"]["recent_runs_collapsed_into_switch_run"] is True
    assert review["visible_surface_audit"][
        "legacy_teacher_learning_duplicates_workspace_flow"
    ] is True

    for phrase in [
        "First-Class User Data",
        "Second-Class User Data",
        "Internal-Only Data",
        "`/teacher-learning` remains a separate full Teacher page",
        "proceed_to_observatory_teacher_route_consolidation_slice",
    ]:
        assert phrase in doc


def test_visible_surface_audit_preserves_boundaries_and_nonclaims() -> None:
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


def test_visible_surface_audit_docs_are_clean_of_local_paths_and_positive_claims() -> None:
    text = DOC.read_text(encoding="utf-8") + REVIEW.read_text(encoding="utf-8")

    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "answer_correctness\": true" not in text
    assert "advice_correctness\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
    assert "action_authorized\": true" not in text
