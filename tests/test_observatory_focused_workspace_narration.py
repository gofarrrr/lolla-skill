from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402
from observatory.product_view_adapters import (  # noqa: E402
    build_observatory_product_view_response,
)


DOC = REPO_ROOT / "docs/product/observatory-focused-workspace-narration-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-focused-workspace-narration-v0/review.json"
)


def _install_launch_case(monkeypatch, *, revised_answer: str | None = None) -> None:
    monkeypatch.setattr(
        serve_result,
        "_RESULT",
        _launch_result(revised_answer=revised_answer),
    )
    monkeypatch.setattr(serve_result, "_RESULT_PATH", None)
    monkeypatch.setattr(serve_result, "_CASE_ID", "lolla-audit")
    monkeypatch.setattr(serve_result, "_CASE_NAME", "Lolla Audit")


def _launch_result(*, revised_answer: str | None = None) -> dict:
    return {
        "usage_summary": {"run_id": "20260627T104146Z_7bfe79"},
        "extraction": {
            "decision_situation": "A public enterprise beta launch is being reviewed."
        },
        "run_health": {"overall": "healthy", "issues": []},
        "revised_answer": revised_answer
        or (
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
    }


def test_workspace_adds_start_here_path_and_browser_focus_mode(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert "Start here" in html
    assert "Use this run as a short lesson." in html
    assert "Read the answer change first." in html
    assert "workspace-step-card" in html
    assert "What changed or survived?" in html
    assert "data-workspace-active-label" in html
    assert "workspace-focus-mode" in html
    assert "updateSections(surface)" in html
    assert 'section.toggleAttribute("hidden", !isActive)' in html
    assert "surfaceLabels" in html


def test_workspace_uses_clear_model_and_relation_page_actions(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert "Open model page" in html
    assert "Open relation page" in html
    assert "Open standalone page" not in html


def test_outcome_summary_strips_markdown_headings_before_product_render() -> None:
    result = _launch_result(
        revised_answer=(
            "## Updated position\n\n"
            "## Updated position\n\n"
            "### What survived\n\n"
            "I would still recommend a limited release, not a broad launch.\n\n"
            "- Keep the first clinic narrow.\n"
        )
    )

    workspace = build_observatory_product_view_response(
        selected_case_id="archive:launch-public-enterprise-beta:20260627T104146Z_7bfe79",
        result=result,
    )["workspace"]
    outcome = workspace["outcome_summary"]

    assert outcome["answer_headline"].startswith("I would still recommend")
    assert outcome["revised_answer_summary"].startswith("I would still recommend")
    assert "##" not in outcome["answer_headline"]
    assert "Updated position" not in outcome["revised_answer_summary"]


def test_map_has_human_labels_and_relation_filter_prefers_edge(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert 'aria-label="Open model: Authority Bias"' in html
    assert (
        'aria-label="Open relation: Authority Bias and First Principles Thinking '
        '(antagonist)"' in html
    )
    assert 'aria-hidden="true">mental_model</text>' in html
    assert "This map is a small wayfinding view for the current lesson." in html
    assert "relationFilterPrefersEdge" in html
    assert "visibleRelationEdges[0]" in html


def test_focused_workspace_docs_review_and_readme_record_boundaries() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert "Observatory Focused Workspace Narration" in readme
    assert "observatory-focused-workspace-narration-v0.md" in readme

    for phrase in [
        "Focused Workspace Mode",
        "Start-Here Narration",
        "Outcome Markdown Cleanup",
        "Clearer Page Actions",
        "Map Narration And Labels",
        "Relation Filter Focus",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not edit `observatory/build`",
        "proceed_to_observatory_focused_workspace_browser_review",
    ]:
        assert phrase in doc

    assert review["decision_gate"] == (
        "proceed_to_observatory_focused_workspace_browser_review"
    )
    assert review["implemented"]["focused_workspace_mode"] is True
    assert review["implemented"]["start_here_narration"] is True
    assert review["implemented"][
        "markdown_heading_cleanup_for_outcome_first_read"
    ] is True
    assert review["implemented"]["map_svg_human_aria_labels"] is True
    assert review["implemented"]["relation_filter_prefers_edge_focus"] is True
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["invokes_lolla_skill"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["compiled_spa_bundle_changed"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False
    assert review["non_claims"]["action_authorized"] is False


def test_focused_workspace_docs_are_clean_of_local_paths_and_positive_claims() -> None:
    text = DOC.read_text(encoding="utf-8") + REVIEW.read_text(encoding="utf-8")

    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "answer_correctness\": true" not in text
    assert "advice_correctness\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
    assert "action_authorized\": true" not in text
