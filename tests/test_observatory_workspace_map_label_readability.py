from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/observatory-workspace-map-label-readability-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-workspace-map-label-readability-v0/review.json"
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


def test_map_labels_translate_contract_tokens_without_losing_raw_data(
    monkeypatch,
) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert 'data-role="mental_model"' in html
    assert 'data-role-display="Model"' in html
    assert 'data-status="partial"' in html
    assert 'data-status-display="Partial source coverage"' in html
    assert 'data-relation-type="antagonist"' in html
    assert 'data-relation-type-display="Antagonist"' in html

    assert ">mental_model<" not in html
    assert ">lesson_neighborhood<" not in html
    assert ">small_neighborhood<" not in html
    assert ">partial<" not in html
    assert ">Model</text>" in html
    assert ">Antagonist</text>" in html
    assert ">Antagonist</button>" in html
    assert ">Lesson map</span>" in html
    assert ">Small map</span>" in html


def test_map_selection_panel_uses_display_labels(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert "element.dataset.roleDisplay" in html
    assert "element.dataset.relationTypeDisplay" in html
    assert "element.dataset.statusDisplay" in html
    assert "element.dataset.role) bits.push(element.dataset.role)" not in html
    assert (
        "element.dataset.relationType) bits.push(element.dataset.relationType)"
        not in html
    )
    assert "element.dataset.status) bits.push(element.dataset.status)" not in html


def test_display_label_helper_covers_current_map_contract_terms() -> None:
    assert serve_result._observatory_display_label("mental_model") == "Model"
    assert serve_result._observatory_display_label("lesson_neighborhood") == (
        "Lesson map"
    )
    assert serve_result._observatory_display_label("small_neighborhood") == "Small map"
    assert serve_result._observatory_display_label("partial") == (
        "Partial source coverage"
    )
    assert serve_result._observatory_display_label("structured_tension") == (
        "Structured tension"
    )


def test_map_label_readability_docs_review_and_readme_capture_gate() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert "Observatory Workspace Map Label Readability" in readme
    assert "observatory-workspace-map-label-readability-v0.md" in readme
    assert review["decision_gate"] == "ready_for_human_review_with_cleaner_map_labels"

    for phrase in [
        "Browser finding",
        "raw contract tokens stay in data attributes",
        "`MENTAL_MODEL`",
        "`LESSON_NEIGHBORHOOD`",
        "`SMALL_NEIGHBORHOOD`",
        "`PARTIAL`",
        "Model",
        "Lesson map",
        "Small map",
        "Partial source coverage",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not edit `observatory/build`",
        "does not claim product proof",
        "does not claim human validation",
    ]:
        assert phrase in doc

    assert review["implemented"]["map_visible_token_translation"] is True
    assert review["implemented"]["raw_contract_tokens_preserved_as_data"] is True
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


def test_map_label_readability_docs_are_clean() -> None:
    text = DOC.read_text(encoding="utf-8") + REVIEW.read_text(encoding="utf-8")

    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "answer_correctness\": true" not in text
    assert "advice_correctness\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
    assert "action_authorized\": true" not in text
