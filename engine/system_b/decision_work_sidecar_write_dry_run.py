"""Default-off dry-run adapter for Decision Work sidecar writes.

PR206 simulates what a future sidecar write would do from a PR202 proposed
sidecar update packet. It may write a preview only under an explicit caller
supplied preview directory. It never writes archive sidecars, mutates archives,
approves resolver refs, wires runtime, calls models, scores answer quality, or
authorizes action.
"""
from __future__ import annotations

import datetime as _dt
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any


SIDECAR_WRITE_DRY_RUN_SCHEMA_VERSION = "lolla.decision_work_sidecar_write_dry_run.v0"
SIDECAR_UPDATE_PACKET_SCHEMA_VERSION = (
    "lolla.decision_work_resolver_candidate_sidecar_update_packet.v0"
)
READY_SIDECAR_UPDATE_STATUS = "ready_for_sidecar_update_packet"
RUNTIME_BLOCK_SIDECAR_UPDATE_STATUS = "packet_with_runtime_block"
DRY_RUN_READY_STATUS = "dry_run_ready"
DRY_RUN_RUNTIME_BLOCK_STATUS = "dry_run_packet_with_runtime_block"
REPO_ROOT = Path(__file__).resolve().parents[2]

PREVIEW_FILE_NAMES = (
    "attachment_status.json",
    "user_receipt.md",
    "agent_handoff_packet.json",
    "safe_supply_summary.json",
    "sidecar_update_packet.json",
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
ARCHIVE_PATH_MARKER_PARTS = {
    "archive",
    "archives",
    "completed-run",
    "completed-runs",
    "completed_runs",
    "run_archive",
    "run_archives",
}
RUNTIME_WRITE_FLAGS = (
    "actual_sidecar_write_performed",
    "archive_mutated",
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
    "dry_run_is_not_an_actual_sidecar_write",
    "dry_run_does_not_write_decision_work_directory",
    "dry_run_does_not_mutate_archives",
    "dry_run_does_not_approve_resolver_refs",
    "dry_run_does_not_mark_resolver_refs_usable",
    "dry_run_does_not_wire_runtime",
    "dry_run_does_not_call_models",
    "dry_run_is_not_product_proof",
    "dry_run_is_not_human_validation",
    "dry_run_does_not_score_answer_quality",
    "dry_run_does_not_validate_advice_correctness",
    "dry_run_does_not_authorize_agent_action",
    "dry_run_does_not_authorize_automatic_action",
)


class DecisionWorkSidecarWriteDryRunError(ValueError):
    """Sanitized sidecar write dry-run input/output error."""


def build_sidecar_write_dry_run(
    *,
    sidecar_update_packet_path: Path | str,
    source_sidecar_update_packet_ref: str | None = None,
    preview_dir: Path | str | None = None,
    write_preview: bool = False,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build a dry-run result from a proposed sidecar update packet."""

    packet_ref = source_sidecar_update_packet_ref or _safe_ref(
        _resolve(sidecar_update_packet_path)
    )
    packet_text, packet, packet_error = _load_optional_json_text(
        sidecar_update_packet_path,
        "sidecar update packet",
    )
    blockers: list[str] = []
    if packet_error == "not_found":
        blockers.append("sidecar_update_packet_missing")
    elif packet_error:
        blockers.append(f"sidecar_update_packet_unreadable:{packet_error}")
    if packet_text and _contains_private_marker(packet_text):
        blockers.append("privacy_marker_detected")
    if packet_text and _contains_local_absolute_path_marker(packet_text):
        blockers.append("local_absolute_path_detected")

    preview_blocker = _preview_dir_blocker(preview_dir)
    if preview_blocker:
        blockers.append(preview_blocker)

    packet_mapping = _mapping(packet)
    blockers.extend(_sidecar_update_packet_blockers(packet_mapping))
    blockers = _dedupe(blockers)
    dry_run_status = _dry_run_status(blockers, packet_mapping)
    dry_run_ready = dry_run_status in {
        DRY_RUN_READY_STATUS,
        DRY_RUN_RUNTIME_BLOCK_STATUS,
    }
    would_write_files = list(PREVIEW_FILE_NAMES) if dry_run_ready else []
    preview_files_written: list[str] = []

    result = {
        "schema_version": SIDECAR_WRITE_DRY_RUN_SCHEMA_VERSION,
        "dry_run_metadata": {
            "created_at": created_at or _utc_now(),
            "generated_by": "decision_work_sidecar_write_dry_run",
            "mode": "dry_run_only",
            "model_calls": 0,
            "runtime_invoked": False,
            "skill_invoked": False,
            "archive_mutated": False,
            "actual_sidecar_write_performed": False,
            "runtime_wiring_changed": False,
        },
        "source_case": dict(_mapping(packet_mapping.get("source_case"))),
        "source_sidecar_update_packet_ref": packet_ref,
        "dry_run_status": dry_run_status,
        "blocker_reasons": blockers,
        "would_write_files": would_write_files,
        "preview_files_written": preview_files_written,
        "preview_scope": {
            "preview_dir_supplied": preview_dir is not None,
            "preview_written": False,
            "preview_is_explicit_output_dir_only": True,
            "preview_is_archive_sidecar": False,
            "preview_is_runtime_sidecar": False,
        },
        "actual_sidecar_write_performed": False,
        "archive_mutated": False,
        "runtime_wiring_changed": False,
        "resolver_refs_approved": False,
        "can_write_runtime_sidecar": False,
        "can_authorize_agent_action": False,
        "can_authorize_automatic_action": False,
        "source_refs": _source_refs(packet_mapping, packet_ref),
        "privacy_summary": dict(_mapping(packet_mapping.get("privacy_summary"))),
        "uncertainty_summary": dict(
            _mapping(packet_mapping.get("uncertainty_summary"))
        ),
        "custody_flags": _custody_flags(),
        "non_claims": list(NON_CLAIMS),
        "downstream_allowed": {
            "can_feed_sidecar_write_dry_run_review": dry_run_ready,
            "can_write_runtime_sidecar": False,
            "can_write_decision_work_directory": False,
            "can_mutate_archive": False,
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
            "write_decision_work_sidecar",
            "write_runtime_sidecar",
            "mutate_archives",
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

    if write_preview and preview_dir is not None and dry_run_ready:
        preview_files_written = write_sidecar_write_dry_run_preview(
            preview_dir=preview_dir,
            dry_run_result=result,
            sidecar_update_packet=packet_mapping,
        )
        result["preview_files_written"] = preview_files_written
        result["preview_scope"] = {
            **dict(_mapping(result["preview_scope"])),
            "preview_written": bool(preview_files_written),
        }

    return result


def render_sidecar_write_dry_run_json(
    result: Mapping[str, Any],
    *,
    pretty: bool = False,
) -> str:
    """Render a sidecar write dry-run result as stable JSON."""

    if pretty:
        return json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return json.dumps(result, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"


def write_sidecar_write_dry_run_result(path: Path | str, payload: str) -> None:
    """Write the dry-run result JSON, refusing sidecar-looking outputs."""

    output = Path(path).expanduser()
    if _path_targets_sidecar_or_archive(output):
        raise DecisionWorkSidecarWriteDryRunError(
            "output path must not target an archive or decision_work sidecar directory"
        )
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    except OSError as exc:
        raise DecisionWorkSidecarWriteDryRunError(
            f"output could not be written:{type(exc).__name__}"
        ) from exc


def write_sidecar_write_dry_run_preview(
    *,
    preview_dir: Path | str,
    dry_run_result: Mapping[str, Any],
    sidecar_update_packet: Mapping[str, Any],
) -> list[str]:
    """Write dry-run preview files only under the explicit preview directory."""

    blocker = _preview_dir_blocker(preview_dir)
    if blocker:
        raise DecisionWorkSidecarWriteDryRunError(
            "preview directory must not target an archive or decision_work sidecar"
        )
    base = Path(preview_dir).expanduser()
    payloads = _preview_payloads(dry_run_result, sidecar_update_packet)
    try:
        base.mkdir(parents=True, exist_ok=True)
        written: list[str] = []
        for name in PREVIEW_FILE_NAMES:
            target = base / name
            resolved_target = target.resolve(strict=False)
            resolved_base = base.resolve(strict=False)
            try:
                resolved_target.relative_to(resolved_base)
            except ValueError as exc:
                raise DecisionWorkSidecarWriteDryRunError(
                    "preview file escaped preview directory"
                ) from exc
            target.write_text(payloads[name], encoding="utf-8")
            written.append(name)
    except OSError as exc:
        raise DecisionWorkSidecarWriteDryRunError(
            f"preview could not be written:{type(exc).__name__}"
        ) from exc
    return written


def _sidecar_update_packet_blockers(packet: Mapping[str, Any]) -> list[str]:
    if not packet:
        return []
    blockers: list[str] = []
    if packet.get("schema_version") != SIDECAR_UPDATE_PACKET_SCHEMA_VERSION:
        blockers.append("sidecar_update_packet_schema_invalid")
    status = _text(packet.get("sidecar_update_packet_status"))
    if status not in {
        READY_SIDECAR_UPDATE_STATUS,
        RUNTIME_BLOCK_SIDECAR_UPDATE_STATUS,
    }:
        if status == "requires_operator_repair":
            blockers.append("requires_operator_repair")
        else:
            blockers.append(f"sidecar_update_packet_not_ready:{status or 'missing'}")
    if packet.get("blocker_reasons") not in ([], None):
        blockers.append("sidecar_update_packet_has_blockers")
    if _any_true_flag(packet, RUNTIME_WRITE_FLAGS):
        blockers.append("actual_write_attempt_detected")
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


def _dry_run_status(
    blockers: list[str],
    packet: Mapping[str, Any],
) -> str:
    if blockers:
        blocker_set = set(blockers)
        if "preview_dir_targets_archive_or_sidecar" in blocker_set:
            return "blocked_archive_path"
        if blocker_set.intersection(
            {
                "sidecar_update_packet_missing",
                "sidecar_update_packet_schema_invalid",
            }
        ) or any(
            item.startswith("sidecar_update_packet_unreadable:") for item in blockers
        ):
            return "blocked_not_sidecar_update_packet"
        if blocker_set.intersection(
            {
                "privacy_marker_detected",
                "local_absolute_path_detected",
            }
        ):
            return "blocked_privacy_risk"
        write_not_false = {
            "can_update_sidecar_not_false",
            "can_write_decision_work_directory_not_false",
            "can_mutate_archive_not_false",
            "can_wire_runtime_not_false",
        }
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
        if "actual_write_attempt_detected" in blocker_set or blocker_set.intersection(
            write_not_false
        ):
            return "blocked_actual_write_attempt"
        if "authority_claim_detected" in blocker_set or blocker_set.intersection(
            authority_not_false
        ):
            return "blocked_authority_claim"
        if "requires_operator_repair" in blocker_set:
            return "requires_operator_repair"
        if any(item.endswith("_missing") for item in blockers):
            return "blocked_missing_required_fields"
        return "blocked_not_sidecar_update_packet"
    status = _text(packet.get("sidecar_update_packet_status"))
    if status == RUNTIME_BLOCK_SIDECAR_UPDATE_STATUS:
        return DRY_RUN_RUNTIME_BLOCK_STATUS
    return DRY_RUN_READY_STATUS


def _preview_payloads(
    dry_run_result: Mapping[str, Any],
    sidecar_update_packet: Mapping[str, Any],
) -> dict[str, str]:
    status = _text(dry_run_result.get("dry_run_status"))
    source_case = dict(_mapping(dry_run_result.get("source_case")))
    source_refs = dict(_mapping(dry_run_result.get("source_refs")))
    non_claims = list(dry_run_result.get("non_claims", []))
    attachment_status = {
        "schema_version": "lolla.decision_work_sidecar_write_dry_run.preview_attachment_status.v0",
        "source_case": source_case,
        "dry_run_status": status,
        "sidecar_update_packet_status": _text(
            sidecar_update_packet.get("sidecar_update_packet_status")
        ),
        "actual_sidecar_write_performed": False,
        "archive_mutated": False,
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
        "schema_version": "lolla.decision_work_sidecar_write_dry_run.preview_safe_supply_summary.v0",
        "source_case": source_case,
        "source_refs": source_refs,
        "privacy_summary": dict(_mapping(dry_run_result.get("privacy_summary"))),
        "uncertainty_summary": dict(_mapping(dry_run_result.get("uncertainty_summary"))),
        "raw_content_included": False,
        "resolver_refs_approved": False,
        "actual_sidecar_write_performed": False,
        "archive_mutated": False,
        "runtime_wiring_changed": False,
    }
    agent_handoff_packet = {
        "schema_version": "lolla.decision_work_sidecar_write_dry_run.preview_agent_handoff.v0",
        "source_case": source_case,
        "dry_run_status": status,
        "agent_inspection_status": dict(
            _mapping(sidecar_update_packet.get("agent_inspection_status"))
        ),
        "agent_action_authorized": False,
        "automatic_action_authorized": False,
        "actual_sidecar_write_performed": False,
        "archive_mutated": False,
        "runtime_wiring_changed": False,
        "non_claims": non_claims,
    }
    receipt = _preview_receipt_markdown(dry_run_result, sidecar_update_packet)
    return {
        "attachment_status.json": _json_text(attachment_status),
        "user_receipt.md": receipt,
        "agent_handoff_packet.json": _json_text(agent_handoff_packet),
        "safe_supply_summary.json": _json_text(safe_supply_summary),
        "sidecar_update_packet.json": _json_text(dict(sidecar_update_packet)),
    }


def _preview_receipt_markdown(
    dry_run_result: Mapping[str, Any],
    sidecar_update_packet: Mapping[str, Any],
) -> str:
    case_id = _text(_mapping(dry_run_result.get("source_case")).get("case_id"), "unknown")
    status = _text(dry_run_result.get("dry_run_status"), "unknown")
    packet_status = _text(
        sidecar_update_packet.get("sidecar_update_packet_status"),
        "unknown",
    )
    return "\n".join(
        [
            "# Decision Work Sidecar Write Dry-Run Preview",
            "",
            f"Source case: `{case_id}`",
            f"Dry-run status: `{status}`",
            f"Source packet status: `{packet_status}`",
            "",
            "This preview is not a runtime sidecar write.",
            "",
            "- actual sidecar write performed: false",
            "- archive mutated: false",
            "- runtime wiring changed: false",
            "- resolver refs approved: false",
            "- agent or automatic action authorized: false",
            "",
            "The preview only shows what a future implementation would need to",
            "consider. It does not prove correctness, human validation, product",
            "value, answer quality, or permission to act.",
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
        "source_resolver_supply_ref": _text(
            packet.get("source_resolver_supply_ref")
        )
        or _text(nested.get("source_resolver_supply_ref")),
        "source_generated_read_ref": _text(nested.get("source_generated_read_ref")),
        "source_intake_ref": _text(nested.get("source_intake_ref")),
        "source_brief_supply_ref": _text(nested.get("source_brief_supply_ref")),
        "source_rendered_brief_ref": _text(nested.get("source_rendered_brief_ref")),
        "source_triage_supply_ref": _text(nested.get("source_triage_supply_ref")),
        "source_triage_ref": _text(nested.get("source_triage_ref")),
        "raw_content_included": False,
    }


def _custody_flags() -> dict[str, Any]:
    return {
        "model_calls": 0,
        "runtime_invoked": False,
        "skill_invoked": False,
        "archive_mutated": False,
        "actual_sidecar_write_performed": False,
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


def _load_optional_json_text(
    path: Path | str,
    description: str,
) -> tuple[str, Mapping[str, Any] | None, str | None]:
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


def _preview_dir_blocker(path: Path | str | None) -> str | None:
    if path is None:
        return None
    if _path_targets_sidecar_or_archive(Path(path).expanduser()):
        return "preview_dir_targets_archive_or_sidecar"
    return None


def _path_targets_sidecar_or_archive(path: Path) -> bool:
    parts = {part.lower() for part in path.parts}
    if "decision_work" in parts:
        return True
    try:
        resolved = path.resolve(strict=False)
        resolved.relative_to(REPO_ROOT)
        return bool(parts.intersection(ARCHIVE_PATH_MARKER_PARTS))
    except ValueError:
        return False


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
