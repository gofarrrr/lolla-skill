from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/observatory-outcome-first-viewport-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-outcome-first-viewport-v0/review.json"
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
    monkeypatch.setattr(serve_result, "_CASE_ID", "lolla-audit")
    monkeypatch.setattr(serve_result, "_CASE_NAME", "Lolla Audit")


def test_outcome_first_viewport_renders_result_before_inventory(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    outcome_index = html.index("<h2>Outcome</h2>")
    answer_index = html.index("Launch in stages after the support risk")
    changed_index = html.index("Why this changed")
    confidence_index = html.index("What would change confidence")
    run_contents_index = html.index("What This Run Contains")
    learn_index = html.index('<section id="learn"')

    assert outcome_index < answer_index < changed_index < confidence_index
    assert confidence_index < run_contents_index < learn_index
    assert "Start with Outcome." not in html
    assert "data-workspace-start-panel" not in html
    assert "Read outcome" not in html
    assert "Practice lesson" not in html
    assert 'aria-label="Next useful moves"' in html
    assert ">Download MD</a>" in html


def test_outcome_first_viewport_renders_run_only_when_teacher_packet_missing(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        serve_result,
        "_RESULT",
        {
            "usage_summary": {"run_id": "no-teacher-packet-run"},
            "extraction": {
                "decision_situation": "A historical case has no Teacher packet."
            },
            "run_health": {"overall": "healthy", "issues": []},
            "revised_answer": (
                "Do not treat the missing Teacher packet as a blank product. "
                "Show the run outcome first and mark lesson surfaces as missing."
            ),
            "delta_card": {
                "top_findings": [
                    {
                        "description": (
                            "The run result exists even when the Teacher packet is absent."
                        )
                    }
                ]
            },
        },
    )
    monkeypatch.setattr(serve_result, "_RESULT_PATH", None)
    monkeypatch.setattr(serve_result, "_CASE_ID", "lolla-audit")
    monkeypatch.setattr(serve_result, "_CASE_NAME", "Lolla Audit")

    html = serve_result._render_workspace_html("lolla-audit")

    assert "<h2>Outcome</h2>" in html
    assert "Show the run outcome first" in html
    assert "No product workspace is available for this run." not in html
    assert "Unavailable Teaching Surfaces" in html
    assert "No Teacher lesson is attached." in html
    assert "No run-specific model pages are attached." in html
    assert "No run-specific relation pages are attached." in html
    assert "No selected-run graph is attached." in html
    assert "What This Run Contains" in html
    assert "This separates what is available now" in html
    assert html.index("<h2>Outcome</h2>") < html.index(
        "Unavailable Teaching Surfaces"
    )


def test_outcome_first_viewport_doc_review_and_readme_capture_gate() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert "Observatory Outcome First Viewport" in readme
    assert "observatory-outcome-first-viewport-v0.md" in readme
    assert review["decision_gate"] == "proceed_to_outcome_browser_review"
    assert review["implemented"]["center_start_panel_removed"] is True
    assert review["implemented"]["run_contents_moved_after_outcome"] is True
    assert review["product_intent"]["outcome_value_is_first_read_source"] is True

    for phrase in [
        "the actual Outcome section",
        "`outcome_value` owns the first read",
        "The sidebar still offers the reading path",
        "no longer preempts the result",
        "visible `Download MD`",
        "does not invoke Lolla",
        "does not call providers or model APIs",
        "does not edit `observatory/build/*`",
        "does not claim answer correctness",
        "proceed_to_outcome_browser_review",
    ]:
        assert phrase in doc

    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["invokes_lolla_skill"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["touches_skill_md"] is False
    assert review["boundary"]["touches_scripts_skill"] is False
    assert review["boundary"]["touches_archive_run"] is False
    assert review["boundary"]["touches_compiled_spa_bundle"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False


def test_outcome_first_viewport_doc_links_are_local() -> None:
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
