from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/observatory-model-local-neighborhoods-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-model-local-neighborhoods-v0/review.json"
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


def _neighborhood_panel(html: str) -> str:
    return html.split('data-model-local-neighborhood', 1)[1].split(
        "<summary>Use, avoid, and source-backed details</summary>",
        1,
    )[0]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_model_detail_shows_reviewed_local_neighborhood(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_model_detail_html(
        "authority-bias",
        "lolla-audit",
    )
    panel = _neighborhood_panel(html)

    assert "Reviewed Neighbors" in panel
    assert "Use this to move through the mental model library" in panel
    assert "navigation context, not proof" in panel
    assert "shown 9" in panel
    assert "relation semantics 9" in panel
    assert "graph edges accounted 39" in panel

    for neighbor in [
        "WYSIATI",
        "Critical Thinking",
        "Scientific Method Evidence Testing",
    ]:
        assert neighbor in panel

    assert 'href="/models/critical-thinking?case_id=lolla-audit"' in panel
    assert "Source quote" in panel
    assert "data/curation/relation_semantics/authority-bias.json" in panel
    assert "data/relationship_graph.json" in panel
    assert "<table" not in panel
    assert "composition_affinity" not in panel
    assert "affinity_rationale" not in panel
    assert "/" + "Users/" not in panel
    assert "Desktop/" + "Apps" not in panel


def test_model_index_stays_light_while_detail_carries_neighborhood(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")
    models_section = html.split('<section id="models"', 1)[1].split(
        '<section id="relations"',
        1,
    )[0]
    detail = serve_result._render_workspace_model_detail_html(
        "authority-bias",
        "lolla-audit",
    )

    assert "Model index" in models_section
    assert "Reviewed Neighbors" not in models_section
    assert "graph edges accounted 39" not in models_section
    assert "Reviewed Neighbors" in detail


def test_neighbor_model_link_opens_library_fallback_page(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_model_detail_html(
        "critical-thinking",
        "lolla-audit",
    )

    assert "Mental model page not found" not in html
    assert "No selected-run product page is available" not in html
    assert "Critical Thinking" in html
    assert "Read this as reusable library knowledge translated from the canonical substrate." in html
    assert "Run context: Library neighbor" in html
    assert "Use Critical Thinking to turn high-stakes judgment under bias risk" in html
    assert "Reviewed Neighbors" in html
    assert "Systems Thinking" in html
    assert 'href="/models/systems-thinking?case_id=lolla-audit"' in html
    assert "data/model_sources/Critical_Thinking_rag.md" in html
    assert "library_model_view_not_selected_run_proof" in html
    assert "relation_edges_are_navigation_not_proof" in html


def test_model_local_neighborhood_docs_review_and_readme() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = _load_json(REVIEW)

    assert "Observatory Model Local Neighborhoods" in readme
    assert "observatory-model-local-neighborhoods-v0.md" in readme
    assert review["decision_gate"] == (
        "proceed_to_relation_page_library_fallback_or_graph_neighborhood_refinement"
    )

    for phrase in [
        "Reviewed Neighbors",
        "local library neighborhood",
        "selected-run map",
        "library fallback model page",
        "data/curation/relation_semantics/<model_id>.json",
        "data/relationship_graph.json",
        "Canonical model Markdown is still source material, not raw UI.",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not wire skill runtime behavior",
        "does not edit `observatory/build`",
        "does not claim product proof",
        "does not claim human validation",
        "does not treat graph edges as proof",
    ]:
        assert phrase in doc

    assert review["implemented"]["reviewed_neighbors_section"] is True
    assert review["implemented"]["library_fallback_model_page"] is True
    assert review["implemented"]["model_index_overloaded"] is False
    assert review["implemented"]["runtime_behavior_changed"] is False
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["touches_compiled_spa_bundle"] is False
    assert review["non_claims"]["graph_edges_are_proof"] is False
    assert review["non_claims"]["product_proof"] is False


def test_model_local_neighborhood_docs_links_are_local() -> None:
    missing = []
    for path in [DOC, README]:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith("#") or re.match(r"^[a-z]+:", target):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).exists():
                missing.append((path.name, clean))
    assert missing == []
