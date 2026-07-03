"""Fixture-only explicit operator sidecar write adapter.

PR210 writes Decision Work sidecar-shaped files only to a caller-supplied
controlled fixture/output directory. It never writes real historical archives,
approves resolver refs, wires runtime, calls models, scores answer quality, or
authorizes action.
"""
from __future__ import annotations

import datetime as _dt
import json
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any


EXPLICIT_OPERATOR_WRITE_RECEIPT_SCHEMA_VERSION = (
    "lolla.decision_work_explicit_operator_sidecar_write_receipt.v0"
)
SIDECAR_UPDATE_PACKET_SCHEMA_VERSION = (
    "lolla.decision_work_resolver_candidate_sidecar_update_packet.v0"
)
SIDECAR_WRITE_DRY_RUN_SCHEMA_VERSION = "lolla.decision_work_sidecar_write_dry_run.v0"
READY_SIDECAR_UPDATE_STATUS = "ready_for_sidecar_update_packet"
RUNTIME_BLOCK_SIDECAR_UPDATE_STATUS = "packet_with_runtime_block"
DRY_RUN_READY_STATUS = "dry_run_ready"
DRY_RUN_RUNTIME_BLOCK_STATUS = "dry_run_packet_with_runtime_block"
WRITE_COMPLETED_STATUS = "write_completed_fixture_only"
WRITE_COMPLETED_BLOCKED_STATUS = "write_completed_blocked_state_fixture_only"
REPO_ROOT = Path(__file__).resolve().parents[2]

ALLOWED_FILE_NAMES = (
    "attachment_status.json",
    "user_receipt.md",
    "agent_handoff_packet.json",
    "safe_supply_summary.json",
    "sidecar_update_packet.json",
    "sidecar_write_receipt.json",
)
RAW_PRIVATE_MARKERS = (
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)
LOCAL_ABSOLUTE_PATH_MARKERS = (
    "/" + "Users" + "/",
    "/home/",
    "/private/",
)
REAL_ARCHIVE_PATH_MARKER_PARTS = {
    "archive",
    "archives",
    "completed-run",
    "completed-runs",
    "completed_runs",
    "run_archive",
    "run_archives",
}
RUNTIME_PATH_MARKER_PARTS = {
    "runtime",
    "runtime-sidecars",
    "runtime_sidecars",
    "post-archive",
    "post_archive",
}
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
AUTHORITY_FLAGS = (
    "resolver_refs_approved",
    "resolver_refs_marked_usable",
    "can_approve_resolver_refs",
    "can_mark_resolver_refs_usable",
    "product_proof",
    "human_validated",
    "answer_quality_scored",
    "advice_correctness_claimed",
    "agent_action_authorized",
    "automatic_action_authorized",
    "can_authorize_agent_action",
    "can_authorize_automatic_action",
    "can_be_used_as_quality_label",
    "customer_ready",
)
NON_CLAIMS = (
    "explicit_operator_write_is_fixture_only",
    "explicit_operator_write_does_not_mutate_real_archives",
    "explicit_operator_write_does_not_mutate_historical_archives",
    "explicit_operator_write_does_not_wire_runtime",
    "explicit_operator_write_does_not_approve_resolver_refs",
    "explicit_operator_write_does_not_mark_resolver_refs_usable",
    "explicit_operator_write_does_not_call_models",
    "explicit_operator_write_is_not_product_proof",
    "explicit_operator_write_is_not_human_validation",
    "explicit_operator_write_does_not_score_answer_quality",
    "explicit_operator_write_does_not_validate_advice_correctness",
    "explicit_operator_write_does_not_authorize_agent_action",
    "explicit_operator_write_does_not_authorize_automatic_action",
)


class DecisionWorkExplicitOperatorSidecarWriteError(ValueError):
    """Sanitized explicit operator sidecar write error."""


