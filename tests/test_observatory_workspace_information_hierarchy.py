from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/observatory-workspace-information-hierarchy-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-workspace-information-hierarchy-v0/review.json"
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


def _workspace_status_bar(html: str) -> str:
    return html.split('data-observatory-status-bar>', 1)[1].split("</nav>", 1)[0]


def test_primary_workspace_navigation_excludes_advanced_audit(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")
    status_bar = _workspace_status_bar(html)

    for label in ["Outcome", "Learn", "Models", "Relations", "Map", "Receipts"]:
        assert f">{label}</a>" in status_bar

    assert "Advanced Audit" not in status_bar
    assert "status-link-advanced" not in html


def test_receipts_own_technical_inspection_without_leading_with_it(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    trust_index = html.index("What can I trust or inspect?")
    technical_index = html.index("Technical inspection")
    source_index = html.index("Source and missingness details")
    audit_index = html.index("Technical audit index")
    boundary_index = html.index("Workspace boundary notes")

    assert trust_index < technical_index < source_index < audit_index < boundary_index
    assert "Use Receipts to understand what exists for this run" in html
    assert 'href="/audit/extraction">Extraction audit</a>' in html
    assert 'href="/usage">Usage</a>' in html
    assert 'href="/audit">Advanced audit</a>' in html
    assert "Source refs and missing fields" not in html
    assert "Advanced inspection index" not in html


def test_map_explains_filter_intersection_and_reset(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert '<button class="filter-chip graph-filter-reset" type="button" data-graph-reset>Reset</button>' in html
    assert "data-graph-filter-note" in html
    assert "Search and relation filters combine. Use Reset to return to the full lesson map." in html
    assert "No relation is visible with the current search or filter" in html
    assert 'search.value = ""' in html
    assert 'activeFilter = "all"' in html


def test_information_hierarchy_docs_review_and_readme_capture_gate() -> None:
    doc = DOC.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    readme = README.read_text(encoding="utf-8")

    assert "Observatory Workspace Information Hierarchy" in readme
    assert "observatory-workspace-information-hierarchy-v0.md" in readme
    assert review["decision_gate"] == (
        "proceed_to_observatory_legacy_teacher_renderer_cleanup"
    )

    for phrase in [
        "Outcome -> Learn -> Models -> Relations -> Map -> Receipts",
        "First-class product data",
        "Second-class support data",
        "Technical inspection data",
        "Advanced Audit is still reachable from Receipts",
        "Browser Check",
        "map reset = returns to 3 models, 1 relation",
        "hidden workspace sections and embedded scripts",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not edit `observatory/build`",
        "proceed_to_observatory_legacy_teacher_renderer_cleanup",
    ]:
        assert phrase in doc

    assert review["implemented"]["primary_workspace_nav_excludes_advanced_audit"] is True
    assert review["implemented"]["advanced_audit_still_available_from_receipts"] is True
    assert review["implemented"]["map_filter_reset_control"] is True
    assert review["browser_grounded"] is True
    assert review["browser_check"]["advanced_audit_in_primary_nav"] is False
    assert review["browser_check"]["map_reset_restores_full_neighborhood"] is True
    assert review["browser_check"]["remaining_accessibility_text_noise"] is True
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["invokes_lolla_skill"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["compiled_spa_bundle_changed"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False
    assert review["non_claims"]["action_authorized"] is False


def test_information_hierarchy_docs_are_clean_of_local_paths_and_positive_claims() -> None:
    text = DOC.read_text(encoding="utf-8") + REVIEW.read_text(encoding="utf-8")

    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "answer_correctness\": true" not in text
    assert "advice_correctness\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
    assert "action_authorized\": true" not in text
