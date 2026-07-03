"""Offline Decision Work interpretation queue item builder.

PR180 prepares checked-in-safe queue items for future bounded interpretation.
It is deterministic and read-only: it records source refs, queue status,
privacy policy, validation requirements, downstream expectations, and
non-claims. It does not run Lolla, call models, create interpretation reads,
mutate archives, update runtime hooks, score advice, or authorize action.
"""
from __future__ import annotations

import datetime as _dt
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from engine.system_b.decision_work_brief_packets import output_path_is_inside_run_dir


QUEUE_CONTRACT_SCHEMA_VERSION = (
    "lolla.decision_work_offline_interpretation_queue_contract.v0"
)
QUEUE_ITEM_SCHEMA_VERSION = "lolla.decision_work_offline_interpretation_queue_item.v0"
SOURCE_PACKET_SCHEMA_VERSION = (
    "lolla.decision_work_conversation_interpretation_packets.v0"
)
TARGET_INTERPRETATION_READ_SCHEMA_VERSION = (
    "lolla.decision_work_conversation_interpretation_read.v0"
)
DEFAULT_CONTRACT_RELPATH = (
    "docs/conversation-understanding/"
    "decision-work-offline-interpretation-queue-contract-v0.json"
)
QUEUE_MODES = (
    "checked_in_safe_metadata_only",
    "local_private_operator",
    "disabled",
)
REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_PRIVATE_MARKERS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)
NON_CLAIMS = (
    "queue_item_is_not_interpretation",
    "queue_item_does_not_fill_semantic_fields",
    "queue_item_does_not_call_models",
    "queue_item_does_not_run_lolla",
    "queue_item_does_not_change_runtime",
    "queue_item_does_not_mutate_archives",
    "queue_item_is_not_product_proof",
    "queue_item_is_not_human_validation",
    "queue_item_does_not_score_answer_quality",
    "queue_item_does_not_validate_advice_correctness",
    "queue_item_does_not_prove_lolla_improved_the_decision",
    "queue_item_does_not_authorize_agent_action",
    "queue_item_does_not_authorize_automatic_action",
    "future_interpretation_read_required",
)


class DecisionWorkOfflineInterpretationQueueError(ValueError):
    """Sanitized offline interpretation queue builder input error."""


