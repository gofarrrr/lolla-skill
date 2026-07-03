"""Controlled archive-shaped fixture writer for Decision Work sidecars.

PR214 writes Decision Work sidecar-shaped files only into synthetic
archive-like fixture directories under safe temp/operator output roots. It does
not mutate real historical archives, wire runtime, approve resolver refs, call
models, score answer quality, or authorize action.
"""
from __future__ import annotations

import datetime as _dt
import json
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from engine.system_b.decision_work_explicit_operator_sidecar_write import (
    ALLOWED_FILE_NAMES,
    AUTHORITY_FLAGS,
    DRY_RUN_READY_STATUS,
    DRY_RUN_RUNTIME_BLOCK_STATUS,
    EXPLICIT_OPERATOR_WRITE_RECEIPT_SCHEMA_VERSION,
    LOCAL_ABSOLUTE_PATH_MARKERS,
    RAW_PRIVATE_MARKERS,
    READY_SIDECAR_UPDATE_STATUS,
    RUNTIME_BLOCK_SIDECAR_UPDATE_STATUS,
    RUNTIME_PATH_MARKER_PARTS,
    SIDECAR_UPDATE_PACKET_SCHEMA_VERSION,
    SIDECAR_WRITE_DRY_RUN_SCHEMA_VERSION,
    _any_true_flag,
    _dedupe,
    _dry_run_result_blockers,
    _json_text,
    _load_optional_json_text,
    _mapping,
    _source_match_blockers,
    _sidecar_update_packet_blockers,
    _source_refs,
    _text,
)


CONTROLLED_ARCHIVE_FIXTURE_SCHEMA_VERSION = (
    "lolla.decision_work_controlled_archive_sidecar_write_fixture.v0"
)
FIXTURE_WRITE_COMPLETED_STATUS = "fixture_write_completed"
FIXTURE_WRITE_COMPLETED_BLOCKED_STATUS = "fixture_write_completed_blocked_state"
REPO_ROOT = Path(__file__).resolve().parents[2]

ARCHIVE_MARKER_PARTS = {
    "archive",
    "archives",
    "case",
    "cases",
    "completed-run",
    "completed-runs",
    "completed_runs",
    "run_archive",
    "run_archives",
}
FIXTURE_MARKER_FRAGMENTS = (
    "fixture",
    "synthetic",
    "operator",
)
HISTORICAL_ARCHIVE_SENTINELS = (
    "agent_result.json",
    "reasoning_trace.json",
    "evaluation.json",
    "run_events.json",
    "memo.md",
)
RUNTIME_WRITE_FLAGS = (
    "archive_mutated",
    "real_archive_mutated",
    "historical_archive_mutated",
    "archive_sidecar_written",
    "runtime_wiring_changed",
    "runtime_hook_changed",
    "runtime_sidecar_updated",
    "can_update_sidecar",
    "can_write_runtime_sidecar",
    "can_write_decision_work_directory",
    "can_mutate_archive",
    "can_wire_runtime",
)
NON_CLAIMS = (
    "controlled_archive_fixture_write_is_synthetic_only",
    "controlled_archive_fixture_write_does_not_mutate_real_archives",
    "controlled_archive_fixture_write_does_not_mutate_historical_archives",
    "controlled_archive_fixture_write_does_not_wire_runtime",
    "controlled_archive_fixture_write_does_not_edit_archive_hook",
    "controlled_archive_fixture_write_does_not_approve_resolver_refs",
    "controlled_archive_fixture_write_does_not_mark_resolver_refs_usable",
    "controlled_archive_fixture_write_does_not_call_models",
    "controlled_archive_fixture_write_is_not_product_proof",
    "controlled_archive_fixture_write_is_not_human_validation",
    "controlled_archive_fixture_write_does_not_score_answer_quality",
    "controlled_archive_fixture_write_does_not_validate_advice_correctness",
    "controlled_archive_fixture_write_does_not_authorize_agent_action",
    "controlled_archive_fixture_write_does_not_authorize_automatic_action",
)


