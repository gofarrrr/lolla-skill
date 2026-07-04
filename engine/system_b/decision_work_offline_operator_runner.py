"""One-shot offline operator runner for Decision Work sidecar readiness.

PR226 reduces operator toil by orchestrating existing deterministic Decision
Work CLIs from explicit input paths. It does not generate semantic
interpretation, call providers/models, wire runtime, approve resolver refs,
write sidecars, mutate archives, score answer quality, or authorize action.
"""
from __future__ import annotations

import datetime as _dt
import json
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


OFFLINE_OPERATOR_RUNNER_SCHEMA_VERSION = (
    "lolla.decision_work_offline_operator_runner.v0"
)
SIDECAR_READY_FOR_EXPLICIT_WRITE = "sidecar_ready_for_explicit_write"
SIDECAR_READY_BLOCKED_STATE = "sidecar_ready_blocked_state"
DEFERRED_MISSING_SEMANTIC_READ = "deferred_missing_semantic_read"
DEFERRED_MISSING_TRIAGE = "deferred_missing_triage"
BLOCKED_PRIVACY_RISK = "blocked_privacy_risk"
BLOCKED_SOURCE_DEPTH_INSUFFICIENT = "blocked_source_depth_insufficient"
BLOCKED_SCHEMA_OR_CUSTODY_FAILURE = "blocked_schema_or_custody_failure"
BLOCKED_RUNTIME_OR_USER_SURFACE_RISK = "blocked_runtime_or_user_surface_risk"
STOPPED_BEFORE_EXPLICIT_WRITE = "stopped_before_explicit_write"
RUNNER_FAILED_CLOSED = "runner_failed_closed"

DRY_RUN_READY_STATUS = "dry_run_ready"
DRY_RUN_RUNTIME_BLOCK_STATUS = "dry_run_packet_with_runtime_block"
REPO_ROOT = Path(__file__).resolve().parents[2]

RAW_PRIVATE_MARKERS = (
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
    "PRIVATE TRANSCRIPT",
    "RAW TRANSCRIPT",
    "PROVIDER OUTPUT",
    "MODEL OUTPUT",
)
LOCAL_ABSOLUTE_PATH_MARKERS = (
    "/" + "Users" + "/",
    "/home/",
    "/private/",
)
ARTIFACT_NAMES = {
    "intake": "intake.json",
    "brief_supply": "brief_supply.json",
    "rendered_brief": "rendered_brief.md",
    "triage_supply": "triage_supply.json",
    "resolver_supply": "resolver_supply.json",
    "sidecar_update_packet": "sidecar_update_packet.json",
    "dry_run": "dry_run.json",
    "runner_summary": "runner_summary.json",
}
CLI_STEPS = (
    "generated_read_intake",
    "brief_supply",
    "rendered_brief",
    "triage_supply",
    "resolver_supply",
    "sidecar_update_packet",
    "sidecar_write_dry_run",
)
NON_CLAIMS = (
    "runner_is_not_runtime_automation",
    "runner_is_not_a_queue_worker",
    "runner_does_not_generate_semantic_interpretation",
    "runner_does_not_call_models_or_providers",
    "runner_does_not_approve_resolver_refs",
    "runner_does_not_write_sidecars",
    "runner_does_not_mutate_archives",
    "runner_does_not_wire_runtime",
    "runner_is_not_product_proof",
    "runner_is_not_human_validation",
    "runner_does_not_score_answer_quality",
    "runner_does_not_validate_advice_correctness",
    "runner_does_not_authorize_agent_action",
    "runner_does_not_authorize_automatic_action",
)


class DecisionWorkOfflineOperatorRunnerError(ValueError):
    """Sanitized offline operator runner error."""


