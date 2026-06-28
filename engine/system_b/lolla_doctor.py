"""Read-only local preflight report for Lolla.

The doctor inspects local wiring and optional review-corpus manifest metadata.
It does not run Lolla, call models, load provider clients, read archive payloads,
or mutate archives.
"""
from __future__ import annotations

import json
import os
import subprocess
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .pricing import PRICES_LAST_VERIFIED, lookup_chat_price


DOCTOR_REPORT_SCHEMA_VERSION = "lolla.doctor_report.v0"

DEFAULT_OPENROUTER_MODEL = "google/gemini-3.1-flash-lite"
DEFAULT_ARCHIVE_ROOT = Path("~/.local/share/lolla/runs")

RUNTIME_LANDMARKS = (
    "SKILL.md",
    "engine/system_b",
    "scripts",
)
REQUIRED_HELPERS = (
    "scripts/skill/setup.sh",
    "scripts/skill/run_extract_step.sh",
    "scripts/skill/run_pipeline_step.sh",
)
OPTIONAL_HELPERS = (
    "scripts/export_review_corpus.py",
    "scripts/analyze_review_corpus_evidence_readiness.py",
)
PROVIDER_CREDENTIAL_ENV_VARS = (
    "LOLLA_OPENROUTER_API_KEY",
    "OPENROUTER_API_KEY",
)
OPTIONAL_CREDENTIAL_ENV_VARS = (
    "OPENAI_API_KEY",
)
RELIANCE_COUNT_FIELDS = (
    "risk_mode_counts",
    "risk_mode_reliance_present_counts",
    "risk_mode_reliance_by_risk_mode_counts",
    "risk_mode_reliance_check_status_counts",
)


class DoctorInputError(ValueError):
    """Sanitized doctor input error."""


def build_doctor_report(
    *,
    runtime_root: Path | str | None = None,
    archive_root: Path | str | None = None,
    manifest_path: Path | str | None = None,
    output_path: Path | str | None = None,
    env: Mapping[str, str] | None = None,
    cwd: Path | str | None = None,
    default_runtime_root: Path | str | None = None,
    default_archive_root: Path | str | None = None,
) -> dict[str, Any]:
    """Build a deterministic doctor report without side effects."""

    cwd_path = Path(cwd or Path.cwd())
    env_map = dict(os.environ if env is None else env)
    runtime = _resolve_runtime_root(
        explicit_root=runtime_root,
        cwd=cwd_path,
        default_runtime_root=default_runtime_root,
    )
    archive = _resolve_archive_root(
        explicit_root=archive_root,
        default_archive_root=default_archive_root,
    )
    manifest = _read_manifest(manifest_path)

    checks: list[dict[str, Any]] = [
        _runtime_discovery_check(runtime, cwd_path),
        _archive_root_check(archive, cwd_path),
        _helper_availability_check(runtime, cwd_path),
        _provider_config_check(env_map),
        _cost_telemetry_check(env_map),
        _review_manifest_check(manifest),
        _risk_mode_counts_check(manifest),
        _high_stakes_evidence_check(manifest),
        _output_path_safety_check(output_path=output_path, archive=archive, cwd=cwd_path),
        _archive_mutation_guard_check(output_path=output_path),
        _repo_runtime_boundary_check(runtime),
        _privacy_output_safety_check(),
    ]
    status = _overall_status(checks)
    warnings = sum(1 for check in checks if check["status"] == "warn")
    failures = sum(1 for check in checks if check["status"] == "fail")
    return {
        "schema_version": DOCTOR_REPORT_SCHEMA_VERSION,
        "status": status,
        "checks": checks,
        "summary": {
            "blocking_failures": failures,
            "warnings": warnings,
            "model_calls": 0,
            "archives_mutated": False,
            "would_run_lolla": False,
            "would_spend_tokens": False,
        },
        "custody_flags": {
            "reads_archives": False,
            "reads_archive_payloads": False,
            "reads_manifest_json": bool(manifest_path),
            "writes_archives": False,
            "model_calls": 0,
            "prints_secrets": False,
            "prints_raw_transcript": False,
            "prints_raw_memo": False,
            "prints_raw_revised_answer": False,
        },
    }


