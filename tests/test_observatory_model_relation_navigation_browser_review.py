from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/observatory-model-relation-navigation-browser-review-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-model-relation-navigation-browser-review-v0/"
    "review.json"
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
    monkeypatch.setattr(serve_result, "_RESULT_MTIME", 0.0)
    monkeypatch.setattr(serve_result, "_CASE_ID", "lolla-audit")
    monkeypatch.setattr(serve_result, "_CASE_NAME", "Lolla Audit")


def _surface_section(html: str, start: str, end: str) -> str:
    return html.split(f'<section id="{start}"', 1)[1].split(
        f'<section id="{end}"',
        1,
    )[0]


def test_workspace_models_stays_selected_run_first(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")
    models = _surface_section(html, "models", "relations")

    assert "Models" in models
    assert "Authority Bias" in models
    assert "Information Asymmetry" in models
    assert "First Principles Thinking" in models
    assert models.count("Open model page") == 3
    assert "Reviewed Neighbors" not in models
    assert "Library Relation Context" not in models


def test_model_detail_bridges_to_library_relation_pages(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_model_detail_html(
        "authority-bias",
        "lolla-audit",
    )

    assert "How to read this page" in html
    assert "Library neighborhood" in html
    assert "Reviewed Neighbors" in html
    assert "navigation, not proof" in html
    assert "Open relation page" in html
    assert (
        'href="/relations/authority-bias__wysiati__ally?case_id=lolla-audit"'
        in html
    )
    assert (
        'href="/relations/authority-bias__critical-thinking__antagonist?case_id=lolla-audit"'
        in html
    )
    assert "composition_affinity" not in html
    assert "affinity_rationale" not in html


def test_library_and_selected_run_relation_scopes_stay_distinct(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    library_html = serve_result._render_workspace_relation_detail_html(
        "authority-bias__wysiati__ally",
        "lolla-audit",
    )
    selected_run_html = serve_result._render_workspace_relation_detail_html(
        "authority-bias__first-principles-thinking__antagonist",
        "lolla-audit",
    )

    assert "Library Relation Context" in library_html
    assert "library fallback" in library_html
    assert "not selected-run proof" in library_html
    assert "WYSIATI amplifies authority-bias" in library_html
    assert "Source quote or reference" in library_html

    assert "Library Relation Context" not in selected_run_html
    assert "Read the model relationship as a lesson" in selected_run_html
    assert "Built from Teacher relation deep-dive source" in selected_run_html
    assert "confidence: medium" in selected_run_html


def test_model_relation_navigation_review_doc_review_and_readme() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert "Observatory Model Relation Navigation Browser Review" in readme
    assert "observatory-model-relation-navigation-browser-review-v0.md" in readme
    assert review["decision_gate"] == "proceed_to_model_detail_library_navigation_polish"

    for phrase in [
        "model-to-relation path",
        "Workspace Models",
        "Model detail",
        "Library Relation Context",
        "Selected-run relation",
        "Map remains the selected-run wayfinding graph",
        "Keep three relation scopes distinct",
        "selected-run relation",
        "local library relation",
        "global graph relation",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not edit `observatory/build`",
        "does not claim product proof",
        "does not treat graph edges as proof",
        "proceed_to_model_detail_library_navigation_polish",
    ]:
        assert phrase in doc

    assert review["browser_review"]["workspace_models_opened"] is True
    assert review["browser_review"]["neighbor_relation_link_clicked"] is True
    assert review["browser_review"]["relationship_graph_fallback_checked"] is True
    assert review["product_decisions"]["map_remains_selected_run_wayfinding"] is True
    assert review["product_decisions"]["global_graph_deferred"] is True
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["non_claims"]["graph_edges_are_proof"] is False


def test_model_relation_navigation_review_artifacts_are_clean() -> None:
    missing = []
    for path in [DOC, README]:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith("#") or re.match(r"^[a-z]+:", target):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                missing.append(f"{path}: {target}")

    combined = DOC.read_text(encoding="utf-8") + REVIEW.read_text(encoding="utf-8")

    assert missing == []
    assert "/" + "Users/" not in combined
    assert "Desktop/" + "Apps" not in combined
    assert "product_proof\": true" not in combined
    assert "human_validated\": true" not in combined
    assert "answer_correctness\": true" not in combined
    assert "advice_correctness\": true" not in combined
    assert "runtime_integration_authorized\": true" not in combined
    assert "action_authorized\": true" not in combined