def run_decision_work_offline_operator(
    *,
    completed_run_archive_dir: Path | str,
    generated_read_path: Path | str,
    generated_triage_path: Path | str,
    case_id: str,
    safe_output_dir: Path | str,
    out_path: Path | str | None = None,
    write_sidecar: bool = False,
    operator_confirm_real_archive_write: bool = False,
    stop_before_write: bool = False,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Run the offline operator chain up to dry-run and emit a summary."""

    context = _RunnerContext(
        completed_run_archive_dir=Path(completed_run_archive_dir).expanduser(),
        generated_read_path=Path(generated_read_path).expanduser(),
        generated_triage_path=Path(generated_triage_path).expanduser(),
        case_id=case_id,
        safe_output_dir=Path(safe_output_dir).expanduser(),
        out_path=Path(out_path).expanduser() if out_path is not None else None,
        write_sidecar=write_sidecar,
        operator_confirm_real_archive_write=operator_confirm_real_archive_write,
        stop_before_write=stop_before_write,
        created_at=created_at or _utc_now(),
    )
    context.prepare_output_dir()
    summary = _base_summary(context)

    preflight_status = _preflight(context, summary)
    if preflight_status is not None:
        return _finalize(context, summary, preflight_status)

    for step in (
        _run_intake,
        _run_brief_supply,
        _run_rendered_brief,
        _run_triage_supply,
        _run_resolver_supply,
        _run_sidecar_update_packet,
        _run_dry_run,
    ):
        status = step(context, summary)
        if status is not None:
            return _finalize(context, summary, status)

    final_status = _ready_status_from_artifacts(context, summary)
    if write_sidecar or operator_confirm_real_archive_write or stop_before_write:
        _add_attention(
            summary,
            "explicit_write_not_performed_by_runner_v0",
        )
        summary["stopped_at"] = "before_explicit_archive_write"
        final_status = STOPPED_BEFORE_EXPLICIT_WRITE
    return _finalize(context, summary, final_status)


def render_offline_operator_runner_summary_json(
    summary: Mapping[str, Any],
    *,
    pretty: bool = False,
) -> str:
    """Render a runner summary as stable JSON."""

    if pretty:
        return json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return json.dumps(summary, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"


def write_offline_operator_runner_summary(path: Path | str, payload: str) -> None:
    """Write a runner summary, refusing sidecar-looking output paths."""

    output = Path(path).expanduser()
    if _path_contains_part(output, "decision_work"):
        raise DecisionWorkOfflineOperatorRunnerError(
            "runner summary must not be written into a decision_work directory"
        )
    try:
        resolved = output.resolve(strict=False)
    except OSError as exc:
        raise DecisionWorkOfflineOperatorRunnerError(
            "runner summary output path is not resolvable"
        ) from exc
    if _is_relative_to(resolved, REPO_ROOT):
        raise DecisionWorkOfflineOperatorRunnerError(
            "runner summary output path must not be inside the repository"
        )
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    except OSError as exc:
        raise DecisionWorkOfflineOperatorRunnerError(
            f"runner summary could not be written:{type(exc).__name__}"
        ) from exc


class _RunnerContext:
    def __init__(
        self,
        *,
        completed_run_archive_dir: Path,
        generated_read_path: Path,
        generated_triage_path: Path,
        case_id: str,
        safe_output_dir: Path,
        out_path: Path | None,
        write_sidecar: bool,
        operator_confirm_real_archive_write: bool,
        stop_before_write: bool,
        created_at: str,
    ) -> None:
        self.completed_run_archive_dir = completed_run_archive_dir
        self.generated_read_path = generated_read_path
        self.generated_triage_path = generated_triage_path
        self.case_id = case_id
        self.safe_output_dir = safe_output_dir
        self.out_path = out_path
        self.write_sidecar = write_sidecar
        self.operator_confirm_real_archive_write = operator_confirm_real_archive_write
        self.stop_before_write = stop_before_write
        self.created_at = created_at

    def artifact_path(self, key: str) -> Path:
        return self.safe_output_dir / ARTIFACT_NAMES[key]

    def summary_path(self) -> Path:
        return self.out_path or self.artifact_path("runner_summary")

    def prepare_output_dir(self) -> None:
        blocker = _safe_output_dir_blocker(self.safe_output_dir)
        if blocker:
            return
        self.safe_output_dir.mkdir(parents=True, exist_ok=True)


def _base_summary(context: _RunnerContext) -> dict[str, Any]:
    return {
        "schema_version": OFFLINE_OPERATOR_RUNNER_SCHEMA_VERSION,
        "runner_metadata": {
            "created_at": context.created_at,
            "generated_by": "decision_work_offline_operator_runner",
            "mode": "offline_operator_runner_v0",
            "model_calls": 0,
            "lolla_invoked": False,
            "new_lolla_runs_created": False,
            "runtime_wired": False,
            "archive_hook_changed": False,
            "queue_worker_added": False,
            "semantic_interpretation_generated": False,
        },
        "case_id": context.case_id,
        "source_refs": {
            "completed_run_archive_dir_supplied": bool(
                str(context.completed_run_archive_dir)
            ),
            "generated_read_ref": _safe_ref(context.generated_read_path),
            "generated_triage_ref": _safe_ref(context.generated_triage_path),
            "safe_output_dir_ref": "safe_output_dir",
        },
        "final_status": RUNNER_FAILED_CLOSED,
        "completed_steps": [],
        "skipped_steps": [],
        "stopped_at": None,
        "artifact_refs": {},
        "missing_required_inputs": [],
        "blocker_reasons": [],
        "deferred_reasons": [],
        "operator_attention_items": [],
        "source_depth_status": None,
        "runtime_use_status": None,
        "user_surface_status": None,
        "non_claims": list(NON_CLAIMS),
        "custody_flags": _custody_flags(),
        "write_attempted": False,
        "actual_sidecar_write_performed": False,
        "archive_mutated": False,
        "historical_archive_mutated": False,
        "resolver_refs_approved": False,
        "runtime_wiring_changed": False,
        "can_authorize_agent_action": False,
        "can_authorize_automatic_action": False,
        "can_be_used_as_quality_label": False,
        "downstream_forbidden": [
            "runtime_wiring",
            "queue_worker_or_daemon",
            "direct_runtime_interpretation",
            "provider_or_model_call",
            "new_lolla_run",
            "resolver_approval",
            "sidecar_write_from_runner_v0",
            "archive_mutation_from_runner_v0",
            "default_on_runtime_attachment",
            "quality_label",
            "product_proof",
            "human_validation",
            "advice_correctness_claim",
            "action_authorization",
        ],
    }


def _preflight(
    context: _RunnerContext,
    summary: dict[str, Any],
) -> str | None:
    output_blocker = _safe_output_dir_blocker(context.safe_output_dir)
    if output_blocker:
        _add_blocker(summary, output_blocker)
        summary["stopped_at"] = "safe_output_dir"
        _mark_skipped(summary, CLI_STEPS)
        return RUNNER_FAILED_CLOSED
    if not context.generated_read_path.exists():
        _add_missing(summary, "generated_read")
        _add_deferred(summary, "generated_read_missing")
        summary["stopped_at"] = "generated_read"
        _mark_skipped(summary, CLI_STEPS)
        return DEFERRED_MISSING_SEMANTIC_READ
    if not context.generated_triage_path.exists():
        _add_missing(summary, "generated_triage")
        _add_deferred(summary, "generated_triage_missing")
        summary["stopped_at"] = "generated_triage"
        _mark_skipped(summary, CLI_STEPS)
        return DEFERRED_MISSING_TRIAGE
    marker_blocker = _input_marker_blocker(
        context.generated_read_path,
        context.generated_triage_path,
    )
    if marker_blocker:
        _add_blocker(summary, marker_blocker)
        summary["stopped_at"] = "input_privacy_scan"
        _mark_skipped(summary, CLI_STEPS)
        return BLOCKED_PRIVACY_RISK
    return None


def _run_intake(
    context: _RunnerContext,
    summary: dict[str, Any],
) -> str | None:
    out = context.artifact_path("intake")
    result = _run_cli(
        "generated_read_intake",
        [
            "scripts/evals/validate_decision_work_generated_interpretation_read.py",
            "--read",
            str(context.generated_read_path),
            "--out",
            str(out),
            "--pretty",
        ],
    )
    _record_process(summary, result, out, "intake")
    if result.returncode != 0:
        return _status_from_cli_failure(summary, "generated_read_intake", result)
    payload = _read_json(out)
    if payload.get("accepted_for_downstream") is not True:
        _add_blockers(summary, _strings(payload.get("blocker_reasons")))
        _add_blocker(summary, f"intake_not_accepted:{payload.get('intake_status')}")
        summary["stopped_at"] = "generated_read_intake"
        _mark_skipped(summary, CLI_STEPS[1:])
        return BLOCKED_SCHEMA_OR_CUSTODY_FAILURE
    return None


def _run_brief_supply(
    context: _RunnerContext,
    summary: dict[str, Any],
) -> str | None:
    out = context.artifact_path("brief_supply")
    result = _run_cli(
        "brief_supply",
        [
            "scripts/evals/build_decision_work_generated_read_brief_supply.py",
            "--read",
            str(context.generated_read_path),
            "--intake",
            str(context.artifact_path("intake")),
            "--out",
            str(out),
            "--pretty",
        ],
    )
    _record_process(summary, result, out, "brief_supply")
    if result.returncode != 0:
        return _status_from_cli_failure(summary, "brief_supply", result)
    payload = _read_json(out)
    status = str(payload.get("supply_status", ""))
    if status and status != "ready_for_offline_brief_rendering":
        _add_blockers(summary, _strings(payload.get("blocker_reasons")))
        summary["stopped_at"] = "brief_supply"
        _mark_skipped(summary, CLI_STEPS[2:])
        return _status_from_artifact_status(status)
    return None


def _run_rendered_brief(
    context: _RunnerContext,
    summary: dict[str, Any],
) -> str | None:
    out = context.artifact_path("rendered_brief")
    result = _run_cli(
        "rendered_brief",
        [
            "scripts/evals/render_decision_work_generated_read_brief.py",
            "--supply",
            str(context.artifact_path("brief_supply")),
            "--case-id",
            context.case_id,
            "--out",
            str(out),
        ],
    )
    _record_process(summary, result, out, "rendered_brief")
    if result.returncode != 0:
        return _status_from_cli_failure(summary, "rendered_brief", result)
    return None


def _run_triage_supply(
    context: _RunnerContext,
    summary: dict[str, Any],
) -> str | None:
    out = context.artifact_path("triage_supply")
    result = _run_cli(
        "triage_supply",
        [
            "scripts/evals/build_decision_work_generated_read_triage_supply.py",
            "--read",
            str(context.generated_read_path),
            "--intake",
            str(context.artifact_path("intake")),
            "--brief-supply",
            str(context.artifact_path("brief_supply")),
            "--rendered-brief",
            str(context.artifact_path("rendered_brief")),
            "--out",
            str(out),
            "--pretty",
        ],
    )
    _record_process(summary, result, out, "triage_supply")
    if result.returncode != 0:
        return _status_from_cli_failure(summary, "triage_supply", result)
    payload = _read_json(out)
    status = str(payload.get("triage_supply_status", ""))
    if status and status != "ready_for_offline_triage_generation":
        _add_blockers(summary, _strings(payload.get("blocker_reasons")))
        summary["stopped_at"] = "triage_supply"
        _mark_skipped(summary, CLI_STEPS[4:])
        return _status_from_artifact_status(status)
    return None


def _run_resolver_supply(
    context: _RunnerContext,
    summary: dict[str, Any],
) -> str | None:
    out = context.artifact_path("resolver_supply")
    result = _run_cli(
        "resolver_supply",
        [
            "scripts/evals/build_decision_work_generated_read_resolver_supply.py",
            "--read",
            str(context.generated_read_path),
            "--intake",
            str(context.artifact_path("intake")),
            "--brief-supply",
            str(context.artifact_path("brief_supply")),
            "--rendered-brief",
            str(context.artifact_path("rendered_brief")),
            "--triage-supply",
            str(context.artifact_path("triage_supply")),
            "--triage",
            str(context.generated_triage_path),
            "--out",
            str(out),
            "--pretty",
        ],
    )
    _record_process(summary, result, out, "resolver_supply")
    if result.returncode != 0:
        return _status_from_cli_failure(summary, "resolver_supply", result)
    payload = _read_json(out)
    _copy_status_summaries(summary, payload)
    status = str(payload.get("resolver_supply_status", ""))
    if status not in {
        "ready_for_resolver_candidate_packet",
        "candidate_packet_with_runtime_block",
    }:
        _add_blockers(summary, _strings(payload.get("blocker_reasons")))
        summary["stopped_at"] = "resolver_supply"
        _mark_skipped(summary, CLI_STEPS[5:])
        return _status_from_artifact_status(status)
    return None


def _run_sidecar_update_packet(
    context: _RunnerContext,
    summary: dict[str, Any],
) -> str | None:
    out = context.artifact_path("sidecar_update_packet")
    result = _run_cli(
        "sidecar_update_packet",
        [
            "scripts/evals/build_decision_work_resolver_candidate_sidecar_update_packet.py",
            "--resolver-supply",
            str(context.artifact_path("resolver_supply")),
            "--source-resolver-supply-ref",
            _safe_ref(context.artifact_path("resolver_supply")),
            "--out",
            str(out),
            "--pretty",
        ],
    )
    _record_process(summary, result, out, "sidecar_update_packet")
    if result.returncode != 0:
        return _status_from_cli_failure(summary, "sidecar_update_packet", result)
    payload = _read_json(out)
    _copy_status_summaries(summary, payload)
    status = str(payload.get("sidecar_update_packet_status", ""))
    if status not in {"ready_for_sidecar_update_packet", "packet_with_runtime_block"}:
        _add_blockers(summary, _strings(payload.get("blocker_reasons")))
        summary["stopped_at"] = "sidecar_update_packet"
        _mark_skipped(summary, CLI_STEPS[6:])
        return _status_from_artifact_status(status)
    return None


def _run_dry_run(
    context: _RunnerContext,
    summary: dict[str, Any],
) -> str | None:
    out = context.artifact_path("dry_run")
    result = _run_cli(
        "sidecar_write_dry_run",
        [
            "scripts/evals/dry_run_decision_work_sidecar_write.py",
            "--sidecar-update-packet",
            str(context.artifact_path("sidecar_update_packet")),
            "--source-sidecar-update-packet-ref",
            _safe_ref(context.artifact_path("sidecar_update_packet")),
            "--out",
            str(out),
            "--pretty",
        ],
    )
    _record_process(summary, result, out, "dry_run")
    if result.returncode != 0:
        return _status_from_cli_failure(summary, "sidecar_write_dry_run", result)
    payload = _read_json(out)
    _copy_status_summaries(summary, payload)
    status = str(payload.get("dry_run_status", ""))
    if status not in {DRY_RUN_READY_STATUS, DRY_RUN_RUNTIME_BLOCK_STATUS}:
        _add_blockers(summary, _strings(payload.get("blocker_reasons")))
        summary["stopped_at"] = "sidecar_write_dry_run"
        return _status_from_artifact_status(status)
    return None


def _ready_status_from_artifacts(
    context: _RunnerContext,
    summary: dict[str, Any],
) -> str:
    dry_run = _read_json(context.artifact_path("dry_run"))
    dry_run_status = dry_run.get("dry_run_status")
    summary["stopped_at"] = "dry_run_complete"
    if dry_run_status == DRY_RUN_RUNTIME_BLOCK_STATUS:
        _add_attention(summary, "runtime_or_user_surface_block_preserved")
        return SIDECAR_READY_BLOCKED_STATE
    if dry_run_status == DRY_RUN_READY_STATUS:
        _add_attention(summary, "manual_explicit_write_available_as_next_step")
        return SIDECAR_READY_FOR_EXPLICIT_WRITE
    return _status_from_artifact_status(str(dry_run_status))


def _finalize(
    context: _RunnerContext,
    summary: dict[str, Any],
    final_status: str,
) -> dict[str, Any]:
    summary["final_status"] = final_status
    summary["completed_steps"] = _dedupe(_strings(summary.get("completed_steps")))
    summary["skipped_steps"] = _dedupe(_strings(summary.get("skipped_steps")))
    summary["missing_required_inputs"] = _dedupe(
        _strings(summary.get("missing_required_inputs"))
    )
    summary["blocker_reasons"] = _dedupe(_strings(summary.get("blocker_reasons")))
    summary["deferred_reasons"] = _dedupe(_strings(summary.get("deferred_reasons")))
    summary["operator_attention_items"] = _dedupe(
        _strings(summary.get("operator_attention_items"))
    )
    if final_status == STOPPED_BEFORE_EXPLICIT_WRITE:
        summary["write_attempted"] = False
        _add_blocker(summary, "write_mode_not_supported_in_runner_v0")
    if not summary["skipped_steps"]:
        completed = set(_strings(summary.get("completed_steps")))
        _mark_skipped(summary, [step for step in CLI_STEPS if step not in completed])
    return summary


def _run_cli(step_name: str, argv: Sequence[str]) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, *argv]
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _record_process(
    summary: dict[str, Any],
    result: subprocess.CompletedProcess[str],
    output_path: Path,
    artifact_key: str,
) -> None:
    step_name = _step_for_artifact(artifact_key)
    if result.returncode == 0 and output_path.exists():
        summary["completed_steps"].append(step_name)
        summary["artifact_refs"][artifact_key] = _safe_ref(output_path)
    else:
        summary["stopped_at"] = step_name
        _add_blocker(summary, f"{step_name}_failed")
        if result.stderr.strip():
            _add_blocker(summary, _sanitize_process_text(result.stderr))


def _status_from_cli_failure(
    summary: dict[str, Any],
    step_name: str,
    result: subprocess.CompletedProcess[str],
) -> str:
    summary["stopped_at"] = step_name
    _mark_skipped(summary, _steps_after(step_name))
    text = f"{result.stdout}\n{result.stderr}".lower()
    if "privacy" in text or "local_absolute" in text or "secret" in text:
        return BLOCKED_PRIVACY_RISK
    if "source" in text and "depth" in text:
        return BLOCKED_SOURCE_DEPTH_INSUFFICIENT
    if "runtime" in text or "user_surface" in text:
        return BLOCKED_RUNTIME_OR_USER_SURFACE_RISK
    return BLOCKED_SCHEMA_OR_CUSTODY_FAILURE


def _status_from_artifact_status(status: str) -> str:
    lower = status.lower()
    if "privacy" in lower or "local_path" in lower:
        return BLOCKED_PRIVACY_RISK
    if "source_depth" in lower or "missing_source" in lower:
        return BLOCKED_SOURCE_DEPTH_INSUFFICIENT
    if "missing_triage" in lower:
        return DEFERRED_MISSING_TRIAGE
    if "runtime" in lower or "user_surface" in lower:
        return BLOCKED_RUNTIME_OR_USER_SURFACE_RISK
    if "deferred" in lower:
        return BLOCKED_SCHEMA_OR_CUSTODY_FAILURE
    if "blocked" in lower:
        return BLOCKED_SCHEMA_OR_CUSTODY_FAILURE
    return RUNNER_FAILED_CLOSED


def _copy_status_summaries(
    summary: dict[str, Any],
    payload: Mapping[str, Any],
) -> None:
    for key in ("runtime_use_status", "user_surface_status"):
        value = payload.get(key)
        if isinstance(value, Mapping):
            summary[key] = dict(value)
    source_depth = payload.get("source_depth_status")
    if isinstance(source_depth, Mapping):
        summary["source_depth_status"] = dict(source_depth)
    elif "source_ref_summary" in payload:
        summary["source_depth_status"] = {
            "status": "source_refs_preserved",
            "source_ref_summary_present": True,
        }
    _add_blockers(summary, _strings(payload.get("blocker_reasons")))


def _safe_output_dir_blocker(path: Path) -> str | None:
    if _path_contains_part(path, "decision_work"):
        return "safe_output_dir_must_not_be_decision_work"
    try:
        resolved = path.resolve(strict=False)
    except OSError:
        return "safe_output_dir_unresolvable"
    if _is_relative_to(resolved, REPO_ROOT):
        return "safe_output_dir_must_not_be_repo_path"
    return None


def _input_marker_blocker(*paths: Path) -> str | None:
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            return "input_unreadable"
        if any(marker in text for marker in RAW_PRIVATE_MARKERS):
            return "privacy_marker_detected"
        if any(marker in text for marker in LOCAL_ABSOLUTE_PATH_MARKERS):
            return "local_absolute_path_detected"
    return None


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DecisionWorkOfflineOperatorRunnerError(
            f"runner artifact unreadable:{path.name}:{type(exc).__name__}"
        ) from exc
    if not isinstance(payload, dict):
        raise DecisionWorkOfflineOperatorRunnerError(
            f"runner artifact must be JSON object:{path.name}"
        )
    return payload


def _safe_ref(path: Path) -> str:
    try:
        resolved = path.resolve(strict=False)
    except OSError:
        return path.name
    if _is_relative_to(resolved, REPO_ROOT):
        return str(resolved.relative_to(REPO_ROOT))
    return path.name


def _step_for_artifact(artifact_key: str) -> str:
    return {
        "intake": "generated_read_intake",
        "brief_supply": "brief_supply",
        "rendered_brief": "rendered_brief",
        "triage_supply": "triage_supply",
        "resolver_supply": "resolver_supply",
        "sidecar_update_packet": "sidecar_update_packet",
        "dry_run": "sidecar_write_dry_run",
    }.get(artifact_key, artifact_key)


def _steps_after(step_name: str) -> list[str]:
    if step_name not in CLI_STEPS:
        return []
    return list(CLI_STEPS[CLI_STEPS.index(step_name) + 1 :])


def _mark_skipped(summary: dict[str, Any], steps: Sequence[str]) -> None:
    existing = set(_strings(summary.get("skipped_steps")))
    for step in steps:
        if step not in existing:
            summary["skipped_steps"].append(step)
            existing.add(step)


def _add_missing(summary: dict[str, Any], reason: str) -> None:
    summary["missing_required_inputs"].append(reason)


def _add_blocker(summary: dict[str, Any], reason: str) -> None:
    if reason:
        summary["blocker_reasons"].append(reason)


def _add_blockers(summary: dict[str, Any], reasons: Sequence[str]) -> None:
    for reason in reasons:
        _add_blocker(summary, reason)


def _add_deferred(summary: dict[str, Any], reason: str) -> None:
    if reason:
        summary["deferred_reasons"].append(reason)


def _add_attention(summary: dict[str, Any], item: str) -> None:
    if item:
        summary["operator_attention_items"].append(item)


def _strings(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [str(item) for item in value if item is not None]
    return [str(value)]


def _dedupe(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            result.append(value)
            seen.add(value)
    return result


def _sanitize_process_text(text: str) -> str:
    cleaned = " ".join(text.strip().split())
    if not cleaned:
        return ""
    for marker in LOCAL_ABSOLUTE_PATH_MARKERS:
        cleaned = cleaned.replace(marker, "/<local-path>/")
    return cleaned[:240]


def _path_contains_part(path: Path, part: str) -> bool:
    return part in set(path.parts)


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _custody_flags() -> dict[str, bool | int]:
    return {
        "model_calls": 0,
        "lolla_invoked": False,
        "new_lolla_runs_created": False,
        "semantic_interpretation_generated": False,
        "runner_implemented_as_queue_worker": False,
        "runtime_wired": False,
        "runtime_attachment_default_on": False,
        "archive_hook_changed": False,
        "write_attempted": False,
        "actual_sidecar_write_performed": False,
        "archive_mutated": False,
        "historical_archive_mutated": False,
        "resolver_refs_approved": False,
        "product_proof": False,
        "human_validated": False,
        "answer_quality_scored": False,
        "advice_correctness_validated": False,
        "agent_action_authorized": False,
        "automatic_action_authorized": False,
    }


def _utc_now() -> str:
    return _dt.datetime.now(tz=_dt.timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00",
        "Z",
    )
