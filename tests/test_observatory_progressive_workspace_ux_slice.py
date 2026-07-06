from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/observatory-progressive-workspace-ux-slice-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-progressive-workspace-ux-slice-v0/review.json"
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


def test_workspace_uses_first_read_cards_before_support_details(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert html.count("data-first-read-card") >= 6
    assert "Read outcome" in html
    assert "Practice lesson" in html
    assert "Outcome support details" in html
    assert "Lesson steps and boundaries" in html
    assert html.index("What happened in this run?") < html.index(
        "Outcome support details"
    )
    assert html.index("What reasoning move can I practice?") < html.index(
        "Lesson steps and boundaries"
    )


def test_model_and_relation_pages_defer_support_metadata(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert "What This Model Helps You See" in html
    assert "Everything We Know" not in html
    assert "Practice and failure detail" in html
    assert "Source, status, and boundaries" in html
    assert "Taxonomy, confidence, and custody" in html

    story_index = html.index("Plain Language Story")
    taxonomy_disclosure_index = html.index("Taxonomy, confidence, and custody")
    confidence_index = html.index("confidence: medium")

    assert story_index < taxonomy_disclosure_index < confidence_index


def test_receipts_and_advanced_audit_are_demoted(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert "Trust summary" in html
    assert "What can I trust or inspect?" in html
    assert "Source refs and missing fields" in html
    assert "Advanced inspection index" in html
    assert "Workspace boundary" in html
    assert "status-link-advanced" in html
    assert 'href="/audit">Advanced Audit</a>' in html
    assert "Advanced Audit Index" not in html


def test_map_selection_reconciles_after_filtering(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert "No visible map item" in html
    assert "No model or relation matches the current search and filters." in html
    assert "visibleItems.length" in html
    assert "selected.classList.contains(\"is-filtered\")" in html
    assert "clearSelection(root)" in html
    assert "aria-disabled" in html


def test_progressive_workspace_slice_docs_review_and_readme_record_boundaries() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert "Observatory Progressive Workspace UX Slice" in readme
    assert "observatory-progressive-workspace-ux-slice-v0.md" in readme

    for phrase in [
        "First-Read Cards",
        "Disclosure Blocks",
        "Model Page Language",
        "Advanced Audit Demotion",
        "Map Selection Fix",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not edit `observatory/build`",
        "proceed_to_observatory_progressive_workspace_browser_review",
    ]:
        assert phrase in doc

    assert review["decision_gate"] == (
        "proceed_to_observatory_progressive_workspace_browser_review"
    )
    assert review["implemented"]["first_read_cards"] is True
    assert review["implemented"]["workspace_disclosure_blocks"] is True
    assert review["implemented"]["advanced_audit_demoted"] is True
    assert review["implemented"]["map_selection_reconciles_after_filter"] is True
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["invokes_lolla_skill"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["compiled_spa_bundle_changed"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False
    assert review["non_claims"]["action_authorized"] is False


def test_progressive_workspace_slice_docs_and_review_are_clean() -> None:
    text = DOC.read_text(encoding="utf-8") + REVIEW.read_text(encoding="utf-8")

    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "answer_correctness\": true" not in text
    assert "advice_correctness\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
    assert "action_authorized\": true" not in text
