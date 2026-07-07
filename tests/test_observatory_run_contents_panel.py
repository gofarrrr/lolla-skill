from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/observatory-run-contents-panel-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-run-contents-panel-v0/review.json"
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


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _json(path: Path) -> dict:
    return json.loads(_read(path))


def test_workspace_main_page_shows_run_contents_after_outcome(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert 'data-run-contents-panel' in html
    assert "What This Run Contains" in html
    assert "This separates what is available now" in html
    assert "private export, or inspection-only" in html
    assert html.index("Launch in stages after the support risk") < html.index(
        "What This Run Contains"
    )

    for label in [
        "Conversation",
        "Interpretation",
        "Outcome",
        "Models",
        "Relations",
        "Practice",
        "Receipts",
        "MD export",
    ]:
        assert label in html

    assert "Data we gather" not in html
    assert "artifact_statuses" not in html
    assert "<table" not in html


def test_run_contents_details_group_user_actions_without_raw_json(
    monkeypatch,
) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")
    panel = html.split('data-run-contents-panel', 1)[1].split("</article>", 1)[0]

    for group in [
        "Understanding",
        "Teaching and navigation",
        "Memory, receipts, and inspection",
    ]:
        assert group in panel

    for phrase in [
        "Source context for the selected run.",
        "The interpretation read of the case.",
        "Clean model cards and drill-down pages",
        "Plain-language model-pair stories",
        "One reasoning rep drawn from the selected run",
        "Not shown as first-read UI.",
        "A private self-explaining run memory",
        "Advanced audit route for extraction, usage, events, traces, and internal checks.",
    ]:
        assert phrase in panel

    for action in [
        "Open Outcome",
        "Open Learn",
        "Open Models",
        "Open Relations",
        "Open Map",
        "Open Receipts",
        "Open Advanced Audit",
    ]:
        assert action in panel

    assert "raw JSON" not in panel
    assert "schema_version" not in panel
    assert "/review/observatory-workspace" not in panel


def test_run_contents_panel_defers_download_md_to_header_and_receipts(
    monkeypatch,
) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")
    panel = html.split('data-run-contents-panel', 1)[1].split("</article>", 1)[0]

    assert ">Download MD</a>" in html
    assert "data-agent-memory-download-toast" in html
    assert "agent-memory-download-hint-main" in html
    assert "agent-memory-download-hint-run-contents" not in html
    assert "Give it to a future agent" in html
    assert (
        'download href="/api/case/lolla-audit/conversation-memory.md?include_raw_conversation=1"'
        in html
    )
    assert ">Download MD</a>" not in panel
    assert "Agent memory Markdown" in panel
    assert "A private self-explaining run memory" in panel
    assert ".workspace-run-contents" in serve_result._WORKSPACE_CSS
    assert ".workspace-content-summary" in serve_result._WORKSPACE_CSS
    assert ".workspace-content-groups" in serve_result._WORKSPACE_CSS
    assert ".workspace-content-item" in serve_result._WORKSPACE_CSS


def test_run_contents_panel_docs_review_and_readme_record_boundaries() -> None:
    doc = _read(DOC)
    readme = _read(README)
    review = _json(REVIEW)

    assert "Observatory Run Contents Panel" in readme
    assert "observatory-run-contents-panel-v0.md" in readme

    for phrase in [
        "What This Run Contains",
        "not a table",
        "first-read card",
        "Download MD",
        "private Markdown memory file",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not wire skill runtime behavior",
        "does not edit `observatory/build`",
        "does not claim product proof",
        "does not claim human validation",
        "proceed_to_observatory_run_inventory_receipt_panel",
    ]:
        assert phrase in doc

    assert review["decision_gate"] == (
        "proceed_to_observatory_run_inventory_receipt_panel"
    )
    assert review["implemented"]["main_page_run_contents_panel"] is True
    assert review["implemented"]["giant_table_rendered_to_user"] is False
    assert review["implemented"]["download_md_visible_on_main_page"] is True
    assert review["implemented"]["runtime_behavior_changed"] is False
    assert review["implemented"]["compiled_spa_bundle_changed"] is False
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["invokes_lolla_skill"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False


def test_run_contents_panel_artifacts_are_clean() -> None:
    missing = []
    for path in [DOC, README]:
        text = _read(path)
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith("#") or re.match(r"^[a-z]+:", target):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                missing.append(f"{path}: {target}")

    combined = _read(DOC) + _read(REVIEW)

    assert missing == []
    assert "/" + "Users/" not in combined
    assert "Desktop/" + "Apps" not in combined
    assert "product_proof\": true" not in combined
    assert "human_validated\": true" not in combined
    assert "answer_correctness\": true" not in combined
    assert "advice_correctness\": true" not in combined
    assert "runtime_integration_authorized\": true" not in combined
    assert "action_authorized\": true" not in combined
