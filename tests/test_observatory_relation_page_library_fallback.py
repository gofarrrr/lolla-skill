from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/observatory-relation-page-library-fallback-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-relation-page-library-fallback-v0/"
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


def test_model_neighbor_cards_link_to_library_relation_pages(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_model_detail_html(
        "authority-bias",
        "lolla-audit",
    )
    panel = html.split('data-model-local-neighborhood', 1)[1].split(
        "<summary>Use, avoid, and source-backed details</summary>",
        1,
    )[0]

    assert "Reviewed Neighbors" in panel
    assert "Critical Thinking" in panel
    assert "Open relation page" in panel
    assert (
        'href="/relations/authority-bias__critical-thinking__antagonist?case_id=lolla-audit"'
        in panel
    )
    assert (
        'href="/models/critical-thinking?case_id=lolla-audit"'
        in panel
    )
    assert "composition_affinity" not in panel
    assert "affinity_rationale" not in panel


def test_relation_semantics_library_relation_page_renders(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_relation_detail_html(
        "authority-bias__critical-thinking__antagonist",
        "lolla-audit",
    )

    assert "Relation page not found" not in html
    assert "Authority Bias and Critical Thinking" in html
    assert "Library Relation Context" in html
    assert "library fallback" in html
    assert "Relation Semantics" in html
    assert "not selected-run proof" in html
    assert "Critical thinking opposes authority bias" in html
    assert "Use this antagonist relation to compare Authority Bias" in html
    assert "The main risk is treating this library relation as proof" in html
    assert "Source quote or reference" in html
    assert "data/curation/relation_semantics/authority-bias.json" in html
    assert "data/relationship_graph.json" in html
    assert "library_relation_view_not_selected_run_proof" in html
    assert "relation_is_not_proof" in html
    assert "confidence_is_not_certification" in html
    assert "not_answer_correctness" in html
    assert "composition_affinity" not in html
    assert "affinity_rationale" not in html
    assert "<table" not in html
    assert "/" + "Users/" not in html
    assert "Desktop/" + "Apps" not in html


def test_relationship_graph_library_relation_fallback_renders(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_relation_detail_html(
        "analogies-and-metaphors__representativeness-heuristic__antagonist",
        "lolla-audit",
    )

    assert "Relation page not found" not in html
    assert "Analogies And Metaphors and Representativeness Heuristic" in html
    assert "Library Relation Context" in html
    assert "Relation Semantics" in html
    assert "Representativeness-heuristic undermines analogies-and-metaphors" in html
    assert "data/relationship_graph.json" in html
    assert "composition_affinity" not in html
    assert "affinity_rationale" not in html
    assert "embedding_similarity" not in html


def test_selected_run_relation_detail_stays_selected_run(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_relation_detail_html(
        "authority-bias__first-principles-thinking__antagonist",
        "lolla-audit",
    )

    assert "Authority Bias and First Principles Thinking" in html
    assert "Library Relation Context" not in html
    assert "confidence: medium" in html
    assert "Built from Teacher relation deep-dive source" in html


def test_relation_page_library_fallback_docs_review_and_readme() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert "Observatory Relation Page Library Fallback" in readme
    assert "observatory-relation-page-library-fallback-v0.md" in readme
    assert review["decision_gate"] == "proceed_to_model_relation_navigation_browser_review"

    for phrase in [
        "relation-page library fallback",
        "Reviewed Neighbors",
        "Open relation page",
        "Library Relation Context",
        "relation semantics first",
        "relationship graph fallback",
        "selected-run relation pages still win",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not edit `observatory/build`",
        "does not claim product proof",
        "does not claim human validation",
        "does not treat graph edges as proof",
        "proceed_to_model_relation_navigation_browser_review",
    ]:
        assert phrase in doc

    assert review["implemented"]["library_relation_detail_route"] is True
    assert review["implemented"]["neighbor_cards_link_to_relation_pages"] is True
    assert review["implemented"]["relation_semantics_primary_source"] is True
    assert review["implemented"]["relationship_graph_fallback"] is True
    assert review["implemented"]["selected_run_relation_pages_still_win"] is True
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["non_claims"]["graph_edges_are_proof"] is False
    assert review["non_claims"]["embedding_similarity_is_validated_relation_semantics"] is False


def test_relation_page_library_fallback_artifacts_are_clean() -> None:
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
