from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = (
    REPO_ROOT
    / "docs/product/observatory-receipts-technical-inspection-disclosure-v0.md"
)
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-receipts-technical-inspection-disclosure-v0/review.json"
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


def _receipts_section(html: str) -> str:
    return html.split('<section id="receipts"', 1)[1].split("</section>", 1)[0]


def test_receipts_collapses_technical_links_after_human_review(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")
    receipts = _receipts_section(html)

    assert "What can I trust or inspect?" in receipts
    assert "Teacher packet" in receipts
    assert "Conversation Understanding" in receipts
    assert "Process brief" in receipts
    assert "Visible non-claims" in receipts
    assert "Human review" in receipts
    assert "Open review guide" in receipts
    assert "Technical inspection (optional)" in receipts
    assert "This is inspection, not the learning path." in receipts

    assert receipts.index("What can I trust or inspect?") < receipts.index(
        "Visible non-claims"
    )
    assert receipts.index("Visible non-claims") < receipts.index("Human review")
    assert receipts.index("Human review") < receipts.index(
        "Technical inspection (optional)"
    )

    assert (
        '<details class="workspace-disclosure">\n'
        "<summary>Technical inspection (optional)</summary>"
    ) in receipts
    assert (
        '<details class="workspace-disclosure" open>\n'
        "<summary>Technical inspection (optional)</summary>"
    ) not in receipts


def test_receipts_preserves_audit_links_as_optional_inspection(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")
    receipts = _receipts_section(html)

    for link in [
        'href="/audit/extraction">Extraction audit</a>',
        'href="/usage">Usage</a>',
        'href="/audit">Advanced audit</a>',
    ]:
        assert link in receipts

    technical_index = receipts.index("Technical inspection (optional)")
    extraction_index = receipts.index('href="/audit/extraction">Extraction audit</a>')
    usage_index = receipts.index('href="/usage">Usage</a>')
    advanced_index = receipts.index('href="/audit">Advanced audit</a>')

    assert technical_index < extraction_index < usage_index < advanced_index
    assert "Source and missingness details" in receipts
    assert "Technical audit index" in receipts
    assert receipts.index("Technical inspection (optional)") < receipts.index(
        "Source and missingness details"
    )


def test_receipts_technical_disclosure_docs_review_and_readme() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = _load_json(REVIEW)

    assert "Observatory Receipts Technical Inspection Disclosure" in readme
    assert "observatory-receipts-technical-inspection-disclosure-v0.md" in readme
    assert review["decision_gate"] == (
        "ready_for_human_hierarchy_review_after_receipts_reduction"
    )

    for phrase in [
        "technical audit links can still look like a normal next product step",
        "Technical inspection (optional)",
        "This is inspection, not the learning path.",
        "`Extraction audit`",
        "`Usage`",
        "`Advanced audit`",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not wire skill runtime behavior",
        "does not edit `observatory/build`",
        "does not claim product proof",
        "does not claim human validation",
    ]:
        assert phrase in doc

    assert review["implemented"]["receipts_trust_summary_remains_visible"] is True
    assert review["implemented"]["receipts_non_claims_remain_visible"] is True
    assert review["implemented"]["receipts_human_review_entry_remains_visible"] is True
    assert review["implemented"]["technical_inspection_links_collapsed"] is True
    assert review["implemented"]["technical_inspection_optional_copy"] is True
    assert review["implemented"]["runtime_behavior_changed"] is False
    assert review["implemented"]["compiled_spa_bundle_changed"] is False
    assert review["technical_links_preserved"] == [
        "Extraction audit",
        "Usage",
        "Advanced audit",
    ]
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["invokes_lolla_skill"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["wires_skill_runtime_behavior"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False
    assert review["non_claims"]["action_authorized"] is False


def test_receipts_technical_disclosure_links_and_privacy_are_clean() -> None:
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