class DecisionWorkControlledArchiveSidecarWriteFixtureError(ValueError):
    """Sanitized controlled archive fixture write error."""


def build_controlled_archive_sidecar_write_fixture(
    *,
    sidecar_update_packet_path: Path | str,
    dry_run_result_path: Path | str | None,
    fixture_archive_dir: Path | str,
    source_sidecar_update_packet_ref: str | None = None,
    source_dry_run_result_ref: str | None = None,
    mode: str = "controlled_archive_fixture_write",
    created_at: str | None = None,
) -> dict[str, Any]:
    """Write sidecar-shaped files into a synthetic archive-like fixture dir."""

    packet_ref = source_sidecar_update_packet_ref or _safe_ref(
        _resolve(sidecar_update_packet_path)
    )
    dry_run_ref = source_dry_run_result_ref or (
        _safe_ref(_resolve(dry_run_result_path)) if dry_run_result_path else None
    )
    packet_text, packet, packet_error = _load_optional_json_text(
        sidecar_update_packet_path
    )
    dry_text, dry_run, dry_error = (
        _load_optional_json_text(dry_run_result_path)
        if dry_run_result_path is not None
        else ("", None, "not_found")
    )
    packet_mapping = _mapping(packet)
    dry_mapping = _mapping(dry_run)

    blockers: list[str] = []
    if mode != "controlled_archive_fixture_write":
        blockers.append("write_mode_not_allowed")
    if packet_error == "not_found":
        blockers.append("sidecar_update_packet_missing")
    elif packet_error:
        blockers.append(f"sidecar_update_packet_unreadable:{packet_error}")
    if dry_error == "not_found":
        blockers.append("dry_run_result_missing")
    elif dry_error:
        blockers.append(f"dry_run_result_unreadable:{dry_error}")
    if packet_text and _contains_private_marker(packet_text):
        blockers.append("privacy_marker_detected")
    if dry_text and _contains_private_marker(dry_text):
        blockers.append("privacy_marker_detected")
    if packet_text and _contains_local_absolute_path_marker(packet_text):
        blockers.append("local_absolute_path_detected")
    if dry_text and _contains_local_absolute_path_marker(dry_text):
        blockers.append("local_absolute_path_detected")
    blockers.extend(_sidecar_update_packet_blockers(packet_mapping))
    blockers.extend(_dry_run_result_blockers(dry_mapping))
    blockers.extend(_source_match_blockers(packet_mapping, dry_mapping))
    target_blocker = _fixture_archive_dir_blocker(fixture_archive_dir)
    if target_blocker:
        blockers.append(target_blocker)
    blockers = _dedupe(blockers)

    fixture_status = _fixture_status(blockers, packet_mapping)
    write_ready = fixture_status in {
        FIXTURE_WRITE_COMPLETED_STATUS,
        FIXTURE_WRITE_COMPLETED_BLOCKED_STATUS,
    }
    fixture_archive_dir_ref = _safe_temp_ref(fixture_archive_dir)
    fixture_sidecar_dir = Path(fixture_archive_dir).expanduser() / "decision_work"
    fixture_sidecar_dir_ref = _safe_temp_ref(fixture_sidecar_dir)
    files_written: list[str] = []

    receipt = {
        "schema_version": CONTROLLED_ARCHIVE_FIXTURE_SCHEMA_VERSION,
        "write_metadata": {
            "created_at": created_at or _utc_now(),
            "generated_by": "decision_work_controlled_archive_sidecar_write_fixture",
            "mode": mode,
            "adapter_scope": "synthetic_archive_shaped_fixture_write_only",
            "model_calls": 0,
            "runtime_invoked": False,
            "skill_invoked": False,
            "archive_hook_changed": False,
            "runtime_wiring_changed": False,
            "real_archive_mutated": False,
            "historical_archive_mutated": False,
        },
        "source_case": dict(_mapping(packet_mapping.get("source_case"))),
        "source_sidecar_update_packet_ref": packet_ref,
        "source_dry_run_result_ref": dry_run_ref,
        "fixture_archive_dir_ref": fixture_archive_dir_ref,
        "fixture_sidecar_dir_ref": fixture_sidecar_dir_ref,
        "fixture_write_status": fixture_status,
        "files_written": files_written,
        "blocker_reasons": blockers,
        "mode": mode,
        "synthetic_archive_fixture_only": True,
        "operator_explicit_write_required": True,
        "actual_sidecar_write_performed": write_ready,
        "fixture_sidecar_write_performed": write_ready,
        "real_archive_mutated": False,
        "historical_archive_mutated": False,
        "archive_hook_changed": False,
        "runtime_wiring_changed": False,
        "resolver_refs_approved": False,
        "can_authorize_agent_action": False,
        "can_authorize_automatic_action": False,
        "can_be_used_as_quality_label": False,
        "product_proof": False,
        "human_validated": False,
        "answer_quality_scored": False,
        "advice_correctness_claimed": False,
        "runtime_use_status": dict(
            _mapping(packet_mapping.get("runtime_use_status"))
        ),
        "user_surface_status": dict(
            _mapping(packet_mapping.get("user_surface_status"))
        ),
        "source_refs": _source_refs(packet_mapping, packet_ref),
        "privacy_summary": dict(_mapping(packet_mapping.get("privacy_summary"))),
        "uncertainty_summary": dict(
            _mapping(packet_mapping.get("uncertainty_summary"))
        ),
        "custody_flags": _custody_flags(write_ready=write_ready),
        "non_claims": list(NON_CLAIMS),
        "downstream_allowed": {
            "can_feed_controlled_archive_fixture_review": write_ready,
            "can_write_controlled_archive_fixture": write_ready,
            "can_write_real_archive_sidecar": False,
            "can_mutate_historical_archive": False,
            "can_wire_runtime": False,
            "can_edit_archive_hook": False,
            "resolver_refs_approved": False,
            "resolver_refs_marked_usable": False,
            "can_authorize_agent_action": False,
            "can_authorize_automatic_action": False,
            "can_be_used_as_quality_label": False,
            "product_proof": False,
            "human_validated": False,
            "answer_quality_scored": False,
            "advice_correctness_claimed": False,
        },
        "downstream_forbidden": [
            "write_real_archive_sidecar",
            "mutate_historical_archive",
            "wire_runtime",
            "edit_archive_hook",
            "approve_resolver_refs",
            "mark_resolver_refs_usable",
            "make_runtime_default_on",
            "call_models_or_providers",
            "score_answer_quality",
            "claim_product_proof",
            "claim_human_validation",
            "claim_advice_correctness",
            "authorize_agent_or_automatic_action",
        ],
    }

    if write_ready:
        files_written = write_controlled_archive_sidecar_fixture_files(
            fixture_archive_dir=fixture_archive_dir,
            receipt=receipt,
            sidecar_update_packet=packet_mapping,
            dry_run_result=dry_mapping,
        )
        receipt["files_written"] = files_written
        receipt["custody_flags"] = _custody_flags(write_ready=True)

    return receipt


