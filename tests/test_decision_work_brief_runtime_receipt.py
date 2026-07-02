from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from engine.system_b.decision_work_brief_runtime_receipt import (
    DecisionWorkBriefRuntimeReceiptError,
    render_decision_work_brief_runtime_receipt,
    render_receipt_from_status,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts/evals/render_decision_work_brief_runtime_receipt.py"
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-runtime-receipt-v0.md"
)
PRIVACY_MARKERS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)
FORBIDDEN_FRAGMENTS = (
    "product proof",
    "human validation",
    "quality score",
    "approved",
    "certified",
    "authorized to act",
)


def test_available_receipt_is_compact_and_caveated() -> None:
    receipt = render_decision_work_brief_runtime_receipt(
        attachment_state="generated",
        action_consequence="The launch path became a narrower beta decision.",
        full_brief_ref="decision_work/decision_work_brief_enriched.md",
        evidence_ref="decision_work/attachment_status.json",
    )

    assert receipt.startswith("Decision Work Brief: available")
    assert "What changed: The launch path became a narrower beta decision." in receipt
    assert "not proof that the advice is correct" in receipt
    assert "Open full brief: `decision_work/decision_work_brief_enriched.md`" in receipt
    assert "Open evidence bundle: `decision_work/attachment_status.json`" in receipt


def test_blocked_receipt_shows_reason_without_full_brief() -> None:
    receipt = render_decision_work_brief_runtime_receipt(
        attachment_state="blocked",
        reasons=["missing_revised_answer"],
        evidence_ref="decision_work/attachment_status.json",
    )

    assert "Decision Work Brief: blocked" in receipt
    assert "Reason: missing_revised_answer." in receipt
    assert "Open full brief" not in receipt
    assert "Open evidence status: `decision_work/attachment_status.json`" in receipt


def test_caveated_and_agent_only_receipts_are_distinct() -> None:
    caveated = render_decision_work_brief_runtime_receipt(
        attachment_state="generated_with_caveats",
        reasons=["private_context_required"],
    )
    agent_only = render_decision_work_brief_runtime_receipt(
        attachment_state="generated_agent_only",
        action_consequence="Inspect the bundle before any user-facing confidence.",
    )

    assert "Decision Work Brief: available with caveats" in caveated
    assert "Decision Work Brief: available for agent inspection" in agent_only
    assert "Agent route: Inspect the bundle" in agent_only


def test_deferred_failed_closed_and_disabled_receipts_are_supported() -> None:
    deferred = render_decision_work_brief_runtime_receipt(
        attachment_state="deferred",
        reasons=["safe_rendered_brief_not_supplied"],
    )
    failed = render_decision_work_brief_runtime_receipt(
        attachment_state="failed_closed",
        reasons=["bundle_generation_error"],
    )
    disabled = render_decision_work_brief_runtime_receipt(
        attachment_state="disabled",
    )

    assert "Decision Work Brief: deferred" in deferred
    assert "Decision Work Brief: failed closed" in failed
    assert "runtime attachment is disabled by default" in disabled


def test_receipt_from_status_uses_soft_blockers_as_caveats() -> None:
    receipt = render_receipt_from_status(
        {
            "attachment_state": "generated",
            "generated_artifacts": {
                "decision_work_brief_markdown": "decision_work/decision_work_brief.md",
                "attachment_status": "decision_work/attachment_status.json",
            },
            "soft_triage_blockers": ["private_context_required"],
        }
    )

    assert "Decision Work Brief: available with caveats" in receipt
    assert "Open full brief: `decision_work/decision_work_brief.md`" in receipt


def test_receipt_rejects_unsafe_refs_and_private_markers() -> None:
    with pytest.raises(DecisionWorkBriefRuntimeReceiptError):
        render_decision_work_brief_runtime_receipt(
            attachment_state="generated",
            full_brief_ref="/tmp/absolute/path.md",
        )
    with pytest.raises(DecisionWorkBriefRuntimeReceiptError):
        render_decision_work_brief_runtime_receipt(
            attachment_state="generated",
            action_consequence="/" + "Users" + "/private",
        )


def test_cli_renders_from_status_json(tmp_path: Path) -> None:
    status_path = tmp_path / "status.json"
    out_path = tmp_path / "receipt.md"
    status_path.write_text(
        json.dumps(
            {
                "attachment_state": "blocked",
                "blocked_reasons": ["missing_required_structured_artifacts"],
                "generated_artifacts": {
                    "attachment_status": "decision_work/attachment_status.json"
                },
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--status-json",
            str(status_path),
            "--out",
            str(out_path),
        ],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Decision Work Brief: blocked" in out_path.read_text(encoding="utf-8")


def test_receipts_do_not_include_private_markers_or_authority_claims() -> None:
    receipts = [
        render_decision_work_brief_runtime_receipt(attachment_state="generated"),
        render_decision_work_brief_runtime_receipt(
            attachment_state="blocked",
            reasons=["missing_revised_answer"],
        ),
        render_decision_work_brief_runtime_receipt(
            attachment_state="generated_agent_only"
        ),
    ]

    rendered = "\n".join(receipts)
    for marker in PRIVACY_MARKERS:
        assert marker not in rendered
    for fragment in FORBIDDEN_FRAGMENTS:
        assert fragment not in rendered.lower()


def test_receipt_docs_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths([DOC_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
