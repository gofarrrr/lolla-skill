from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/observatory-conversation-understanding-receipts-card-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-conversation-understanding-receipts-card-v0/review.json"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_receipts_card_doc_and_review_are_indexed() -> None:
    assert DOC.exists()
    assert REVIEW.exists()
    readme = _read(README)

    assert "Observatory Conversation Understanding Receipts Card" in readme
    assert "observatory-conversation-understanding-receipts-card-v0.md" in readme


def test_injected_html_contains_conversation_understanding_card() -> None:
    html = serve_result._inject_telemetry_fab(b"<html><body></body></html>").decode(
        "utf-8"
    )

    assert "Conversation Understanding" in html
    assert "decision-work" in html
    assert "decisionWorkEndpointFor" in html
    assert "/audit/extraction" in html
    assert "Show receipt" in html
    assert "Status JSON" in html
    assert "Case Surfaces" in html
    assert "safe interpretation read" in html
    assert "triage read" in html
    assert 'href="/teacher-learning#models"' in html
    assert 'href="/teacher-learning#relations"' in html
    assert 'href="/teacher-learning#map"' in html


def test_card_copy_supports_required_statuses_without_generation_action() -> None:
    script = serve_result._SELECTED_RUN_CUSTODY_PANEL_SCRIPT

    for fragment in [
        "Decision Work not requested",
        "No richer Decision Work receipt is attached yet.",
        "Richer Decision Work material is attached for this run.",
        "Waiting on safe inputs.",
        "Blocked for this run.",
        "failed closed",
    ]:
        assert fragment in script

    forbidden = [
        "call providers",
        "run offline operator",
        "write sidecar",
        "approval",
        "certification",
        "quality score",
        "authorized",
    ]
    for fragment in forbidden:
        assert fragment not in script


def test_card_uses_observatory_custody_aesthetics() -> None:
    style = serve_result._SELECTED_RUN_CUSTODY_PANEL_STYLE

    for fragment in [
        ".lolla-conversation-understanding",
        ".lolla-surface-switcher",
        ".lolla-surface-link.active",
        ".lolla-conversation-heading",
        ".lolla-conversation-row",
        ".lolla-custody-status.deferred",
        ".lolla-custody-status.blocked",
        "rgba(6, 7, 97, 0.96)",
    ]:
        assert fragment in style


def test_review_records_no_runtime_or_generation_boundary() -> None:
    review = __import__("json").loads(_read(REVIEW))

    assert (
        review["decision_gate"]
        == "proceed_to_observatory_decision_work_opt_in_flow_design"
    )
    assert review["implemented"]["ui_surface"] == "selected-run custody panel"
    assert review["implemented"]["compiled_spa_bundle_changed"] is False
    assert review["boundary"]["prepare_process_brief_button_added"] is False
    assert review["boundary"]["observatory_job_action_added"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["creates_interpretation_read"] is False
    assert review["boundary"]["runs_offline_operator"] is False
    assert review["boundary"]["writes_sidecar"] is False
    assert review["boundary"]["mutates_archive"] is False
    assert review["boundary"]["changes_runtime_behavior"] is False
    assert review["boundary"]["touches_skill_md"] is False
    assert review["boundary"]["touches_scripts_skill"] is False
    assert review["boundary"]["touches_archive_run"] is False

    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False
    assert review["non_claims"]["agent_action_authorized"] is False
    assert review["non_claims"]["automatic_action_authorized"] is False


def test_receipts_card_artifacts_have_no_private_markers_or_authority_claims() -> None:
    text = (
        _read(DOC)
        + _read(REVIEW)
        + serve_result._SELECTED_RUN_CUSTODY_PANEL_SCRIPT
        + serve_result._SELECTED_RUN_CUSTODY_PANEL_STYLE
    )

    for forbidden in [
        "/" + "Users/",
        "Desktop/" + "Apps",
    ]:
        assert forbidden not in text
    for key in [
        "product_proof",
        "human_validated",
        "answer_correctness",
        "advice_correctness",
        "agent_action_authorized",
        "automatic_action_authorized",
        "archive_mutated",
        "sidecar_written",
    ]:
        assert f'"{key}": true' not in text
