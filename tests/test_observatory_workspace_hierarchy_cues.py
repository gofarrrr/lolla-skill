from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/observatory-workspace-hierarchy-cues-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-workspace-hierarchy-cues-v0/review.json"
)


def _install_launch_case_without_revised_answer(monkeypatch) -> None:
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


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_outcome_missingness_points_to_learn_instead_of_feeling_blank(
    monkeypatch,
) -> None:
    _install_launch_case_without_revised_answer(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")
    outcome = _surface_section(html, "outcome", "learn")

    assert "Outcome missing" in outcome
    assert "Outcome artifact is unavailable for this run." in outcome
    assert "No revised answer artifact is available for this selected run" in outcome
    assert "Continue to Learn to review the teaching surface" in outcome
    assert "Receipts shows what is present, missing, and not claimed" in outcome
    assert 'href="/workspace?case_id=lolla-audit#learn"' in outcome


def test_model_index_cards_show_selected_run_roles_without_proof_claims(
    monkeypatch,
) -> None:
    _install_launch_case_without_revised_answer(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")
    models = _surface_section(html, "models", "relations")

    assert "Run role" in models
    assert "Primary model" in models
    assert "Supporting model" in models
    assert "Contrast model" in models
    assert "inferred role cue" in models
    assert "navigation cue, not proof" in models
    assert "Source, status, and boundaries" not in models
    assert "canonical_model_markdown" not in models


def test_model_detail_separates_library_view_from_run_context(
    monkeypatch,
) -> None:
    _install_launch_case_without_revised_answer(monkeypatch)

    authority = serve_result._render_workspace_model_detail_html(
        "authority-bias",
        "lolla-audit",
    )
    first_principles = serve_result._render_workspace_model_detail_html(
        "first-principles-thinking",
        "lolla-audit",
    )

    assert "Library view first, run context second." in authority
    assert "Library view explains the model as reusable knowledge" in authority
    assert "Run context: Primary model" in authority
    assert "That role helps you navigate this selected lesson" in authority
    assert "it is not a proof or score" in authority
    assert authority.index("Library view first") < authority.index(
        "What This Model Helps You See"
    )
    assert "Run context: Contrast model" in first_principles


def test_hierarchy_cues_docs_review_and_readme_capture_gate() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = _load_json(REVIEW)

    assert "Observatory Workspace Hierarchy Cues" in readme
    assert "observatory-workspace-hierarchy-cues-v0.md" in readme
    assert review["decision_gate"] == "ready_for_human_review_with_hierarchy_cues"

    for phrase in [
        "Outcome missingness is now a purposeful state",
        "Model cards now show selected-run role cues",
        "Model detail pages now separate Library view from Run context",
        "Role labels are inferred",
        "navigation cue, not proof",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not wire skill runtime behavior",
        "does not edit `observatory/build`",
        "does not claim product proof",
        "does not claim human validation",
    ]:
        assert phrase in doc

    assert review["implemented"]["outcome_missingness_cue"] is True
    assert review["implemented"]["model_role_cues"] is True
    assert review["implemented"]["model_library_run_context_cue"] is True
    assert review["implemented"]["runtime_behavior_changed"] is False
    assert review["implemented"]["compiled_spa_bundle_changed"] is False
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["invokes_lolla_skill"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["compiled_spa_bundle_changed"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False
    assert review["non_claims"]["action_authorized"] is False


def test_hierarchy_cues_links_and_privacy_markers_are_clean() -> None:
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
