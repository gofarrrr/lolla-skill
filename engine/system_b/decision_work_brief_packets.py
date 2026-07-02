"""Read-only Decision Work Brief packet construction.

PR115 prepares bounded input packets for future Decision Work Brief
interpretation. The packet builder is offline and deterministic: it records
source availability, custody flags, redaction/private status, missingness, and
non-claims. It does not run Lolla, call models, mutate archives, generate a
brief, or infer messy decision semantics from prose.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import re
import string
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from engine.system_b.decision_trail_report import RAW_ARTIFACTS_NOT_READ


DECISION_WORK_BRIEF_PACKETS_SCHEMA_VERSION = (
    "lolla.decision_work_brief_packets.v0"
)
DECISION_WORK_BRIEF_SCHEMA_VERSION = "lolla.decision_work_brief.v0"
DEFAULT_BRIEF_SCHEMA_RELPATH = (
    "docs/conversation-understanding/decision-work-brief-v0.json"
)
DEFAULT_BRIEF_PACKET_BUILDER_DOC_RELPATH = (
    "docs/conversation-understanding/decision-work-brief-packet-builder-v0.md"
)

PACKET_MODES = ("metadata_only", "local_private")
BRIEF_SECTIONS = (
    "decision",
    "starting_direction",
    "what_lolla_pressed_on",
    "what_changed",
    "what_this_means_for_action",
    "what_still_might_be_wrong",
    "what_was_not_proven",
    "evidence_receipt",
)
STRUCTURED_RUNTIME_ARTIFACTS = (
    ("agent_result.json", "structured_runtime_artifact", "agent_handoff"),
    ("evaluation.json", "evaluation_artifact", "deterministic_evaluation"),
    ("reasoning_trace.json", "structured_runtime_artifact", "reasoning_trace"),
    ("extraction.json", "structured_runtime_artifact", "extraction"),
    ("result.json", "audit_artifact", "audit_pipeline"),
    ("memo_note.json", "generated_runtime_artifact", "memo_note"),
    (
        "graph_survival_report.json",
        "generated_runtime_artifact",
        "graph_survival_report",
    ),
)
OPTIONAL_REPORT_INPUTS = (
    ("decision_work_receipt", "decision_work_receipt", "decision_work_receipt"),
    ("decision_trail_report", "decision_trail_report", "decision_trail_report"),
    ("product_delta_report", "product_delta_artifact", "product_delta_report"),
)
RAW_TRANSCRIPT_ARTIFACTS = frozenset({"conversation.txt", "live_transcript.txt"})
RAW_REVISED_ARTIFACTS = frozenset({"revised.txt"})
RAW_MEMO_ARTIFACTS = frozenset({"memo.md"})
AVAILABLE_SOURCE_STATUSES = frozenset(
    {
        "available_from_structured_artifact",
        "explicit_in_source",
    }
)
UNAVAILABLE_OR_REDACTED_STATUSES = frozenset(
    {
        "not_supplied",
        "unavailable_missing_artifact",
        "unavailable_malformed_artifact",
        "available_but_redacted_in_safe_mode",
        "available_in_private_artifact_not_exported",
        "unclear",
    }
)
NON_CLAIMS = (
    "packet_is_not_a_brief",
    "packet_is_not_product_proof",
    "packet_does_not_score_answer_quality",
    "packet_does_not_authorize_agent_action",
    "packet_does_not_validate_decision_correctness",
    "missingness_is_not_negative_semantic_evidence",
    "clean_artifacts_do_not_imply_good_advice",
    "future_interpretation_required",
)

SECTION_SPECS: dict[str, dict[str, Any]] = {
    "decision": {
        "future_question": "What decision was being made?",
        "allowed_sources": (
            "extraction.json",
            "reasoning_trace.json",
            "agent_result.json",
            "decision_work_receipt",
            "decision_trail_report",
        ),
    },
    "starting_direction": {
        "future_question": (
            "What was the likely starting action or recommendation before Lolla "
            "pressure?"
        ),
        "allowed_sources": (
            "conversation.txt",
            "extraction.json",
            "reasoning_trace.json",
            "decision_trail_report",
            "product_delta_report",
        ),
    },
    "what_lolla_pressed_on": {
        "future_question": (
            "What assumption, missing gate, stakeholder, frame, uncertainty, or "
            "trade-off did Lolla pressure?"
        ),
        "allowed_sources": (
            "result.json",
            "agent_result.json",
            "graph_survival_report.json",
            "decision_work_receipt",
            "decision_trail_report",
        ),
    },
    "what_changed": {
        "future_question": (
            "What changed in action, threshold, sequence, evidence gate, stop "
            "rule, or scope?"
        ),
        "allowed_sources": (
            "revised.txt",
            "agent_result.json",
            "result.json",
            "decision_work_receipt",
            "decision_trail_report",
            "product_delta_report",
        ),
    },
    "what_this_means_for_action": {
        "future_question": "What would the decision-maker do differently now?",
        "allowed_sources": (
            "revised.txt",
            "memo.md",
            "agent_result.json",
            "decision_trail_report",
            "product_delta_report",
        ),
    },
    "what_still_might_be_wrong": {
        "future_question": (
            "What remains missing, uncertain, private, unresolved, or dependent "
            "on human judgment?"
        ),
        "allowed_sources": (
            "evaluation.json",
            "reasoning_trace.json",
            "operator.log",
            "decision_work_receipt",
            "decision_trail_report",
            "product_delta_report",
        ),
    },
    "what_was_not_proven": {
        "future_question": "What must the audit not claim?",
        "allowed_sources": (
            DEFAULT_BRIEF_SCHEMA_RELPATH,
            "decision_work_receipt",
            "decision_trail_report",
            "product_delta_report",
        ),
    },
    "evidence_receipt": {
        "future_question": (
            "What receipt, Decision Trail, Product Delta, and archive refs back "
            "this brief?"
        ),
        "allowed_sources": (
            "decision_work_receipt",
            "decision_trail_report",
            "product_delta_report",
            "agent_result.json",
            "evaluation.json",
            "reasoning_trace.json",
        ),
    },
}


class DecisionWorkBriefPacketInputError(ValueError):
    """Deterministic, sanitized packet-builder input error."""


def build_decision_work_brief_packets(
    *,
    run_dir: Path | str,
    mode: str = "metadata_only",
    include_private_text: bool = False,
    decision_work_receipt_path: Path | str | None = None,
    decision_trail_report_path: Path | str | None = None,
    product_delta_report_path: Path | str | None = None,
    created_at: str | None = None,
    max_text_chars: int = 12000,
) -> dict[str, Any]:
    """Build a ``lolla.decision_work_brief_packets.v0`` packet."""

    if mode not in PACKET_MODES:
        raise DecisionWorkBriefPacketInputError("unsupported packet mode")
    if include_private_text and mode != "local_private":
        raise DecisionWorkBriefPacketInputError(
            "include-private-text requires local_private mode"
        )
    if max_text_chars < 1:
        raise DecisionWorkBriefPacketInputError("max text chars must be positive")

    run_path = Path(run_dir).expanduser()
    if not run_path.exists():
        raise DecisionWorkBriefPacketInputError("run directory was not found")
    if not run_path.is_dir():
        raise DecisionWorkBriefPacketInputError("run directory is not a directory")

    input_refs: list[dict[str, Any]] = []
    payloads: dict[str, Mapping[str, Any]] = {}

    for artifact_name, source_kind, activity_kind in STRUCTURED_RUNTIME_ARTIFACTS:
        record, payload = _structured_source_record(
            run_path=run_path,
            artifact_name=artifact_name,
            source_kind=source_kind,
            activity_kind=activity_kind,
        )
        input_refs.append(record)
        if payload is not None:
            payloads[artifact_name] = payload

    for artifact_name, role, activity_kind, redacted_status in RAW_ARTIFACTS_NOT_READ:
        input_refs.append(
            _raw_or_private_source_record(
                run_path=run_path,
                artifact_name=artifact_name,
                role=role,
                activity_kind=activity_kind,
                redacted_status=redacted_status,
                mode=mode,
                include_private_text=include_private_text,
                max_text_chars=max_text_chars,
            )
        )

    optional_paths = {
        "decision_work_receipt": decision_work_receipt_path,
        "decision_trail_report": decision_trail_report_path,
        "product_delta_report": product_delta_report_path,
    }
    for input_id, source_kind, activity_kind in OPTIONAL_REPORT_INPUTS:
        record, payload = _optional_report_source_record(
            input_id=input_id,
            source_kind=source_kind,
            activity_kind=activity_kind,
            report_path=optional_paths[input_id],
        )
        input_refs.append(record)
        if payload is not None:
            payloads[record["artifact"]] = payload

    case_id = _case_id(payloads=payloads, run_path=run_path)
    run_id = _run_id(payloads=payloads, run_path=run_path)
    raw_private_content_included = any(
        bool(record.get("raw_private_content_included")) for record in input_refs
    )
    checked_in_safe = mode == "metadata_only" and not raw_private_content_included

    return {
        "schema_version": DECISION_WORK_BRIEF_PACKETS_SCHEMA_VERSION,
        "packet_metadata": {
            "packet_id": f"decision_work_brief_packets:{case_id}:{run_id}",
            "created_at": created_at or _utc_now_iso(),
            "case_id": case_id,
            "run_id": run_id,
            "archive_relpath": f"{case_id}/{run_id}",
            "generated_by": "decision_work_brief_packet_builder",
            "schema_version": DECISION_WORK_BRIEF_PACKETS_SCHEMA_VERSION,
            "notes": [
                "PR115 prepares source-aware input packets only; it does not generate a Decision Work Brief."
            ],
        },
        "mode": mode,
        "source_run": {
            "case_id": case_id,
            "run_id": run_id,
            "archive_relpath": f"{case_id}/{run_id}",
            "run_dir_name": _safe_identifier(run_path.name),
            "run_parent_name": _safe_identifier(run_path.parent.name),
            "local_absolute_path_included": False,
        },
        "input_refs": input_refs,
        "custody_flags": _custody_flags(
            mode=mode,
            raw_private_content_included=raw_private_content_included,
            checked_in_safe=checked_in_safe,
            input_refs=input_refs,
        ),
        "packet_sections": _packet_sections(input_refs=input_refs),
        "required_future_output": {
            "schema_version": DECISION_WORK_BRIEF_SCHEMA_VERSION,
            "schema_path": DEFAULT_BRIEF_SCHEMA_RELPATH,
            "target_sections": list(BRIEF_SECTIONS),
            "packet_builder_fills_brief": False,
            "future_interpreter_required": True,
        },
        "non_claims": list(NON_CLAIMS),
    }


def render_decision_work_brief_packets_json(
    packet: Mapping[str, Any],
    *,
    pretty: bool = False,
) -> str:
    """Render a Decision Work Brief packet as JSON."""

    if pretty:
        return json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return json.dumps(
        packet,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ) + "\n"


def output_path_is_inside_run_dir(*, output_path: Path | str, run_dir: Path | str) -> bool:
    output = Path(output_path).expanduser().resolve(strict=False)
    run_path = Path(run_dir).expanduser().resolve(strict=False)
    return output == run_path or run_path in output.parents


def validate_output_path(
    *,
    output_path: Path | str,
    run_dir: Path | str,
    mode: str = "metadata_only",
    include_private_text: bool = False,
    repo_root: Path | str | None = None,
) -> Path:
    """Validate a packet output path without touching the archive."""

    if output_path_is_inside_run_dir(output_path=output_path, run_dir=run_dir):
        raise DecisionWorkBriefPacketInputError(
            "output path must be outside run directory"
        )
    output = Path(output_path).expanduser()
    if output.exists() and output.is_dir():
        raise DecisionWorkBriefPacketInputError("output path is a directory")
    if mode == "local_private" and include_private_text and repo_root is not None:
        resolved_output = output.resolve(strict=False)
        resolved_repo = Path(repo_root).expanduser().resolve(strict=False)
        if resolved_output == resolved_repo or resolved_repo in resolved_output.parents:
            raise DecisionWorkBriefPacketInputError(
                "local-private include-text output must be outside repository"
            )
    return output


def write_decision_work_brief_packets_output(path: Path | str, payload: str) -> None:
    """Write rendered packet JSON."""

    output = Path(path).expanduser()
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    except OSError as exc:
        raise DecisionWorkBriefPacketInputError(
            f"output could not be written:{type(exc).__name__}"
        ) from exc


def _structured_source_record(
    *,
    run_path: Path,
    artifact_name: str,
    source_kind: str,
    activity_kind: str,
) -> tuple[dict[str, Any], Mapping[str, Any] | None]:
    path = run_path / artifact_name
    base = _source_record_base(
        artifact_name=artifact_name,
        source_kind=source_kind,
        activity_kind=activity_kind,
        read_status="read_safe_structured_fields",
    )
    if not path.exists():
        status = "unavailable_missing_artifact"
        return {
            **base,
            "status": status,
            "source_status": status,
            "read_status": status,
            "notes": ["Artifact was not found in the run directory."],
        }, None
    if not path.is_file():
        status = "unclear"
        return {
            **base,
            "status": status,
            "source_status": status,
            "read_status": "not_read",
            "notes": ["Path exists but is not a file; no content was read."],
        }, None

    stat = path.stat()
    try:
        text = path.read_text(encoding="utf-8")
        payload = json.loads(text)
    except json.JSONDecodeError:
        status = "unavailable_malformed_artifact"
        return {
            **base,
            "status": status,
            "source_status": status,
            "read_status": status,
            "byte_count": stat.st_size,
            "sha256": _sha256_text(text) if "text" in locals() else None,
            "notes": ["Structured JSON artifact could not be parsed."],
        }, None
    except UnicodeDecodeError:
        status = "unavailable_malformed_artifact"
        return {
            **base,
            "status": status,
            "source_status": status,
            "read_status": status,
            "byte_count": stat.st_size,
            "notes": ["Structured JSON artifact was not valid UTF-8."],
        }, None
    except OSError as exc:
        status = "unclear"
        return {
            **base,
            "status": status,
            "source_status": status,
            "read_status": "unknown",
            "byte_count": stat.st_size,
            "notes": [f"Structured JSON artifact could not be read:{type(exc).__name__}"],
        }, None

    if not isinstance(payload, dict):
        status = "unavailable_malformed_artifact"
        return {
            **base,
            "status": status,
            "source_status": status,
            "read_status": status,
            "byte_count": stat.st_size,
            "sha256": _sha256_text(text),
            "notes": ["Structured JSON artifact root was not an object."],
        }, None

    status = "available_from_structured_artifact"
    return {
        **base,
        "status": status,
        "source_status": status,
        "schema_version": _text(payload.get("schema_version")) or None,
        "sha256": _sha256_text(text),
        "byte_count": stat.st_size,
        "content_included": False,
        "notes": [
            "Safe structured metadata was read; full artifact content was not copied into the packet."
        ],
    }, payload


def _raw_or_private_source_record(
    *,
    run_path: Path,
    artifact_name: str,
    role: str,
    activity_kind: str,
    redacted_status: str,
    mode: str,
    include_private_text: bool,
    max_text_chars: int,
) -> dict[str, Any]:
    path = run_path / artifact_name
    base = _source_record_base(
        artifact_name=artifact_name,
        source_kind=role if role != "not_read" else "raw_or_private_artifact",
        activity_kind=activity_kind,
        read_status="not_read_redacted_safe_mode",
    )
    if not path.exists():
        status = "unavailable_missing_artifact"
        return {
            **base,
            "status": status,
            "source_status": status,
            "read_status": status,
            "notes": ["Artifact was not found in the run directory."],
        }
    if not path.is_file():
        status = "unclear"
        return {
            **base,
            "status": status,
            "source_status": status,
            "read_status": "not_read",
            "notes": ["Path exists but is not a file; no content was read."],
        }

    stat = path.stat()
    if mode == "metadata_only" or not include_private_text:
        read_status = (
            "not_read_redacted_safe_mode"
            if redacted_status == "available_but_redacted_in_safe_mode"
            else "not_read_private_not_exported"
        )
        return {
            **base,
            "status": redacted_status,
            "source_status": redacted_status,
            "read_status": read_status,
            "byte_count": stat.st_size,
            "notes": [
                "Artifact existence was recorded, but content was not read in this packet mode."
            ],
        }

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        status = "unavailable_malformed_artifact"
        return {
            **base,
            "status": status,
            "source_status": status,
            "read_status": status,
            "byte_count": stat.st_size,
            "notes": ["Artifact was not valid UTF-8 and content was not included."],
        }
    except OSError as exc:
        status = "unavailable_malformed_artifact"
        return {
            **base,
            "status": status,
            "source_status": status,
            "read_status": status,
            "byte_count": stat.st_size,
            "notes": [f"Artifact could not be read:{type(exc).__name__}"],
        }

    truncated = len(text) > max_text_chars
    status = "explicit_in_source"
    return {
        **base,
        "status": status,
        "source_status": status,
        "read_status": "read_complete_text_local_private",
        "byte_count": stat.st_size,
        "sha256": _sha256_text(text),
        "raw_content_read": True,
        "content_included": True,
        "raw_private_content_included": True,
        "content_excerpt": text[:max_text_chars],
        "text_truncated": truncated,
        "notes": [
            "Artifact text is included because local_private include-private-text mode was explicitly requested.",
            "Output is unsafe for commit.",
        ],
    }


def _optional_report_source_record(
    *,
    input_id: str,
    source_kind: str,
    activity_kind: str,
    report_path: Path | str | None,
) -> tuple[dict[str, Any], Mapping[str, Any] | None]:
    if report_path is None:
        return {
            **_source_record_base(
                artifact_name=f"{input_id}:not_supplied",
                source_kind=source_kind,
                activity_kind=activity_kind,
                read_status="not_supplied",
            ),
            "status": "not_supplied",
            "source_status": "not_supplied",
            "notes": [
                "Optional report path was not supplied; this is source availability, not a semantic finding."
            ],
        }, None

    path = Path(report_path).expanduser()
    artifact_name = _external_report_artifact_name(
        prefix=f"external_{input_id}",
        path=path,
    )
    base = _source_record_base(
        artifact_name=artifact_name,
        source_kind=source_kind,
        activity_kind=activity_kind,
        read_status="read_safe_structured_fields",
    )
    if not path.exists():
        status = "unavailable_missing_artifact"
        return {
            **base,
            "status": status,
            "source_status": status,
            "read_status": status,
            "notes": [
                "External report path was provided but not found.",
                "Missing optional report is source availability, not a semantic finding.",
                "local_path_not_included:true",
            ],
        }, None
    if not path.is_file():
        status = "unclear"
        return {
            **base,
            "status": status,
            "source_status": status,
            "read_status": "not_read",
            "notes": [
                "External report path exists but is not a file; no content was read.",
                "local_path_not_included:true",
            ],
        }, None

    stat = path.stat()
    try:
        text = path.read_text(encoding="utf-8")
        payload = json.loads(text)
    except json.JSONDecodeError:
        status = "unavailable_malformed_artifact"
        return {
            **base,
            "status": status,
            "source_status": status,
            "read_status": status,
            "byte_count": stat.st_size,
            "sha256": _sha256_text(text) if "text" in locals() else None,
            "notes": [
                "External structured JSON report could not be parsed.",
                "local_path_not_included:true",
            ],
        }, None
    except UnicodeDecodeError:
        status = "unavailable_malformed_artifact"
        return {
            **base,
            "status": status,
            "source_status": status,
            "read_status": status,
            "byte_count": stat.st_size,
            "notes": [
                "External structured JSON report was not valid UTF-8.",
                "local_path_not_included:true",
            ],
        }, None
    except OSError as exc:
        status = "unclear"
        return {
            **base,
            "status": status,
            "source_status": status,
            "read_status": "unknown",
            "byte_count": stat.st_size,
            "notes": [
                f"External structured JSON report could not be read:{type(exc).__name__}",
                "local_path_not_included:true",
            ],
        }, None

    if not isinstance(payload, dict):
        status = "unavailable_malformed_artifact"
        return {
            **base,
            "status": status,
            "source_status": status,
            "read_status": status,
            "byte_count": stat.st_size,
            "sha256": _sha256_text(text),
            "notes": [
                "External structured JSON report root was not an object.",
                "local_path_not_included:true",
            ],
        }, None

    status = "available_from_structured_artifact"
    return {
        **base,
        "status": status,
        "source_status": status,
        "schema_version": _text(payload.get("schema_version")) or None,
        "sha256": _sha256_text(text),
        "byte_count": stat.st_size,
        "content_included": False,
        "notes": [
            "External report path was provided; local path was not included in the packet.",
            "Safe structured metadata was read; full report content was not copied into the packet.",
        ],
    }, payload


def _source_record_base(
    *,
    artifact_name: str,
    source_kind: str,
    activity_kind: str,
    read_status: str,
) -> dict[str, Any]:
    return {
        "ref_id": _source_ref_id(artifact_name),
        "source_kind": source_kind,
        "activity_kind": activity_kind,
        "artifact": artifact_name,
        "relative_path": artifact_name if ":" not in artifact_name else None,
        "status": "not_supplied",
        "source_status": "not_supplied",
        "read_status": read_status,
        "schema_version": None,
        "sha256": None,
        "byte_count": None,
        "raw_content_read": False,
        "content_included": False,
        "raw_private_content_included": False,
        "provider_text_included": False,
        "local_absolute_path_included": False,
        "text_truncated": False,
        "content_excerpt": None,
        "notes": [],
    }


def _packet_sections(*, input_refs: list[dict[str, Any]]) -> dict[str, Any]:
    sections: dict[str, Any] = {}
    for section_id in BRIEF_SECTIONS:
        spec = SECTION_SPECS[section_id]
        relevant_refs = _records_for_allowed_sources(
            input_refs=input_refs,
            allowed_sources=spec["allowed_sources"],
        )
        available_refs = [
            _section_source_ref(record)
            for record in relevant_refs
            if _record_available_for_section(record)
        ]
        unavailable_refs = [
            _section_source_ref(record)
            for record in relevant_refs
            if not _record_available_for_section(record)
        ]
        sections[section_id] = {
            "section_id": section_id,
            "target_brief_section": section_id,
            "future_question": spec["future_question"],
            "allowed_sources": list(spec["allowed_sources"]),
            "available_source_refs": available_refs,
            "unavailable_or_redacted_sources": unavailable_refs,
            "known_limits": _known_limits(
                section_id=section_id,
                unavailable_or_redacted_sources=unavailable_refs,
            ),
            "interpretation_required": True,
            "required_output_contract_ref": {
                "schema_version": DECISION_WORK_BRIEF_SCHEMA_VERSION,
                "schema_path": DEFAULT_BRIEF_SCHEMA_RELPATH,
                "brief_section": section_id,
                "json_pointer": f"#/$defs/sections/properties/{section_id}",
            },
        }
    return sections


def _records_for_allowed_sources(
    *,
    input_refs: list[dict[str, Any]],
    allowed_sources: tuple[str, ...],
) -> list[dict[str, Any]]:
    records = []
    for source in allowed_sources:
        if source == DEFAULT_BRIEF_SCHEMA_RELPATH:
            records.append(_brief_schema_ref())
            continue
        matched = [
            record
            for record in input_refs
            if record.get("artifact") == source or record.get("source_kind") == source
        ]
        if matched:
            records.extend(matched)
    return _dedupe_records(records)


def _brief_schema_ref() -> dict[str, Any]:
    return {
        "ref_id": "decision_work_brief_schema_v0",
        "source_kind": "required_future_output_contract",
        "activity_kind": "brief_schema_contract",
        "artifact": DEFAULT_BRIEF_SCHEMA_RELPATH,
        "relative_path": DEFAULT_BRIEF_SCHEMA_RELPATH,
        "status": "available_from_structured_artifact",
        "source_status": "available_from_structured_artifact",
        "read_status": "repo_contract_reference",
        "schema_version": DECISION_WORK_BRIEF_SCHEMA_VERSION,
        "sha256": None,
        "byte_count": None,
        "raw_content_read": False,
        "content_included": False,
        "raw_private_content_included": False,
        "provider_text_included": False,
        "local_absolute_path_included": False,
        "text_truncated": False,
        "content_excerpt": None,
        "notes": [
            "Schema contract reference only; the packet builder does not fill the brief."
        ],
    }


def _record_available_for_section(record: Mapping[str, Any]) -> bool:
    status = _text(record.get("source_status")) or _text(record.get("status"))
    return status in AVAILABLE_SOURCE_STATUSES or bool(record.get("content_included"))


def _section_source_ref(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "ref_id": _text(record.get("ref_id")),
        "artifact": _text(record.get("artifact")),
        "source_kind": _text(record.get("source_kind")),
        "source_status": _text(record.get("source_status")),
        "read_status": _text(record.get("read_status")),
        "content_included": bool(record.get("content_included")),
        "raw_private_content_included": bool(
            record.get("raw_private_content_included")
        ),
        "provider_text_included": bool(record.get("provider_text_included")),
        "local_absolute_path_included": bool(
            record.get("local_absolute_path_included")
        ),
    }


def _known_limits(
    *,
    section_id: str,
    unavailable_or_redacted_sources: list[dict[str, Any]],
) -> list[str]:
    limits = [
        "packet_builder_did_not_interpret_section",
        "future_llm_or_human_review_must_cite_source_refs",
        "clean_source_manifest_does_not_imply_good_advice",
    ]
    if unavailable_or_redacted_sources:
        limits.append(
            "missing_redacted_or_private_sources_are_availability_status_not_semantic_evidence"
        )
    if section_id != "evidence_receipt":
        limits.append("brief_value_not_generated_in_pr115")
    return limits


def _custody_flags(
    *,
    mode: str,
    raw_private_content_included: bool,
    checked_in_safe: bool,
    input_refs: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "runtime_invoked": False,
        "skill_invoked": False,
        "archive_mutated": False,
        "model_calls": 0,
        "provider_calls": 0,
        "brief_generated": False,
        "semantic_interpretation_performed": False,
        "human_validated": False,
        "product_proof": False,
        "answer_quality_scored": False,
        "agent_action_authorized": False,
        "raw_private_content_included": raw_private_content_included,
        "provider_text_included": False,
        "raw_transcript_included": _any_included(
            input_refs=input_refs,
            artifact_names=RAW_TRANSCRIPT_ARTIFACTS,
        ),
        "raw_revised_answer_included": _any_included(
            input_refs=input_refs,
            artifact_names=RAW_REVISED_ARTIFACTS,
        ),
        "raw_memo_included": _any_included(
            input_refs=input_refs,
            artifact_names=RAW_MEMO_ARTIFACTS,
        ),
        "private_reasoning_included": False,
        "local_absolute_paths_included": False,
        "secrets_included": False,
        "llm_judge_used": False,
        "automatic_labels_created": False,
        "checked_in_safe": checked_in_safe,
        "unsafe_for_commit": mode == "local_private" and raw_private_content_included,
        "requires_operator_review_before_share": mode == "local_private",
    }


def _any_included(
    *,
    input_refs: list[dict[str, Any]],
    artifact_names: frozenset[str],
) -> bool:
    return any(
        _text(record.get("artifact")) in artifact_names
        and bool(record.get("content_included"))
        for record in input_refs
    )


def _case_id(payloads: Mapping[str, Mapping[str, Any]], run_path: Path) -> str:
    for artifact_name in (
        "agent_result.json",
        "reasoning_trace.json",
        "evaluation.json",
    ):
        payload = _mapping(payloads.get(artifact_name))
        case_id = _text(payload.get("case_id"))
        if case_id:
            return _safe_identifier(case_id)
        case = _mapping(payload.get("case"))
        case_id = _text(case.get("case_id"))
        if case_id:
            return _safe_identifier(case_id)
    return _safe_identifier(run_path.parent.name) or "unknown_case"


def _run_id(payloads: Mapping[str, Mapping[str, Any]], run_path: Path) -> str:
    for artifact_name in (
        "agent_result.json",
        "reasoning_trace.json",
        "evaluation.json",
    ):
        payload = _mapping(payloads.get(artifact_name))
        run_id = _text(payload.get("run_id"))
        if run_id:
            return _safe_identifier(run_id)
        case = _mapping(payload.get("case"))
        run_id = _text(case.get("run_id"))
        if run_id:
            return _safe_identifier(run_id)
    return _safe_identifier(run_path.name) or "unknown_run"


def _external_report_artifact_name(*, prefix: str, path: Path) -> str:
    name = path.name or "report.json"
    return f"{prefix}_{_safe_token(name)}"


def _source_ref_id(artifact_name: str) -> str:
    return _safe_identifier(artifact_name.replace(":", "_"))


def _safe_token(value: str) -> str:
    allowed = set(string.ascii_letters + string.digits + "._-")
    cleaned = "".join(char if char in allowed else "_" for char in value.strip())
    return cleaned.strip("._-") or "artifact"


def _safe_identifier(value: str) -> str:
    text = value.strip()
    if not text:
        return ""
    slug = re.sub(r"[^a-zA-Z0-9_.-]+", "_", text)
    return slug.strip("._-") or "unknown"


def _dedupe_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    result = []
    for record in records:
        key = (_text(record.get("ref_id")), _text(record.get("artifact")))
        if key in seen:
            continue
        seen.add(key)
        result.append(record)
    return result


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _utc_now_iso() -> str:
    return _dt.datetime.now(tz=_dt.UTC).replace(microsecond=0).isoformat()
