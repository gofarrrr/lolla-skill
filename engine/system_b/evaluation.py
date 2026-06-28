"""Deterministic run-readiness evaluation artifact for archived Lolla runs.

This artifact checks the run envelope: files, schemas, custody links, health
signals, and caller policy consistency. It does not score advice quality.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import shutil
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .agent_result import AGENT_RESULT_SCHEMA_VERSION, CALLER_ACTIONS
from .capture_adequacy import (
    CAPTURE_ADEQUACY_SCHEMA_VERSION,
    capture_adequacy_from_artifacts,
)
from .extraction_adequacy_report import (
    EXTRACTION_ADEQUACY_REPORT_SCHEMA_VERSION,
    extraction_adequacy_report_from_artifacts,
)
from .provider_boundary_health import PROVIDER_BOUNDARY_HEALTH_SCHEMA_VERSION
from .reasoning_trace import REASONING_TRACE_SCHEMA_VERSION


EVALUATION_SCHEMA_VERSION = "lolla.evaluation.v0"
EVALUATION_FILENAME = "evaluation.json"

REQUIRED_ARTIFACTS = (
    "conversation.txt",
    "extraction.json",
    "result.json",
    "revised.txt",
    "memo.md",
    "agent_result.json",
    "reasoning_trace.json",
    "run_events.json",
)

OPTIONAL_ARTIFACTS = (
    "extraction_adequacy_report.json",
    "graph_survival_report.json",
    "graph_survival_report.md",
)

_PROVIDER_BOUNDARY_ONLY_REASON = (
    "provider-boundary warning is contained; conservative policy still requires inspection"
)


def build_evaluation(
    run_dir: Path,
    *,
    run_id: str,
    case_id: str,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build deterministic readiness checks for an archived run directory."""

    run_dir = Path(run_dir)
    extraction = _read_json_object(run_dir / "extraction.json")
    result = _read_json_object(run_dir / "result.json")
    agent_result = _read_json_object(run_dir / "agent_result.json")
    reasoning_trace = _read_json_object(run_dir / "reasoning_trace.json")
    run_health = _mapping(result.get("run_health"))
    provider_health = _mapping(
        run_health.get("provider_boundary_health")
        or agent_result.get("provider_boundary_health")
    )
    capture_adequacy = capture_adequacy_from_artifacts(
        extraction=extraction,
        result=result,
    )
    extraction_adequacy_report = extraction_adequacy_report_from_artifacts(run_dir)

    checks: list[dict[str, Any]] = []
    checks.extend(_artifact_presence_checks(run_dir))
    checks.extend(_schema_checks(
        agent_result=agent_result,
        reasoning_trace=reasoning_trace,
        provider_health=provider_health,
        capture_adequacy=capture_adequacy,
        extraction_adequacy_report=extraction_adequacy_report,
    ))
    checks.extend(_agent_policy_checks(agent_result=agent_result, run_health=run_health, provider_health=provider_health))
    checks.extend(_reasoning_trace_checks(run_dir=run_dir, reasoning_trace=reasoning_trace))
    checks.extend(_capture_adequacy_checks(capture_adequacy=capture_adequacy))
    checks.extend(_extraction_adequacy_checks(report=extraction_adequacy_report))
    checks.extend(_hygiene_checks(run_health=run_health))
    checks.extend(_provider_boundary_checks(agent_result=agent_result, provider_health=provider_health))
    checks.extend(_archive_readiness_checks(run_dir=run_dir, agent_result=agent_result))

    summary = _summary(checks)
    overall = _overall(summary)
    return {
        "schema_version": EVALUATION_SCHEMA_VERSION,
        "run_id": run_id,
        "case_id": case_id,
        "created_at": created_at or _utc_now_iso(),
        "overall": overall,
        "caller_readiness": _caller_readiness(
            overall=overall,
            agent_result=agent_result,
        ),
        "checks": checks,
        "summary": summary,
        "scope": {
            "artifact": "run_readiness",
            "advice_quality_scored": False,
            "model_calls": 0,
            "llm_judge_used": False,
        },
    }


