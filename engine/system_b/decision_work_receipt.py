"""Read-only Decision Work Receipt exporter.

PR106 builds the first sparse ``lolla.decision_work_receipt.v0`` artifact over
completed Lolla run directories. PR107 adds deterministic conversation-process
metadata, PR108 adds deterministic challenge-surface coverage, and PR109
composes optional Decision Trail/Product Delta references into the receipt. The
exporter does not run Lolla, call models, mutate archives, read raw/private
artifacts in checked-in safe mode, or infer messy conversation semantics from
prose.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import string
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from engine.system_b.decision_trail_report import (
    RAW_ARTIFACTS_NOT_READ,
    STRUCTURED_ARTIFACTS,
)


DECISION_WORK_RECEIPT_SCHEMA_VERSION = "lolla.decision_work_receipt.v0"

RECEIPT_MODES = (
    "checked_in_safe_mode",
    "local_private_mode",
    "future_runtime_mode_not_implemented",
)

GENERATED_RUNTIME_ARTIFACTS = (
    "memo_note.json",
    "gapcheck_lanes.json",
    "run_events.json",
    "control_result.json",
    "graph_survival_report.json",
)

DECISION_TRAIL_REPORT_ARTIFACTS = (
    "decision_trail_report.json",
    "decision_trail_report.v0.json",
)

PRODUCT_DELTA_REVIEW_ARTIFACTS = (
    "product_delta_review.json",
    "product_delta_report.json",
    "product_delta_provisional_review.json",
)

SEMANTIC_PROCESS_FIELD_NAMES = (
    "new_context_added",
    "user_corrections_or_redirects",
    "options_explored",
    "assistant_challenge_or_pushback",
    "premortem_or_counterframe_used",
    "abandoned_paths",
    "final_output_divergence",
)

CORE_CHALLENGE_SURFACE_IDS = frozenset(
    {
        "lane1_structural_pressure",
        "lane2_model_companion",
        "lane3_frame_pressure",
        "lane4_structural_coverage",
        "delivery_bullshit_index",
        "v60_private_enrichment",
        "optional_pressure_check_state",
    }
)


class DecisionWorkReceiptInputError(ValueError):
    """Sanitized exporter input error."""


def build_decision_work_receipt(
    *,
    run_dir: Path | str,
    receipt_mode: str = "checked_in_safe_mode",
    created_at: str | None = None,
    decision_trail_report_paths: list[Path | str] | None = None,
    product_delta_report_paths: list[Path | str] | None = None,
) -> dict[str, Any]:
    """Build a sparse ``lolla.decision_work_receipt.v0`` receipt."""

    if receipt_mode not in RECEIPT_MODES:
        raise DecisionWorkReceiptInputError("unsupported receipt mode")
    if receipt_mode != "checked_in_safe_mode":
        raise DecisionWorkReceiptInputError(
            "only checked_in_safe_mode is implemented in PR106"
        )

    run_path = Path(run_dir).expanduser()
    if not run_path.exists():
        raise DecisionWorkReceiptInputError("run directory was not found")
    if not run_path.is_dir():
        raise DecisionWorkReceiptInputError("run directory is not a directory")

    sources: list[dict[str, Any]] = []
    payloads: dict[str, Mapping[str, Any]] = {}

    for artifact_name, _role, _activity_kind in STRUCTURED_ARTIFACTS:
        record, payload = _structured_source_record(
            run_path=run_path,
            artifact_name=artifact_name,
            source_kind="structured_runtime_artifact",
        )
        sources.append(record)
        if payload is not None:
            payloads[artifact_name] = payload

    for artifact_name, _role, _activity_kind, redacted_status in RAW_ARTIFACTS_NOT_READ:
        source_kind = (
            "conversation_capture"
            if artifact_name in {"conversation.txt", "live_transcript.txt"}
            else "raw_or_private_artifact"
        )
        sources.append(
            _not_read_source_record(
                run_path=run_path,
                artifact_name=artifact_name,
                source_kind=source_kind,
                redacted_status=redacted_status,
            )
        )

    for artifact_name in GENERATED_RUNTIME_ARTIFACTS:
        record, payload = _structured_source_record(
            run_path=run_path,
            artifact_name=artifact_name,
            source_kind="generated_runtime_artifact",
        )
        sources.append(record)
        if payload is not None:
            payloads[artifact_name] = payload

    decision_trail_artifacts = list(DECISION_TRAIL_REPORT_ARTIFACTS)
    product_delta_artifacts = list(PRODUCT_DELTA_REVIEW_ARTIFACTS)

    for artifact_name in DECISION_TRAIL_REPORT_ARTIFACTS:
        record, payload = _optional_structured_source_record(
            run_path=run_path,
            artifact_name=artifact_name,
            source_kind="decision_trail_report",
        )
        if record is not None:
            sources.append(record)
        if payload is not None:
            payloads[artifact_name] = payload

    for index, report_path in enumerate(decision_trail_report_paths or (), start=1):
        artifact_name = _external_report_artifact_name(
            prefix="external_decision_trail_report",
            path=report_path,
            index=index,
        )
        decision_trail_artifacts.append(artifact_name)
        record, payload = _external_structured_source_record(
            report_path=report_path,
            artifact_name=artifact_name,
            source_kind="decision_trail_report",
        )
        sources.append(record)
        if payload is not None:
            payloads[artifact_name] = payload

    for artifact_name in PRODUCT_DELTA_REVIEW_ARTIFACTS:
        record, payload = _optional_structured_source_record(
            run_path=run_path,
            artifact_name=artifact_name,
            source_kind="product_delta_artifact",
        )
        if record is not None:
            sources.append(record)
        if payload is not None:
            payloads[artifact_name] = payload

    for index, report_path in enumerate(product_delta_report_paths or (), start=1):
        artifact_name = _external_report_artifact_name(
            prefix="external_product_delta_report",
            path=report_path,
            index=index,
        )
        product_delta_artifacts.append(artifact_name)
        record, payload = _external_structured_source_record(
            report_path=report_path,
            artifact_name=artifact_name,
            source_kind="product_delta_artifact",
        )
        sources.append(record)
        if payload is not None:
            payloads[artifact_name] = payload

    case_id = _case_id(payloads, run_path)
    run_id = _run_id(payloads, run_path)

    conversation_process_map = _conversation_process_map(payloads)
    artifact_statuses = {
        source["artifact_or_reference"]: source["status"]
        for source in sources
    }
    challenge_coverage = _challenge_coverage(
        payloads=payloads,
        artifact_statuses=artifact_statuses,
    )
    decision_trail_summary = _decision_trail_summary(
        payloads=payloads,
        artifact_statuses=artifact_statuses,
        artifact_names=tuple(decision_trail_artifacts),
    )
    product_delta_summary = _product_delta_summary(
        payloads=payloads,
        artifact_statuses=artifact_statuses,
        artifact_names=tuple(product_delta_artifacts),
    )

    return {
        "schema_version": DECISION_WORK_RECEIPT_SCHEMA_VERSION,
        "receipt_metadata": {
            "receipt_id": f"decision_work_receipt:{case_id}:{run_id}",
            "created_at": created_at or _utc_now_iso(),
            "case_id": case_id,
            "run_id": run_id,
            "archive_relpath": f"{case_id}/{run_id}",
            "receipt_mode": receipt_mode,
            "generated_by": "decision_work_receipt_exporter",
            "schema_version": DECISION_WORK_RECEIPT_SCHEMA_VERSION,
            "notes": [
                "PR112 composes source inventory, deterministic process metadata, challenge coverage, and optional run-local or external Decision Trail/Product Delta references; semantic work-trail fields remain sparse."
            ],
        },
        "source_context_inventory": _source_context_inventory(
            sources=sources,
            receipt_mode=receipt_mode,
        ),
        "conversation_process_map": conversation_process_map,
        "challenge_coverage": challenge_coverage,
        "decision_trail_summary": decision_trail_summary,
        "product_delta_summary": product_delta_summary,
        "process_evidence_readiness": _process_evidence_readiness(
            conversation_process_map,
            challenge_coverage,
            decision_trail_summary,
            product_delta_summary,
        ),
        "missingness_and_redaction": _missingness_and_redaction(sources),
        "human_review": _human_review(),
        "non_claims": _non_claims(),
        "boundary": _boundary(),
    }


def render_decision_work_receipt_json(
    receipt: Mapping[str, Any],
    *,
    pretty: bool = False,
) -> str:
    """Render a Decision Work Receipt as JSON."""

    if pretty:
        return json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return json.dumps(
        receipt,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ) + "\n"


def output_path_is_inside_run_dir(*, output_path: Path | str, run_dir: Path | str) -> bool:
    output = Path(output_path).expanduser().resolve(strict=False)
    run_path = Path(run_dir).expanduser().resolve(strict=False)
    return output == run_path or run_path in output.parents


def validate_output_path(*, output_path: Path | str, run_dir: Path | str) -> Path:
    if output_path_is_inside_run_dir(output_path=output_path, run_dir=run_dir):
        raise DecisionWorkReceiptInputError("output path must be outside run directory")
    output = Path(output_path).expanduser()
    if output.exists() and output.is_dir():
        raise DecisionWorkReceiptInputError("output path is a directory")
    return output


def write_decision_work_receipt_output(path: Path | str, payload: str) -> None:
    output = Path(path).expanduser()
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    except OSError as exc:
        raise DecisionWorkReceiptInputError(
            f"output could not be written:{type(exc).__name__}"
        ) from exc


def _structured_source_record(
    *,
    run_path: Path,
    artifact_name: str,
    source_kind: str,
) -> tuple[dict[str, Any], Mapping[str, Any] | None]:
    path = run_path / artifact_name
    base = _source_record_base(
        artifact_name=artifact_name,
        source_kind=source_kind,
        read_status="read_safe_structured_fields",
    )

    if not path.exists():
        status = "unavailable_missing_artifact"
        return {
            **base,
            "status": status,
            "read_status": "unavailable_missing_artifact",
            "source_refs": [],
            "notes": ["Artifact was not found in the run directory."],
        }, None
    if not path.is_file():
        status = "unclear"
        return {
            **base,
            "status": status,
            "read_status": "not_read",
            "source_refs": [],
            "notes": ["Path exists but is not a file; no content was read."],
        }, None

    try:
        text = path.read_text(encoding="utf-8")
        payload = json.loads(text)
    except json.JSONDecodeError:
        status = "unavailable_malformed_artifact"
        return {
            **base,
            "status": status,
            "read_status": "unavailable_malformed_artifact",
            "source_refs": [],
            "notes": ["Structured JSON artifact could not be parsed."],
        }, None
    except UnicodeDecodeError:
        status = "unavailable_malformed_artifact"
        return {
            **base,
            "status": status,
            "read_status": "unavailable_malformed_artifact",
            "source_refs": [],
            "notes": ["Structured JSON artifact was not valid UTF-8."],
        }, None
    except OSError as exc:
        status = "unclear"
        return {
            **base,
            "status": status,
            "read_status": "unknown",
            "source_refs": [],
            "notes": [f"Structured JSON artifact could not be read:{type(exc).__name__}"],
        }, None

    if not isinstance(payload, dict):
        status = "unavailable_malformed_artifact"
        return {
            **base,
            "status": status,
            "read_status": "unavailable_malformed_artifact",
            "source_refs": [],
            "notes": ["Structured JSON artifact root was not an object."],
        }, None

    status = "available_from_structured_artifact"
    return {
        **base,
        "status": status,
        "source_refs": [
            _source_ref(
                artifact=artifact_name,
                field="structured_artifact_metadata",
                source_status=status,
                content_included=False,
            )
        ],
        "notes": [
            "Safe structured metadata was read; full artifact content was not copied into the receipt.",
            f"sha256:{_sha256_text(text)}",
            f"byte_count:{path.stat().st_size}",
        ],
    }, payload


def _optional_structured_source_record(
    *,
    run_path: Path,
    artifact_name: str,
    source_kind: str,
) -> tuple[dict[str, Any] | None, Mapping[str, Any] | None]:
    path = run_path / artifact_name
    if not path.exists():
        return None, None
    return _structured_source_record(
        run_path=run_path,
        artifact_name=artifact_name,
        source_kind=source_kind,
    )


def _external_structured_source_record(
    *,
    report_path: Path | str,
    artifact_name: str,
    source_kind: str,
) -> tuple[dict[str, Any], Mapping[str, Any] | None]:
    path = Path(report_path).expanduser()
    base = _source_record_base(
        artifact_name=artifact_name,
        source_kind=source_kind,
        read_status="read_safe_structured_fields",
    )

    if not path.exists():
        return {
            **base,
            "status": "unavailable_missing_artifact",
            "read_status": "unavailable_missing_artifact",
            "source_refs": [],
            "notes": [
                "External report path was provided but not found.",
                "local_path_not_included:true",
            ],
        }, None
    if not path.is_file():
        return {
            **base,
            "status": "unclear",
            "read_status": "not_read",
            "source_refs": [],
            "notes": [
                "External report path exists but is not a file; no content was read.",
                "local_path_not_included:true",
            ],
        }, None

    try:
        text = path.read_text(encoding="utf-8")
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {
            **base,
            "status": "unavailable_malformed_artifact",
            "read_status": "unavailable_malformed_artifact",
            "source_refs": [],
            "notes": [
                "External structured JSON report could not be parsed.",
                "local_path_not_included:true",
            ],
        }, None
    except UnicodeDecodeError:
        return {
            **base,
            "status": "unavailable_malformed_artifact",
            "read_status": "unavailable_malformed_artifact",
            "source_refs": [],
            "notes": [
                "External structured JSON report was not valid UTF-8.",
                "local_path_not_included:true",
            ],
        }, None
    except OSError as exc:
        return {
            **base,
            "status": "unclear",
            "read_status": "unknown",
            "source_refs": [],
            "notes": [
                f"External structured JSON report could not be read:{type(exc).__name__}",
                "local_path_not_included:true",
            ],
        }, None

    if not isinstance(payload, dict):
        return {
            **base,
            "status": "unavailable_malformed_artifact",
            "read_status": "unavailable_malformed_artifact",
            "source_refs": [],
            "notes": [
                "External structured JSON report root was not an object.",
                "local_path_not_included:true",
            ],
        }, None

    status = "available_from_structured_artifact"
    return {
        **base,
        "status": status,
        "source_refs": [
            _source_ref(
                artifact=artifact_name,
                field="external_report_metadata",
                source_status=status,
                content_included=False,
            )
        ],
        "notes": [
            "External report path was provided; local path was not included in the receipt.",
            "Safe structured metadata was read; full report content was not copied into the receipt.",
            f"sha256:{_sha256_text(text)}",
            f"byte_count:{path.stat().st_size}",
        ],
    }, payload


def _external_report_artifact_name(
    *,
    prefix: str,
    path: Path | str,
    index: int,
) -> str:
    name = Path(path).name or "report.json"
    return f"{prefix}_{index}_{_safe_token(name)}"


def _safe_token(value: str) -> str:
    allowed = set(string.ascii_letters + string.digits + "._-")
    cleaned = "".join(char if char in allowed else "_" for char in value.strip())
    return cleaned.strip("._-") or "report.json"


def _not_read_source_record(
    *,
    run_path: Path,
    artifact_name: str,
    source_kind: str,
    redacted_status: str,
) -> dict[str, Any]:
    path = run_path / artifact_name
    base = _source_record_base(
        artifact_name=artifact_name,
        source_kind=source_kind,
        read_status="not_read_redacted_safe_mode",
    )
    if not path.exists():
        status = "unavailable_missing_artifact"
        return {
            **base,
            "status": status,
            "read_status": "unavailable_missing_artifact",
            "source_refs": [],
            "notes": ["Artifact was not found in the run directory."],
        }
    if not path.is_file():
        status = "unclear"
        return {
            **base,
            "status": status,
            "read_status": "not_read",
            "source_refs": [],
            "notes": ["Path exists but is not a file; no content was read."],
        }

    read_status = (
        "not_read_redacted_safe_mode"
        if redacted_status == "available_but_redacted_in_safe_mode"
        else "not_read_private_not_exported"
    )
    return {
        **base,
        "status": redacted_status,
        "read_status": read_status,
        "source_refs": [
            _source_ref(
                artifact=artifact_name,
                field="raw_or_private_artifact_not_read",
                source_status=redacted_status,
                content_included=False,
            )
        ],
        "notes": [
            "Artifact existence was recorded, but content was not read in checked-in safe mode.",
            f"byte_count:{path.stat().st_size}",
        ],
    }


def _source_record_base(
    *,
    artifact_name: str,
    source_kind: str,
    read_status: str,
) -> dict[str, Any]:
    return {
        "source_id": artifact_name.replace(".", "_").replace("-", "_"),
        "source_kind": source_kind,
        "artifact_or_reference": artifact_name,
        "status": "not_supplied",
        "read_status": read_status,
        "content_included": False,
        "raw_private_content_included": False,
        "local_absolute_path_included": False,
        "source_refs": [],
        "notes": [],
    }


def _source_context_inventory(
    *,
    sources: list[dict[str, Any]],
    receipt_mode: str,
) -> dict[str, Any]:
    status = (
        "available_from_structured_artifact"
        if any(source["status"] == "available_from_structured_artifact" for source in sources)
        else "not_supplied"
    )
    return {
        "status": status,
        "receipt_mode": receipt_mode,
        "sources": sources,
        "source_counts": _source_counts(sources),
        "attachment_custody_policy": {
            "attachments_are_first_class_archived_sources": False,
            "pdf_ingestion_implemented": False,
            "link_fetching_implemented": False,
            "ocr_implemented": False,
            "embeddings_or_chunking_implemented": False,
            "empty_meaning": (
                "Absence of attachment records is not evidence that no attachments "
                "were discussed; attachments are not first-class archived sources in PR106."
            ),
        },
        "limitations": [
            "PR106 inventories archive artifacts and redaction state; it does not infer which sources influenced the final answer.",
            "PDFs, file uploads, and links are not first-class archived source objects in the current runtime.",
            "Raw/private artifact content is not read in checked-in safe mode.",
        ],
    }


def _source_counts(sources: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {"total": len(sources)}
    for source in sources:
        for key in (source["status"], source["source_kind"], source["read_status"]):
            counts[key] = counts.get(key, 0) + 1
    return counts


def _conversation_process_map(
    payloads: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    counts = _conversation_turn_counts(payloads)
    capture_evidence = _capture_metadata_evidence(payloads)

    source_refs = counts["source_refs"] + capture_evidence["source_refs"]
    deterministic_evidence = counts["evidence"] + capture_evidence["evidence"]
    process_depth = _process_depth(
        turn_count=counts["turn_count"],
        user_turn_count=counts["user_turn_count"],
        assistant_turn_count=counts["assistant_turn_count"],
    )
    if process_depth != "not_measured":
        deterministic_evidence.append(f"process_depth:{process_depth}")

    status = (
        "available_from_structured_artifact"
        if source_refs
        else "not_measured"
    )
    source_status = status

    return {
        "status": status,
        "source_status": source_status,
        "source_refs": source_refs,
        "turn_count": counts["turn_count"],
        "user_turn_count": counts["user_turn_count"],
        "assistant_turn_count": counts["assistant_turn_count"],
        "process_depth": process_depth,
        "deterministic_process_evidence": deterministic_evidence,
        "semantic_process_fields": {
            name: _semantic_process_field()
            for name in SEMANTIC_PROCESS_FIELD_NAMES
        },
        "limitations": [
            "PR107 reads structured turn and capture metadata only; raw conversation text is not read in checked-in safe mode.",
            "Turn count and process depth are process-shape evidence, not evidence of good thinking or good advice.",
            "Semantic process events such as new context, options explored, pushback, and abandoned paths still require LLM or human interpretation.",
            "If the initial extraction view was partial, counts may describe that bounded view while the preserved middle turns remain uninterpreted by extraction.",
        ],
    }


def _semantic_process_field() -> dict[str, Any]:
    return {
        "status": "requires_llm_interpretation",
        "source_refs": [],
        "empty_meaning": (
            "PR107 does not interpret conversation process events; absence is not evidence the event did not occur."
        ),
        "requires_llm_interpretation": True,
        "requires_human_review": False,
        "exporter_inferred_from_prose": False,
        "items": [],
    }


def _challenge_coverage(
    *,
    payloads: Mapping[str, Mapping[str, Any]],
    artifact_statuses: Mapping[str, str],
) -> dict[str, Any]:
    surfaces = [
        _challenge_surface_from_candidates(
            surface_id="lane1_structural_pressure",
            surface_name="Lane 1 structural pressure",
            candidates=(("result.json", "delta_card", "/delta_card"),),
            payloads=payloads,
            artifact_statuses=artifact_statuses,
            expected=True,
        ),
        _challenge_surface_from_candidates(
            surface_id="lane2_model_companion",
            surface_name="Lane 2 model companion",
            candidates=(
                ("result.json", "companion_cheat_sheet", "/companion_cheat_sheet"),
                ("result.json", "companion_card", "/companion_card"),
            ),
            payloads=payloads,
            artifact_statuses=artifact_statuses,
            expected=True,
        ),
        _challenge_surface_from_candidates(
            surface_id="lane3_frame_pressure",
            surface_name="Lane 3 frame pressure",
            candidates=(("result.json", "frame_pressure_card", "/frame_pressure_card"),),
            payloads=payloads,
            artifact_statuses=artifact_statuses,
            expected=True,
        ),
        _challenge_surface_from_candidates(
            surface_id="lane4_structural_coverage",
            surface_name="Lane 4 structural coverage",
            candidates=(
                ("result.json", "structural_coverage_card", "/structural_coverage_card"),
            ),
            payloads=payloads,
            artifact_statuses=artifact_statuses,
            expected=True,
        ),
        _challenge_surface_from_candidates(
            surface_id="delivery_bullshit_index",
            surface_name="Delivery bullshit-index check",
            candidates=(("result.json", "bullshit_profile", "/bullshit_profile"),),
            payloads=payloads,
            artifact_statuses=artifact_statuses,
            expected=False,
        ),
        _challenge_surface_from_candidates(
            surface_id="audit_summary_trace",
            surface_name="Audit summary and boundary trace",
            candidates=(("result.json", "audit_summary", "/audit_summary"),),
            payloads=payloads,
            artifact_statuses=artifact_statuses,
            expected=True,
        ),
        _challenge_surface_from_candidates(
            surface_id="v60_private_enrichment",
            surface_name="V60 private enrichment",
            candidates=(("result.json", "v60_enrichment", "/v60_enrichment"),),
            payloads=payloads,
            artifact_statuses=artifact_statuses,
            expected=False,
        ),
        _optional_pressure_check_surface(
            payloads=payloads,
            artifact_statuses=artifact_statuses,
        ),
        _challenge_surface_from_candidates(
            surface_id="pre_step6_private_table",
            surface_name="Pre-Step-6 private table",
            candidates=(
                (
                    "result.json",
                    "pre_step6_private_table",
                    "/pre_step6_private_table",
                ),
                (
                    "pre_step6_private_table.json",
                    "private_table_artifact",
                    "/",
                ),
            ),
            payloads=payloads,
            artifact_statuses=artifact_statuses,
            expected=False,
        ),
        _challenge_surface_from_candidates(
            surface_id="graph_survival_report",
            surface_name="Graph survival report",
            candidates=(
                (
                    "graph_survival_report.json",
                    "graph_survival_report",
                    "/",
                ),
            ),
            payloads=payloads,
            artifact_statuses=artifact_statuses,
            expected=False,
        ),
    ]
    run_health_caveats, caveat_refs = _run_health_caveats(payloads)
    source_refs = [
        ref
        for surface in surfaces
        if surface["present"] is True
        for ref in surface["source_refs"]
    ] + caveat_refs
    status = (
        "available_from_structured_artifact"
        if source_refs
        else "not_supplied"
    )
    return {
        "status": status,
        "source_refs": source_refs,
        "surfaces": surfaces,
        "run_health_caveats": run_health_caveats,
        "challenge_quality_scored": False,
        "empty_meaning": (
            "Challenge coverage records artifact presence only; absent surfaces are not evidence that no challenge occurred, and present surfaces are not evidence that the challenge was good."
        ),
    }


def _challenge_surface_from_candidates(
    *,
    surface_id: str,
    surface_name: str,
    candidates: tuple[tuple[str, str, str], ...],
    payloads: Mapping[str, Mapping[str, Any]],
    artifact_statuses: Mapping[str, str],
    expected: bool,
) -> dict[str, Any]:
    checked_refs: list[dict[str, Any]] = []
    missing_statuses: list[str] = []
    for artifact_name, field_name, json_pointer in candidates:
        artifact_status = artifact_statuses.get(
            artifact_name,
            "unavailable_missing_artifact",
        )
        if artifact_status in {
            "available_but_redacted_in_safe_mode",
            "available_in_private_artifact_not_exported",
        }:
            return _challenge_surface(
                surface_id=surface_id,
                surface_name=surface_name,
                status=artifact_status,
                present=True,
                source_refs=[
                    _source_ref(
                        artifact=artifact_name,
                        field=field_name,
                        json_pointer=json_pointer,
                        source_status=artifact_status,
                        content_included=False,
                    )
                ],
                notes=[
                    "Artifact exists but content was not read in checked-in safe mode.",
                    "quality_not_assessed:true",
                    f"expected_surface:{str(expected).lower()}",
                ],
            )
        payload = payloads.get(artifact_name)
        if isinstance(payload, Mapping):
            value = payload if json_pointer == "/" else _value_at_pointer(payload, json_pointer)
            if value is not None:
                return _challenge_surface(
                    surface_id=surface_id,
                    surface_name=surface_name,
                    status="available_from_structured_artifact",
                    present=True,
                    source_refs=[
                        _source_ref(
                            artifact=artifact_name,
                            field=field_name,
                            json_pointer=json_pointer,
                            source_status="available_from_structured_artifact",
                            content_included=False,
                        )
                    ],
                    notes=[
                        "Structured artifact field exists; content was not copied into this receipt.",
                        "quality_not_assessed:true",
                        f"expected_surface:{str(expected).lower()}",
                    ],
                )
            checked_refs.append(
                _source_ref(
                    artifact=artifact_name,
                    field=field_name,
                    json_pointer=json_pointer,
                    source_status="not_supplied",
                    content_included=False,
                )
            )
            continue
        if artifact_status in {
            "unavailable_missing_artifact",
            "unavailable_malformed_artifact",
            "unclear",
        }:
            missing_statuses.append(artifact_status)
            checked_refs.append(
                _source_ref(
                    artifact=artifact_name,
                    field=field_name,
                    json_pointer=json_pointer,
                    source_status=artifact_status,
                    content_included=False,
                )
            )

    status = _surface_missing_status(missing_statuses)
    return _challenge_surface(
        surface_id=surface_id,
        surface_name=surface_name,
        status=status,
        present=False if status in {"not_supplied", "unavailable_missing_artifact"} else None,
        source_refs=checked_refs,
        notes=[
            "Surface was not found in the checked structured fields.",
            "absence_is_not_evidence_of_no_challenge",
            "quality_not_assessed:true",
            f"expected_surface:{str(expected).lower()}",
        ],
    )


def _optional_pressure_check_surface(
    *,
    payloads: Mapping[str, Mapping[str, Any]],
    artifact_statuses: Mapping[str, str],
) -> dict[str, Any]:
    gapcheck_payload = payloads.get("gapcheck_lanes.json")
    if isinstance(gapcheck_payload, Mapping):
        return _challenge_surface(
            surface_id="optional_pressure_check_state",
            surface_name="Optional Step-7 pressure-check state",
            status="available_from_structured_artifact",
            present=True,
            source_refs=[
                _source_ref(
                    artifact="gapcheck_lanes.json",
                    field="gapcheck_lanes",
                    json_pointer="/",
                    source_status="available_from_structured_artifact",
                    content_included=False,
                )
            ],
            notes=[
                "Checked-in-safe gap-check lanes artifact exists.",
                "quality_not_assessed:true",
                "expected_surface:false",
            ],
        )
    result = payloads.get("result.json")
    if isinstance(result, Mapping):
        gap_check = _value_at_pointer(result, "/gap_check")
        has_gap_check = result.get("has_gap_check")
        mode = _text(result.get("pressure_check_mode"))
        if isinstance(gap_check, Mapping):
            present = bool(gap_check.get("lanes")) or bool(gap_check.get("summary"))
            return _challenge_surface(
                surface_id="optional_pressure_check_state",
                surface_name="Optional Step-7 pressure-check state",
                status="available_from_structured_artifact",
                present=present,
                source_refs=[
                    _source_ref(
                        artifact="result.json",
                        field="gap_check",
                        json_pointer="/gap_check",
                        source_status="available_from_structured_artifact",
                        content_included=False,
                    )
                ],
                notes=[
                    f"gap_check.status:{_text(gap_check.get('status')) or 'unknown'}",
                    "quality_not_assessed:true",
                    "expected_surface:false",
                ],
            )
        if has_gap_check is False or mode:
            note = f"pressure_check_mode:{mode or 'rested_or_not_requested'}"
            return _challenge_surface(
                surface_id="optional_pressure_check_state",
                surface_name="Optional Step-7 pressure-check state",
                status="available_from_structured_artifact",
                present=False,
                source_refs=[
                    _source_ref(
                        artifact="result.json",
                        field="pressure_check_state",
                        json_pointer="/pressure_check_mode",
                        source_status="available_from_structured_artifact",
                        content_included=False,
                    )
                ],
                notes=[
                    note,
                    "Optional pressure-check state was recorded as absent/rested.",
                    "quality_not_assessed:true",
                    "expected_surface:false",
                ],
            )

    artifact_status = artifact_statuses.get(
        "gapcheck_lanes.json",
        "unavailable_missing_artifact",
    )
    return _challenge_surface(
        surface_id="optional_pressure_check_state",
        surface_name="Optional Step-7 pressure-check state",
        status="not_supplied" if artifact_status == "unavailable_missing_artifact" else artifact_status,
        present=False,
        source_refs=[
            _source_ref(
                artifact="gapcheck_lanes.json",
                field="gapcheck_lanes",
                json_pointer="/",
                source_status=artifact_status,
                content_included=False,
            )
        ],
        notes=[
            "Optional pressure-check surface was not found; this is expected when deeper review was not requested.",
            "quality_not_assessed:true",
            "expected_surface:false",
        ],
    )


def _challenge_surface(
    *,
    surface_id: str,
    surface_name: str,
    status: str,
    present: bool | None,
    source_refs: list[dict[str, Any]],
    notes: list[str],
) -> dict[str, Any]:
    return {
        "surface_id": surface_id,
        "surface_name": surface_name,
        "status": status,
        "source_refs": source_refs,
        "present": present,
        "quality_not_assessed": True,
        "notes": notes,
    }


def _surface_missing_status(statuses: list[str]) -> str:
    if "unavailable_malformed_artifact" in statuses:
        return "unavailable_malformed_artifact"
    if "unclear" in statuses:
        return "unclear"
    if statuses and all(status == "unavailable_missing_artifact" for status in statuses):
        return "unavailable_missing_artifact"
    return "not_supplied"


def _run_health_caveats(
    payloads: Mapping[str, Mapping[str, Any]],
) -> tuple[list[str], list[dict[str, Any]]]:
    run_health, artifact_name, pointer = _run_health_source(payloads)
    if not run_health:
        return [], []

    source_ref = _source_ref(
        artifact=artifact_name,
        field="run_health",
        json_pointer=pointer,
        source_status="available_from_structured_artifact",
        content_included=False,
    )
    caveats: list[str] = []
    overall = _text(run_health.get("overall"))
    if overall and overall != "healthy":
        caveats.append(f"run_health.overall:{overall}")
    for field in ("capture", "substrate", "embeddings", "fingerprint"):
        value = _text(run_health.get(field))
        if value and value not in {"good", "ok", "active"}:
            caveats.append(f"run_health.{field}:{value}")
    if run_health.get("findings_produced") is False:
        caveats.append("run_health.findings_produced:false")
    if run_health.get("capture_truncated") is True:
        caveats.append("run_health.capture_truncated:true")
    omitted = run_health.get("omitted_turns")
    if isinstance(omitted, int) and omitted > 0:
        caveats.append(f"run_health.omitted_turns:{omitted}")
    for issue in _string_list(run_health.get("issues")):
        caveats.append(f"run_health.issue:{issue}")
    for issue in _string_list(run_health.get("partial_health_causes")):
        caveats.append(f"run_health.partial_health_cause:{issue}")
    warnings = run_health.get("warnings")
    if isinstance(warnings, list) and warnings:
        caveats.append(f"run_health.warnings_count:{len(warnings)}")

    capture_adequacy = _value_at_pointer(run_health, "/capture_adequacy")
    if isinstance(capture_adequacy, Mapping):
        capture_status = _text(capture_adequacy.get("status"))
        if capture_status and capture_status != "good":
            caveats.append(f"capture_adequacy.status:{capture_status}")
        omitted_count = capture_adequacy.get("omitted_turn_count")
        if isinstance(omitted_count, int) and omitted_count > 0:
            caveats.append(f"capture_adequacy.omitted_turn_count:{omitted_count}")
        for risk_flag in _string_list(capture_adequacy.get("risk_flags")):
            caveats.append(f"capture_adequacy.risk_flag:{risk_flag}")

    return caveats, [source_ref] if caveats else []


def _run_health_source(
    payloads: Mapping[str, Mapping[str, Any]],
) -> tuple[Mapping[str, Any], str, str]:
    for artifact_name, pointer in (
        ("result.json", "/run_health"),
        ("reasoning_trace.json", "/process/run_health"),
    ):
        payload = payloads.get(artifact_name)
        if not isinstance(payload, Mapping):
            continue
        run_health = _value_at_pointer(payload, pointer)
        if isinstance(run_health, Mapping):
            return run_health, artifact_name, pointer
    agent = payloads.get("agent_result.json")
    if isinstance(agent, Mapping):
        run_health = {
            "overall": agent.get("run_health_overall"),
            "product_output_health": agent.get("product_output_health"),
            "live_output_health": agent.get("live_output_health"),
        }
        if any(run_health.values()):
            return run_health, "agent_result.json", "/"
    return {}, "", ""


def _linked_summary(
    *,
    status: str,
    summary: str | None,
    limitations: list[str],
    source_refs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "status": status,
        "source_refs": list(source_refs or []),
        "summary": summary,
        "content_included": False,
        "human_validated": False,
        "product_proof": False,
        "limitations": limitations,
    }


def _decision_trail_summary(
    *,
    payloads: Mapping[str, Mapping[str, Any]],
    artifact_statuses: Mapping[str, str],
    artifact_names: tuple[str, ...] = DECISION_TRAIL_REPORT_ARTIFACTS,
) -> dict[str, Any]:
    return _optional_report_summary(
        artifact_names=artifact_names,
        payloads=payloads,
        artifact_statuses=artifact_statuses,
        field_name="decision_trail_report_reference",
        available_summary=(
            "Decision Trail report reference is available as a structured artifact; "
            "the Work Receipt links it without copying report content or treating it "
            "as human validation."
        ),
        absent_limitation=(
            "No checked-in-safe Decision Trail report artifact was found in the run "
            "directory. This does not prove no Decision Trail report exists elsewhere, "
            "because PR87 reports are normally generated outside archive run folders."
        ),
        present_limitation=(
            "Decision Trail report presence makes missingness easier to inspect, but "
            "does not validate interpretation quality, answer quality, or product value."
        ),
    )


def _product_delta_summary(
    *,
    payloads: Mapping[str, Mapping[str, Any]],
    artifact_statuses: Mapping[str, str],
    artifact_names: tuple[str, ...] = PRODUCT_DELTA_REVIEW_ARTIFACTS,
) -> dict[str, Any]:
    return _optional_report_summary(
        artifact_names=artifact_names,
        payloads=payloads,
        artifact_statuses=artifact_statuses,
        field_name="product_delta_review_reference",
        available_summary=(
            "Product Delta review reference is available as a structured artifact; "
            "the Work Receipt links it without copying review conclusions or treating "
            "candidate reads as product proof."
        ),
        absent_limitation=(
            "No checked-in-safe Product Delta review artifact was found in the run "
            "directory. This does not prove no Product Delta review exists elsewhere, "
            "because Product Delta artifacts are offline eval-lane outputs."
        ),
        present_limitation=(
            "Product Delta artifact presence can support later review of what changed, "
            "but does not prove Lolla improved the answer and does not authorize action."
        ),
    )


def _optional_report_summary(
    *,
    artifact_names: tuple[str, ...],
    payloads: Mapping[str, Mapping[str, Any]],
    artifact_statuses: Mapping[str, str],
    field_name: str,
    available_summary: str,
    absent_limitation: str,
    present_limitation: str,
) -> dict[str, Any]:
    for artifact_name in artifact_names:
        status = artifact_statuses.get(artifact_name)
        if status != "available_from_structured_artifact":
            continue
        source_refs = [
            _source_ref(
                artifact=artifact_name,
                field=field_name,
                json_pointer="/schema_version" if "schema_version" in payloads.get(artifact_name, {}) else "/",
                source_status=status,
                content_included=False,
            )
        ]
        return _linked_summary(
            status=status,
            summary=available_summary,
            source_refs=source_refs,
            limitations=[
                present_limitation,
                "The linked artifact is treated as a review/custody reference, not as a score, judge verdict, approval, or correctness proof.",
            ],
        )

    for artifact_name in artifact_names:
        status = artifact_statuses.get(artifact_name)
        if status in {
            "unavailable_missing_artifact",
            "unavailable_malformed_artifact",
            "unclear",
        }:
            source_refs = [
                _source_ref(
                    artifact=artifact_name,
                    field=field_name,
                    json_pointer=None,
                    source_status=status,
                    content_included=False,
                )
            ]
            return _linked_summary(
                status=status,
                summary=None,
                source_refs=source_refs,
                limitations=[
                    "A candidate review/report artifact was provided or present but could not be read as safe structured JSON.",
                    "Malformed or unclear optional artifacts do not become semantic findings.",
                ],
            )

    return _linked_summary(
        status="not_supplied",
        summary=None,
        limitations=[
            absent_limitation,
            "Absence of this optional reference keeps the receipt sparse; it is not evidence that the run lacked challenge, review, or useful work.",
        ],
    )


def _conversation_turn_counts(
    payloads: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    turn_counts = _turn_counts_from_structured_turns(payloads)
    if turn_counts["found"]:
        return turn_counts
    manifest_counts = _turn_counts_from_capture_manifest(payloads)
    if manifest_counts["found"]:
        return manifest_counts
    adequacy_counts = _turn_counts_from_capture_adequacy(payloads)
    if adequacy_counts["found"]:
        return adequacy_counts
    return _empty_turn_count_result()


def _turn_counts_from_structured_turns(
    payloads: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    for artifact_name in ("extraction.json", "result.json", "reasoning_trace.json"):
        payload = payloads.get(artifact_name)
        if not isinstance(payload, Mapping):
            continue
        for pointer in ("/turns", "/conversation/turns", "/context/turns"):
            turns = _value_at_pointer(payload, pointer)
            if not isinstance(turns, list):
                continue
            user_turns = 0
            assistant_turns = 0
            for turn in turns:
                if not isinstance(turn, Mapping):
                    continue
                speaker = str(turn.get("speaker", "")).strip().lower()
                role = str(turn.get("role", "")).strip().lower()
                normalized = speaker or role
                if normalized == "user":
                    user_turns += 1
                elif normalized == "assistant":
                    assistant_turns += 1
            result = _empty_turn_count_result()
            result.update(
                {
                    "found": True,
                    "turn_count": len(turns),
                    "user_turn_count": user_turns,
                    "assistant_turn_count": assistant_turns,
                    "source_refs": [
                        _source_ref(
                            artifact=artifact_name,
                            field="structured_turns",
                            json_pointer=pointer,
                            source_status="available_from_structured_artifact",
                            content_included=False,
                        )
                    ],
                    "evidence": [
                        f"turn_count:{len(turns)} from {artifact_name}{pointer}",
                        f"user_turn_count:{user_turns} from {artifact_name}{pointer}",
                        f"assistant_turn_count:{assistant_turns} from {artifact_name}{pointer}",
                    ],
                }
            )
            return result
    return _empty_turn_count_result()


def _turn_counts_from_capture_manifest(
    payloads: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    for artifact_name in (
        "extraction.json",
        "agent_result.json",
        "evaluation.json",
        "reasoning_trace.json",
        "result.json",
    ):
        payload = payloads.get(artifact_name)
        if not isinstance(payload, Mapping):
            continue
        for pointer in (
            "/capture_manifest",
            "/capture/capture_manifest",
            "/run_health/capture_manifest",
            "/metadata/capture_manifest",
        ):
            manifest = _value_at_pointer(payload, pointer)
            if not isinstance(manifest, Mapping):
                continue
            user_turns = _first_int(
                manifest,
                ("actual_user_turns", "captured_user_turns", "declared_user_turns", "declared_user"),
            )
            assistant_turns = _first_int(
                manifest,
                (
                    "actual_assistant_turns",
                    "captured_assistant_turns",
                    "declared_assistant_turns",
                    "declared_assistant",
                ),
            )
            turn_count = _first_int(
                manifest,
                (
                    "actual_total_turns",
                    "captured_turn_count",
                    "declared_turns",
                    "declared_turn_count",
                    "total_turns",
                ),
            )
            if turn_count is None and user_turns is not None and assistant_turns is not None:
                turn_count = user_turns + assistant_turns
            if turn_count is None and user_turns is None and assistant_turns is None:
                continue

            evidence: list[str] = []
            if turn_count is not None:
                evidence.append(f"turn_count:{turn_count} from {artifact_name}{pointer}")
            if user_turns is not None:
                evidence.append(
                    f"user_turn_count:{user_turns} from {artifact_name}{pointer}"
                )
            if assistant_turns is not None:
                evidence.append(
                    f"assistant_turn_count:{assistant_turns} from {artifact_name}{pointer}"
                )
            for key in (
                "capture_health",
                "last_turn_role",
                "truncation_applied",
                "kept_turns",
                "omitted_turns",
                "truncation_reason",
            ):
                value = manifest.get(key)
                if value is not None:
                    evidence.append(f"capture_manifest.{key}:{value}")

            result = _empty_turn_count_result()
            result.update(
                {
                    "found": True,
                    "turn_count": turn_count,
                    "user_turn_count": user_turns,
                    "assistant_turn_count": assistant_turns,
                    "source_refs": [
                        _source_ref(
                            artifact=artifact_name,
                            field="capture_manifest",
                            json_pointer=pointer,
                            source_status="available_from_structured_artifact",
                            content_included=False,
                        )
                    ],
                    "evidence": evidence,
                }
            )
            return result
    return _empty_turn_count_result()


def _turn_counts_from_capture_adequacy(
    payloads: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    for artifact_name in (
        "extraction.json",
        "agent_result.json",
        "evaluation.json",
        "reasoning_trace.json",
        "result.json",
    ):
        payload = payloads.get(artifact_name)
        if not isinstance(payload, Mapping):
            continue
        for pointer in (
            "/capture_adequacy",
            "/run_health/capture_adequacy",
            "/metadata/capture_adequacy",
        ):
            adequacy = _value_at_pointer(payload, pointer)
            if not isinstance(adequacy, Mapping):
                continue
            turn_count = _first_int(
                adequacy,
                ("captured_turn_count", "declared_turn_count"),
            )
            if turn_count is None:
                continue
            evidence = [f"turn_count:{turn_count} from {artifact_name}{pointer}"]
            for key in (
                "status",
                "capture_strategy",
                "omitted_turn_count",
                "risk_flags",
            ):
                value = adequacy.get(key)
                if value is not None:
                    evidence.append(f"capture_adequacy.{key}:{value}")

            result = _empty_turn_count_result()
            result.update(
                {
                    "found": True,
                    "turn_count": turn_count,
                    "source_refs": [
                        _source_ref(
                            artifact=artifact_name,
                            field="capture_adequacy",
                            json_pointer=pointer,
                            source_status="available_from_structured_artifact",
                            content_included=False,
                        )
                    ],
                    "evidence": evidence,
                }
            )
            return result
    return _empty_turn_count_result()


def _capture_metadata_evidence(
    payloads: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    source_refs: list[dict[str, Any]] = []
    evidence: list[str] = [
        "raw conversation text was not read in checked-in safe mode"
    ]
    for artifact_name in (
        "extraction.json",
        "agent_result.json",
        "evaluation.json",
        "reasoning_trace.json",
        "result.json",
    ):
        payload = payloads.get(artifact_name)
        if not isinstance(payload, Mapping):
            continue
        for pointer, field_name in (
            ("/capture_adequacy", "capture_adequacy"),
            ("/run_health/capture_adequacy", "capture_adequacy"),
            ("/capture_health", "capture_health"),
            ("/capture_warnings", "capture_warnings"),
        ):
            value = _value_at_pointer(payload, pointer)
            if value is None:
                continue
            source_refs.append(
                _source_ref(
                    artifact=artifact_name,
                    field=field_name,
                    json_pointer=pointer,
                    source_status="available_from_structured_artifact",
                    content_included=False,
                )
            )
            if isinstance(value, Mapping):
                status = value.get("status") or value.get("capture_health")
                if status is not None:
                    evidence.append(f"{field_name}.status:{status}")
                strategy = value.get("capture_strategy")
                if strategy is not None:
                    evidence.append(f"{field_name}.capture_strategy:{strategy}")
                omitted = value.get("omitted_turn_count")
                if omitted is not None:
                    evidence.append(f"{field_name}.omitted_turn_count:{omitted}")
                risk_flags = value.get("risk_flags")
                if risk_flags:
                    evidence.append(f"{field_name}.risk_flags:{risk_flags}")
            elif isinstance(value, list):
                evidence.append(f"{field_name}.count:{len(value)}")
            else:
                evidence.append(f"{field_name}:{value}")
    return {"source_refs": source_refs, "evidence": evidence}


def _empty_turn_count_result() -> dict[str, Any]:
    return {
        "found": False,
        "turn_count": None,
        "user_turn_count": None,
        "assistant_turn_count": None,
        "source_refs": [],
        "evidence": [],
    }


def _process_depth(
    *,
    turn_count: int | None,
    user_turn_count: int | None,
    assistant_turn_count: int | None,
) -> str:
    if turn_count is None and user_turn_count is None and assistant_turn_count is None:
        return "not_measured"
    if turn_count is not None and turn_count <= 2:
        return "one_shot_candidate"
    if (
        user_turn_count is not None
        and assistant_turn_count is not None
        and user_turn_count <= 1
        and assistant_turn_count <= 1
    ):
        return "one_shot_candidate"
    if (
        (turn_count is not None and turn_count > 2)
        or (user_turn_count is not None and user_turn_count > 1)
        or (assistant_turn_count is not None and assistant_turn_count > 1)
    ):
        return "multi_turn_evidence"
    return "unclear"


def _process_evidence_readiness(
    conversation_process_map: Mapping[str, Any],
    challenge_coverage: Mapping[str, Any],
    decision_trail_summary: Mapping[str, Any],
    product_delta_summary: Mapping[str, Any],
) -> dict[str, Any]:
    process_depth = conversation_process_map.get("process_depth")
    challenge_surface_ids = _present_core_challenge_surface_ids(challenge_coverage)
    decision_trail_ready = _summary_is_available(decision_trail_summary)
    product_delta_ready = _summary_is_available(product_delta_summary)
    if decision_trail_ready or product_delta_ready:
        label = "decision_trail_review_ready"
        status = "available_from_structured_artifact"
    elif challenge_surface_ids:
        label = "challenged_and_revised_process"
        status = "available_from_structured_artifact"
    elif process_depth == "one_shot_candidate":
        label = "one_shot_or_thin_process"
        status = "available_from_structured_artifact"
    elif process_depth == "multi_turn_evidence":
        label = "multi_turn_unreviewed_process"
        status = "available_from_structured_artifact"
    else:
        label = "insufficient_process_evidence"
        status = "not_measured"

    deterministic_basis = list(
        conversation_process_map.get("deterministic_process_evidence") or []
    )
    if not deterministic_basis:
        deterministic_basis = [
            "No structured turn or capture-count metadata was available."
        ]
    for surface_id in challenge_surface_ids:
        deterministic_basis.append(f"challenge_surface_present:{surface_id}")
    if decision_trail_ready:
        deterministic_basis.append("decision_trail_summary_reference_present:true")
    if product_delta_ready:
        deterministic_basis.append("product_delta_summary_reference_present:true")

    return {
        "label": label,
        "status": status,
        "basis_refs": (
            list(conversation_process_map.get("source_refs") or [])
            + list(challenge_coverage.get("source_refs") or [])
            + list(decision_trail_summary.get("source_refs") or [])
            + list(product_delta_summary.get("source_refs") or [])
        ),
        "deterministic_basis": deterministic_basis,
        "semantic_limitations": [
            "PR109 readiness is based on process-shape, challenge-artifact metadata, and optional review/report artifact references only.",
            "It does not assess conversation quality, challenge quality, decision usefulness, or whether Lolla improved the answer.",
            "Semantic process events still require LLM or human interpretation.",
            "Decision Trail or Product Delta references, when present, make the work trail more review-ready; they are not human validation or product proof."
        ],
        "answer_quality_scored": False,
        "correctness_claimed": False,
        "agent_action_authorized": False,
        "empty_meaning": (
            "The readiness label is a non-claim about available process evidence, not a finding that the underlying work was shallow, deep, good, or bad."
        ),
    }


def _summary_is_available(summary: Mapping[str, Any]) -> bool:
    return summary.get("status") in {
        "available_from_structured_artifact",
        "available_from_review_artifact",
    }


def _present_core_challenge_surface_ids(
    challenge_coverage: Mapping[str, Any],
) -> list[str]:
    surfaces = challenge_coverage.get("surfaces")
    if not isinstance(surfaces, list):
        return []
    ids: list[str] = []
    for surface in surfaces:
        if not isinstance(surface, Mapping):
            continue
        surface_id = _text(surface.get("surface_id"))
        if surface_id in CORE_CHALLENGE_SURFACE_IDS and surface.get("present") is True:
            ids.append(surface_id)
    return ids


def _missingness_and_redaction(sources: list[dict[str, Any]]) -> dict[str, Any]:
    missing = [
        source for source in sources
        if source["status"] == "unavailable_missing_artifact"
    ]
    redacted_or_private = [
        source for source in sources
        if source["status"] in {
            "available_but_redacted_in_safe_mode",
            "available_in_private_artifact_not_exported",
        }
    ]
    referenced = [
        source for source in sources
        if source["status"] == "referenced_but_not_archived"
    ]
    return {
        "missing_sources": missing,
        "redacted_or_private_sources": redacted_or_private,
        "referenced_but_not_archived_sources": referenced,
        "interpretation_needed_fields": [
            "conversation_process_map.semantic_process_fields",
            "challenge_coverage.challenge_quality",
            "decision_trail_summary.semantic_interpretation",
            "product_delta_summary.product_value",
            "process_evidence_readiness.semantic_meaning",
        ],
        "empty_meaning": (
            "Missing lists describe source custody only; they do not prove the conversation lacked the underlying context."
        ),
    }


def _human_review() -> dict[str, Any]:
    return {
        "status": "not_performed",
        "source_refs": [],
        "reviewer_refs": [],
        "correction_fields_present": False,
        "human_validation_included": False,
        "product_proof": False,
        "notes": ["PR109 does not perform or import human review."],
    }


def _non_claims() -> dict[str, Any]:
    return {
        "not_answer_quality_scoring": True,
        "not_correctness_proof": True,
        "not_product_proof": True,
        "not_agent_action_authorization": True,
        "not_runtime_integration": True,
        "not_llm_judge": True,
        "clean_artifacts_do_not_imply_good_advice": True,
    }


def _boundary() -> dict[str, Any]:
    return {
        "runtime_invoked": False,
        "skill_invoked": False,
        "archive_mutated": False,
        "model_calls": 0,
        "provider_calls": 0,
        "raw_private_content_included": False,
        "local_absolute_paths_included": False,
        "answer_quality_scored": False,
        "llm_judge_used": False,
        "automatic_labels_created": False,
        "agent_action_authorized": False,
        "graph_memory_or_embedding_work_added": False,
    }


def _case_id(payloads: Mapping[str, Mapping[str, Any]], run_path: Path) -> str:
    for artifact_name in ("agent_result.json", "reasoning_trace.json", "evaluation.json"):
        payload = payloads.get(artifact_name)
        if not isinstance(payload, Mapping):
            continue
        case_id = _text(payload.get("case_id"))
        if case_id:
            return case_id
        case = payload.get("case")
        if isinstance(case, Mapping):
            case_id = _text(case.get("case_id"))
            if case_id:
                return case_id
    if run_path.parent.name:
        return _safe_identifier(run_path.parent.name)
    return "unknown_case"


def _run_id(payloads: Mapping[str, Mapping[str, Any]], run_path: Path) -> str:
    for artifact_name in ("agent_result.json", "reasoning_trace.json", "evaluation.json"):
        payload = payloads.get(artifact_name)
        if not isinstance(payload, Mapping):
            continue
        run_id = _text(payload.get("run_id"))
        if run_id:
            return run_id
        case = payload.get("case")
        if isinstance(case, Mapping):
            run_id = _text(case.get("run_id"))
            if run_id:
                return run_id
    if run_path.name:
        return _safe_identifier(run_path.name)
    return "unknown_run"


def _source_ref(
    *,
    artifact: str,
    field: str,
    source_status: str,
    content_included: bool,
    json_pointer: str | None = None,
) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "field": field,
        "json_pointer": json_pointer,
        "source_status": source_status,
        "content_included": content_included,
        "notes": [],
    }


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _utc_now_iso() -> str:
    return _dt.datetime.now(tz=_dt.UTC).replace(microsecond=0).isoformat()


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def _value_at_pointer(payload: Mapping[str, Any], pointer: str) -> Any:
    if pointer == "":
        return payload
    current: Any = payload
    for raw_part in pointer.strip("/").split("/"):
        if not isinstance(current, Mapping):
            return None
        part = raw_part.replace("~1", "/").replace("~0", "~")
        current = current.get(part)
    return current


def _first_int(payload: Mapping[str, Any], keys: tuple[str, ...]) -> int | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
    return None


def _safe_identifier(value: str) -> str:
    return value.strip() or "unknown"
