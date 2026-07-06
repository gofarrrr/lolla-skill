"""Read-only Observatory status adapter for Decision Work sidecars.

The adapter inspects an already-selected Lolla run and any existing
``decision_work/`` sidecar files. It does not generate interpretation, call
providers, run Lolla, mutate archives, write sidecars, score advice, or
authorize action.
"""
from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any


OBSERVATORY_DECISION_WORK_STATUS_SCHEMA_VERSION = (
    "lolla.observatory_decision_work_status.v0"
)
DECISION_WORK_ARTIFACTS = (
    ("attachment_status", "attachment_status.json", "application/json"),
    ("user_receipt", "user_receipt.md", "text/markdown"),
    ("agent_handoff_packet", "agent_handoff_packet.json", "application/json"),
    ("safe_supply_summary", "safe_supply_summary.json", "application/json"),
    ("sidecar_update_packet", "sidecar_update_packet.json", "application/json"),
    ("sidecar_write_receipt", "sidecar_write_receipt.json", "application/json"),
    ("decision_work_brief", "decision_work_brief.md", "text/markdown"),
    (
        "decision_work_brief_enriched",
        "decision_work_brief_enriched.md",
        "text/markdown",
    ),
    ("automatic_triage_read", "automatic_triage_read.json", "application/json"),
)
AVAILABLE_ATTACHMENT_STATES = {
    "generated",
    "generated_with_caveats",
    "generated_agent_only",
}
NOT_REQUESTED_ATTACHMENT_STATES = {"not_requested", "disabled", "not_eligible"}
FAILED_ATTACHMENT_STATES = {"failed_closed"}
RAW_PRIVATE_MARKERS = (
    "/" + "Users" + "/",
    "/home/",
    "/private/",
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
NON_CLAIMS = {
    "product_proof": False,
    "human_validated": False,
    "answer_correctness": False,
    "advice_correctness": False,
    "resolver_approved": False,
    "agent_action_authorized": False,
    "automatic_action_authorized": False,
    "graph_or_sidecar_is_proof": False,
}
CUSTODY_FLAGS = {
    "read_only": True,
    "model_calls": 0,
    "provider_or_model_calls_used": False,
    "lolla_skill_invoked": False,
    "new_lolla_run_created": False,
    "runtime_behavior_changed": False,
    "archive_mutated": False,
    "sidecar_written": False,
    "automatic_semantic_interpretation_enabled": False,
}


def build_observatory_decision_work_status(
    *,
    selected_case_id: str,
    result: Mapping[str, Any] | None = None,
    result_path: Path | str | None = None,
    decision_work_files: Mapping[str, Path | str] | None = None,
) -> dict[str, Any]:
    """Return a product-safe Decision Work status payload for Observatory."""

    result_payload = result if isinstance(result, Mapping) else {}
    result_file = Path(result_path) if result_path is not None else None
    run_id = _selected_run_id(result_payload, result_file)
    files = _normalize_file_map(decision_work_files)
    if decision_work_files is None and result_file is not None:
        files = _discover_sidecar_files(result_file.parent)

    source_artifacts = _artifact_records(files)
    attachment_status, attachment_status_error = _load_status(
        files.get("attachment_status")
    )
    receipt = _receipt_payload(files.get("user_receipt"))
    live_extraction_status = _live_extraction_status(result_payload, result_file)
    blockers: list[str] = []
    missingness: list[str] = []
    deferred_reasons: list[str] = []

    if attachment_status_error:
        blockers.append(attachment_status_error)
    if receipt["status"] == "blocked_unsafe_content":
        blockers.append("user_receipt_contains_private_or_local_marker")

    if not files:
        decision_work_status = "decision_work_not_present"
        attachment_state = "not_present"
        missingness.append("decision_work_sidecar")
    elif attachment_status is None:
        decision_work_status = "decision_work_malformed"
        attachment_state = "malformed"
        if "attachment_status" not in files:
            blockers.append("attachment_status_missing")
        missingness.append("valid_attachment_status")
    else:
        attachment_state = _text(attachment_status.get("attachment_state"), "unknown")
        blocked_reasons = _string_list(attachment_status.get("blocked_reasons"))
        deferred_reasons = _string_list(attachment_status.get("deferred_reasons"))
        blockers.extend(blocked_reasons)
        missingness.extend(_missing_artifact_names(attachment_status))
        decision_work_status = _status_from_attachment_state(attachment_state)

    if live_extraction_status != "available":
        missingness.append("live_extraction")

    return {
        "schema_version": OBSERVATORY_DECISION_WORK_STATUS_SCHEMA_VERSION,
        "selected_case_id": selected_case_id,
        "selected_run_id": run_id,
        "available": decision_work_status == "decision_work_available",
        "decision_work_status": decision_work_status,
        "attachment_state": attachment_state,
        "live_extraction_status": live_extraction_status,
        "conversation_understanding": {
            "live_extraction": live_extraction_status,
            "richer_decision_work": decision_work_status,
            "user_action": _user_action_for_status(decision_work_status),
        },
        "source_artifacts": source_artifacts,
        "receipt": receipt,
        "blockers": _dedupe(blockers),
        "deferred_reasons": _dedupe(deferred_reasons),
        "missingness": _dedupe(missingness),
        "links": {
            "extraction_audit": "/audit/extraction",
            "decision_work_api": f"/api/case/{selected_case_id}/decision-work",
        },
        "non_claims": dict(NON_CLAIMS),
        "custody_flags": dict(CUSTODY_FLAGS),
    }


def _discover_sidecar_files(run_dir: Path) -> dict[str, Path]:
    sidecar_dir = run_dir / "decision_work"
    files: dict[str, Path] = {}
    for artifact_id, filename, _content_type in DECISION_WORK_ARTIFACTS:
        path = sidecar_dir / filename
        if path.is_file():
            files[artifact_id] = path
    return files


def _normalize_file_map(
    files: Mapping[str, Path | str] | None,
) -> dict[str, Path]:
    if not files:
        return {}
    allowed = {
        artifact_id for artifact_id, _filename, _content_type in DECISION_WORK_ARTIFACTS
    }
    normalized: dict[str, Path] = {}
    for artifact_id, path in files.items():
        if artifact_id not in allowed:
            continue
        candidate = Path(path)
        if candidate.is_file():
            normalized[artifact_id] = candidate
    return normalized


def _artifact_records(files: Mapping[str, Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    content_types = {
        artifact_id: content_type
        for artifact_id, _filename, content_type in DECISION_WORK_ARTIFACTS
    }
    filenames = {
        artifact_id: filename
        for artifact_id, filename, _content_type in DECISION_WORK_ARTIFACTS
    }
    for artifact_id, path in sorted(files.items()):
        try:
            size = path.stat().st_size
        except OSError:
            continue
        records.append(
            {
                "artifact_id": artifact_id,
                "ref": f"decision_work/{filenames.get(artifact_id, path.name)}",
                "content_type": content_types.get(
                    artifact_id,
                    "application/octet-stream",
                ),
                "bytes": size,
                "status": "available",
            }
        )
    return records


def _load_status(path: Path | None) -> tuple[dict[str, Any] | None, str | None]:
    if path is None:
        return None, None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None, "attachment_status_malformed_json"
    except UnicodeDecodeError:
        return None, "attachment_status_not_utf8"
    except OSError:
        return None, "attachment_status_unreadable"
    if not isinstance(payload, dict):
        return None, "attachment_status_not_object"
    return payload, None


def _receipt_payload(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {
            "available": False,
            "status": "missing",
            "markdown": None,
            "ref": None,
        }
    try:
        markdown = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return {
            "available": False,
            "status": "blocked_unreadable",
            "markdown": None,
            "ref": "decision_work/user_receipt.md",
        }
    if _has_private_marker(markdown):
        return {
            "available": False,
            "status": "blocked_unsafe_content",
            "markdown": None,
            "ref": "decision_work/user_receipt.md",
        }
    return {
        "available": True,
        "status": "available",
        "markdown": markdown,
        "ref": "decision_work/user_receipt.md",
    }


def _live_extraction_status(
    result: Mapping[str, Any],
    result_path: Path | None,
) -> str:
    extraction = result.get("extraction")
    if isinstance(extraction, Mapping) and extraction:
        return "available"
    if result_path is not None and (result_path.parent / "extraction.json").is_file():
        return "available"
    if result_path is not None and result_path.name.endswith("_result.json"):
        prefix = result_path.name[: -len("_result.json")]
        if (result_path.parent / f"{prefix}_extraction.json").is_file():
            return "available"
    return "missing"


def _selected_run_id(result: Mapping[str, Any], result_path: Path | None) -> str:
    usage = result.get("usage_summary")
    if isinstance(usage, Mapping) and usage.get("run_id"):
        return str(usage.get("run_id"))
    if result_path is not None:
        return result_path.parent.name
    return ""


def _status_from_attachment_state(attachment_state: str) -> str:
    if attachment_state in AVAILABLE_ATTACHMENT_STATES:
        return "decision_work_available"
    if attachment_state == "deferred":
        return "decision_work_deferred"
    if attachment_state == "blocked":
        return "decision_work_blocked"
    if attachment_state in FAILED_ATTACHMENT_STATES:
        return "decision_work_failed_closed"
    if attachment_state in NOT_REQUESTED_ATTACHMENT_STATES:
        return "decision_work_not_requested"
    return "decision_work_unknown"


def _user_action_for_status(status: str) -> str:
    return {
        "decision_work_available": "open_receipt",
        "decision_work_deferred": "inspect_missing_inputs",
        "decision_work_blocked": "inspect_blockers",
        "decision_work_failed_closed": "inspect_failed_closed_status",
        "decision_work_not_requested": "prepare_process_brief_optional",
        "decision_work_not_present": "prepare_process_brief_optional",
        "decision_work_malformed": "inspect_sidecar_status",
        "decision_work_unknown": "inspect_sidecar_status",
    }.get(status, "inspect_status")


def _missing_artifact_names(status: Mapping[str, Any]) -> list[str]:
    missing = status.get("missing_artifacts")
    if not isinstance(missing, Mapping):
        return []
    return [str(key) for key, value in missing.items() if str(value).strip()]


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def _text(value: Any, fallback: str = "") -> str:
    return value if isinstance(value, str) and value else fallback


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def _has_private_marker(text: str) -> bool:
    return any(marker in text for marker in RAW_PRIVATE_MARKERS)