def write_evaluation(
    run_dir: Path,
    *,
    run_id: str,
    case_id: str,
    created_at: str | None = None,
    tmp_copy_path: Path | None = None,
) -> tuple[Path, dict[str, Any]]:
    """Write ``evaluation.json`` and optionally copy it to an in-flight path."""

    run_dir = Path(run_dir)
    payload = build_evaluation(
        run_dir,
        run_id=run_id,
        case_id=case_id,
        created_at=created_at,
    )
    path = run_dir / EVALUATION_FILENAME
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if tmp_copy_path is not None:
        tmp_copy_path = Path(tmp_copy_path)
        tmp_copy_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, tmp_copy_path)
    return path, payload


def _artifact_presence_checks(run_dir: Path) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for filename in REQUIRED_ARTIFACTS:
        exists = (run_dir / filename).is_file()
        checks.append(
            _check(
                id=f"artifact_required_{filename.replace('.', '_')}",
                status="pass" if exists else "fail",
                severity="info" if exists else "blocking",
                message=(
                    f"Required artifact {filename} is present."
                    if exists
                    else f"Required artifact {filename} is missing."
                ),
                artifact=filename,
            )
        )
    for filename in OPTIONAL_ARTIFACTS:
        exists = (run_dir / filename).is_file()
        checks.append(
            _check(
                id=f"artifact_optional_{filename.replace('.', '_')}",
                status="pass" if exists else "warn",
                severity="info" if exists else "warning",
                message=(
                    f"Optional artifact {filename} is present."
                    if exists
                    else f"Optional artifact {filename} is unavailable."
                ),
                artifact=filename,
            )
        )
    return checks


def _schema_checks(
    *,
    agent_result: Mapping[str, Any],
    reasoning_trace: Mapping[str, Any],
    provider_health: Mapping[str, Any],
    capture_adequacy: Mapping[str, Any],
    extraction_adequacy_report: Mapping[str, Any],
) -> list[dict[str, Any]]:
    checks = [
        _schema_check(
            id="agent_result_schema_version",
            artifact="agent_result.json",
            observed=_text(agent_result.get("schema_version")),
            expected=AGENT_RESULT_SCHEMA_VERSION,
        ),
        _schema_check(
            id="reasoning_trace_schema_version",
            artifact="reasoning_trace.json",
            observed=_text(reasoning_trace.get("schema_version")),
            expected=REASONING_TRACE_SCHEMA_VERSION,
        ),
    ]
    observed_provider_schema = _text(provider_health.get("schema_version"))
    if observed_provider_schema:
        checks.append(
            _schema_check(
                id="provider_boundary_health_schema_version",
                artifact="result.json",
                observed=observed_provider_schema,
                expected=PROVIDER_BOUNDARY_HEALTH_SCHEMA_VERSION,
            )
        )
    else:
        checks.append(
            _check(
                id="provider_boundary_health_schema_version",
                status="warn",
                severity="warning",
                message="Provider-boundary health metadata is not present.",
                artifact="result.json",
            )
        )
    observed_capture_schema = _text(capture_adequacy.get("schema_version"))
    if observed_capture_schema:
        checks.append(
            _schema_check(
                id="capture_adequacy_schema_version",
                artifact="extraction.json",
                observed=observed_capture_schema,
                expected=CAPTURE_ADEQUACY_SCHEMA_VERSION,
            )
        )
    else:
        checks.append(
            _check(
                id="capture_adequacy_schema_version",
                status="warn",
                severity="warning",
                message="Capture adequacy metadata is not present.",
                artifact="extraction.json",
            )
        )
    observed_extraction_adequacy_schema = _text(
        extraction_adequacy_report.get("schema_version")
    )
    if observed_extraction_adequacy_schema:
        checks.append(
            _schema_check(
                id="extraction_adequacy_report_schema_version",
                artifact="extraction_adequacy_report.json",
                observed=observed_extraction_adequacy_schema,
                expected=EXTRACTION_ADEQUACY_REPORT_SCHEMA_VERSION,
            )
        )
    else:
        checks.append(
            _check(
                id="extraction_adequacy_report_schema_version",
                status="warn",
                severity="warning",
                message="Extraction adequacy report is not present.",
                artifact="extraction_adequacy_report.json",
            )
        )
    return checks