def render_doctor_report_json(report: Mapping[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_doctor_report_text(report: Mapping[str, Any]) -> str:
    summary = _mapping(report.get("summary"))
    lines = [
        f"Lolla doctor: {_text(report.get('status'))}",
        (
            "blocking_failures="
            f"{_safe_int(summary.get('blocking_failures'))} "
            f"warnings={_safe_int(summary.get('warnings'))} "
            "model_calls=0 archives_mutated=false"
        ),
        "",
        "Checks:",
    ]
    for check in _checks(report.get("checks")):
        lines.append(
            "- "
            f"{_text(check.get('check_id'))}: "
            f"{_text(check.get('status'))} - "
            f"{_text(check.get('summary'))}"
        )
    return "\n".join(lines) + "\n"


def report_allows_output_write(report: Mapping[str, Any]) -> bool:
    for check in _checks(report.get("checks")):
        if check.get("check_id") == "output.path_safety":
            return check.get("status") != "fail"
    return True


def write_report_output(path: Path | str, payload: str) -> None:
    output = Path(path)
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    except OSError as exc:
        raise DoctorInputError(f"output could not be written:{type(exc).__name__}") from exc


def _runtime_discovery_check(
    runtime: Mapping[str, Any], cwd: Path
) -> dict[str, Any]:
    status = _text(runtime.get("status"))
    root = runtime.get("root")
    explicit = bool(runtime.get("explicit"))
    details = {
        "runtime_root_provided": explicit,
        "discovery_source": _text(runtime.get("source")),
        "path_hint": _safe_path_hint(root, cwd),
        "expected_landmarks": list(RUNTIME_LANDMARKS),
        "missing_landmarks": list(runtime.get("missing_landmarks") or []),
    }
    if status == "missing":
        return _check(
            "runtime.discovery",
            "fail",
            "Lolla runtime root was not discoverable.",
            details,
        )
    if status == "not_directory":
        return _check(
            "runtime.discovery",
            "fail",
            "Runtime root is not a directory.",
            details,
        )
    if runtime.get("missing_landmarks"):
        return _check(
            "runtime.discovery",
            "fail",
            "Runtime root is missing expected Lolla landmarks.",
            details,
        )
    return _check(
        "runtime.discovery",
        "pass",
        "Lolla runtime root is discoverable.",
        details,
    )


def _archive_root_check(archive: Mapping[str, Any], cwd: Path) -> dict[str, Any]:
    state = _text(archive.get("state"))
    explicit = bool(archive.get("explicit"))
    details = {
        "archive_root_provided": explicit,
        "default_used": bool(archive.get("default_used")),
        "path_state": state,
        "path_hint": _safe_path_hint(archive.get("root"), cwd),
        "archive_payloads_read": False,
    }
    if state == "directory":
        return _check(
            "archive_root.discovery",
            "pass",
            "Archive root exists as a directory.",
            details,
        )
    if explicit:
        return _check(
            "archive_root.discovery",
            "fail",
            "Explicit archive root is not a readable directory.",
            details,
        )
    if state == "file":
        return _check(
            "archive_root.discovery",
            "fail",
            "Default archive root resolves to a file.",
            details,
        )
    return _check(
        "archive_root.discovery",
        "warn",
        "Default archive root was not found; doctor did not read archives.",
        details,
    )


def _helper_availability_check(
    runtime: Mapping[str, Any], cwd: Path
) -> dict[str, Any]:
    root = runtime.get("root")
    if not isinstance(root, Path) or runtime.get("missing_landmarks"):
        return _check(
            "helper_scripts.availability",
            "not_applicable",
            "Helper scripts were not checked because runtime discovery failed.",
            {"checked": False},
        )
    missing_required = [
        rel for rel in REQUIRED_HELPERS if not (root / rel).is_file()
    ]
    missing_optional = [
        rel for rel in OPTIONAL_HELPERS if not (root / rel).is_file()
    ]
    details = {
        "runtime_path_hint": _safe_path_hint(root, cwd),
        "required_helpers_present": not missing_required,
        "missing_required_helpers": missing_required,
        "missing_optional_helpers": missing_optional,
    }
    if missing_required:
        return _check(
            "helper_scripts.availability",
            "fail",
            "Required doctor/runtime helper files are missing.",
            details,
        )
    if missing_optional:
        return _check(
            "helper_scripts.availability",
            "warn",
            "Core helpers exist, but optional review-corpus helpers are missing.",
            details,
        )
    return _check(
        "helper_scripts.availability",
        "pass",
        "Expected helper scripts are present.",
        details,
    )


def _provider_config_check(env: Mapping[str, str]) -> dict[str, Any]:
    openrouter_present = any(bool(env.get(name)) for name in PROVIDER_CREDENTIAL_ENV_VARS)
    embedding_present = any(bool(env.get(name)) for name in OPTIONAL_CREDENTIAL_ENV_VARS)
    details = {
        "openrouter_credential_present": openrouter_present,
        "embedding_credential_present": embedding_present,
        "credential_values_printed": False,
        "network_validation": False,
    }
    if openrouter_present:
        return _check(
            "provider_config.presence",
            "pass",
            "Provider configuration presence is inspectable without exposing values.",
            details,
        )
    return _check(
        "provider_config.presence",
        "warn",
        "Provider credential is absent; doctor still made no model calls.",
        details,
    )


def _cost_telemetry_check(env: Mapping[str, str]) -> dict[str, Any]:
    configured_model = _text(env.get("LOLLA_OPENROUTER_MODEL")) or DEFAULT_OPENROUTER_MODEL
    price_known = lookup_chat_price("openrouter", configured_model) is not None
    details = {
        "provider": "openrouter",
        "configured_model": configured_model,
        "cost_estimation_state": "known" if price_known else "unknown",
        "pricing_table_version": PRICES_LAST_VERIFIED,
        "model_calls": 0,
    }
    if price_known:
        return _check(
            "telemetry.cost_readiness",
            "pass",
            "Configured model is known to the local pricing table.",
            details,
        )
    return _check(
        "telemetry.cost_readiness",
        "warn",
        "Configured model is not recognized for local cost estimation.",
        details,
    )


def _review_manifest_check(manifest: Mapping[str, Any]) -> dict[str, Any]:
    details = {
        "manifest_supplied": bool(manifest.get("supplied")),
        "manifest_read": bool(manifest.get("payload")),
        "manifest_path_included": False,
    }
    if not manifest.get("supplied"):
        return _check(
            "review_corpus.manifest_readable",
            "warn",
            "No review-corpus manifest supplied.",
            details,
        )
    if manifest.get("error"):
        details["error"] = manifest.get("error")
        return _check(
            "review_corpus.manifest_readable",
            "fail",
            "Supplied review-corpus manifest could not be parsed.",
            details,
        )
    payload = _mapping(manifest.get("payload"))
    details.update(
        {
            "schema_version": _text(payload.get("schema_version")),
            "record_schema_version": _text(payload.get("record_schema_version")),
            "record_count": _safe_int(payload.get("record_count")),
        }
    )
    return _check(
        "review_corpus.manifest_readable",
        "pass",
        "Supplied review-corpus manifest parsed as JSON object.",
        details,
    )


def _risk_mode_counts_check(manifest: Mapping[str, Any]) -> dict[str, Any]:
    payload = manifest.get("payload")
    if not manifest.get("supplied"):
        return _check(
            "risk_mode.reliance_counts",
            "not_applicable",
            "Reliance counts require a review-corpus manifest.",
            {"manifest_supplied": False},
        )
    if not isinstance(payload, Mapping):
        return _check(
            "risk_mode.reliance_counts",
            "not_applicable",
            "Reliance counts were not checked because manifest parsing failed.",
            {"manifest_supplied": True},
        )
    missing = [field for field in RELIANCE_COUNT_FIELDS if field not in payload]
    if missing:
        return _check(
            "risk_mode.reliance_counts",
            "warn",
            "Manifest lacks PR44 reliance aggregate fields.",
            {
                "readiness_state": "insufficient_manifest_fields",
                "missing_manifest_fields": missing,
            },
        )
    counts: dict[str, dict[str, int]] = {}
    invalid_fields: list[str] = []
    for field in RELIANCE_COUNT_FIELDS:
        field_counts, valid = _strict_count_mapping(payload.get(field))
        counts[field] = field_counts
        if not valid:
            invalid_fields.append(field)
    if invalid_fields:
        return _check(
            "risk_mode.reliance_counts",
            "fail",
            "Manifest reliance count fields have invalid shapes.",
            {
                "invalid_manifest_fields": invalid_fields,
            },
        )
    return _check(
        "risk_mode.reliance_counts",
        "pass",
        "Risk-mode reliance aggregate counts are visible.",
        counts,
    )


def _high_stakes_evidence_check(manifest: Mapping[str, Any]) -> dict[str, Any]:
    payload = manifest.get("payload")
    if not manifest.get("supplied"):
        return _check(
            "high_stakes.evidence_visibility",
            "not_applicable",
            "High-stakes evidence visibility requires a review-corpus manifest.",
            {"manifest_supplied": False},
        )
    if not isinstance(payload, Mapping):
        return _check(
            "high_stakes.evidence_visibility",
            "not_applicable",
            "High-stakes evidence visibility was not checked because manifest parsing failed.",
            {"manifest_supplied": True},
        )
    by_risk_mode, valid = _strict_count_mapping(
        payload.get("risk_mode_reliance_by_risk_mode_counts")
    )
    if not valid:
        return _check(
            "high_stakes.evidence_visibility",
            "warn",
            "Manifest cannot support a high-stakes evidence claim.",
            {"readiness_state": "insufficient_manifest_fields"},
        )
    high_stakes_count = _safe_int(by_risk_mode.get("high_stakes|true"))
    details = {
        "high_stakes_reliance_present_count": high_stakes_count,
        "answer_quality_judged": False,
        "high_stakes_use_approved": False,
    }
    if high_stakes_count > 0:
        return _check(
            "high_stakes.evidence_visibility",
            "pass",
            "Manifest explicitly reports high-stakes reliance-present records.",
            details,
        )
    return _check(
        "high_stakes.evidence_visibility",
        "warn",
        "No high-stakes reliance-present evidence is visible in the manifest.",
        details,
    )


def _output_path_safety_check(
    *,
    output_path: Path | str | None,
    archive: Mapping[str, Any],
    cwd: Path,
) -> dict[str, Any]:
    if not output_path:
        return _check(
            "output.path_safety",
            "pass",
            "No output path supplied; report will be printed to stdout.",
            {"output_path_supplied": False},
        )
    output = _expand_path(output_path)
    details = {
        "output_path_supplied": True,
        "output_path_hint": _safe_path_hint(output, cwd),
        "inside_archive_root": False,
    }
    if output.exists() and output.is_dir():
        return _check(
            "output.path_safety",
            "fail",
            "Output path points to a directory.",
            details,
        )
    archive_root = archive.get("root")
    if isinstance(archive_root, Path) and archive.get("state") == "directory":
        inside = _is_same_or_inside(output, archive_root)
        details["inside_archive_root"] = inside
        if inside:
            return _check(
                "output.path_safety",
                "fail",
                "Output path resolves inside the archive root.",
                details,
            )
    return _check(
        "output.path_safety",
        "pass",
        "Output path is not inside the archive root.",
        details,
    )


def _archive_mutation_guard_check(output_path: Path | str | None) -> dict[str, Any]:
    return _check(
        "archive_mutation.guard",
        "pass",
        "Doctor declares zero archive writes and no archive repair behavior.",
        {
            "archives_mutated": False,
            "writes_archive_payloads": False,
            "repairs_archives": False,
            "external_output_requested": bool(output_path),
        },
    )


def _repo_runtime_boundary_check(runtime: Mapping[str, Any]) -> dict[str, Any]:
    root = runtime.get("root")
    if not isinstance(root, Path) or not (root / ".git").exists():
        return _check(
            "repo_runtime.boundary",
            "not_applicable",
            "Runtime root is not a git working tree.",
            {"git_checked": False},
        )
    try:
        result = subprocess.run(
            [
                "git",
                "status",
                "--porcelain",
                "--",
                "SKILL.md",
                "engine",
                "scripts",
                "observatory",
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return _check(
            "repo_runtime.boundary",
            "warn",
            "Runtime git boundary status could not be checked.",
            {"git_checked": False, "error": type(exc).__name__},
        )
    changed_count = len([line for line in result.stdout.splitlines() if line.strip()])
    details = {
        "git_checked": True,
        "runtime_surface_dirty": changed_count > 0,
        "changed_runtime_surface_count": changed_count,
        "checked_paths": ["SKILL.md", "engine", "scripts", "observatory"],
    }
    if result.returncode != 0:
        details["git_status_returncode"] = result.returncode
        return _check(
            "repo_runtime.boundary",
            "warn",
            "Runtime git boundary status returned a non-zero code.",
            details,
        )
    if changed_count:
        return _check(
            "repo_runtime.boundary",
            "warn",
            "Runtime surface has local changes.",
            details,
        )
    return _check(
        "repo_runtime.boundary",
        "pass",
        "Runtime surface has no local changes in checked paths.",
        details,
    )


def _privacy_output_safety_check() -> dict[str, Any]:
    return _check(
        "privacy.output_safety",
        "pass",
        "Doctor output contains safe-to-print metadata only.",
        {
            "prints_credential_values": False,
            "prints_raw_transcript": False,
            "prints_raw_memo": False,
            "prints_raw_revised_answer": False,
            "prints_provider_reasoning": False,
            "safe_to_print_details_only": True,
        },
    )


def _resolve_runtime_root(
    *,
    explicit_root: Path | str | None,
    cwd: Path,
    default_runtime_root: Path | str | None,
) -> dict[str, Any]:
    if explicit_root:
        root = _expand_path(explicit_root)
        return _runtime_candidate(root=root, explicit=True, source="explicit")
    if default_runtime_root:
        root = _expand_path(default_runtime_root)
        candidate = _runtime_candidate(root=root, explicit=False, source="script")
        if candidate["status"] != "missing":
            return candidate
    for candidate_root in (cwd, *cwd.parents):
        candidate = _runtime_candidate(
            root=candidate_root,
            explicit=False,
            source="cwd_parent",
        )
        if candidate["status"] == "ok":
            return candidate
    for candidate_root in _installed_runtime_candidates(cwd):
        candidate = _runtime_candidate(
            root=candidate_root,
            explicit=False,
            source="installed_candidate",
        )
        if candidate["status"] == "ok":
            return candidate
    return {
        "root": None,
        "explicit": False,
        "source": "not_found",
        "status": "missing",
        "missing_landmarks": list(RUNTIME_LANDMARKS),
    }


def _runtime_candidate(root: Path, explicit: bool, source: str) -> dict[str, Any]:
    if not root.exists():
        return {
            "root": root,
            "explicit": explicit,
            "source": source,
            "status": "missing",
            "missing_landmarks": list(RUNTIME_LANDMARKS),
        }
    if not root.is_dir():
        return {
            "root": root,
            "explicit": explicit,
            "source": source,
            "status": "not_directory",
            "missing_landmarks": list(RUNTIME_LANDMARKS),
        }
    missing = [rel for rel in RUNTIME_LANDMARKS if not (root / rel).exists()]
    return {
        "root": root,
        "explicit": explicit,
        "source": source,
        "status": "ok",
        "missing_landmarks": missing,
    }


def _installed_runtime_candidates(cwd: Path) -> list[Path]:
    home = Path.home()
    return [
        cwd / ".codex/skills/lolla",
        cwd / ".claude/skills/lolla",
        home / ".codex/skills/lolla",
        home / ".claude/skills/lolla",
    ]


def _resolve_archive_root(
    *,
    explicit_root: Path | str | None,
    default_archive_root: Path | str | None,
) -> dict[str, Any]:
    explicit = bool(explicit_root)
    root = _expand_path(
        explicit_root
        if explicit_root
        else (default_archive_root or DEFAULT_ARCHIVE_ROOT)
    )
    if root.is_dir():
        state = "directory"
    elif root.is_file():
        state = "file"
    elif root.exists():
        state = "other"
    else:
        state = "missing"
    return {
        "root": root,
        "explicit": explicit,
        "default_used": not explicit,
        "state": state,
    }


def _read_manifest(manifest_path: Path | str | None) -> dict[str, Any]:
    if not manifest_path:
        return {"supplied": False, "payload": None, "error": ""}
    path = _expand_path(manifest_path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "supplied": True,
            "payload": None,
            "error": "manifest is not valid JSON",
        }
    except OSError as exc:
        return {
            "supplied": True,
            "payload": None,
            "error": f"manifest could not be read:{type(exc).__name__}",
        }
    if not isinstance(payload, dict):
        return {
            "supplied": True,
            "payload": None,
            "error": "manifest is not a JSON object",
        }
    return {"supplied": True, "payload": payload, "error": ""}


def _strict_count_mapping(value: Any) -> tuple[dict[str, int], bool]:
    if not isinstance(value, Mapping):
        return {}, False
    counts: dict[str, int] = {}
    for key, raw_count in value.items():
        if not isinstance(key, str) or not key:
            return {}, False
        if isinstance(raw_count, bool) or not isinstance(raw_count, int):
            return {}, False
        counts[key] = raw_count
    return counts, True


def _check(
    check_id: str,
    status: str,
    summary: str,
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "status": status,
        "summary": summary,
        "details": dict(details or {}),
        "safe_to_print": True,
    }


def _overall_status(checks: list[Mapping[str, Any]]) -> str:
    statuses = {_text(check.get("status")) for check in checks}
    if "fail" in statuses:
        return "fail"
    if "warn" in statuses:
        return "warn"
    return "pass"


def _expand_path(path: Path | str) -> Path:
    return Path(path).expanduser()


def _safe_path_hint(path: Any, cwd: Path) -> str:
    if not isinstance(path, Path):
        return ""
    try:
        resolved = path.resolve(strict=False)
    except OSError:
        resolved = path.absolute()
    try:
        cwd_resolved = cwd.resolve(strict=False)
        rel = resolved.relative_to(cwd_resolved)
        return "." if str(rel) == "." else str(rel)
    except ValueError:
        pass
    try:
        home = Path.home().resolve(strict=False)
        rel = resolved.relative_to(home)
        return "~" if str(rel) == "." else f"~/{rel}"
    except ValueError:
        return path.name or "."


def _is_same_or_inside(path: Path, parent: Path) -> bool:
    try:
        path_resolved = path.resolve(strict=False)
        parent_resolved = parent.resolve(strict=False)
        if path_resolved == parent_resolved:
            return True
        path_resolved.relative_to(parent_resolved)
        return True
    except (OSError, ValueError):
        return False


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _checks(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _text(value: Any) -> str:
    return str(value or "").strip()
