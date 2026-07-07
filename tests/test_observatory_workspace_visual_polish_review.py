from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/observatory-workspace-visual-polish-review-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-workspace-visual-polish-review-v0/review.json"
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
        },
    )
    monkeypatch.setattr(serve_result, "_RESULT_PATH", None)
    monkeypatch.setattr(serve_result, "_CASE_ID", "lolla-audit")
    monkeypatch.setattr(serve_result, "_CASE_NAME", "Lolla Audit")


def test_workspace_first_view_uses_product_facing_learning_frame(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert "<h1>Run Learning Workspace</h1>" in html
    assert "Start with the run result." in html
    assert "Launch in stages after the support risk is made explicit." in html
    assert "Why this changed" in html
    assert "What would change confidence" in html
    assert "Selected Run Workspace" not in html
    assert "Use this run as a short lesson." not in html


def test_workspace_no_longer_uses_center_start_panel(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert "data-workspace-start-panel" not in html
    assert ".workspace-start-panel[hidden]" in html
    assert 'const showStartPanel = surface === "outcome";' not in html
    assert 'panel.toggleAttribute("hidden", !showStartPanel)' not in html
    assert 'data-workspace-default-surface="outcome"' in html


def test_workspace_sidebar_surface_homes_are_wayfinding_not_explanation(
    monkeypatch,
) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert "Reading Path" in html
    assert 'aria-label="Workspace reading path"' in html
    for surface in ["outcome", "learn", "models", "relations", "map", "receipts"]:
        assert f'data-workspace-surface-link="{surface}"' in html
    for old_label in [
        "Outcome: run result",
        "Learn: reasoning move",
        "Models: mental model knowledge",
        "Relations: model-pair lesson",
        "Receipts: custody and missingness",
    ]:
        assert old_label not in html


def test_visual_polish_docs_review_and_readme_capture_gate() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert "Observatory Workspace Visual Polish Review" in readme
    assert "observatory-workspace-visual-polish-review-v0.md" in readme

    for phrase in [
        "Run Learning Workspace",
        "Start Here panel is hidden",
        "browser click-through covered Outcome, Learn, Models, Relations, Map, and",
        "Start Here remains visible only on Outcome",
        "Outcome -> Learn -> Models -> Relations -> Map -> Receipts",
        "first read -> optional support -> drill-down page -> receipts/audit",
        "mobile body width does not exceed viewport width",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not edit `observatory/build`",
        "proceed_to_observatory_workspace_user_review_packet",
    ]:
        assert phrase in doc

    assert review["decision_gate"] == "proceed_to_observatory_workspace_user_review_packet"
    assert review["implemented"]["workspace_title_reframed"] is True
    assert review["implemented"]["workspace_lede_shortened"] is True
    assert review["implemented"]["start_panel_outcome_only"] is True
    assert review["implemented"]["focused_surfaces_hide_start_panel"] is True
    assert review["implemented"]["surface_homes_sidebar_compacted"] is True
    assert review["browser_check"]["performed"] is True
    assert review["browser_check"]["clicked_surface_progression"] == [
        "Outcome",
        "Learn",
        "Models",
        "Relations",
        "Map",
        "Receipts",
    ]
    assert review["browser_check"]["desktop_start_panel_hidden_on_focused_surfaces"] is True
    assert review["browser_check"]["mobile_start_panel_hidden_on_learn"] is True
    assert review["browser_check"]["mobile_horizontal_overflow"] is False
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["invokes_lolla_skill"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["compiled_spa_bundle_changed"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False
    assert review["non_claims"]["action_authorized"] is False


def test_visual_polish_docs_are_clean_of_local_paths_and_positive_claims() -> None:
    text = DOC.read_text(encoding="utf-8") + REVIEW.read_text(encoding="utf-8")

    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "answer_correctness\": true" not in text
    assert "advice_correctness\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
    assert "action_authorized\": true" not in text
