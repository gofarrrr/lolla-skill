from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from engine.system_b.decision_work_brief_safe_supply_resolver import (
    RESOLVER_SCHEMA_VERSION,
    resolve_decision_work_brief_safe_supply,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts/evals/resolve_decision_work_brief_safe_supply.py"
CONTRACT_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-runtime-safe-supply-resolver-contract-v0.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-runtime-safe-supply-resolver-v0.md"
)
PR170_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-runtime-safe-supply-resolver-contract-v0.md"
)
REQUIRED_FALSE_FLAGS = {
    "human_validated",
    "human_review_completed",
    "product_proof",
    "runtime_invoked",
    "runtime_behavior_changed",
    "skill_invoked",
    "archive_mutated",
    "prompt_changed",
    "skill_files_changed",
    "answer_quality_scored",
    "agent_action_authorized",
    "automatic_action_authorized",
    "raw_private_content_included",
    "provider_text_included",
    "local_absolute_paths_included",
}
REQUIRED_INPUTS = {
    "completed_run_dir_ref",
    "decision_work_brief_json_ref",
    "rendered_brief_markdown_ref",
    "enriched_brief_markdown_ref",
    "interpretation_read_json_ref",
    "automatic_triage_packet_json_ref",
    "automatic_triage_read_json_ref",
    "source_refs",
    "eligibility_result_ref",
    "attachment_status_ref",
    "user_receipt_ref",
    "agent_handoff_ref",
}
REQUIRED_UNSAFE_INPUTS = {
    "raw_conversation_text",
    "raw_revised_answer_text",
    "raw_memo_text",
    "provider_text",
    "private_ledgers",
    "local_absolute_paths",
    "secrets",
    "hidden_chain_of_thought_style_material",
    "runtime_model_generated_interpretation",
    "action_authorization",
    "score_or_approval_labels",
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
            json.dumps({"schema_version": "fixture.v0", "artifact": name}),
            encoding="utf-8",
        )
    (run_dir / "revised.txt").write_text(
        "Safe fixture revised answer placeholder.",
        encoding="utf-8",
    )


def _write_json(path: Path, schema_version: str) -> Path:
    path.write_text(
        json.dumps({"schema_version": schema_version, "fixture": True}),
        encoding="utf-8",
    )
    return path


def _write_markdown(path: Path, text: str = "Safe Decision Work Brief fixture.") -> Path:
    path.write_text(text + "\n", encoding="utf-8")
    return path


def _resolve(run_dir: Path, **kwargs: Any) -> dict[str, Any]:
    return resolve_decision_work_brief_safe_supply(
        run_dir=run_dir,
        contract_path=CONTRACT_PATH,
        created_at="2026-07-02T00:00:00Z",
        **kwargs,
    )


def _record(result: dict[str, Any], input_name: str) -> dict[str, Any]:
    matches = [
        item for item in result["input_classification"] if item["input_name"] == input_name
    ]
    assert len(matches) == 1
    return matches[0]


def test_contract_json_still_parses() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    assert contract["schema_version"] == (
        "lolla.decision_work_brief_runtime_safe_supply_resolver_contract.v0"
    )


