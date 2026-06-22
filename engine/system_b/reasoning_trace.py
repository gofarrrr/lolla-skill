"""Archive-time ReasoningTrace manifest builder.

This module turns an archived Lolla run directory into a local custody
manifest. It deliberately indexes raw artifacts by path and hash rather than
duplicating conversation or memo text into the trace itself.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


REASONING_TRACE_SCHEMA_VERSION = "lolla.reasoning_trace.v0.1"
REASONING_TRACE_FILENAME = "reasoning_trace.json"

ARTIFACT_ROLES: dict[str, str] = {
    "conversation.txt": "source_conversation",
    "extraction.json": "decision_structure",
    "result.json": "pipeline_result",
    "revised.txt": "reconsidered_position",
    "memo.md": "decision_memo",
    "memo_note.json": "decision_memo_fields",
    "gapcheck.txt": "pressure_check_summary",
    "gapcheck_lanes.json": "pressure_check_state",
    "v60_ledger_skeleton.json": "private_enrichment_ledger_skeleton",
    "v60_ledger.json": "private_enrichment_ledger",
    "pre_step6_shadow_portfolio.json": "shadow_portfolio_trace",
    "pre_step6_private_table.json": "private_reasoning_table",
    "pre_step6_private_table.md": "private_reasoning_table_markdown",
    "pre_step6_private_table_ledger.json": "private_reasoning_table_ledger",
    "live_transcript.txt": "live_product_surface",
}

CONTENT_TYPES = {
    ".json": "application/json",
    ".md": "text/markdown",
    ".txt": "text/plain",
}


def build_reasoning_trace(
    run_dir: Path,
    *,
    run_id: str,
    case_id: str,
    fingerprint: str,
    how_matched: str,
    files_copied: Sequence[str],
    files_missing: Sequence[str],
    manifest: Mapping[str, Any],
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build a JSON-safe ReasoningTrace payload for an archived run."""
    run_dir = Path(run_dir)
    extraction = _read_json_object(run_dir / "extraction.json")
    result = _read_json_object(run_dir / "result.json")
    artifacts = _artifact_records(run_dir=run_dir, filenames=files_copied)
    missing_artifacts = _missing_artifact_records(files_missing)

    trace: dict[str, Any] = {
        "schema_version": REASONING_TRACE_SCHEMA_VERSION,
        "trace_id": f"trace_{run_id}",
        "created_at": created_at or _utc_now_iso(),
        "source": {
            "adapter": "lolla_skill",
            "capture_hook": "archive_run",
            "storage_mode": "local_archive",
            "project_root": None,
        },
        "participants": _participants(extraction=extraction, result=result),
        "privacy": {
            "mode": "local_only",
            "raw_transcript_saved": (run_dir / "conversation.txt").exists(),
            "summary_saved": bool(extraction),
            "retention_days": None,
            "raw_text_duplicated_in_trace": False,
            "external_egress_by_trace_builder": False,
        },
        "case": {
            "case_id": case_id,
            "run_id": run_id,
            "decision_situation": _decision_situation(extraction),
            "fingerprint": fingerprint,
            "how_matched": how_matched,
            "run_count": _safe_int(manifest.get("run_count")),
            "case_manifest_ref": "../.case-manifest.json",
        },
        "content_hashes": {
            "conversation_sha256": _sha256_uri_or_none(run_dir / "conversation.txt"),
            "result_sha256": _sha256_uri_or_none(run_dir / "result.json"),
            "artifact_index_sha256": _object_sha256_uri(artifacts),
        },
        "capture": _capture_summary(extraction=extraction, result=result),
        "process": {
            "run_health": _mapping(result.get("run_health")),
            "audit_summary": _audit_summary(result),
            "pressure_check": _pressure_check(result),
            "private_custody": _private_custody(result=result, run_dir=run_dir),
            "usage": _usage_summary(result),
        },
        "artifacts": artifacts,
        "missing_artifacts": missing_artifacts,
        "candidate_commitments": [],
        "decision_packets": [],
        "outcome_reviews": [],
        "model_calls": [],
        "tool_calls": [],
    }
    return trace


def write_reasoning_trace(
    run_dir: Path,
    *,
    run_id: str,
    case_id: str,
    fingerprint: str,
    how_matched: str,
    files_copied: Sequence[str],
    files_missing: Sequence[str],
    manifest: Mapping[str, Any],
    created_at: str | None = None,
) -> tuple[Path, dict[str, Any]]:
    """Write ``reasoning_trace.json`` into ``run_dir`` and return path/payload."""
    payload = build_reasoning_trace(
        run_dir,
        run_id=run_id,
        case_id=case_id,
        fingerprint=fingerprint,
        how_matched=how_matched,
        files_copied=files_copied,
        files_missing=files_missing,
        manifest=manifest,
        created_at=created_at,
    )
    path = Path(run_dir) / REASONING_TRACE_FILENAME
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path, payload


