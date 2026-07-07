from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/observatory-model-detail-library-navigation-polish-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-model-detail-library-navigation-polish-v0/"
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


def _neighborhood_panel(html: str) -> str:
    return html.split('data-model-local-neighborhood', 1)[1].split(
        "<summary>Use, avoid, and source-backed details</summary>",
        1,
    )[0]


def test_model_detail_neighborhood_starts_with_scan_layer(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_model_detail_html(
        "authority-bias",
        "lolla-audit",
    )
    panel = _neighborhood_panel(html)

    assert "Library neighborhood" in panel
    assert "Reviewed Neighbors" in panel
    assert "What this is" in panel
    assert "How to scan" in panel
    assert "How to trust it" in panel
    assert "not the selected-run Map and not the full corpus graph" in panel
    assert "Jump to:" in panel
    assert 'href="#neighborhood-authority-bias-ally"' in panel
    assert 'href="#neighborhood-authority-bias-antagonist"' in panel
    assert 'href="#neighborhood-authority-bias-structured_tension"' in panel
    assert "Ally 3" in panel
    assert "Antagonist 3" in panel
    assert "Structured tension 3" in panel


def test_model_detail_relation_groups_preserve_cards_and_counts(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_model_detail_html(
        "authority-bias",
        "lolla-audit",
    )
    panel = _neighborhood_panel(html)

    assert 'id="neighborhood-authority-bias-ally"' in panel
    assert 'id="neighborhood-authority-bias-antagonist"' in panel
    assert 'id="neighborhood-authority-bias-structured_tension"' in panel
    assert "Allies" in panel
    assert "Antagonists" in panel
    assert "Structured tensions" in panel
    assert "<span class=\"workspace-muted\">(3)</span>" in panel
    assert "WYSIATI" in panel
    assert "Critical Thinking" in panel
    assert "Open model page" in panel
    assert "Open relation page" in panel
    assert (
        'href="/relations/authority-bias__wysiati__ally?case_id=lolla-audit"'
        in panel
    )
    assert "composition_affinity" not in panel
    assert "affinity_rationale" not in panel


def test_workspace_models_remains_light_after_neighborhood_polish(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")
    models = html.split('<section id="models"', 1)[1].split(
        '<section id="relations"',
        1,
    )[0]

    assert "Model index" in models
    assert models.count("Open model page") == 3
    assert "Reviewed Neighbors" not in models
    assert "What this is" not in models
    assert "Jump to:" not in models


def test_model_detail_library_navigation_docs_review_and_readme() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert "Observatory Model Detail Library Navigation Polish" in readme
    assert "observatory-model-detail-library-navigation-polish-v0.md" in readme
    assert review["decision_gate"] == "proceed_to_library_graph_scope_decision"

    for phrase in [
        "scan layer",
        "What this is",
        "How to scan",
        "How to trust it",
        "Jump to: Ally 3 | Antagonist 3 | Structured tension 3",
        "selected-run Map remains small wayfinding",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not edit `observatory/build`",
        "does not claim product proof",
        "does not treat graph edges as proof",
        "proceed_to_library_graph_scope_decision",
    ]:
        assert phrase in doc

    assert review["implemented"]["model_neighborhood_scan_layer"] is True
    assert review["implemented"]["relation_type_jump_chips"] is True
    assert review["implemented"]["workspace_models_remain_light"] is True
    assert review["product_decisions"]["local_neighborhood_is_not_full_corpus_graph"] is True
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["touches_compiled_spa_bundle"] is False
    assert review["non_claims"]["graph_edges_are_proof"] is False


def test_model_detail_library_navigation_artifacts_are_clean() -> None:
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