def _agent_policy_checks(
    *,
    agent_result: Mapping[str, Any],
    run_health: Mapping[str, Any],
    provider_health: Mapping[str, Any],
) -> list[dict[str, Any]]:
    status = _text(agent_result.get("status"))
    caller_action = _text(agent_result.get("caller_action"))
    risk_mode = _text(agent_result.get("risk_mode"))
    checks = [
        _check(
            id="caller_action_valid",
            status="pass" if caller_action in CALLER_ACTIONS else "fail",
            severity="info" if caller_action in CALLER_ACTIONS else "blocking",
            message=(
                f"caller_action is valid: {caller_action}."
                if caller_action in CALLER_ACTIONS
                else f"caller_action is invalid: {caller_action or 'missing'}."
            ),
            artifact="agent_result.json",
        )
    ]

    conservative_required = status in {"partial", "degraded", "incomplete"}
    checks.append(
        _check(
            id="non_ok_status_conservative",
            status=(
                "pass"
                if not conservative_required or caller_action == "do_not_use_run_degraded"
                else "fail"
            ),
            severity=(
                "info"
                if not conservative_required or caller_action == "do_not_use_run_degraded"
                else "blocking"
            ),
            message=(
                "Partial/degraded/incomplete status remains conservative."
                if conservative_required and caller_action == "do_not_use_run_degraded"
                else "Run status does not require degraded caller action."
                if not conservative_required
                else "Partial/degraded/incomplete status did not remain conservative."
            ),
            artifact="agent_result.json",
        )
    )

    if risk_mode == "high_stakes" and status == "ok":
        checks.append(
            _check(
                id="high_stakes_clean_policy",
                status="pass" if caller_action == "ask_user_first" else "fail",
                severity="info" if caller_action == "ask_user_first" else "blocking",
                message=(
                    "High-stakes clean run asks the user first."
                    if caller_action == "ask_user_first"
                    else "High-stakes clean run did not ask the user first."
                ),
                artifact="agent_result.json",
            )
        )
    if risk_mode == "high_stakes":
        if status == "ok":
            reliance_ok = caller_action == "ask_user_first"
            message = (
                "High-stakes mode keeps reliance conservative through caller_action ask_user_first; "
                "a human or domain-qualified reviewer must inspect before relying, and this "
                "run-readiness check does not authorize action."
                if reliance_ok
                else "High-stakes mode did not keep reliance conservative through caller_action ask_user_first."
            )
        else:
            reliance_ok = caller_action == "do_not_use_run_degraded"
            message = (
                "High-stakes mode does not override degraded or incomplete run state; "
                "caller_action do_not_use_run_degraded blocks reliance until the run is resolved."
                if reliance_ok
                else "High-stakes mode did not preserve degraded-run caller blocking."
            )
        checks.append(
            _check(
                id="risk_mode_reliance_policy",
                status="pass" if reliance_ok else "fail",
                severity="info" if reliance_ok else "blocking",
                message=message,
                artifact="agent_result.json",
            )
        )

    if _text(provider_health.get("status")) == "warning_contained":
        pure_provider_warning = _provider_boundary_only_partial(run_health)
        expected_reason = _PROVIDER_BOUNDARY_ONLY_REASON if pure_provider_warning else ""
        reason_ok = (
            not pure_provider_warning
            or _text(agent_result.get("status_reason")) == expected_reason
        )
        acceptable_statuses = (
            {"partial"}
            if pure_provider_warning
            else {"partial", "degraded", "incomplete"}
        )
        conservative_ok = (
            status in acceptable_statuses
            and caller_action == "do_not_use_run_degraded"
        )
        checks.append(
            _check(
                id="provider_boundary_contained_policy",
                status="pass" if conservative_ok and reason_ok else "fail",
                severity="info" if conservative_ok and reason_ok else "blocking",
                message=(
                    "Contained provider-boundary warning follows PR7B conservative policy."
                    if conservative_ok and reason_ok
                    else "Contained provider-boundary warning does not follow PR7B conservative policy."
                ),
                artifact="agent_result.json",
            )
        )
    return checks