def build_decision_work_offline_interpretation_queue_item(
    *,
    run_dir: Path | str,
    contract_path: Path | str = DEFAULT_CONTRACT_RELPATH,
    source_packet_path: Path | str | None = None,
    mode: str = "checked_in_safe_metadata_only",
    output_destination_ref: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build a checked-in-safe offline interpretation queue item."""

    if mode not in QUEUE_MODES:
        raise DecisionWorkOfflineInterpretationQueueError("unsupported queue mode")

    contract = load_queue_contract(contract_path)
    run_path = Path(run_dir).expanduser()
    run_status, run_reason = _run_status(run_path)
    source_packet = _source_packet_status(source_packet_path)
    privacy_mode = (
        "local_private_metadata_only"
        if mode == "local_private_operator"
        else "checked_in_safe"
    )

    queue_status, reasons = _queue_status(
        mode=mode,
        run_status=run_status,
        source_packet_status=source_packet["status"],
    )
    requested_fields = _requested_fields(contract)
    checked_in_safe = mode != "local_private_operator"
    validation_requirements = _validation_requirements(contract)

    return {
        "schema_version": QUEUE_ITEM_SCHEMA_VERSION,
        "queue_metadata": {
            "queue_item_id": _queue_item_id(run_path, source_packet),
            "created_at": created_at or _utc_now(),
            "generated_by": "decision_work_offline_interpretation_queue_builder",
            "contract_ref": _safe_ref(contract_path),
            "contract_schema_version": contract["schema_version"],
            "builder_mode": "deterministic_refs_and_status_only",
        },
        "queue_mode": mode,
        "source_run_ref": {
            "run_ref": _run_ref(run_path),
            "status": run_status,
            "reason": run_reason,
            "content_included": False,
            "raw_private_content_included": False,
        },
        "source_packet_ref": {
            "input_ref": source_packet["ref"],
            "status": source_packet["status"],
            "schema_version": source_packet.get("schema_version"),
            "reason": source_packet["reason"],
            "content_included": False,
            "raw_private_content_included": False,
            "source_mode": (
                "checked_in_safe_packet_ref"
                if source_packet["status"] == "available"
                else "not_available"
            ),
        },
        "allowed_source_refs": _allowed_source_refs(source_packet),
        "requested_interpretation_fields": requested_fields,
        "privacy_mode": privacy_mode,
        "custody_flags": _custody_flags(checked_in_safe=checked_in_safe),
        "queue_status": queue_status,
        "blocked_or_deferred_reasons": reasons,
        "output_destinations": _output_destinations(output_destination_ref),
        "validation_requirements": validation_requirements,
        "downstream_refs": _downstream_refs(),
        "known_limits": _known_limits(queue_status=queue_status, mode=mode),
        "semantic_fields_filled": False,
        "non_claims": list(NON_CLAIMS),
    }


def render_decision_work_offline_interpretation_queue_item_json(
    item: Mapping[str, Any],
    *,
    pretty: bool = False,
) -> str:
    """Render an offline interpretation queue item as stable JSON."""

    if pretty:
        return json.dumps(item, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return json.dumps(
        item,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ) + "\n"


def validate_output_path(*, output_path: Path | str, run_dir: Path | str) -> Path:
    """Validate output location without touching the run archive."""

    if output_path_is_inside_run_dir(output_path=output_path, run_dir=run_dir):
        raise DecisionWorkOfflineInterpretationQueueError(
            "output path must be outside run directory"
        )
    output = Path(output_path).expanduser()
    if output.exists() and output.is_dir():
        raise DecisionWorkOfflineInterpretationQueueError(
            "output path is a directory"
        )
    return output


def write_decision_work_offline_interpretation_queue_output(
    path: Path | str,
    payload: str,
) -> None:
    """Write rendered queue item JSON."""

    output = Path(path).expanduser()
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    except OSError as exc:
        raise DecisionWorkOfflineInterpretationQueueError(
            f"output could not be written:{type(exc).__name__}"
        ) from exc


def load_queue_contract(path: Path | str) -> dict[str, Any]:
    """Load and validate the PR179 queue contract."""

    payload = _load_json_object(path, description="queue contract JSON")
    if payload.get("schema_version") != QUEUE_CONTRACT_SCHEMA_VERSION:
        raise DecisionWorkOfflineInterpretationQueueError(
            "queue contract schema version was unsupported"
        )
    _validation_requirements(payload)
    return payload


def _queue_status(
    *,
    mode: str,
    run_status: str,
    source_packet_status: str,
) -> tuple[str, list[str]]:
    if mode == "disabled":
        return "not_requested", []
    if source_packet_status == "blocked_privacy_risk":
        return "blocked_privacy_risk", ["privacy_marker_detected"]
    if source_packet_status == "blocked_schema_invalid":
        return "blocked_schema_invalid", ["source_packet_schema_invalid"]
    if run_status != "available":
        return "blocked_missing_packet", ["source_run_unavailable"]
    if mode == "local_private_operator":
        return "requires_local_private_operator", ["local_private_context_required"]
    if source_packet_status == "available":
        return "queued", []
    return "blocked_missing_packet", ["missing_source_packet"]


def _run_status(run_path: Path) -> tuple[str, str]:
    if not run_path.exists() or not run_path.is_dir():
        return "missing", "run_directory_not_found"
    return "available", "completed_run_ref_available"


def _source_packet_status(path: Path | str | None) -> dict[str, Any]:
    if path is None:
        return {
            "ref": None,
            "status": "missing",
            "schema_version": None,
            "reason": "source_packet_not_supplied",
            "payload": None,
        }
    packet_path = Path(path).expanduser()
    ref = _safe_ref(packet_path)
    if not packet_path.exists() or not packet_path.is_file():
        return {
            "ref": ref,
            "status": "missing",
            "schema_version": None,
            "reason": "source_packet_not_found",
            "payload": None,
        }
    try:
        text = packet_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return {
            "ref": ref,
            "status": "blocked_schema_invalid",
            "schema_version": None,
            "reason": "source_packet_not_utf8",
            "payload": None,
        }
    if _contains_private_marker(text):
        return {
            "ref": ref,
            "status": "blocked_privacy_risk",
            "schema_version": None,
            "reason": "privacy_marker_detected",
            "payload": None,
        }
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {
            "ref": ref,
            "status": "blocked_schema_invalid",
            "schema_version": None,
            "reason": "source_packet_json_invalid",
            "payload": None,
        }
    if not isinstance(payload, dict):
        return {
            "ref": ref,
            "status": "blocked_schema_invalid",
            "schema_version": None,
            "reason": "source_packet_not_object",
            "payload": None,
        }
    schema = _text(payload.get("schema_version"))
    if schema != SOURCE_PACKET_SCHEMA_VERSION:
        return {
            "ref": ref,
            "status": "blocked_schema_invalid",
            "schema_version": schema or None,
            "reason": "unsupported_source_packet_schema",
            "payload": None,
        }
    return {
        "ref": ref,
        "status": "available",
        "schema_version": schema,
        "reason": "source_packet_schema_supported",
        "payload": payload,
    }


def _allowed_source_refs(source_packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    payload = source_packet.get("payload")
    if not isinstance(payload, Mapping):
        return []

    refs: list[dict[str, Any]] = []
    seen: set[str] = set()
    for record in _list_of_mappings(payload.get("source_inventory")):
        ref = _first_text(
            record,
            (
                "artifact",
                "artifact_ref",
                "input_ref",
                "source_ref",
                "ref",
                "input_id",
            ),
        )
        safe = _safe_relative_or_name(ref)
        if safe and safe not in seen:
            seen.add(safe)
            refs.append(
                {
                    "ref": safe,
                    "source_mode": "checked_in_safe_packet_ref",
                    "content_included": False,
                    "raw_private_content_included": False,
                }
            )

    if source_packet.get("ref") and source_packet["ref"] not in seen:
        refs.insert(
            0,
            {
                "ref": source_packet["ref"],
                "source_mode": "checked_in_safe_packet_ref",
                "content_included": False,
                "raw_private_content_included": False,
            },
        )
    return refs


def _requested_fields(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    fields = []
    for field in _list_of_mappings(contract.get("requested_interpretation_fields")):
        fields.append(
            {
                "field_name": _text(field.get("field_name"), "unknown_field"),
                "target_schema_ref": TARGET_INTERPRETATION_READ_SCHEMA_VERSION,
                "source_refs_required": bool(field.get("source_refs_required", True)),
                "uncertainty_required": bool(field.get("uncertainty_required", True)),
                "semantic_field_filled": False,
                "value": None,
                "interpretation_status": "requested_not_filled",
                "must_not_be_used_as_quality_label": True,
            }
        )
    return fields


def _validation_requirements(contract: Mapping[str, Any]) -> list[str]:
    requirements = contract.get("validation_requirements")
    if not isinstance(requirements, list) or not all(
        isinstance(item, str) and item for item in requirements
    ):
        raise DecisionWorkOfflineInterpretationQueueError(
            "queue contract validation requirements were missing or malformed"
        )
    return list(requirements)


def _output_destinations(output_destination_ref: str | None) -> dict[str, Any]:
    return {
        "interpretation_read_ref": (
            _safe_relative_or_name(output_destination_ref)
            if output_destination_ref
            else None
        ),
        "interpretation_read_schema": TARGET_INTERPRETATION_READ_SCHEMA_VERSION,
        "output_status": "not_created",
        "archive_mutation_required": False,
        "runtime_sidecar_update_required": False,
    }


def _downstream_refs() -> dict[str, Any]:
    return {
        "expected_interpretation_read_schema": (
            TARGET_INTERPRETATION_READ_SCHEMA_VERSION
        ),
        "expected_brief_render": "future_decision_work_brief_render",
        "expected_enrichment": "future_decision_work_brief_enrichment",
        "expected_triage": "future_decision_work_automatic_triage_read",
        "expected_resolver_feed": (
            "lolla.decision_work_brief_runtime_safe_supply_resolver.v0"
        ),
        "downstream_outputs_created": False,
    }


def _known_limits(*, queue_status: str, mode: str) -> list[str]:
    limits = [
        "queue_item_records_refs_and_status_only",
        "semantic_interpretation_not_performed",
        "interpretation_read_not_created",
        "brief_enrichment_triage_not_created",
        "runtime_sidecar_not_updated",
        "future_validation_required_before_resolver_feed",
    ]
    if queue_status == "blocked_missing_packet":
        limits.append("source_packet_missing_or_run_unavailable")
    if mode == "local_private_operator":
        limits.append("local_private_operator_required")
    return limits


def _custody_flags(*, checked_in_safe: bool) -> dict[str, Any]:
    return {
        "runtime_invoked": False,
        "skill_invoked": False,
        "archive_mutated": False,
        "model_calls": 0,
        "human_validated": False,
        "product_proof": False,
        "answer_quality_scored": False,
        "agent_action_authorized": False,
        "automatic_action_authorized": False,
        "raw_private_content_included": False,
        "provider_text_included": False,
        "private_ledgers_included": False,
        "raw_transcript_included": False,
        "raw_revised_answer_included": False,
        "raw_memo_included": False,
        "local_absolute_paths_included": False,
        "semantic_fields_filled": False,
        "queue_runner_invoked": False,
        "checked_in_safe": checked_in_safe,
    }


def _queue_item_id(run_path: Path, source_packet: Mapping[str, Any]) -> str:
    packet_ref = _text(source_packet.get("ref"), "missing_packet")
    return f"decision_work_offline_interpretation_queue:{_run_ref(run_path)}:{_safe_slug(packet_ref)}"


def _load_json_object(path: Path | str, *, description: str) -> dict[str, Any]:
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    try:
        payload = json.loads(candidate.read_text(encoding="utf-8"))
    except OSError as exc:
        raise DecisionWorkOfflineInterpretationQueueError(
            f"{description} could not be read"
        ) from exc
    except json.JSONDecodeError as exc:
        raise DecisionWorkOfflineInterpretationQueueError(
            f"{description} was not valid JSON"
        ) from exc
    if not isinstance(payload, dict):
        raise DecisionWorkOfflineInterpretationQueueError(
            f"{description} must be a JSON object"
        )
    return payload


def _safe_ref(path: Path | str | None) -> str | None:
    if path is None:
        return None
    candidate = Path(path).expanduser()
    try:
        return str(candidate.resolve(strict=False).relative_to(REPO_ROOT))
    except ValueError:
        return candidate.name


def _run_ref(run_path: Path) -> str:
    parts = [part for part in run_path.parts if part]
    if len(parts) >= 2:
        return f"{_safe_slug(parts[-2])}/{_safe_slug(parts[-1])}"
    return _safe_slug(run_path.name)


def _safe_relative_or_name(value: Any) -> str | None:
    text = _text(value)
    if not text:
        return None
    candidate = Path(text)
    if candidate.is_absolute():
        return candidate.name
    cleaned = re.sub(r"[^A-Za-z0-9_./=-]+", "-", text).strip("-")
    return cleaned or None


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.=-]+", "-", value).strip("-")
    return slug or "unknown"


def _contains_private_marker(text: str) -> bool:
    return any(marker in text for marker in RAW_PRIVATE_MARKERS)


def _first_text(record: Mapping[str, Any], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = record.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _list_of_mappings(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _text(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        return value
    return default


def _utc_now() -> str:
    return (
        _dt.datetime.now(tz=_dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
