from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.decision_work_brief_runtime_bundle import (
    ATTACHMENT_STATUS_SCHEMA_VERSION,
)
from engine.system_b.decision_work_brief_runtime_eligibility import (
    ELIGIBILITY_SCHEMA_VERSION,
    HARD_BLOCKER_VOCABULARY,
    SOFT_TRIAGE_BLOCKER_VOCABULARY,
    evaluate_runtime_attachment_eligibility,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-runtime-eligibility-gate-v0.md"
)
TRIAGE_READ_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-automatic-triage-provisional-read-v0/read.json"
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


def _write_completed_run(run_dir: Path) -> None:
    run_dir.mkdir(parents=True)
    for name in (
        "agent_result.json",
        "evaluation.json",
        "reasoning_trace.json",
        "extraction.json",
        "result.json",
    ):
        (run_dir / name).write_text(
            json.dumps({"artifact": name, "status": "present"}),
            encoding="utf-8",
        )
    (run_dir / "revised.txt").write_text(
        "Safe revised-answer placeholder for fixture use only.",
        encoding="utf-8",
    )


def _attachment_status(state: str = "generated") -> dict[str, Any]:
    return {
        "schema_version": ATTACHMENT_STATUS_SCHEMA_VERSION,
        "attachment_state": state,
        "generated_artifacts": {
            "attachment_status": "decision_work/attachment_status.json",
            "decision_work_brief_markdown": "decision_work/decision_work_brief.md",
            "user_receipt": "decision_work/user_receipt.md",
        },
        "blocked_reasons": [],
        "deferred_reasons": [],
        "custody_flags": {
            "model_calls": 0,
            "runtime_invoked": False,
            "skill_invoked": False,
            "archive_mutated": False,
            "answer_quality_scored": False,
            "agent_action_authorized": False,
            "automatic_action_authorized": False,
        },
    }


def _triage_read(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "lolla.decision_work_automatic_triage_provisional_read.v0",
        "model_calls": 0,
        "runtime_invoked": False,
        "skill_invoked": False,
        "archive_mutated": False,
        "answer_quality_scored": False,
        "agent_action_authorized": False,
        "automatic_action_authorized": False,
        "case_triage_reads": [case],
    }


def _case(
    *,
    case_id: str,
    categories: list[str] | None = None,
    user_route: str = "allowed_with_caveats",
    agent_route: str = "allowed_with_caveats",
    human_route: str = "not_evaluated",
    domain_route: str = "not_evaluated",
    runtime_route: str = "allowed_with_caveats",
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "triage_categories": categories or ["normal_brief_candidate"],
        "user_surface_route": user_route,
        "agent_inspection_route": agent_route,
        "human_calibration_route": human_route,
        "domain_review_route": domain_route,
        "runtime_attachment_route": runtime_route,
        "must_not_be_used_as_quality_label": True,
    }


