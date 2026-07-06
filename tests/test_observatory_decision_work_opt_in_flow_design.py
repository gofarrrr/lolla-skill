from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.decision_work_offline_operator_runner import (
    OFFLINE_OPERATOR_RUNNER_SCHEMA_VERSION,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/product/observatory-decision-work-opt-in-flow-design-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-decision-work-opt-in-flow-design-v0/"
    "review.json"
)
RUNNER_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-offline-operator-runner-adapter-v0.md"
)
RUNNER_SCRIPT = REPO_ROOT / "scripts/evals/run_decision_work_offline_operator.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_opt_in_design_doc_and_review_are_indexed() -> None:
    assert DOC.exists()
    assert REVIEW.exists()

    readme = _read(README)
    assert "Observatory Decision Work Opt-In Flow Design" in readme
    assert "observatory-decision-work-opt-in-flow-design-v0.md" in readme


def test_design_defines_prepare_process_brief_without_runtime_generation() -> None:
    text = " ".join(_read(DOC).split())

    for phrase in [
        "Prepare process brief means:",
        "take a completed run",
        "run only explicit offline/operator-safe steps when inputs are present",
        "preserve blockers and missingness",
        "show status -> explain what would be needed -> provide the exact CLI path",
        "The first browser action should not pretend to produce a complete process brief",
        "Do not write `decision_work/` in the first Observatory action.",
    ]:
        assert phrase in text

    for phrase in [
        "run `$lolla`",
        "invoke the Lolla skill",
        "call providers or models from Observatory",
        "generate arbitrary semantic interpretation from a browser click",
        "make Decision Work default-on runtime behavior",
    ]:
        assert phrase in text


def test_design_sets_information_tiers_and_page_shape() -> None:
    text = _read(DOC)

    for row in [
        "| Conversation captured/extracted | First-class status | Compact status row with extraction audit link |",
        "| Runner summary | Second-class receipt detail | Link or collapsible technical summary after run |",
        "| Raw conversation | Internal/private | Never shown as product copy |",
        "| Teacher reasoning move | Separate Learn surface | Linkable, but not part of process brief generation |",
    ]:
        assert row in text

    for heading in [
        "### 1. Status Strip",
        "### 2. What This Would Do",
        "### 3. Action Or Next Step",
        "### 4. Receipt And Technical Links",
    ]:
        assert heading in text


def test_design_state_machine_preserves_missingness_and_blockers() -> None:
    text = _read(DOC)
    normalized = " ".join(text.split())

    for state in [
        "decision_work_not_present",
        "process_brief_not_requested",
        "needs_safe_inputs",
        "offline_command_available",
        "offline_runner_ready_for_review",
        "explicit_attach_required",
        "decision_work_available",
        "deferred_missing_semantic_read",
        "deferred_missing_triage",
        "sidecar_ready_for_explicit_write",
        "sidecar_ready_blocked_state",
        "blocked_privacy_risk",
        "blocked_source_depth_insufficient",
        "blocked_schema_or_custody_failure",
        "blocked_runtime_or_user_surface_risk",
    ]:
        assert state in text

    assert "blocked high-risk case is not a failed product" in normalized


def test_design_selects_cli_first_and_names_existing_runner() -> None:
    text = _read(DOC)
    runner_doc = _read(RUNNER_DOC)

    assert RUNNER_SCRIPT.exists()
    assert OFFLINE_OPERATOR_RUNNER_SCHEMA_VERSION in runner_doc
    assert "## CLI-First Decision" in text
    assert "python3 scripts/evals/run_decision_work_offline_operator.py" in text
    for argument in [
        "--completed-run-archive-dir",
        "--generated-read",
        "--generated-triage",
        "--case-id",
        "--safe-output-dir",
        "--out",
    ]:
        assert argument in text


def test_design_includes_privacy_cost_and_latency_copy() -> None:
    text = _read(DOC)
    normalized = " ".join(text.split())

    for phrase in [
        "It may inspect conversation-derived material and Decision Work inputs.",
        "It does not upload raw conversation text from this button, and this action does not call a model.",
        "No model/provider call is made by this preparation step.",
        "A generated interpretation read is required before this runner can prepare a brief.",
        "This usually takes seconds and writes a local runner summary.",
        "The interpretation-read step may take longer",
    ]:
        assert phrase in normalized


def test_review_json_records_cli_first_boundaries() -> None:
    review = json.loads(_read(REVIEW))

    assert (
        review["schema"]
        == "lolla.observatory_decision_work_opt_in_flow_design_review.v0"
    )
    assert review["artifact"] == (
        "docs/product/observatory-decision-work-opt-in-flow-design-v0.md"
    )
    assert review["decision_gate"] == (
        "proceed_to_observatory_offline_process_brief_runner"
    )
    assert review["design_decisions"]["user_action_name"] == "Prepare process brief"
    assert review["design_decisions"]["first_implementation_mode"] == "cli_first"
    assert review["design_decisions"]["observatory_browser_action_now"] is False
    assert review["design_decisions"]["requires_explicit_generated_read"] is True
    assert review["design_decisions"]["requires_explicit_generated_triage"] is True
    assert review["design_decisions"]["sidecar_attachment_is_separate_gate"] is True

    boundary = review["boundary"]
    for key in [
        "browser_button_added",
        "new_server_route_added",
        "runs_offline_operator",
        "creates_interpretation_read",
        "calls_provider_or_model",
        "runs_lolla",
        "invokes_skill",
        "creates_new_lolla_run",
        "writes_sidecar",
        "mutates_archive",
        "changes_runtime_behavior",
        "makes_default_on",
        "touches_skill_md",
        "touches_scripts_skill",
        "touches_archive_run",
    ]:
        assert boundary[key] is False


def test_review_json_records_required_user_copy_and_non_claims() -> None:
    review = json.loads(_read(REVIEW))

    for key in [
        "privacy_copy_required_before_action",
        "cost_copy_required_before_action",
        "latency_copy_required_before_action",
        "must_explain_missing_generated_read",
        "must_explain_missing_generated_triage",
        "must_preserve_blocked_states",
    ]:
        assert review["copy_requirements"][key] is True

    for key in [
        "product_proof",
        "human_validated",
        "answer_correctness",
        "advice_correctness",
        "approval_or_certification",
        "answer_quality_scoring",
        "agent_action_authorized",
        "automatic_action_authorized",
    ]:
        assert review["non_claims"][key] is False


def test_artifacts_pass_boundary_lint_and_have_no_private_markers() -> None:
    report = lint_product_delta_paths([DOC, REVIEW])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }

    text = _read(DOC) + _read(REVIEW)
    for forbidden in [
        "/" + "Users/",
        "Desktop/" + "Apps",
        "product_proof\": true",
        "human_validated\": true",
        "answer_correctness\": true",
        "advice_correctness\": true",
        "agent_action_authorized\": true",
        "automatic_action_authorized\": true",
        "calls_provider_or_model\": true",
        "writes_sidecar\": true",
        "mutates_archive\": true",
        "changes_runtime_behavior\": true",
    ]:
        assert forbidden not in text
