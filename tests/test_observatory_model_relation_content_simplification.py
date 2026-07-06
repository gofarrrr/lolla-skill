from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/observatory-model-relation-content-simplification-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-model-relation-content-simplification-v0/review.json"
)


def _install_launch_case(monkeypatch) -> None:
    monkeypatch.setattr(
        serve_result,
        "_RESULT",
        {"usage_summary": {"run_id": "20260627T104146Z_7bfe79"}},
    )
    monkeypatch.setattr(serve_result, "_RESULT_PATH", None)
    monkeypatch.setattr(serve_result, "_CASE_ID", "lolla-audit")
    monkeypatch.setattr(serve_result, "_CASE_NAME", "Lolla Audit")


def _surface_section(html: str, surface: str, next_surface: str) -> str:
    return html.split(f'<section id="{surface}"', 1)[1].split(
        f'<section id="{next_surface}"',
        1,
    )[0]


def test_models_workspace_surface_is_light_index(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")
    models = _surface_section(html, "models", "relations")
    detail = serve_result._render_workspace_model_detail_html(
        "authority-bias",
        "lolla-audit",
    )

    assert "workspace-model-index-card" in models
    assert "Model index" in models
    assert "Open model page" in models
    assert "What This Model Helps You See" not in models
    assert "Source, status, and boundaries" not in models
    assert "canonical_model_markdown" not in models
    assert "What This Model Helps You See" in detail
    assert "Source, status, and boundaries" in detail
    assert "canonical_model_markdown" in detail


def test_relations_workspace_surface_is_story_first_index(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")
    relations = _surface_section(html, "relations", "map")
    detail = serve_result._render_workspace_relation_detail_html(
        "authority-bias__first-principles-thinking__antagonist",
        "lolla-audit",
    )

    assert "workspace-relation-index-card" in relations
    assert "Relation story" in relations
    assert "Why it matters" in relations
    assert "Misread risk" in relations
    assert "Open relation page" in relations
    assert "Taxonomy, confidence, and custody" not in relations
    assert "confidence: medium" not in relations
    assert "Plain Language Story" in detail
    assert "Taxonomy, confidence, and custody" in detail
    assert "confidence: medium" in detail


def test_content_simplification_docs_review_and_readme_capture_gate() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert "Observatory Model Relation Content Simplification" in readme
    assert "observatory-model-relation-content-simplification-v0.md" in readme
    assert review["decision_gate"] == (
        "proceed_to_observatory_workspace_visual_polish_review"
    )

    for phrase in [
        "Models workspace surface is now a light index",
        "Relations workspace surface is now a story-first index",
        "full model detail remains on `/models/<model-id>`",
        "full relation detail remains on `/relations/<relation-id>`",
        "Browser Check",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not edit `observatory/build`",
        "proceed_to_observatory_workspace_visual_polish_review",
    ]:
        assert phrase in doc

    assert review["implemented"]["models_workspace_light_index"] is True
    assert review["implemented"]["relations_workspace_story_first_index"] is True
    assert review["implemented"]["model_detail_route_preserved"] is True
    assert review["implemented"]["relation_detail_route_preserved"] is True
    assert review["browser_check"]["performed"] is True
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["invokes_lolla_skill"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["compiled_spa_bundle_changed"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False
    assert review["non_claims"]["action_authorized"] is False


def test_content_simplification_docs_are_clean() -> None:
    text = DOC.read_text(encoding="utf-8") + REVIEW.read_text(encoding="utf-8")

    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "answer_correctness\": true" not in text
    assert "advice_correctness\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
    assert "action_authorized\": true" not in text