def _artifact_records(*, run_dir: Path, filenames: Sequence[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for filename in filenames:
        path = run_dir / filename
        if not path.exists() or not path.is_file():
            continue
        stat = path.stat()
        records.append(
            {
                "path": filename,
                "role": _artifact_role(filename),
                "sha256": _sha256_uri(path),
                "bytes": stat.st_size,
                "content_type": CONTENT_TYPES.get(path.suffix.lower(), "application/octet-stream"),
            }
        )
    return records


def _missing_artifact_records(filenames: Sequence[str]) -> list[dict[str, str]]:
    return [
        {
            "path": filename,
            "role": _artifact_role(filename),
        }
        for filename in filenames
    ]


def _artifact_role(filename: str) -> str:
    return ARTIFACT_ROLES.get(filename, "archived_artifact")


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


def _sha256_uri_or_none(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    return _sha256_uri(path)


def _object_sha256_uri(value: Any) -> str:
    canonical = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(canonical).hexdigest()}"


def _utc_now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _participants(*, extraction: Mapping[str, Any], result: Mapping[str, Any]) -> list[str]:
    speakers: list[str] = []
    seen: set[str] = set()
    for payload in (extraction, result):
        turns = _turns(payload)
        for turn in turns:
            speaker = str(_mapping(turn).get("speaker") or "").strip()
            if speaker and speaker not in seen:
                seen.add(speaker)
                speakers.append(speaker)
    return speakers


def _turns(payload: Mapping[str, Any]) -> list[Any]:
    extraction = _mapping(payload.get("extraction"))
    turns = extraction.get("turns")
    return turns if isinstance(turns, list) else []


def _decision_situation(extraction_payload: Mapping[str, Any]) -> str:
    extraction = _mapping(extraction_payload.get("extraction"))
    return str(extraction.get("decision_situation") or "").strip()


def _capture_summary(
    *,
    extraction: Mapping[str, Any],
    result: Mapping[str, Any],
) -> dict[str, Any]:
    capture_manifest = _mapping(extraction.get("capture_manifest"))
    capture_health = str(extraction.get("capture_health") or "").strip()
    if not capture_health:
        capture_health = str(_mapping(result.get("run_health")).get("capture") or "").strip()
    return {
        "capture_health": capture_health or "unknown",
        "capture_manifest": dict(capture_manifest),
        "decision_structure": _decision_structure_summary(extraction),
    }


def _decision_structure_summary(extraction_payload: Mapping[str, Any]) -> dict[str, Any]:
    extraction = _mapping(extraction_payload.get("extraction"))
    return {
        "live_constraint_count": len(_list(extraction.get("live_constraints"))),
        "reasoning_passage_count": len(_list(extraction.get("reasoning_passages"))),
        "dropped_thread_count": len(_list(extraction.get("dropped_threads"))),
        "original_framing_present": bool(str(extraction.get("original_framing") or "").strip()),
        "synthesized_position_present": bool(
            str(extraction.get("synthesized_position") or "").strip()
        ),
    }


def _audit_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    audit = _mapping(result.get("audit_summary"))
    deep_results = [_mapping(item) for item in _list(audit.get("deep_check_results"))]
    route_trace = _mapping(audit.get("route_trace"))
    return {
        "triggered_tendency_count": len(_list(audit.get("triggered_tendencies"))),
        "deep_check_count": len(deep_results),
        "detected_tendency_count": sum(1 for item in deep_results if item.get("detected")),
        "routing_decision_count": len(_list(audit.get("routing_decisions"))),
        "boundary_call_count": _safe_int(audit.get("boundary_call_count")),
        "warning_count": len(_list(audit.get("warnings"))),
        "route_trace_schema_version": str(route_trace.get("schema_version") or ""),
        "route_trace_summary": dict(_mapping(route_trace.get("summary"))),
    }


def _pressure_check(result: Mapping[str, Any]) -> dict[str, Any]:
    gap_check = _mapping(result.get("gap_check"))
    return {
        "has_gap_check": bool(result.get("has_gap_check")),
        "mode": str(result.get("pressure_check_mode") or ""),
        "status": str(gap_check.get("status") or ""),
        "reason": str(gap_check.get("reason") or ""),
        "lane_count": len(_list(gap_check.get("lanes"))),
        "summary_present": bool(str(result.get("gap_check_summary") or "").strip()),
    }


def _private_custody(*, result: Mapping[str, Any], run_dir: Path) -> dict[str, Any]:
    run_health = _mapping(result.get("run_health"))
    private_table = _mapping(result.get("pre_step6_private_table"))
    v60 = _mapping(result.get("v60_enrichment"))
    v60_validation = _mapping(result.get("v60_consideration_validation"))
    return {
        "v60_enrichment_status": str(v60.get("status") or ""),
        "v60_consideration_ledger_status": str(
            v60_validation.get("status") or run_health.get("v60_consideration_ledger") or ""
        ),
        "v60_ledger_file_present": (run_dir / "v60_ledger.json").exists(),
        "pre_step6_private_table_status": str(private_table.get("status") or ""),
        "pre_step6_private_table_ledger_file_present": (
            run_dir / "pre_step6_private_table_ledger.json"
        ).exists(),
        "pre_step6_shadow_portfolio_file_present": (
            run_dir / "pre_step6_shadow_portfolio.json"
        ).exists(),
    }


def _usage_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    usage = _mapping(result.get("usage_summary"))
    vendors = _mapping(usage.get("vendors"))
    vendor_calls: dict[str, int] = {}
    for vendor_name, raw_vendor in vendors.items():
        vendor = _mapping(raw_vendor)
        vendor_calls[str(vendor_name)] = _safe_int(vendor.get("calls"))
    return {
        "run_id": str(usage.get("run_id") or ""),
        "pricing_table_version": str(usage.get("pricing_table_version") or ""),
        "estimated_total_cost_usd": usage.get("estimated_total_cost_usd"),
        "cost_estimate_state": str(usage.get("cost_estimate_state") or ""),
        "vendor_calls": vendor_calls,
    }


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0