def test_disabled_mode_returns_not_requested(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    _write_completed_run(run_dir)

    result = _resolve(run_dir, mode="disabled")

    assert result["schema_version"] == RESOLVER_SCHEMA_VERSION
    assert result["resolver_status"] == "not_requested"
    assert result["feeds_runtime_bundle"] is False
    assert result["reason_if_not_feedable"] == "resolver_disabled"


def test_direct_runtime_interpretation_mode_is_blocked(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    _write_completed_run(run_dir)

    result = _resolve(
        run_dir,
        mode="future_direct_runtime_interpretation_not_allowed",
    )

    assert result["resolver_status"] == "blocked_direct_runtime_interpretation"
    assert result["feeds_runtime_bundle"] is False
    assert result["reason_if_not_feedable"] == (
        "direct_runtime_interpretation_blocked_by_contract"
    )


def test_no_supplied_safe_inputs_returns_no_safe_inputs(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    _write_completed_run(run_dir)

    result = _resolve(run_dir, mode="manual_ref_supply_only")

    assert result["resolver_status"] == "no_safe_inputs"
    assert result["feeds_runtime_bundle"] is False
    assert result["reason_if_not_feedable"] == "no_safe_semantic_inputs_supplied"
    assert {item["input_name"] for item in result["input_classification"]} == (
        REQUIRED_INPUTS
    )


def test_manual_safe_refs_resolve_and_feed_runtime_bundle(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    _write_completed_run(run_dir)
    brief = _write_markdown(tmp_path / "brief.md")
    enriched = _write_markdown(tmp_path / "enriched.md")
    triage_read = _write_json(
        tmp_path / "triage-read.json",
        "lolla.decision_work_automatic_triage_provisional_read.v0",
    )

    result = _resolve(
        run_dir,
        mode="manual_ref_supply_only",
        brief_markdown_path=brief,
        enriched_brief_path=enriched,
        triage_read_path=triage_read,
    )

    assert result["resolver_status"] == "resolved"
    assert result["feeds_runtime_bundle"] is True
    assert result["reason_if_not_feedable"] is None
    assert _record(result, "rendered_brief_markdown_ref")["input_status"] == "resolved"
    assert _record(result, "automatic_triage_read_json_ref")["input_status"] == (
        "resolved"
    )


def test_checked_in_safe_case_registry_mode_resolves_known_case(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "runs/case/run"
    _write_completed_run(run_dir)
    registry = (
        REPO_ROOT
        / "docs/conversation-understanding/"
        "decision-work-brief-runtime-checked-in-safe-case-registry-v0.json"
    )

    result = _resolve(
        run_dir,
        mode="checked_in_safe_case_registry",
        case_registry_path=registry,
        case_key="launch-public-enterprise-beta",
    )

    assert result["resolver_status"] == "resolved"
    assert result["feeds_runtime_bundle"] is True
    assert result["case_registry"]["case_key"] == "launch-public-enterprise-beta"
    assert _record(result, "rendered_brief_markdown_ref")["input_status"] == "resolved"
    assert _record(result, "automatic_triage_read_json_ref")["input_status"] == (
        "resolved"
    )


def test_safe_local_absolute_refs_are_redacted_in_output(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    _write_completed_run(run_dir)
    brief = _write_markdown(tmp_path / "brief.md")

    result = _resolve(run_dir, mode="manual_ref_supply_only", brief_markdown_path=brief)
    rendered = json.dumps(result, sort_keys=True)

    assert result["resolver_status"] == "partially_resolved"
    assert result["feeds_runtime_bundle"] is True
    assert str(tmp_path) not in rendered
    assert _record(result, "rendered_brief_markdown_ref")["input_ref"] == "brief.md"
    assert _record(result, "rendered_brief_markdown_ref")["input_ref_kind"] == (
        "local_ref_redacted"
    )


def test_missing_manual_ref_blocks_with_clear_reason(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    _write_completed_run(run_dir)

    result = _resolve(
        run_dir,
        mode="manual_ref_supply_only",
        brief_markdown_path=tmp_path / "missing.md",
    )

    assert result["resolver_status"] == "blocked_untrusted_source"
    assert result["feeds_runtime_bundle"] is False
    assert _record(result, "rendered_brief_markdown_ref")["reason"] == (
        "supplied_ref_missing"
    )


def test_privacy_marker_content_is_blocked(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    _write_completed_run(run_dir)
    unsafe = tmp_path / "unsafe.md"
    unsafe.write_text("fixture " + "raw_message" + "_content\n", encoding="utf-8")

    result = _resolve(run_dir, mode="manual_ref_supply_only", brief_markdown_path=unsafe)

    assert result["resolver_status"] == "blocked_privacy_risk"
    assert result["feeds_runtime_bundle"] is False
    assert _record(result, "rendered_brief_markdown_ref")["input_status"] == "unsafe"


def test_bad_json_schema_is_blocked(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    _write_completed_run(run_dir)
    triage_read = _write_json(tmp_path / "triage-read.json", "wrong.schema.v0")

    result = _resolve(
        run_dir,
        mode="manual_ref_supply_only",
        triage_read_path=triage_read,
    )

    assert result["resolver_status"] == "blocked_schema_invalid"
    assert result["feeds_runtime_bundle"] is False
    assert _record(result, "automatic_triage_read_json_ref")["reason"] == (
        "json_ref_schema_version_unsupported"
    )


def test_partial_safe_inputs_can_feed_agent_only_bundle(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    _write_completed_run(run_dir)
    brief = _write_markdown(tmp_path / "brief.md")

    result = _resolve(run_dir, mode="manual_ref_supply_only", brief_markdown_path=brief)

    assert result["resolver_status"] == "partially_resolved"
    assert result["feeds_runtime_bundle"] is True
    assert "supply_safe_triage_read_ref_or_accept_agent_only" in (
        result["manual_operator_requirements"]
    )


def test_offline_queue_and_local_private_modes_do_not_feed_bundle(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    _write_completed_run(run_dir)

    queued = _resolve(run_dir, mode="offline_interpretation_queue")
    local_private = _resolve(run_dir, mode="local_private_operator_mode")

    assert queued["resolver_status"] == "queued_for_offline_interpretation"
    assert queued["feeds_runtime_bundle"] is False
    assert queued["queue_handoff"]["queued"] is True
    assert local_private["resolver_status"] == "local_private_operator_required"
    assert local_private["feeds_runtime_bundle"] is False


def test_unsafe_inputs_are_excluded_and_custody_flags_are_conservative(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "runs/case/run"
    _write_completed_run(run_dir)

    result = _resolve(run_dir, mode="manual_ref_supply_only")
    unsafe = {item["input_name"] for item in result["unsafe_inputs_excluded"]}
    custody = result["custody_flags"]

    assert REQUIRED_UNSAFE_INPUTS <= unsafe
    assert custody["model_calls"] == 0
    for field in REQUIRED_FALSE_FLAGS:
        assert custody[field] is False


def test_cli_writes_resolver_output(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    out = tmp_path / "resolver-output.json"
    _write_completed_run(run_dir)
    brief = _write_markdown(tmp_path / "brief.md")
    triage_read = _write_json(
        tmp_path / "triage-read.json",
        "lolla.decision_work_automatic_triage_provisional_read.v0",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--run-dir",
            str(run_dir),
            "--contract",
            str(CONTRACT_PATH),
            "--brief-markdown",
            str(brief),
            "--triage-read",
            str(triage_read),
            "--out",
            str(out),
            "--pretty",
        ],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["resolver_status"] == "resolved"
    assert payload["feeds_runtime_bundle"] is True


def test_docs_json_and_tests_have_no_private_markers() -> None:
    rendered = (
        DOC_PATH.read_text(encoding="utf-8")
        + "\n"
        + CONTRACT_PATH.read_text(encoding="utf-8")
        + "\n"
        + Path(__file__).read_text(encoding="utf-8")
    )

    for marker in PRIVACY_MARKERS:
        assert marker not in rendered


def test_pr171_docs_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths([DOC_PATH, PR170_DOC_PATH, CONTRACT_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