def build_explicit_operator_sidecar_write(
    *,
    sidecar_update_packet_path: Path | str,
    dry_run_result_path: Path | str | None,
    target_sidecar_dir: Path | str,
    source_sidecar_update_packet_ref: str | None = None,
    source_dry_run_result_ref: str | None = None,
    mode: str = "explicit_operator_write",
    created_at: str | None = None,
) -> dict[str, Any]:
    """Write fixture-only sidecar files and return the write receipt.

    Blocked inputs return a receipt with no fixture files written. Only safe
    temp/output directories named ``decision_work`` are eligible for writes.
    """

    packet_ref = source_sidecar_update_packet_ref or _safe_ref(
        _resolve(sidecar_update_packet_path)
    )
    dry_run_ref = source_dry_run_result_ref or (
        _safe_ref(_resolve(dry_run_result_path)) if dry_run_result_path else None
    )
    packet_text, packet, packet_error = _load_optional_json_text(
        sidecar_update_packet_path,
    )
    dry_text, dry_run, dry_error = (
        _load_optional_json_text(dry_run_result_path)
        if dry_run_result_path is not None
        else ("", None, "not_found")
    )

    blockers: list[str] = []
    if mode != "explicit_operator_write":
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

    packet_mapping = _mapping(packet)
    dry_mapping = _mapping(dry_run)
    blockers.extend(_sidecar_update_packet_blockers(packet_mapping))
    blockers.extend(_dry_run_result_blockers(dry_mapping))
    blockers.extend(_source_match_blockers(packet_mapping, dry_mapping))
    target_blocker = _target_sidecar_dir_blocker(target_sidecar_dir)
    if target_blocker:
        blockers.append(target_blocker)

    blockers = _dedupe(blockers)
    write_status = _write_status(blockers, packet_mapping, dry_mapping)
    write_ready = write_status in {WRITE_COMPLETED_STATUS, WRITE_COMPLETED_BLOCKED_STATUS}
    files_written: list[str] = []
    target_ref = _target_sidecar_dir_ref(target_sidecar_dir)

    receipt = {
        "schema_version": EXPLICIT_OPERATOR_WRITE_RECEIPT_SCHEMA_VERSION,
        "write_metadata": {
            "created_at": created_at or _utc_now(),
            "generated_by": "decision_work_explicit_operator_sidecar_write",
            "mode": mode,
            "adapter_scope": "fixture_only_explicit_operator_write",
            "model_calls": 0,
            "runtime_invoked": False,
            "skill_invoked": False,
            "runtime_wiring_changed": False,
            "real_archive_mutated": False,
            "historical_archive_mutated": False,
        },
        "source_case": dict(_mapping(packet_mapping.get("source_case"))),
        "source_sidecar_update_packet_ref": packet_ref,
        "source_dry_run_result_ref": dry_run_ref,
        "target_sidecar_dir_ref": target_ref,
        "write_status": write_status,
        "files_written": files_written,
        "blocker_reasons": blockers,
        "mode": mode,
        "operator_explicit_write_required": True,
        "fixture_only": True,
        "actual_sidecar_write_performed": write_ready,
        "real_archive_mutated": False,
        "historical_archive_mutated": False,
        "runtime_wiring_changed": False,
        "resolver_refs_approved": False,
        "can_authorize_agent_action": False,
        "can_authorize_automatic_action": False,
        "can_be_used_as_quality_label": False,
        "product_proof": False,
        "human_validated": False,
        "answer_quality_scored": False,
        "advice_correctness_claimed": False,
        "source_refs": _source_refs(packet_mapping, packet_ref),
        "privacy_summary": dict(_mapping(packet_mapping.get("privacy_summary"))),
        "uncertainty_summary": dict(
            _mapping(packet_mapping.get("uncertainty_summary"))
        ),
        "custody_flags": _custody_flags(write_ready=write_ready),
        "non_claims": list(NON_CLAIMS),
        "downstream_allowed": {
            "can_feed_explicit_operator_sidecar_write_review": write_ready,
            "can_write_controlled_fixture_sidecar": write_ready,
            "can_write_real_archive_sidecar": False,
            "can_mutate_historical_archive": False,
            "can_wire_runtime": False,
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
            "write_historical_archive",
            "wire_runtime",
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
        files_written = write_explicit_operator_sidecar_files(
            target_sidecar_dir=target_sidecar_dir,
            receipt=receipt,
            sidecar_update_packet=packet_mapping,
            dry_run_result=dry_mapping,
        )
        receipt["files_written"] = files_written
        receipt["custody_flags"] = _custody_flags(write_ready=True)

    return receipt


def render_explicit_operator_sidecar_write_json(
    result: Mapping[str, Any],
    *,
    pretty: bool = False,
) -> str:
    """Render an explicit operator sidecar write receipt as stable JSON."""

    if pretty:
        return json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return json.dumps(result, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"


def write_explicit_operator_sidecar_write_receipt(path: Path | str, payload: str) -> None:
    """Write a receipt JSON, refusing sidecar/archive-looking output paths."""

    output = Path(path).expanduser()
    if _path_targets_archive_or_runtime(output) or "decision_work" in output.parts:
        raise DecisionWorkExplicitOperatorSidecarWriteError(
            "receipt output must not target an archive or decision_work sidecar path"
        )
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    except OSError as exc:
        raise DecisionWorkExplicitOperatorSidecarWriteError(
            f"receipt output could not be written:{type(exc).__name__}"
        ) from exc


def write_explicit_operator_sidecar_files(
    *,
    target_sidecar_dir: Path | str,
    receipt: Mapping[str, Any],
    sidecar_update_packet: Mapping[str, Any],
    dry_run_result: Mapping[str, Any],
) -> list[str]:
    """Write sidecar-shaped files under the explicit safe fixture directory."""

    blocker = _target_sidecar_dir_blocker(target_sidecar_dir)
    if blocker:
        raise DecisionWorkExplicitOperatorSidecarWriteError(
            "target sidecar directory is not a safe fixture/output directory"
        )
    base = Path(target_sidecar_dir).expanduser()
    payloads = _sidecar_payloads(receipt, sidecar_update_packet, dry_run_result)
    try:
        base.mkdir(parents=True, exist_ok=True)
        resolved_base = base.resolve(strict=False)
        written: list[str] = []
        for name in ALLOWED_FILE_NAMES:
            target = base / name
            resolved_target = target.resolve(strict=False)
            try:
                resolved_target.relative_to(resolved_base)
            except ValueError as exc:
                raise DecisionWorkExplicitOperatorSidecarWriteError(
                    "sidecar file escaped target sidecar directory"
                ) from exc
            target.write_text(payloads[name], encoding="utf-8")
            written.append(name)
    except OSError as exc:
        raise DecisionWorkExplicitOperatorSidecarWriteError(
            f"sidecar files could not be written:{type(exc).__name__}"
        ) from exc
    return written


def _sidecar_update_packet_blockers(packet: Mapping[str, Any]) -> list[str]:
    if not packet:
        return []
    blockers: list[str] = []
    if packet.get("schema_version") != SIDECAR_UPDATE_PACKET_SCHEMA_VERSION:
        blockers.append("sidecar_update_packet_schema_invalid")
    status = _text(packet.get("sidecar_update_packet_status"))
    if status not in {READY_SIDECAR_UPDATE_STATUS, RUNTIME_BLOCK_SIDECAR_UPDATE_STATUS}:
        blockers.append(f"sidecar_update_packet_not_write_eligible:{status or 'missing'}")
    if packet.get("blocker_reasons") not in ([], None):
        blockers.append("sidecar_update_packet_has_blockers")
    if _any_true_flag(packet, RUNTIME_WRITE_FLAGS):
        blockers.append("runtime_or_archive_write_attempt_detected")
    if _any_true_flag(packet, AUTHORITY_FLAGS):
        blockers.append("authority_claim_detected")
    downstream = _mapping(packet.get("downstream_allowed"))
    expected_false_fields = (
        "can_update_sidecar",
        "can_write_decision_work_directory",
        "can_mutate_archive",
        "can_wire_runtime",
        "resolver_refs_approved",
        "can_authorize_agent_action",
        "can_authorize_automatic_action",
        "can_be_used_as_quality_label",
        "product_proof",
        "human_validated",
        "answer_quality_scored",
        "advice_correctness_claimed",
    )
    for field in expected_false_fields:
        if downstream.get(field) is not False:
            blockers.append(f"{field}_not_false")
    privacy_summary = _mapping(packet.get("privacy_summary"))
    if privacy_summary.get("privacy_marker_detected") is True:
        blockers.append("privacy_marker_detected")
    if privacy_summary.get("local_absolute_path_detected") is True:
        blockers.append("local_absolute_path_detected")
    source_refs = _source_refs(packet, _text(packet.get("source_ref")))
    required_refs = (
        "source_resolver_supply_ref",
        "source_generated_read_ref",
        "source_intake_ref",
        "source_brief_supply_ref",
        "source_rendered_brief_ref",
        "source_triage_supply_ref",
        "source_triage_ref",
    )
    for field in required_refs:
        if not source_refs.get(field):
            blockers.append(f"{field}_missing")
    return blockers


def _dry_run_result_blockers(dry_run: Mapping[str, Any]) -> list[str]:
    if not dry_run:
        return []
    blockers: list[str] = []
    if dry_run.get("schema_version") != SIDECAR_WRITE_DRY_RUN_SCHEMA_VERSION:
        blockers.append("dry_run_schema_invalid")
    status = _text(dry_run.get("dry_run_status"))
    if status not in {DRY_RUN_READY_STATUS, DRY_RUN_RUNTIME_BLOCK_STATUS}:
        blockers.append(f"dry_run_not_write_eligible:{status or 'missing'}")
    if dry_run.get("blocker_reasons") not in ([], None):
        blockers.append("dry_run_has_blockers")
    if dry_run.get("actual_sidecar_write_performed") is not False:
        blockers.append("dry_run_actual_write_not_false")
    if dry_run.get("archive_mutated") is not False:
        blockers.append("dry_run_archive_mutated_not_false")
    if dry_run.get("runtime_wiring_changed") is not False:
        blockers.append("dry_run_runtime_wiring_not_false")
    if dry_run.get("resolver_refs_approved") is not False:
        blockers.append("dry_run_resolver_refs_approved_not_false")
    if dry_run.get("can_write_runtime_sidecar") is not False:
        blockers.append("dry_run_runtime_sidecar_write_not_false")
    if _any_true_flag(dry_run, AUTHORITY_FLAGS):
        blockers.append("authority_claim_detected")
    privacy_summary = _mapping(dry_run.get("privacy_summary"))
    if privacy_summary.get("privacy_marker_detected") is True:
        blockers.append("privacy_marker_detected")
    if privacy_summary.get("local_absolute_path_detected") is True:
        blockers.append("local_absolute_path_detected")
    return blockers


def _source_match_blockers(
    packet: Mapping[str, Any],
    dry_run: Mapping[str, Any],
) -> list[str]:
    if not packet or not dry_run:
        return []
    blockers: list[str] = []
    packet_status = _text(packet.get("sidecar_update_packet_status"))
    dry_status = _text(dry_run.get("dry_run_status"))
    expected_dry_status = (
        DRY_RUN_RUNTIME_BLOCK_STATUS
        if packet_status == RUNTIME_BLOCK_SIDECAR_UPDATE_STATUS
        else DRY_RUN_READY_STATUS
    )
    if dry_status != expected_dry_status:
        blockers.append("dry_run_status_does_not_match_packet")
    packet_case = _mapping(packet.get("source_case"))
    dry_case = _mapping(dry_run.get("source_case"))
    if _text(packet_case.get("case_id")) != _text(dry_case.get("case_id")):
        blockers.append("dry_run_case_does_not_match_packet")
    packet_refs = _source_refs(packet, _text(packet.get("source_ref")))
    dry_refs = _mapping(dry_run.get("source_refs"))
    for field in (
        "source_resolver_supply_ref",
        "source_generated_read_ref",
        "source_intake_ref",
        "source_brief_supply_ref",
        "source_rendered_brief_ref",
        "source_triage_supply_ref",
        "source_triage_ref",
    ):
        if _text(packet_refs.get(field)) != _text(dry_refs.get(field)):
            blockers.append(f"{field}_dry_run_mismatch")
    return blockers


def _write_status(
    blockers: list[str],
    packet: Mapping[str, Any],
    dry_run: Mapping[str, Any],
) -> str:
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
            return "blocked_dry_run_not_matching_packet"
        if blocker_set.intersection(
            {
                "target_path_not_absolute",
                "target_not_named_decision_work",
                "target_not_under_safe_temp_root",
                "target_inside_repository",
            }
        ):
            return "blocked_target_path_unsafe"
        if "target_path_targets_real_archive" in blocker_set:
            return "blocked_real_archive_path"
        if "target_path_targets_runtime" in blocker_set:
            return "blocked_runtime_path"
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
        return WRITE_COMPLETED_BLOCKED_STATUS
    return WRITE_COMPLETED_STATUS


def _sidecar_payloads(
    receipt: Mapping[str, Any],
    sidecar_update_packet: Mapping[str, Any],
    dry_run_result: Mapping[str, Any],
) -> dict[str, str]:
    write_status = _text(receipt.get("write_status"))
    source_case = dict(_mapping(receipt.get("source_case")))
    source_refs = dict(_mapping(receipt.get("source_refs")))
    non_claims = list(receipt.get("non_claims", []))
    attachment_status = {
        "schema_version": "lolla.decision_work_explicit_operator_sidecar_write.fixture_attachment_status.v0",
        "source_case": source_case,
        "write_status": write_status,
        "fixture_only": True,
        "dry_run_status": _text(dry_run_result.get("dry_run_status")),
        "sidecar_update_packet_status": _text(
            sidecar_update_packet.get("sidecar_update_packet_status")
        ),
        "actual_sidecar_write_performed": True,
        "real_archive_mutated": False,
        "historical_archive_mutated": False,
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
        "schema_version": "lolla.decision_work_explicit_operator_sidecar_write.fixture_safe_supply_summary.v0",
        "source_case": source_case,
        "source_refs": source_refs,
        "privacy_summary": dict(_mapping(receipt.get("privacy_summary"))),
        "uncertainty_summary": dict(_mapping(receipt.get("uncertainty_summary"))),
        "raw_content_included": False,
        "resolver_refs_approved": False,
        "actual_sidecar_write_performed": True,
        "fixture_only": True,
        "real_archive_mutated": False,
        "historical_archive_mutated": False,
        "runtime_wiring_changed": False,
    }
    agent_handoff_packet = {
        "schema_version": "lolla.decision_work_explicit_operator_sidecar_write.fixture_agent_handoff.v0",
        "source_case": source_case,
        "write_status": write_status,
        "fixture_only": True,
        "agent_inspection_status": dict(
            _mapping(sidecar_update_packet.get("agent_inspection_status"))
        ),
        "agent_action_authorized": False,
        "automatic_action_authorized": False,
        "actual_sidecar_write_performed": True,
        "real_archive_mutated": False,
        "historical_archive_mutated": False,
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
    write_status = _text(receipt.get("write_status"), "unknown")
    packet_status = _text(
        sidecar_update_packet.get("sidecar_update_packet_status"),
        "unknown",
    )
    return "\n".join(
        [
            "# Decision Work Explicit Operator Sidecar Write Fixture",
            "",
            f"Source case: `{case_id}`",
            f"Fixture write status: `{write_status}`",
            f"Source packet status: `{packet_status}`",
            "",
            "This is a controlled fixture/output write only.",
            "",
            "- actual sidecar write performed: true, fixture only",
            "- real archive mutated: false",
            "- historical archive mutated: false",
            "- runtime wiring changed: false",
            "- resolver refs approved: false",
            "- agent or automatic action authorized: false",
            "",
            "The fixture files do not prove correctness, human validation,",
            "product value, answer quality, or permission to act.",
            "",
        ]
    )


def _source_refs(
    packet: Mapping[str, Any],
    packet_ref: str | None,
) -> dict[str, Any]:
    nested = _mapping(packet.get("source_refs"))
    return {
        "source_sidecar_update_packet_ref": packet_ref,
        "source_resolver_supply_ref": _text(packet.get("source_resolver_supply_ref"))
        or _text(nested.get("source_resolver_supply_ref")),
        "source_generated_read_ref": _text(nested.get("source_generated_read_ref")),
        "source_intake_ref": _text(nested.get("source_intake_ref")),
        "source_brief_supply_ref": _text(nested.get("source_brief_supply_ref")),
        "source_rendered_brief_ref": _text(nested.get("source_rendered_brief_ref")),
        "source_triage_supply_ref": _text(nested.get("source_triage_supply_ref")),
        "source_triage_ref": _text(nested.get("source_triage_ref")),
        "raw_content_included": False,
    }


def _custody_flags(*, write_ready: bool) -> dict[str, Any]:
    return {
        "model_calls": 0,
        "runtime_invoked": False,
        "skill_invoked": False,
        "actual_sidecar_write_performed": write_ready,
        "fixture_only": True,
        "real_archive_mutated": False,
        "historical_archive_mutated": False,
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


def _target_sidecar_dir_blocker(path: Path | str) -> str | None:
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        return "target_path_not_absolute"
    if candidate.name != "decision_work":
        return "target_not_named_decision_work"
    if _path_targets_archive_or_runtime(candidate):
        parts = {part.lower() for part in candidate.parts}
        if parts.intersection(RUNTIME_PATH_MARKER_PARTS):
            return "target_path_targets_runtime"
        return "target_path_targets_real_archive"
    try:
        candidate.resolve(strict=False).relative_to(REPO_ROOT)
        return "target_inside_repository"
    except ValueError:
        pass
    if not _path_under_safe_temp_root(candidate):
        return "target_not_under_safe_temp_root"
    return None


def _path_targets_archive_or_runtime(path: Path) -> bool:
    parts = {part.lower() for part in path.parts}
    return bool(
        parts.intersection(REAL_ARCHIVE_PATH_MARKER_PARTS)
        or parts.intersection(RUNTIME_PATH_MARKER_PARTS)
    )


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


def _target_sidecar_dir_ref(path: Path | str) -> str:
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


def _load_optional_json_text(
    path: Path | str | None,
) -> tuple[str, Mapping[str, Any] | None, str | None]:
    if path is None:
        return "", None, "not_found"
    candidate = _resolve(path)
    try:
        text = candidate.read_text(encoding="utf-8")
        payload = json.loads(text)
    except FileNotFoundError:
        return "", None, "not_found"
    except json.JSONDecodeError:
        return "", None, "invalid_json"
    except UnicodeDecodeError:
        return "", None, "invalid_utf8"
    except OSError as exc:
        return "", None, type(exc).__name__
    if not isinstance(payload, Mapping):
        return text, None, "not_object"
    return text, payload, None


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
        return candidate.name


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _text(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        return value
    return default


def _contains_private_marker(text: str) -> bool:
    return any(marker in text for marker in RAW_PRIVATE_MARKERS)


def _contains_local_absolute_path_marker(text: str) -> bool:
    return any(marker in text for marker in LOCAL_ABSOLUTE_PATH_MARKERS)


def _any_true_flag(value: Any, flag_names: tuple[str, ...]) -> bool:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if key in flag_names and item is True:
                return True
            if _any_true_flag(item, flag_names):
                return True
    elif isinstance(value, list):
        return any(_any_true_flag(item, flag_names) for item in value)
    return False


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _json_text(value: Mapping[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _utc_now() -> str:
    return (
        _dt.datetime.now(tz=_dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