def _reasoning_trace_checks(
    *,
    run_dir: Path,
    reasoning_trace: Mapping[str, Any],
) -> list[dict[str, Any]]:
    artifacts = [
        _mapping(item)
        for item in _list(reasoning_trace.get("artifacts"))
        if isinstance(item, Mapping)
    ]
    missing_artifacts = {
        _text(_mapping(item).get("path"))
        for item in _list(reasoning_trace.get("missing_artifacts"))
        if isinstance(item, Mapping)
    }
    artifact_paths = {_text(item.get("path")) for item in artifacts}
    checks = [
        _check(
            id="reasoning_trace_indexes_agent_result",
            status="pass" if "agent_result.json" in artifact_paths else "fail",
            severity="info" if "agent_result.json" in artifact_paths else "blocking",
            message=(
                "reasoning_trace.json indexes agent_result.json."
                if "agent_result.json" in artifact_paths
                else "reasoning_trace.json does not index agent_result.json."
            ),
            artifact="reasoning_trace.json",
        )
    ]

    unrecorded_missing = [
        filename
        for filename in REQUIRED_ARTIFACTS
        if not (run_dir / filename).is_file()
        and filename not in missing_artifacts
        and filename != "reasoning_trace.json"
    ]
    checks.append(
        _check(
            id="reasoning_trace_records_missing_required_artifacts",
            status="pass" if not unrecorded_missing else "fail",
            severity="info" if not unrecorded_missing else "blocking",
            message=(
                "Missing required artifacts are recorded or not missing."
                if not unrecorded_missing
                else "Missing required artifacts were not recorded: "
                + ", ".join(unrecorded_missing)
            ),
            artifact="reasoning_trace.json",
        )
    )

    hash_failures: list[str] = []
    for item in artifacts:
        relative = _text(item.get("path"))
        if not relative:
            continue
        path = run_dir / relative
        if not path.is_file():
            hash_failures.append(f"{relative}: missing")
            continue
        expected = _text(item.get("sha256"))
        if expected and expected != _sha256_uri(path):
            hash_failures.append(f"{relative}: sha256 mismatch")
    checks.append(
        _check(
            id="reasoning_trace_artifact_hashes_match",
            status="pass" if not hash_failures else "fail",
            severity="info" if not hash_failures else "blocking",
            message=(
                "Indexed artifact hashes match existing files."
                if not hash_failures
                else "Indexed artifact hash problems: " + "; ".join(hash_failures)
            ),
            artifact="reasoning_trace.json",
        )
    )
    return checks


def _capture_adequacy_checks(
    *,
    capture_adequacy: Mapping[str, Any],
) -> list[dict[str, Any]]:
    if not capture_adequacy:
        return [
            _check(
                id="capture_adequacy_status",
                status="warn",
                severity="warning",
                message="Capture adequacy metadata is missing; inspect older archive manually.",
                artifact="extraction.json",
            )
        ]
    status = _text(capture_adequacy.get("status")) or "unknown"
    omitted = _safe_int(capture_adequacy.get("omitted_turn_count"))
    if status == "good":
        check_status = "pass"
        severity = "info"
        message = "Capture adequacy is good."
    elif status == "warn":
        check_status = "warn"
        severity = "warning"
        message = f"Capture adequacy is warning-level; omitted_turn_count={omitted}."
    elif status == "critical":
        check_status = "fail"
        severity = "blocking"
        message = "Capture adequacy is critical."
    else:
        check_status = "warn"
        severity = "warning"
        message = f"Capture adequacy status is {status}."
    return [
        _check(
            id="capture_adequacy_status",
            status=check_status,
            severity=severity,
            message=message,
            artifact="extraction.json",
        )
    ]


