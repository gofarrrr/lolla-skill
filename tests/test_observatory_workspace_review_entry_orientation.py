from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/observatory-workspace-user-surface-review-removal-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-workspace-user-surface-review-removal-v0/review.json"
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


def test_workspace_keeps_reading_path_without_review_guide_entry(
    monkeypatch,
) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert "<h3>Reading Path</h3>" in html
    assert "<h3>Review Guide</h3>" not in html
    assert "Open review guide" not in html
    assert "judge whether this reads as one product journey" not in html
    assert 'href="/review/observatory-workspace?case_id=lolla-audit"' not in html

    for anchor, label, question, purpose in serve_result._WORKSPACE_READING_PATH:
        assert f'data-workspace-surface-link="{anchor}"' in html
        assert f'href="/workspace?case_id=lolla-audit#{anchor}"' in html
        assert f"<strong>{label}</strong>" in html
        assert question in html
        assert purpose in html


def test_receipts_places_optional_technical_inspection_after_non_claims(
    monkeypatch,
) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert html.index("What can I trust or inspect?") < html.index("Visible non-claims")
    assert html.index("Visible non-claims") < html.index("Technical inspection")
    assert "Human review" not in html
    assert "what confused you" not in html
    assert "the six surfaces read as one Observatory product" not in html
    assert 'href="/review/observatory-workspace?case_id=lolla-audit"' not in html


def test_review_guide_explains_task_progression_output_and_boundaries(
    monkeypatch,
) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_review_guide_html("lolla-audit")

    assert "<title>Lolla - Observatory Review Guide</title>" in html
    assert "Review the Observatory Workspace" in html
    assert "Does this feel like one Observatory product surface?" in html
    assert "Start cold. Spend about ten seconds" in html
    assert "human review not completed" in html
    assert "blank form: docs/product/observatory-workspace-user-review-packet-v0/human-review-form.md" in html

    for anchor, _label, _question, _purpose in serve_result._WORKSPACE_READING_PATH:
        assert f'href="/workspace?case_id=lolla-audit#{anchor}"' in html

    for boundary in [
        "Do not run Lolla for this review.",
        "Do not create a new run.",
        "Do not treat this as product proof or human validation.",
        "Do not claim answer correctness or advice correctness.",
        "Do not treat graph edges as proof or relation confidence as certification.",
        "Do not authorize automatic action.",
    ]:
        assert boundary in html


def test_http_handler_declares_review_guide_route() -> None:
    source = (REPO_ROOT / "observatory/serve_result.py").read_text(encoding="utf-8")

    assert 'if path == "/review/observatory-workspace":' in source
    assert "_render_workspace_review_guide_html(selected_case_id)" in source


def test_review_removal_docs_review_and_readme_capture_gate() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = _load_json(REVIEW)

    assert "Observatory Workspace User Surface Review Removal" in readme
    assert "observatory-workspace-user-surface-review-removal-v0.md" in readme
    assert review["decision_gate"] == "proceed_to_observatory_data_exposure_audit"

    for phrase in [
        "Product Correction",
        "Review mechanics are internal process",
        "does not link to `/review/observatory-workspace`",
        "Receipts no longer asks the user to review the product",
        "Outcome -> Learn -> Models -> Relations -> Map -> Receipts",
        "Technical inspection remains optional",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not wire skill runtime behavior",
        "does not edit `observatory/build`",
        "does not claim product proof",
        "does not claim human validation",
    ]:
        assert phrase in doc

    assert review["implemented"]["sidebar_review_guide_entry_visible"] is False
    assert review["implemented"]["receipts_human_review_entry_visible"] is False
    assert review["implemented"]["workspace_links_review_route"] is False
    assert review["implemented"]["server_rendered_review_guide_route_internal_only"] is True
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


def test_review_entry_docs_links_and_claims_are_clean() -> None:
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
