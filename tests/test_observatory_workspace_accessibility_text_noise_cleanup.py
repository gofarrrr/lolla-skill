from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/observatory-workspace-accessibility-text-noise-cleanup-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-workspace-accessibility-text-noise-cleanup-v0/review.json"
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


def test_workspace_server_default_exposes_only_outcome_section(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert 'data-workspace-default-surface="outcome"' in html
    assert (
        '<section id="outcome" class="workspace-section workspace-section--active" '
        'data-workspace-section="outcome">'
    ) in html
    for surface in ["learn", "models", "relations", "map", "receipts"]:
        assert (
            f'<section id="{surface}" class="workspace-section" '
            f'data-workspace-section="{surface}" hidden aria-hidden="true">'
        ) in html


def test_workspace_navigation_unhides_only_active_surface(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert 'page.dataset.activeSurface = surface' in html
    assert 'page.querySelectorAll("[data-workspace-section]")' in html
    assert 'section.toggleAttribute("hidden", !isActive)' in html
    assert 'section.removeAttribute("aria-hidden")' in html
    assert 'section.setAttribute("aria-hidden", "true")' in html
    assert "workspace-focus-mode" in html


def test_first_read_progression_stays_visible_without_showing_all_detail(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    start_index = html.index("Start with Outcome.")
    outcome_index = html.index("<h2>Outcome</h2>")
    learn_hidden_index = html.index('id="learn"')
    receipts_hidden_index = html.index('id="receipts"')

    assert start_index < outcome_index < learn_hidden_index < receipts_hidden_index
    assert "What reasoning move can I practice?" in html
    assert 'id="learn" class="workspace-section" data-workspace-section="learn" hidden' in html
    assert "Technical audit index" in html
    assert 'id="receipts" class="workspace-section" data-workspace-section="receipts" hidden' in html


def test_accessibility_text_noise_docs_review_and_readme_capture_gate() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert "Observatory Workspace Accessibility Text Noise Cleanup" in readme
    assert "observatory-workspace-accessibility-text-noise-cleanup-v0.md" in readme
    assert review["decision_gate"] == (
        "proceed_to_observatory_workspace_content_audit_and_simplification"
    )

    for phrase in [
        "server default is Start Here plus Outcome",
        "non-active surfaces are hidden",
        "Outcome -> Learn -> Models -> Relations -> Map -> Receipts",
        "Browser Check",
        "default workspace snapshot exposed Outcome without dumping Learn, Models, Relations, Map, and Receipts",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not edit `observatory/build`",
        "proceed_to_observatory_workspace_content_audit_and_simplification",
    ]:
        assert phrase in doc

    assert review["implemented"]["server_default_outcome_only"] is True
    assert review["implemented"]["non_active_workspace_sections_hidden"] is True
    assert review["implemented"]["aria_hidden_tracks_workspace_surface"] is True
    assert review["browser_check"]["performed"] is True
    assert review["browser_check"]["default_snapshot_keeps_inactive_surfaces_out"] is True
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["invokes_lolla_skill"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["compiled_spa_bundle_changed"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False
    assert review["non_claims"]["action_authorized"] is False


def test_accessibility_text_noise_docs_are_clean_of_local_paths_and_positive_claims() -> None:
    text = DOC.read_text(encoding="utf-8") + REVIEW.read_text(encoding="utf-8")

    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "answer_correctness\": true" not in text
    assert "advice_correctness\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
    assert "action_authorized\": true" not in text
