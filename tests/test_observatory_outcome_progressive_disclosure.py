from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/observatory-outcome-progressive-disclosure-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-outcome-progressive-disclosure-v0/review.json"
)


def _install_launch_case(monkeypatch, *, run_id: str = "20260627T104146Z_7bfe79") -> None:
    monkeypatch.setattr(
        serve_result,
        "_RESULT",
        {
            "usage_summary": {"run_id": run_id},
            "extraction": {
                "decision_situation": (
                    "A public enterprise beta launch is being reviewed."
                )
            },
            "run_health": {"overall": "healthy", "issues": []},
            "revised_answer": (
                "Launch in stages after the support risk is made explicit. "
                "Keep the first cohort narrow and treat the beta as a learning gate. "
                "Do not treat enterprise interest as proof of readiness."
            ),
            "memo_what_changed": (
                "The answer changed because authority and enterprise posture were "
                "separated from evidence."
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


def _outcome_section(html: str) -> str:
    return html.split('<section id="outcome"', 1)[1].split(
        '<section id="learn"',
        1,
    )[0]


def test_outcome_first_read_has_one_recommended_continuation(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")
    outcome = _outcome_section(html)

    assert "Launch in stages after the support risk is made explicit." in outcome
    assert outcome.count('aria-label="Recommended continuation"') == 1
    assert "Practice the reasoning move" in outcome
    assert outcome.index('aria-label="Recommended continuation"') < outcome.index(
        "More outcome detail"
    )
    assert 'aria-label="Next useful moves"' not in outcome
    assert 'aria-label="Other outcome actions"' in outcome
    assert outcome.index("More outcome detail") < outcome.index(
        "What This Run Contains"
    )


def test_outcome_uses_receipts_as_primary_when_teacher_surfaces_are_missing(
    monkeypatch,
) -> None:
    _install_launch_case(monkeypatch, run_id="no-teacher-packet-run")

    html = serve_result._render_workspace_html("lolla-audit")
    outcome = _outcome_section(html)

    assert "Check what is available" in outcome
    assert "No Teacher lesson is attached to this run" in outcome
    assert outcome.index("Check what is available") < outcome.index(
        "More outcome detail"
    )
    assert "Unavailable Teaching Surfaces" in html


def test_outcome_progressive_disclosure_doc_review_and_readme() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert "Observatory Outcome Progressive Disclosure" in readme
    assert "observatory-outcome-progressive-disclosure-v0.md" in readme
    assert review["decision_gate"] == "proceed_to_browser_review_outcome_flow"

    for phrase in [
        "one recommended continuation",
        "secondary actions behind disclosure",
        "Outcome remains the result-first surface",
        "Download MD stays visible in the workspace header",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not edit `observatory/build/*`",
        "does not claim answer correctness",
    ]:
        assert phrase in doc

    assert review["implemented"]["single_primary_outcome_continuation"] is True
    assert review["implemented"]["secondary_actions_are_disclosed"] is True
    assert review["implemented"]["download_md_header_affordance_preserved"] is True
    assert review["implemented"]["standalone_current_result_md_export_fallback"] is True
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["touches_compiled_spa_bundle"] is False
    assert review["non_claims"]["answer_correctness"] is False


def test_outcome_progressive_disclosure_doc_links_are_local() -> None:
    missing = []
    for path in [DOC, README]:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith("#") or re.match(r"^[a-z]+:", target):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).exists():
                missing.append((path.name, clean))
    assert missing == []