def _extraction_adequacy_checks(*, report: Mapping[str, Any]) -> list[dict[str, Any]]:
    if not report:
        return [
            _check(
                id="extraction_adequacy_status",
                status="warn",
                severity="warning",
                message="Extraction adequacy report is missing; inspect older archive manually.",
                artifact="extraction_adequacy_report.json",
            )
        ]
    status = _text(report.get("adequacy_status")) or "unknown"
    if status == "good":
        check_status = "pass"
        severity = "info"
        message = "Extraction/provenance adequacy report is good."
    elif status == "warn":
        check_status = "warn"
        severity = "warning"
        message = "Extraction/provenance adequacy report is warning-level."
    elif status == "critical":
        check_status = "fail"
        severity = "blocking"
        message = "Extraction/provenance adequacy report is critical."
    else:
        check_status = "warn"
        severity = "warning"
        message = f"Extraction/provenance adequacy status is {status}."
    return [
        _check(
            id="extraction_adequacy_status",
            status=check_status,
            severity=severity,
            message=message,
            artifact="extraction_adequacy_report.json",
        )
    ]


def _hygiene_checks(run_health: Mapping[str, Any]) -> list[dict[str, Any]]:
    product = _text(run_health.get("product_output_health")) or "unknown"
    live = _text(run_health.get("live_output_health")) or "unknown"
    checks = [
        _check(
            id="product_output_health",
            status="fail" if product == "unsafe" else "pass" if product == "clean" else "warn",
            severity="blocking" if product == "unsafe" else "info" if product == "clean" else "warning",
            message=(
                "Product output hygiene is clean."
                if product == "clean"
                else "Product output hygiene is unsafe."
                if product == "unsafe"
                else f"Product output hygiene is {product}."
            ),
            artifact="result.json",
        ),
        _check(
            id="live_output_health",
            status="fail" if live == "unsafe" else "pass" if live == "clean" else "warn",
            severity="blocking" if live == "unsafe" else "info" if live == "clean" else "warning",
            message=(
                "Live output hygiene is clean."
                if live == "clean"
                else "Live output hygiene is unsafe."
                if live == "unsafe"
                else f"Live output hygiene is {live}; inspect before treating live surface as proven clean."
            ),
            artifact="result.json",
        ),
    ]
    return checks


def _provider_boundary_checks(
    *,
    agent_result: Mapping[str, Any],
    provider_health: Mapping[str, Any],
) -> list[dict[str, Any]]:
    status = _text(provider_health.get("status")) or "unknown"
    caller_action = _text(agent_result.get("caller_action"))
    if status == "clean":
        check_status = "pass"
        severity = "info"
        message = "No provider-boundary issue is recorded."
    elif status == "warning_contained":
        check_status = "warn" if caller_action == "do_not_use_run_degraded" else "fail"
        severity = "warning" if caller_action == "do_not_use_run_degraded" else "blocking"
        message = (
            "Contained provider-boundary warning remains conservative under PR7B policy."
            if caller_action == "do_not_use_run_degraded"
            else "Contained provider-boundary warning was not kept conservative."
        )
    elif status == "warning_unknown_persistence":
        check_status = "fail"
        severity = "blocking"
        message = "Provider-boundary warning has unknown persistence status."
    elif status == "confirmed_contamination":
        check_status = "fail"
        severity = "blocking"
        message = "Provider-boundary warning has confirmed output contamination."
    else:
        check_status = "warn"
        severity = "warning"
        message = f"Provider-boundary health status is {status}."
    return [
        _check(
            id="provider_boundary_policy",
            status=check_status,
            severity=severity,
            message=message,
            artifact="agent_result.json",
        )
    ]