def test_generated_state_from_clean_run_status_and_safe_triage(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/launch/run"
    _write_completed_run(run_dir)

    result = evaluate_runtime_attachment_eligibility(
        run_dir=run_dir,
        output_dir=tmp_path / "bundle-output",
        attachment_status=_attachment_status("generated"),
        triage_read=_triage_read(_case(case_id="launch")),
        case_id="launch",
        created_at="2026-07-02T00:00:00Z",
    )

    assert result["schema_version"] == ELIGIBILITY_SCHEMA_VERSION
    assert result["attachment_state"] == "generated"
    assert result["eligible_for_generation"] is True
    assert result["eligible_for_user_surface"] is True
    assert result["hard_blockers"] == []
    assert result["soft_triage_blockers"] == []


def test_blocked_state_for_missing_required_run_artifacts(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    run_dir.mkdir(parents=True)

    result = evaluate_runtime_attachment_eligibility(
        run_dir=run_dir,
        attachment_status=_attachment_status("generated"),
        created_at="2026-07-02T00:00:00Z",
    )

    assert result["attachment_state"] == "blocked"
    assert "incomplete_run_artifacts" in result["hard_blockers"]
    assert "missing_revised_answer" in result["hard_blockers"]
    assert set(result["hard_blockers"]) <= set(HARD_BLOCKER_VOCABULARY)


def test_deferred_state_without_attachment_status(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    _write_completed_run(run_dir)

    result = evaluate_runtime_attachment_eligibility(
        run_dir=run_dir,
        created_at="2026-07-02T00:00:00Z",
    )

    assert result["attachment_state"] == "deferred"
    assert result["attachment_status_read"]["deferred_reasons"] == [
        "attachment_status_not_supplied"
    ]


def test_agent_only_state_from_explicit_triage_routes(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/cofounder/run"
    _write_completed_run(run_dir)
    triage = _triage_read(
        _case(
            case_id="cofounder",
            categories=[
                "agent_inspection_only",
                "high_overtrust_risk",
                "private_context_required",
                "legal_or_compliance_review_recommended",
                "relationship_or_political_risk",
                "lost_value_risk",
                "runtime_attachment_blocked",
            ],
            user_route="not_ready",
            agent_route="agent_only",
            human_route="requires_human_calibration",
            domain_route="requires_domain_review",
            runtime_route="blocked_runtime",
        )
    )

    result = evaluate_runtime_attachment_eligibility(
        run_dir=run_dir,
        attachment_status=_attachment_status("generated"),
        triage_read=triage,
        case_id="cofounder",
        created_at="2026-07-02T00:00:00Z",
    )

    assert result["attachment_state"] == "generated_agent_only"
    assert result["eligible_for_user_surface"] is False
    assert result["agent_inspection_only"] is True
    assert set(result["soft_triage_blockers"]) == {
        "agent_inspection_only",
        "high_overtrust_risk",
        "private_context_required",
        "legal_domain_compliance_or_safety_escalation",
        "relationship_or_political_sensitivity",
        "unresolved_lost_value_risk",
        "runtime_attachment_blocked",
    }
    assert set(result["soft_triage_blockers"]) <= set(SOFT_TRIAGE_BLOCKER_VOCABULARY)


def test_hard_blockers_cover_unsafe_path_and_unsafe_custody(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    _write_completed_run(run_dir)
    status = _attachment_status("generated")
    status["custody_flags"]["answer_quality_scored"] = True
    status["custody_flags"]["agent_action_authorized"] = True

    result = evaluate_runtime_attachment_eligibility(
        run_dir=run_dir,
        output_dir=run_dir / "decision_work",
        attachment_status=status,
        created_at="2026-07-02T00:00:00Z",
    )

    assert result["attachment_state"] == "blocked"
    assert "unsafe_output_path" in result["hard_blockers"]
    assert "attempted_answer_quality_scoring" in result["hard_blockers"]
    assert "attempted_action_authorization" in result["hard_blockers"]


def test_real_triage_read_routes_cofounder_to_agent_only(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/ceo-remove-founding-cofounder/run"
    _write_completed_run(run_dir)
    triage_read = json.loads(TRIAGE_READ_PATH.read_text(encoding="utf-8"))

    result = evaluate_runtime_attachment_eligibility(
        run_dir=run_dir,
        attachment_status=_attachment_status("generated"),
        triage_read=triage_read,
        case_id="ceo-remove-founding-cofounder",
        created_at="2026-07-02T00:00:00Z",
    )

    assert result["attachment_state"] == "generated_agent_only"
    assert "high_overtrust_risk" in result["soft_triage_blockers"]
    assert "runtime_attachment_blocked" in result["soft_triage_blockers"]


def test_eligibility_result_is_conservative_and_private_safe(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    _write_completed_run(run_dir)

    result = evaluate_runtime_attachment_eligibility(
        run_dir=run_dir,
        attachment_status=_attachment_status("generated"),
        created_at="2026-07-02T00:00:00Z",
    )
    rendered = json.dumps(result, sort_keys=True)

    assert result["custody_flags"]["model_calls"] == 0
    for field in REQUIRED_FALSE_FLAGS:
        assert result["custody_flags"][field] is False
    assert "triage_is_routing_not_scoring" in result["non_claims"]
    for marker in PRIVACY_MARKERS:
        assert marker not in rendered
    assert str(tmp_path) not in rendered


def test_eligibility_docs_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths([DOC_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
