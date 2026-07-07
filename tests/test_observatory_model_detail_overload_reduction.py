from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/observatory-model-detail-overload-reduction-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-model-detail-overload-reduction-v0/review.json"
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


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_model_detail_keeps_first_read_visible_and_collapses_long_bullets(
    monkeypatch,
) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_model_detail_html(
        "authority-bias",
        "lolla-audit",
    )

    first_read = html.index("What This Model Helps You See")
    support_note = html.index(
        "Detailed bullets are supporting material, not the main lesson."
    )
    disclosure = html.index("<summary>Use, avoid, and source-backed details</summary>")
    helps_notice = html.index("Helps notice")
    source_boundary = html.index("Source, status, and boundaries")

    assert first_read < support_note < disclosure < helps_notice
    assert disclosure < source_boundary
    assert (
        '<details class="workspace-disclosure">\n'
        "<summary>Use, avoid, and source-backed details</summary>"
    ) in html
    assert (
        '<details class="workspace-disclosure" open>\n'
        "<summary>Use, avoid, and source-backed details</summary>"
    ) not in html
    assert "Practice and failure detail" in html
    assert "Source, status, and boundaries" in html
    assert "Run context: Primary model" in html
    assert "not proof" in html


def test_workspace_model_index_stays_light_while_detail_has_support_disclosure(
    monkeypatch,
) -> None:
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
    assert "Use, avoid, and source-backed details" not in models_section
    assert "Detailed bullets are supporting material" not in models_section
    assert "Open model page" in models_section
    assert "What This Model Helps You See" in detail
    assert "Detailed bullets are supporting material" in detail
    assert "Use, avoid, and source-backed details" in detail
    assert "canonical_model_markdown" in detail


def test_model_detail_overload_reduction_docs_review_and_readme() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = _load_json(REVIEW)

    assert "Observatory Model Detail Overload Reduction" in readme
    assert "observatory-model-detail-overload-reduction-v0.md" in readme
    assert review["decision_gate"] == (
        "ready_for_human_hierarchy_review_after_model_detail_reduction"
    )

    for phrase in [
        "supporting model detail as equal to the main Learn journey",
        "What does this model help me notice in the selected lesson?",
        "Detailed bullets are supporting material, not the main lesson.",
        "Use, avoid, and source-backed details",
        "This does not prove that a human learner understands the hierarchy.",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not wire skill runtime behavior",
        "does not edit `observatory/build`",
        "does not claim product proof",
        "does not claim human validation",
    ]:
        assert phrase in doc

    assert review["implemented"]["model_detail_first_read_remains_visible"] is True
    assert review["implemented"]["model_detail_supporting_bullets_collapsed"] is True
    assert review["implemented"]["supporting_material_hierarchy_cue"] is True
    assert review["implemented"]["runtime_behavior_changed"] is False
    assert review["implemented"]["compiled_spa_bundle_changed"] is False
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["invokes_lolla_skill"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["wires_skill_runtime_behavior"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False
    assert review["non_claims"]["action_authorized"] is False


def test_model_detail_overload_reduction_links_and_privacy_are_clean() -> None:
    missing = []
    for path in [DOC, README]:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith("#") or re.match(r"^[a-z]+:", target):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                missing.append(f"{path}: {target}")

    text = DOC.read_text(encoding="utf-8") + REVIEW.read_text(encoding="utf-8")

    assert missing == []
    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "answer_correctness\": true" not in text
    assert "advice_correctness\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
    assert "action_authorized\": true" not in text