def _archive_readiness_checks(
    *,
    run_dir: Path,
    agent_result: Mapping[str, Any],
) -> list[dict[str, Any]]:
    archive_path = _text(_mapping(agent_result.get("artifact_paths")).get("archive"))
    archive_ok = bool(archive_path) and Path(archive_path).exists()
    sidecar_failures = [
        filename
        for filename in ("agent_result.json", "reasoning_trace.json", "memo.md")
        if not (run_dir / filename).is_file()
    ]
    return [
        _check(
            id="archive_path_exists",
            status="pass" if archive_ok else "warn",
            severity="info" if archive_ok else "warning",
            message=(
                "agent_result artifact_paths.archive exists."
                if archive_ok
                else "agent_result artifact_paths.archive is missing or unavailable."
            ),
            artifact="agent_result.json",
        ),
        _check(
            id="advertised_sidecars_exist",
            status="pass" if not sidecar_failures else "fail",
            severity="info" if not sidecar_failures else "blocking",
            message=(
                "Core advertised sidecars exist."
                if not sidecar_failures
                else "Core advertised sidecars are missing: " + ", ".join(sidecar_failures)
            ),
            artifact="agent_result.json",
        ),
    ]


def _provider_boundary_only_partial(run_health: Mapping[str, Any]) -> bool:
    issue_details = [
        _mapping(item)
        for item in _list(run_health.get("issue_details"))
        if isinstance(item, Mapping)
        and _text(_mapping(item).get("severity")) in {"partial", "degraded", "critical"}
    ]
    if issue_details:
        return {
            _text(item.get("code"))
            for item in issue_details
        } == {"vendor_boundary_reasoning_leak"}
    partial_causes = {
        _text(item)
        for item in _list(run_health.get("partial_health_causes"))
        if _text(item)
    }
    if partial_causes:
        return partial_causes == {"vendor_boundary_reasoning_leak"}
    issues = {_text(item) for item in _list(run_health.get("issues")) if _text(item)}
    return issues == {"vendor_boundary_reasoning_leak"}


def _schema_check(*, id: str, artifact: str, observed: str, expected: str) -> dict[str, Any]:
    ok = observed == expected
    return _check(
        id=id,
        status="pass" if ok else "fail",
        severity="info" if ok else "blocking",
        message=(
            f"{artifact} schema_version is {expected}."
            if ok
            else f"{artifact} schema_version is {observed or 'missing'}, expected {expected}."
        ),
        artifact=artifact,
    )


def _check(
    *,
    id: str,
    status: str,
    severity: str,
    message: str,
    artifact: str,
) -> dict[str, Any]:
    return {
        "id": id,
        "status": status,
        "severity": severity,
        "message": message,
        "artifact": artifact,
    }


def _summary(checks: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    summary = {"pass": 0, "warn": 0, "fail": 0, "blocking": 0}
    for check in checks:
        status = _text(check.get("status"))
        severity = _text(check.get("severity"))
        if status in {"pass", "warn", "fail"}:
            summary[status] += 1
        if severity == "blocking":
            summary["blocking"] += 1
    return summary


def _overall(summary: Mapping[str, int]) -> str:
    if int(summary.get("fail") or 0) > 0 or int(summary.get("blocking") or 0) > 0:
        return "fail"
    if int(summary.get("warn") or 0) > 0:
        return "warn"
    return "pass"


def _caller_readiness(*, overall: str, agent_result: Mapping[str, Any]) -> str:
    caller_action = _text(agent_result.get("caller_action"))
    if caller_action == "do_not_use_run_degraded" or overall == "fail":
        return "do_not_use"
    if overall == "warn" or caller_action == "ask_user_first":
        return "inspect_first"
    return "ready"


def _read_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _sha256_uri(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: Any) -> str:
    return str(value or "").strip()


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _utc_now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
