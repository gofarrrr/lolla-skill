from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/observatory-workspace-first-read-progression-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-workspace-first-read-progression-v0/review.json"
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


def test_workspace_sidebar_is_clickable_reading_path(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert "<h3>Reading Path</h3>" in html
    assert "Surface Homes" not in html
    assert 'aria-label="Workspace reading path"' in html
    assert "Use this path to move from the run result to the lesson" in html

    for anchor, label, question, purpose in serve_result._WORKSPACE_READING_PATH:
        assert f'data-workspace-surface-link="{anchor}"' in html
        assert f'href="/workspace?case_id=lolla-audit#{anchor}"' in html
        assert f"<strong>{label}</strong>" in html
        assert question in html
        assert purpose in html


def test_workspace_center_starts_with_outcome_not_six_step_panel(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert "Start with the run result." in html
    assert "Launch in stages after the support risk is made explicit." in html
    assert "Why this changed" in html
    assert "What would change confidence" in html
    assert "Next useful moves" in html
    assert "Start with Outcome." not in html
    assert "Read outcome" not in html
    assert "Practice lesson" not in html
    assert html.index("Launch in stages after the support risk") < html.index(
        "What This Run Contains"
    )
    assert 'href="/workspace?case_id=lolla-audit#learn"' in html
    assert 'href="/workspace?case_id=lolla-audit#receipts"' in html


def test_workspace_navigation_updates_reading_path_active_state(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert 'const page = document.querySelector(".workspace-page");' in html
    assert 'page.querySelectorAll("[data-workspace-surface-link]")' in html
    assert 'link.dataset.workspaceSurfaceLink === surface' in html
    assert 'link.classList.contains("workspace-surface-link")' in html
    assert 'link.classList.contains("workspace-step-card")' in html
    assert 'link.setAttribute("aria-current", "page")' in html


def test_first_read_progression_docs_review_and_readme_capture_gate() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert "Observatory Workspace First-Read Progression" in readme
    assert "observatory-workspace-first-read-progression-v0.md" in readme
    assert review["decision_gate"] == (
        "ready_for_human_review_with_clearer_first_read_path"
    )

    for phrase in [
        "Browser finding",
        "Reading Path",
        "Outcome -> Learn -> Models -> Relations -> Map -> Receipts",
        "clickable and explanatory",
        "Start from the selected run",
        "Relation and Map are no longer skipped",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not edit `observatory/build`",
        "does not claim product proof",
        "does not claim human validation",
    ]:
        assert phrase in doc

    assert review["implemented"]["clickable_reading_path_sidebar"] is True
    assert review["implemented"]["six_step_start_panel"] is True
    assert review["implemented"]["reading_path_active_state"] is True
    assert review["browser_grounded"] is True
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["invokes_lolla_skill"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["compiled_spa_bundle_changed"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False
    assert review["non_claims"]["action_authorized"] is False


def test_first_read_progression_docs_are_clean() -> None:
    text = DOC.read_text(encoding="utf-8") + REVIEW.read_text(encoding="utf-8")

    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "answer_correctness\": true" not in text
    assert "advice_correctness\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
    assert "action_authorized\": true" not in text
