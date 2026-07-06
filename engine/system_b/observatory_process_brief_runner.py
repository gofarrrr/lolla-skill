"""Offline Observatory adapter for preparing a Decision Work process brief.

The adapter is deliberately narrower than a browser job system. It can inspect
a completed run, explain missing safe inputs, build a command template, and
optionally delegate to the existing no-provider offline operator runner when
explicit generated-read and generated-triage refs are supplied.
"""
from __future__ import annotations

import datetime as _dt
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from engine.system_b.decision_work_offline_operator_runner import (
    render_offline_operator_runner_summary_json,
    run_decision_work_offline_operator,
    write_offline_operator_runner_summary,
)
from engine.system_b.observatory_decision_work_status import (
    build_observatory_decision_work_status,
)


OBSERVATORY_PROCESS_BRIEF_RUNNER_SCHEMA_VERSION = (
    "lolla.observatory_process_brief_runner.v0"
)
PROCESS_BRIEF_ALREADY_ATTACHED = "process_brief_already_attached"
NEEDS_SAFE_INPUTS = "needs_safe_inputs"
OFFLINE_COMMAND_AVAILABLE = "offline_command_available"
OFFLINE_RUNNER_SUMMARY_READY = "offline_runner_summary_ready"
BLOCKED_COMPLETED_RUN_UNAVAILABLE = "blocked_completed_run_unavailable"
RUNNER_FAILED_CLOSED = "runner_failed_closed"
RUNNER_SUMMARY_FILENAME = "runner_summary.json"
STATE_FILENAME = "observatory_process_brief_runner.json"
REPO_ROOT = Path(__file__).resolve().parents[2]

NON_CLAIMS = {
    "product_proof": False,
    "human_validated": False,
    "answer_correctness": False,
    "advice_correctness": False,
    "resolver_approved": False,
    "approval_or_certification": False,
    "answer_quality_scoring": False,
    "agent_action_authorized": False,
    "automatic_action_authorized": False,
}
CUSTODY_FLAGS = {
    "model_calls": 0,
    "provider_or_model_calls_used": False,
    "lolla_skill_invoked": False,
    "new_lolla_run_created": False,
    "creates_interpretation_read": False,
    "writes_sidecar": False,
    "mutates_archive": False,
    "changes_runtime_behavior": False,
    "makes_default_on": False,
    "touches_skill_md": False,
    "touches_scripts_skill": False,
    "touches_archive_run": False,
}


class ObservatoryProcessBriefRunnerError(ValueError):
    """Sanitized process brief runner adapter error."""