def render_controlled_archive_sidecar_write_fixture_json(
    result: Mapping[str, Any],
    *,
    pretty: bool = False,
) -> str:
    """Render a controlled archive fixture receipt as stable JSON."""

    if pretty:
        return json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return json.dumps(result, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"


def write_controlled_archive_sidecar_write_fixture_receipt(
    path: Path | str,
    payload: str,
) -> None:
    """Write a fixture receipt JSON outside sidecar/archive target dirs."""

    output = Path(path).expanduser()
    if not output.is_absolute():
        raise DecisionWorkControlledArchiveSidecarWriteFixtureError(
            "receipt output path must be absolute"
        )
    if "decision_work" in output.parts or _path_has_runtime_marker(output):
        raise DecisionWorkControlledArchiveSidecarWriteFixtureError(
            "receipt output must not target decision_work or runtime paths"
        )
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    except OSError as exc:
        raise DecisionWorkControlledArchiveSidecarWriteFixtureError(
            f"fixture receipt output could not be written:{type(exc).__name__}"
        ) from exc


def write_controlled_archive_sidecar_fixture_files(
    *,
    fixture_archive_dir: Path | str,
    receipt: Mapping[str, Any],
    sidecar_update_packet: Mapping[str, Any],
    dry_run_result: Mapping[str, Any],
) -> list[str]:
    """Write sidecar files under ``fixture_archive_dir / decision_work``."""

    blocker = _fixture_archive_dir_blocker(fixture_archive_dir)
    if blocker:
        raise DecisionWorkControlledArchiveSidecarWriteFixtureError(
            "fixture archive directory is not safe for synthetic fixture writes"
        )
    archive_dir = Path(fixture_archive_dir).expanduser()
    sidecar_dir = archive_dir / "decision_work"
    payloads = _sidecar_payloads(receipt, sidecar_update_packet, dry_run_result)
    try:
        sidecar_dir.mkdir(parents=True, exist_ok=True)
        resolved_base = sidecar_dir.resolve(strict=False)
        written: list[str] = []
        for name in ALLOWED_FILE_NAMES:
            target = sidecar_dir / name
            resolved_target = target.resolve(strict=False)
            try:
                resolved_target.relative_to(resolved_base)
            except ValueError as exc:
                raise DecisionWorkControlledArchiveSidecarWriteFixtureError(
                    "sidecar file escaped controlled fixture directory"
                ) from exc
            target.write_text(payloads[name], encoding="utf-8")
            written.append(name)
    except OSError as exc:
        raise DecisionWorkControlledArchiveSidecarWriteFixtureError(
            f"fixture sidecar files could not be written:{type(exc).__name__}"
        ) from exc
    return written


def _fixture_archive_dir_blocker(path: Path | str) -> str | None:
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        return "target_path_not_absolute"
    if candidate.name == "decision_work":
        return "target_points_at_sidecar_dir"
    try:
        candidate.resolve(strict=False).relative_to(REPO_ROOT)
        return "target_inside_repository"
    except ValueError:
        pass
    if _path_has_runtime_marker(candidate):
        return "target_path_targets_runtime"
    if not _path_under_safe_temp_root(candidate):
        return "target_not_under_safe_temp_root"
    parts_lower = [part.lower() for part in candidate.parts]
    if not any("archive" in part for part in parts_lower):
        return "target_not_archive_shaped"
    if not any(
        fragment in part for part in parts_lower for fragment in FIXTURE_MARKER_FRAGMENTS
    ):
        return "target_path_targets_real_archive"
    if _path_looks_like_existing_historical_archive(candidate):
        return "target_existing_historical_archive"
    sidecar_dir = candidate / "decision_work"
    if sidecar_dir.exists():
        disallowed = [
            child.name
            for child in sidecar_dir.iterdir()
            if child.name not in ALLOWED_FILE_NAMES
        ]
        if disallowed:
            return "target_existing_untrusted_sidecar_files"
    return None


def _fixture_status(blockers: list[str], packet: Mapping[str, Any]) -> str:
    if blockers:
        blocker_set = set(blockers)
        if "dry_run_result_missing" in blocker_set:
            return "blocked_dry_run_missing"
        if blocker_set.intersection(
            {
                "dry_run_status_does_not_match_packet",
                "dry_run_case_does_not_match_packet",
            }
        ) or any(item.endswith("_dry_run_mismatch") for item in blockers):
            return "blocked_dry_run_mismatch"
        if "target_inside_repository" in blocker_set:
            return "blocked_repo_path"
        if "target_existing_historical_archive" in blocker_set:
            return "blocked_existing_archive_path"
        if "target_path_targets_real_archive" in blocker_set:
            return "blocked_real_archive_path"
        if blocker_set.intersection(
            {
                "target_path_not_absolute",
                "target_points_at_sidecar_dir",
                "target_path_targets_runtime",
                "target_not_under_safe_temp_root",
                "target_not_archive_shaped",
                "target_existing_untrusted_sidecar_files",
            }
        ):
            return "blocked_target_path_unsafe"
        if blocker_set.intersection(
            {
                "privacy_marker_detected",
                "local_absolute_path_detected",
            }
        ):
            return "blocked_privacy_risk"
        authority_not_false = {
            "resolver_refs_approved_not_false",
            "can_authorize_agent_action_not_false",
            "can_authorize_automatic_action_not_false",
            "can_be_used_as_quality_label_not_false",
            "product_proof_not_false",
            "human_validated_not_false",
            "answer_quality_scored_not_false",
            "advice_correctness_claimed_not_false",
        }
        if "authority_claim_detected" in blocker_set or blocker_set.intersection(
            authority_not_false
        ):
            return "blocked_authority_claim"
        return "blocked_packet_not_write_eligible"
    if _text(packet.get("sidecar_update_packet_status")) == RUNTIME_BLOCK_SIDECAR_UPDATE_STATUS:
        return FIXTURE_WRITE_COMPLETED_BLOCKED_STATUS
    return FIXTURE_WRITE_COMPLETED_STATUS


def _sidecar_payloads(
    receipt: Mapping[str, Any],
    sidecar_update_packet: Mapping[str, Any],
    dry_run_result: Mapping[str, Any],
) -> dict[str, str]:
    fixture_status = _text(receipt.get("fixture_write_status"))
    source_case = dict(_mapping(receipt.get("source_case")))
    source_refs = dict(_mapping(receipt.get("source_refs")))
    non_claims = list(receipt.get("non_claims", []))
    attachment_status = {
        "schema_version": "lolla.decision_work_controlled_archive_sidecar_write_fixture.attachment_status.v0",
        "source_case": source_case,
        "fixture_write_status": fixture_status,
        "synthetic_archive_fixture_only": True,
        "dry_run_status": _text(dry_run_result.get("dry_run_status")),
        "sidecar_update_packet_status": _text(
            sidecar_update_packet.get("sidecar_update_packet_status")
        ),
        "actual_sidecar_write_performed": True,
        "real_archive_mutated": False,
        "historical_archive_mutated": False,
        "archive_hook_changed": False,
        "runtime_wiring_changed": False,
        "resolver_refs_approved": False,
        "runtime_use_status": dict(
            _mapping(sidecar_update_packet.get("runtime_use_status"))
        ),
        "user_surface_status": dict(
            _mapping(sidecar_update_packet.get("user_surface_status"))
        ),
        "source_refs": source_refs,
        "non_claims": non_claims,
    }
    safe_supply_summary = {
        "schema_version": "lolla.decision_work_controlled_archive_sidecar_write_fixture.safe_supply_summary.v0",
        "source_case": source_case,
        "source_refs": source_refs,
        "privacy_summary": dict(_mapping(receipt.get("privacy_summary"))),
        "uncertainty_summary": dict(_mapping(receipt.get("uncertainty_summary"))),
        "raw_content_included": False,
        "resolver_refs_approved": False,
        "synthetic_archive_fixture_only": True,
        "actual_sidecar_write_performed": True,
        "real_archive_mutated": False,
        "historical_archive_mutated": False,
        "archive_hook_changed": False,
        "runtime_wiring_changed": False,
    }
    agent_handoff_packet = {
        "schema_version": "lolla.decision_work_controlled_archive_sidecar_write_fixture.agent_handoff.v0",
        "source_case": source_case,
        "fixture_write_status": fixture_status,
        "synthetic_archive_fixture_only": True,
        "agent_inspection_status": dict(
            _mapping(sidecar_update_packet.get("agent_inspection_status"))
        ),
        "agent_action_authorized": False,
        "automatic_action_authorized": False,
        "actual_sidecar_write_performed": True,
        "real_archive_mutated": False,
        "historical_archive_mutated": False,
        "archive_hook_changed": False,
        "runtime_wiring_changed": False,
        "resolver_refs_approved": False,
        "non_claims": non_claims,
    }
    return {
        "attachment_status.json": _json_text(attachment_status),
        "user_receipt.md": _receipt_markdown(receipt, sidecar_update_packet),
        "agent_handoff_packet.json": _json_text(agent_handoff_packet),
        "safe_supply_summary.json": _json_text(safe_supply_summary),
        "sidecar_update_packet.json": _json_text(dict(sidecar_update_packet)),
        "sidecar_write_receipt.json": _json_text(dict(receipt)),
    }


def _receipt_markdown(
    receipt: Mapping[str, Any],
    sidecar_update_packet: Mapping[str, Any],
) -> str:
    case_id = _text(_mapping(receipt.get("source_case")).get("case_id"), "unknown")
    fixture_status = _text(receipt.get("fixture_write_status"), "unknown")
    packet_status = _text(
        sidecar_update_packet.get("sidecar_update_packet_status"),
        "unknown",
    )
    return "\n".join(
        [
            "# Decision Work Controlled Archive Sidecar Write Fixture",
            "",
            f"Source case: `{case_id}`",
            f"Fixture write status: `{fixture_status}`",
            f"Source packet status: `{packet_status}`",
            "",
            "This is a synthetic archive-shaped fixture write only.",
            "",
            "- actual sidecar write performed: true, fixture only",
            "- real archive mutated: false",
            "- historical archive mutated: false",
            "- archive hook changed: false",
            "- runtime wiring changed: false",
            "- resolver refs approved: false",
            "- agent or automatic action authorized: false",
            "",
            "The fixture files do not prove correctness, human validation,",
            "product value, answer quality, or permission to act.",
            "",
        ]
    )


def _custody_flags(*, write_ready: bool) -> dict[str, Any]:
    return {
        "model_calls": 0,
        "runtime_invoked": False,
        "skill_invoked": False,
        "actual_sidecar_write_performed": write_ready,
        "fixture_sidecar_write_performed": write_ready,
        "synthetic_archive_fixture_only": True,
        "real_archive_mutated": False,
        "historical_archive_mutated": False,
        "archive_hook_changed": False,
        "runtime_wiring_changed": False,
        "resolver_refs_approved": False,
        "resolver_refs_marked_usable": False,
        "product_proof": False,
        "human_validated": False,
        "answer_quality_scored": False,
        "advice_correctness_claimed": False,
        "agent_action_authorized": False,
        "automatic_action_authorized": False,
    }


def _path_looks_like_existing_historical_archive(path: Path) -> bool:
    return any((path / sentinel).exists() for sentinel in HISTORICAL_ARCHIVE_SENTINELS)


def _path_has_runtime_marker(path: Path) -> bool:
    parts = {part.lower() for part in path.parts}
    return bool(parts.intersection(RUNTIME_PATH_MARKER_PARTS))


def _path_under_safe_temp_root(path: Path) -> bool:
    resolved = path.resolve(strict=False)
    roots = {
        Path(tempfile.gettempdir()).resolve(strict=False),
        Path("/tmp").resolve(strict=False),
        Path("/var/tmp").resolve(strict=False),
        Path("/private/tmp").resolve(strict=False),
    }
    for root in roots:
        try:
            resolved.relative_to(root)
            return True
        except ValueError:
            continue
    return False


def _safe_temp_ref(path: Path | str) -> str:
    candidate = Path(path).expanduser().resolve(strict=False)
    for root in (
        Path(tempfile.gettempdir()).resolve(strict=False),
        Path("/tmp").resolve(strict=False),
        Path("/var/tmp").resolve(strict=False),
        Path("/private/tmp").resolve(strict=False),
    ):
        try:
            return f"tmp/{candidate.relative_to(root).as_posix()}"
        except ValueError:
            continue
    return candidate.name


def _resolve(path: Path | str) -> Path:
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    return candidate


def _safe_ref(path: Path | str | None) -> str | None:
    if path is None:
        return None
    candidate = Path(path).expanduser()
    try:
        return str(candidate.resolve(strict=False).relative_to(REPO_ROOT))
    except ValueError:
        return _safe_temp_ref(candidate)


def _contains_private_marker(text: str) -> bool:
    return any(marker in text for marker in RAW_PRIVATE_MARKERS)


def _contains_local_absolute_path_marker(text: str) -> bool:
    return any(marker in text for marker in LOCAL_ABSOLUTE_PATH_MARKERS)


def _utc_now() -> str:
    return (
        _dt.datetime.now(tz=_dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
