from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/observatory-review-guide-hierarchy-prompts-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-review-guide-hierarchy-prompts-v0/review.json"
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


def test_review_guide_checks_cold_user_information_hierarchy(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_review_guide_html("lolla-audit")

    assert "Cold user hierarchy check" in html
    assert "Can you tell what is primary, supporting, and inspection-only?" in html
    assert "Outcome state -> Learn -> Models -> Relations -> Map -> Receipts" in html
    assert "primary: Outcome and Learn" in html
    assert "supporting: Models, Relations, and Map" in html
    assert "inspection: Receipts and Audit" in html
    assert "Can you tell Outcome from Learn" in html
    assert "result state versus teaching move" in html
    assert "Can you tell Library view from Run context" in html
    assert "navigation cues, not proof" in html
    assert "technical audit pages stay optional" in html
    assert "human review not completed" in html

    for anchor, _label, _question, _purpose in serve_result._WORKSPACE_READING_PATH:
        assert f'href="/workspace?case_id=lolla-audit#{anchor}"' in html


def test_review_guide_records_confusion_without_turning_audit_into_product(
    monkeypatch,
) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_review_guide_html("lolla-audit")

    for phrase in [
        "The first thing you thought the workspace was for.",
        "The first surface or link you wanted to open next.",
        "primary product content blurred into receipts, audit, or telemetry",
        "Library view and selected-run context were hard to separate",
        "technical detail that pulled attention away from the learning journey",
    ]:
        assert phrase in html

    assert "Complete the blank human review form only after clicking through the workspace" in html
    assert "do not pre-fill a positive result" in html


def test_review_guide_hierarchy_docs_review_and_readme_capture_gate() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = _load_json(REVIEW)

    assert "Observatory Review Guide Hierarchy Prompts" in readme
    assert "observatory-review-guide-hierarchy-prompts-v0.md" in readme
    assert review["decision_gate"] == "ready_for_human_review_with_hierarchy_prompts"

    for phrase in [
        "cold user hierarchy check",
        "primary product content",
        "reusable learning material",
        "optional inspection",
        "Outcome state -> Learn -> Models -> Relations -> Map -> Receipts",
        "Library view from Run context",
        "role labels as navigation cues, not proof",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not wire skill runtime behavior",
        "does not edit `observatory/build`",
        "does not claim product proof",
        "does not claim human validation",
    ]:
        assert phrase in doc

    assert review["implemented"]["cold_user_hierarchy_check"] is True
    assert review["implemented"]["primary_supporting_inspection_ladder"] is True
    assert review["implemented"]["library_run_context_prompt"] is True
    assert review["implemented"]["model_role_prompt"] is True
    assert review["implemented"]["human_form_prefilled"] is False
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


def test_review_guide_hierarchy_links_and_claims_are_clean() -> None:
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