def prepare_observatory_process_brief(
    *,
    selected_case_id: str,
    completed_run_archive_dir: Path | str,
    safe_output_dir: Path | str,
    generated_read_path: Path | str | None = None,
    generated_triage_path: Path | str | None = None,
    run_offline_operator: bool = False,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Return a product-safe process brief preparation state.

    When ``run_offline_operator`` is true and both safe inputs exist, this
    delegates to the existing Decision Work offline operator runner. It still
    does not create semantic reads, call providers, write sidecars, mutate the
    archive, or change runtime behavior.
    """

    run_dir = Path(completed_run_archive_dir).expanduser()
    output_dir = Path(safe_output_dir).expanduser()
    generated_read = _optional_path(generated_read_path)
    generated_triage = _optional_path(generated_triage_path)
    state = _base_state(
        selected_case_id=selected_case_id,
        run_dir=run_dir,
        safe_output_dir=output_dir,
        generated_read=generated_read,
        generated_triage=generated_triage,
        run_offline_operator=run_offline_operator,
        created_at=created_at or _utc_now(),
    )

    run_blocker = _completed_run_blocker(run_dir)
    if run_blocker:
        state["blocker_reasons"].append(run_blocker)
        return _finalize(state, BLOCKED_COMPLETED_RUN_UNAVAILABLE)

    decision_work_status = build_observatory_decision_work_status(
        selected_case_id=selected_case_id,
        result_path=_result_path(run_dir),
    )
    state["decision_work_status"] = {
        "status": decision_work_status["decision_work_status"],
        "attachment_state": decision_work_status["attachment_state"],
        "available": decision_work_status["available"],
        "live_extraction_status": decision_work_status["live_extraction_status"],
        "missingness": list(decision_work_status["missingness"]),
        "blockers": list(decision_work_status["blockers"]),
        "deferred_reasons": list(decision_work_status["deferred_reasons"]),
        "receipt_available": bool(decision_work_status["receipt"]["available"]),
    }

    if decision_work_status["available"]:
        state["operator_attention_items"].append("existing_decision_work_attached")
        state["next_action"] = "view_receipt"
        return _finalize(state, PROCESS_BRIEF_ALREADY_ATTACHED)

    missing_inputs = _missing_safe_inputs(generated_read, generated_triage)
    if missing_inputs:
        state["missing_required_inputs"].extend(missing_inputs)
        state["deferred_reasons"].extend(
            f"{item}_missing" for item in missing_inputs
        )
        state["next_action"] = "supply_generated_read_and_triage"
        return _finalize(state, NEEDS_SAFE_INPUTS)

    state["operator_command"] = _operator_command_payload(
        selected_case_id=selected_case_id,
        run_dir=run_dir,
        safe_output_dir=output_dir,
        generated_read=generated_read,
        generated_triage=generated_triage,
    )

    if not run_offline_operator:
        state["next_action"] = "copy_offline_command"
        return _finalize(state, OFFLINE_COMMAND_AVAILABLE)

    runner_summary = run_decision_work_offline_operator(
        completed_run_archive_dir=run_dir,
        generated_read_path=generated_read,
        generated_triage_path=generated_triage,
        case_id=selected_case_id,
        safe_output_dir=output_dir,
        out_path=output_dir / RUNNER_SUMMARY_FILENAME,
        created_at=state["metadata"]["created_at"],
    )
    state["runner_summary"] = _compact_runner_summary(runner_summary)
    state["runner_summary_ref"] = RUNNER_SUMMARY_FILENAME
    try:
        write_offline_operator_runner_summary(
            output_dir / RUNNER_SUMMARY_FILENAME,
            render_offline_operator_runner_summary_json(
                runner_summary,
                pretty=True,
            ),
        )
    except Exception as exc:  # noqa: BLE001 - keep UI adapter fail-closed.
        state["blocker_reasons"].append(
            f"runner_summary_write_failed:{type(exc).__name__}"
        )
        return _finalize(state, RUNNER_FAILED_CLOSED)

    state["next_action"] = _next_action_for_runner_status(
        str(runner_summary.get("final_status") or "")
    )
    return _finalize(state, OFFLINE_RUNNER_SUMMARY_READY)


def render_observatory_process_brief_runner_json(
    state: Mapping[str, Any],
    *,
    pretty: bool = False,
) -> str:
    """Render a process brief preparation state as stable JSON."""

    if pretty:
        return json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return json.dumps(state, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"


def write_observatory_process_brief_runner_json(
    path: Path | str,
    payload: str,
) -> None:
    """Write a process brief runner state, refusing repo and sidecar outputs."""

    output = Path(path).expanduser()
    blocker = _output_file_blocker(output)
    if blocker:
        raise ObservatoryProcessBriefRunnerError(blocker)
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    except OSError as exc:
        raise ObservatoryProcessBriefRunnerError(
            f"process brief runner state could not be written:{type(exc).__name__}"
        ) from exc


def _base_state(
    *,
    selected_case_id: str,
    run_dir: Path,
    safe_output_dir: Path,
    generated_read: Path | None,
    generated_triage: Path | None,
    run_offline_operator: bool,
    created_at: str,
) -> dict[str, Any]:
    return {
        "schema_version": OBSERVATORY_PROCESS_BRIEF_RUNNER_SCHEMA_VERSION,
        "metadata": {
            "created_at": created_at,
            "generated_by": "observatory_process_brief_runner",
            "mode": "offline_cli_first_adapter_v0",
        },
        "selected_case_id": selected_case_id,
        "prepare_process_brief_status": RUNNER_FAILED_CLOSED,
        "next_action": "inspect_state",
        "requested": {
            "run_offline_operator": run_offline_operator,
            "attach_sidecar": False,
            "create_interpretation_read": False,
        },
        "source_refs": {
            "completed_run_archive_dir": _safe_ref(run_dir),
            "safe_output_dir": _safe_ref(safe_output_dir),
            "generated_read": _safe_ref(generated_read) if generated_read else None,
            "generated_triage": (
                _safe_ref(generated_triage) if generated_triage else None
            ),
        },
        "decision_work_status": None,
        "operator_command": None,
        "runner_summary_ref": None,
        "runner_summary": None,
        "missing_required_inputs": [],
        "blocker_reasons": [],
        "deferred_reasons": [],
        "operator_attention_items": [],
        "copy": _copy_payload(),
        "links": {
            "extraction_audit": "/audit/extraction",
            "decision_work_api": f"/api/case/{selected_case_id}/decision-work",
        },
        "non_claims": dict(NON_CLAIMS),
        "custody_flags": dict(CUSTODY_FLAGS),
    }


def _copy_payload() -> dict[str, str]:
    return {
        "what_it_does": (
            "Prepares a process brief for a completed run when explicit safe "
            "Decision Work inputs are supplied."
        ),
        "what_it_does_not_do": (
            "It does not revise the answer, certify it, score advice, authorize "
            "action, or run Lolla."
        ),
        "privacy": (
            "This uses local completed-run artifacts and explicit Decision Work "
            "inputs. It does not upload raw conversation text from this action."
        ),
        "cost": "No model/provider call is made by this preparation step.",
        "latency": "The deterministic runner usually takes seconds.",
        "missing_inputs": (
            "A generated interpretation read and generated triage read are "
            "required before the offline runner can prepare a brief."
        ),
    }


def _completed_run_blocker(run_dir: Path) -> str | None:
    if not run_dir.exists() or not run_dir.is_dir():
        return "completed_run_archive_dir_missing"
    if not _result_path(run_dir).is_file():
        return "completed_run_result_json_missing"
    return None


def _result_path(run_dir: Path) -> Path:
    return run_dir / "result.json"


def _missing_safe_inputs(
    generated_read: Path | None,
    generated_triage: Path | None,
) -> list[str]:
    missing: list[str] = []
    if generated_read is None or not generated_read.is_file():
        missing.append("generated_read")
    if generated_triage is None or not generated_triage.is_file():
        missing.append("generated_triage")
    return missing


def _operator_command_payload(
    *,
    selected_case_id: str,
    run_dir: Path,
    safe_output_dir: Path,
    generated_read: Path,
    generated_triage: Path,
) -> dict[str, Any]:
    argv = [
        "python3",
        "scripts/evals/run_decision_work_offline_operator.py",
        "--completed-run-archive-dir",
        _safe_ref(run_dir),
        "--generated-read",
        _safe_ref(generated_read),
        "--generated-triage",
        _safe_ref(generated_triage),
        "--case-id",
        selected_case_id,
        "--safe-output-dir",
        _safe_ref(safe_output_dir),
        "--out",
        f"{_safe_ref(safe_output_dir)}/{RUNNER_SUMMARY_FILENAME}",
        "--pretty",
    ]
    return {
        "mode": "cli_first",
        "argv": argv,
        "display": " ".join(argv),
        "writes_sidecar": False,
        "mutates_archive": False,
        "calls_provider_or_model": False,
    }


def _compact_runner_summary(summary: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": summary.get("schema_version"),
        "final_status": summary.get("final_status"),
        "completed_steps": list(_strings(summary.get("completed_steps"))),
        "skipped_steps": list(_strings(summary.get("skipped_steps"))),
        "stopped_at": summary.get("stopped_at"),
        "missing_required_inputs": list(
            _strings(summary.get("missing_required_inputs"))
        ),
        "blocker_reasons": list(_strings(summary.get("blocker_reasons"))),
        "deferred_reasons": list(_strings(summary.get("deferred_reasons"))),
        "operator_attention_items": list(
            _strings(summary.get("operator_attention_items"))
        ),
        "write_attempted": bool(summary.get("write_attempted")),
        "actual_sidecar_write_performed": bool(
            summary.get("actual_sidecar_write_performed")
        ),
        "archive_mutated": bool(summary.get("archive_mutated")),
        "runtime_wiring_changed": bool(summary.get("runtime_wiring_changed")),
        "resolver_refs_approved": bool(summary.get("resolver_refs_approved")),
        "can_authorize_agent_action": bool(
            summary.get("can_authorize_agent_action")
        ),
        "can_be_used_as_quality_label": bool(
            summary.get("can_be_used_as_quality_label")
        ),
    }


def _next_action_for_runner_status(status: str) -> str:
    if status == "sidecar_ready_for_explicit_write":
        return "review_runner_summary_then_explicit_attach"
    if status == "sidecar_ready_blocked_state":
        return "review_blocked_state"
    if status.startswith("deferred"):
        return "inspect_missing_inputs"
    if status.startswith("blocked"):
        return "inspect_blockers"
    return "inspect_runner_summary"


def _finalize(state: dict[str, Any], status: str) -> dict[str, Any]:
    state["prepare_process_brief_status"] = status
    for key in ("missing_required_inputs", "blocker_reasons", "deferred_reasons"):
        state[key] = _dedupe(_strings(state.get(key)))
    state["operator_attention_items"] = _dedupe(
        _strings(state.get("operator_attention_items"))
    )
    state["custody_flags"]["runs_offline_operator"] = (
        state.get("runner_summary") is not None
    )
    return state


def _optional_path(path: Path | str | None) -> Path | None:
    if path is None:
        return None
    return Path(path).expanduser()


def _safe_ref(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        resolved = path.resolve(strict=False)
    except OSError:
        return path.name
    if _is_relative_to(resolved, REPO_ROOT):
        return str(resolved.relative_to(REPO_ROOT))
    return path.name


def _output_file_blocker(path: Path) -> str | None:
    if _path_contains_part(path, "decision_work"):
        return "process_brief_state_must_not_target_decision_work_dir"
    try:
        resolved = path.resolve(strict=False)
    except OSError:
        return "process_brief_state_output_unresolvable"
    if _is_relative_to(resolved, REPO_ROOT):
        return "process_brief_state_output_must_not_be_repo_path"
    return None


def _path_contains_part(path: Path, part: str) -> bool:
    return part in path.parts


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _strings(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list | tuple):
        return [str(item) for item in value if str(item)]
    return []


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value and value not in seen:
            deduped.append(value)
            seen.add(value)
    return deduped


def _utc_now() -> str:
    return _dt.datetime.now(tz=_dt.UTC).replace(microsecond=0).isoformat()
