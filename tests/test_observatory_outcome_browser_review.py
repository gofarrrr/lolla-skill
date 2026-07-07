from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/observatory-outcome-browser-review-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-outcome-browser-review-v0/review.json"
)


def _install_result(monkeypatch, *, run_id: str, revised_answer: str) -> None:
    monkeypatch.setattr(
        serve_result,
        "_RESULT",
        {
            "usage_summary": {"run_id": run_id},
            "extraction": {
                "decision_situation": "A browser-review fixture run.",
                "turns": [
                    {
                        "role": "user",
                        "content": "Should the Observatory show the outcome first?",
                    },
                    {
                        "role": "assistant",
                        "content": "Show the result first, then reveal details.",
                    },
                ],
            },
            "run_health": {"overall": "healthy", "issues": []},
            "revised_answer": revised_answer,
            "memo_what_changed": "The visible flow became result-first.",
            "delta_card": {
                "top_findings": [
                    {
                        "description": (
                            "The workspace should not make export, review, and "
                            "teaching choices compete with the answer."
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


def _outcome_section(html: str) -> str:
    return html.split('<section id="outcome"', 1)[1].split(
        '<section id="learn"',
        1,
    )[0]


def test_browser_review_teacher_backed_flow_stays_result_first(monkeypatch) -> None:
    _install_result(
        monkeypatch,
        run_id="20260627T104146Z_7bfe79",
        revised_answer=(
            "Launch in stages after the support risk is made explicit. "
            "Keep the beta as a learning gate."
        ),
    )

    html = serve_result._render_workspace_html("lolla-audit")
    outcome = _outcome_section(html)

    assert "Launch in stages after the support risk" in outcome
    assert outcome.count('aria-label="Recommended continuation"') == 1
    assert "Practice the reasoning move" in outcome
    assert "Unavailable Teaching Surfaces" not in html
    assert "Open relation lesson" in html
    assert html.index("<h2>Outcome</h2>") < html.index("What This Run Contains")
    assert html.index("What This Run Contains") < html.index('<section id="learn"')
    assert "agent-memory-download-hint-main" in html
    assert "agent-memory-download-hint-receipts" in html
    assert "agent-memory-download-hint-run-contents" not in html


def test_browser_review_run_only_flow_names_missing_teacher_surfaces(
    monkeypatch,
) -> None:
    _install_result(
        monkeypatch,
        run_id="run-only-browser-review-v0",
        revised_answer=(
            "Keep the outcome visible and mark the Teacher lesson as missing "
            "instead of showing a blank workspace."
        ),
    )

    html = serve_result._render_workspace_html("lolla-audit")
    outcome = _outcome_section(html)

    assert "Keep the outcome visible" in outcome
    assert outcome.count('aria-label="Recommended continuation"') == 1
    assert "Check what is available" in outcome
    assert "No Teacher lesson is attached to this run" in outcome
    assert "Unavailable Teaching Surfaces" in html
    assert "No Teacher lesson is attached." in html
    assert "No run-specific model pages are attached." in html
    assert "No run-specific relation pages are attached." in html
    assert "No selected-run graph is attached." in html
    assert "agent-memory-download-hint-main" in html
    assert "agent-memory-download-hint-receipts" in html
    assert "agent-memory-download-hint-run-contents" not in html


def test_outcome_browser_review_doc_review_and_readme() -> None:
    assert DOC.exists()
    assert REVIEW.exists()

    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert "Observatory Outcome Browser Review" in readme
    assert "observatory-outcome-browser-review-v0.md" in readme
    assert review["decision_gate"] == "proceed_to_relation_page_library_fallback"

    for phrase in [
        "Teacher-backed run",
        "run-only fallback",
        "header `Download MD`",
        "Receipts `Download MD`",
        "Run Contents no longer owns a duplicate `Download MD` button",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not edit `observatory/build/*`",
        "does not claim product proof",
        "proceed_to_relation_page_library_fallback",
    ]:
        assert phrase in doc

    assert review["browser_review"]["teacher_backed_run_reviewed"] is True
    assert review["browser_review"]["run_only_fallback_reviewed"] is True
    assert review["browser_review"]["recommended_continuation_clicked"] is True
    assert review["implemented"]["run_contents_duplicate_download_removed"] is True
    assert review["implemented"]["header_download_md_preserved"] is True
    assert review["implemented"]["receipts_download_md_preserved"] is True
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False


def test_outcome_browser_review_artifacts_are_clean() -> None:
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
