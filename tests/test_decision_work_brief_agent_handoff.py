from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from engine.system_b.decision_work_brief_agent_handoff import (
    AGENT_HANDOFF_SCHEMA_VERSION,
    build_decision_work_brief_agent_handoff,
)
from engine.system_b.decision_work_brief_runtime_bundle import (
    ATTACHMENT_STATUS_SCHEMA_VERSION,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts/evals/build_decision_work_brief_agent_handoff.py"
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-agent-handoff-v0.md"
)
CONTRACT_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-agent-handoff-v0.json"
)
TRIAGE_READ_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-automatic-triage-provisional-read-v0/read.json"
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
REQUIRED_FALSE_FLAGS = {
    "human_validated",
    "human_review_completed",
    "product_proof",
    "runtime_invoked",
    "skill_invoked",
    "archive_mutated",
    "answer_quality_scored",
    "agent_action_authorized",
    "automatic_action_authorized",
    "raw_private_content_included",
    "provider_text_included",
    "local_absolute_paths_included",
}


def _attachment_status(state: str = "generated") -> dict[str, Any]:
    return {
        "schema_version": ATTACHMENT_STATUS_SCHEMA_VERSION,
        "attachment_state": state,
        "generated_artifacts": {
            "attachment_status": "decision_work/attachment_status.json",
            "decision_work_brief_markdown": "decision_work/decision_work_brief.md",
            "decision_work_brief_enriched_markdown": (
                "decision_work/decision_work_brief_enriched.md"
            ),
            "automatic_triage_read": "decision_work/automatic_triage_read.json",
        },
        "missing_artifacts": {
            "agent_handoff_packet": "not_generated_until_pr165"
        },
        "blocked_reasons": [],
        "deferred_reasons": [],
        "run_artifact_status": {
            "source_run_ref": "launch-public-enterprise-beta/run",
            "archive_finalized": True,
            "required_artifacts": {},
        },
    }


def _eligibility(state: str = "generated") -> dict[str, Any]:
    return {
        "attachment_state": state,
        "agent_inspection_only": state == "generated_agent_only",
        "hard_blockers": [],
        "soft_triage_blockers": [],
        "run_artifact_status": {
            "source_run_ref": "launch-public-enterprise-beta/run",
            "archive_finalized": True,
            "required_artifacts": {},
        },
    }


def _triage_read() -> dict[str, Any]:
    return json.loads(TRIAGE_READ_PATH.read_text(encoding="utf-8"))


def test_agent_handoff_packet_contains_safe_refs_routes_and_non_claims() -> None:
    handoff = build_decision_work_brief_agent_handoff(
        source_run_ref="launch-public-enterprise-beta/20260627T104146Z_7bfe79",
        attachment_status=_attachment_status(),
        eligibility_result=_eligibility(),
        triage_read=_triage_read(),
        case_id="launch-public-enterprise-beta",
        created_at="2026-07-02T00:00:00Z",
    )

    assert handoff["schema_version"] == AGENT_HANDOFF_SCHEMA_VERSION
    assert handoff["attachment_status_ref"] == "decision_work/attachment_status.json"
    assert handoff["brief_refs"]["decision_work_brief_markdown"] == (
        "decision_work/decision_work_brief.md"
    )
    assert handoff["enriched_brief_refs"][
        "decision_work_brief_enriched_markdown"
    ] == "decision_work/decision_work_brief_enriched.md"
    assert handoff["triage_refs"]["automatic_triage_read"] == (
        "decision_work/automatic_triage_read.json"
    )
    assert handoff["route_outputs"]["user_surface_route"] == "allowed_with_caveats"
    assert handoff["route_outputs"]["agent_action_authorized"] is False
    assert handoff["route_outputs"]["automatic_action_authorized"] is False
    assert handoff["route_outputs"]["must_not_be_used_as_quality_label"] is True
    assert "handoff_is_for_inspection_not_action" in handoff["non_claims"]


def test_agent_handoff_preserves_agent_only_and_blocked_state() -> None:
    handoff = build_decision_work_brief_agent_handoff(
        source_run_ref="ceo-remove-founding-cofounder/20260627T093131Z_59d153",
        attachment_status=_attachment_status("generated_agent_only"),
        eligibility_result={
            **_eligibility("generated_agent_only"),
            "soft_triage_blockers": ["high_overtrust_risk", "agent_inspection_only"],
        },
        triage_read=_triage_read(),
        case_id="ceo-remove-founding-cofounder",
        created_at="2026-07-02T00:00:00Z",
    )

    assert handoff["attachment_state"] == "generated_agent_only"
    assert handoff["route_outputs"]["agent_inspection_route"] == "agent_only"
    assert handoff["blocked_or_deferred_state"]["soft_triage_blockers"] == [
        "high_overtrust_risk",
        "agent_inspection_only",
    ]
    assert "high_overtrust_risk" in handoff["agent_inspection_focus"]


def test_agent_handoff_custody_and_privacy_are_conservative() -> None:
    handoff = build_decision_work_brief_agent_handoff(
        source_run_ref="launch-public-enterprise-beta/run",
        attachment_status=_attachment_status(),
        eligibility_result=_eligibility(),
        created_at="2026-07-02T00:00:00Z",
    )
    rendered = json.dumps(handoff, sort_keys=True)

    assert handoff["custody_flags"]["model_calls"] == 0
    for field in REQUIRED_FALSE_FLAGS:
        assert handoff["custody_flags"][field] is False
    assert handoff["privacy_redaction_status"]["raw_conversation_text_included"] is False
    assert handoff["privacy_redaction_status"]["provider_text_included"] is False
    for marker in PRIVACY_MARKERS:
        assert marker not in rendered


def test_agent_handoff_cli_writes_json(tmp_path: Path) -> None:
    status_path = tmp_path / "attachment_status.json"
    out_path = tmp_path / "agent_handoff_packet.json"
    status_path.write_text(json.dumps(_attachment_status()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--source-run-ref",
            "launch-public-enterprise-beta/run",
            "--attachment-status",
            str(status_path),
            "--triage-read",
            str(TRIAGE_READ_PATH),
            "--case-id",
            "launch-public-enterprise-beta",
            "--out",
            str(out_path),
            "--pretty",
        ],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == AGENT_HANDOFF_SCHEMA_VERSION
    assert payload["route_outputs"]["agent_action_authorized"] is False


def test_agent_handoff_contract_json_shape_and_docs_lint() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    assert contract["schema_version"] == (
        "lolla.decision_work_brief_agent_handoff_contract.v0"
    )
    assert contract["route_output_rules"][
        "agent_action_authorized_must_be_false"
    ] is True
    assert contract["route_output_rules"][
        "automatic_action_authorized_must_be_false"
    ] is True
    assert contract["route_output_rules"][
        "must_not_be_used_as_quality_label"
    ] is True
    for field in REQUIRED_FALSE_FLAGS:
        assert contract["custody_flags"][field] is False
    assert contract["custody_flags"]["model_calls"] == 0

    report = lint_product_delta_paths([DOC_PATH, CONTRACT_PATH])
    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
