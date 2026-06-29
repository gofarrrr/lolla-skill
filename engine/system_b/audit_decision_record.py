"""Read-only audit decision record exporter for archived Lolla runs.

The exporter builds a compact accountability shell from structured, custody-safe
artifacts. It does not run Lolla, call models, read raw transcript/memo/revised
answer files, mutate archives, create labels, or score advice quality.
"""
from __future__ import annotations

import json
import hashlib
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


AUDIT_DECISION_RECORD_SCHEMA_VERSION = "lolla.audit_decision_record.v0"

ACTIONABLE_DELTA_LABELS = (
    "action_changed",
    "threshold_changed",
    "sequence_changed",
    "evidence_gate_added",
    "stop_rule_added",
    "written_term_added",
    "user_question_added",
    "scope_narrowed",
    "overclaim_retracted",
    "no_op_prose_change",
)

STRUCTURED_ARTIFACTS = (
    ("evaluation.json", "deterministic_run_readiness", True),
    ("agent_result.json", "agent_handoff", True),
    ("reasoning_trace.json", "artifact_index", True),
    ("extraction_adequacy_report.json", "extraction_custody", True),
    ("extraction.json", "decision_structure_metadata_not_read", False),
    ("result.json", "pipeline_result_metadata_not_read", False),
)

RAW_ARTIFACTS_NOT_READ = (
    "conversation.txt",
    "memo.md",
    "revised.txt",
    "live_transcript.txt",
    "operator.log",
    "pre_step6_private_table.json",
    "pre_step6_private_table.md",
    "pre_step6_private_table_ledger.json",
    "v60_ledger.json",
    "v60_ledger_skeleton.json",
)


class AuditDecisionRecordInputError(ValueError):
    """Sanitized exporter input error."""


def build_audit_decision_record(
    *,
    run_dir: Path | str,
    review_json: Path | str | None = None,
) -> dict[str, Any]:
    """Build a read-only ``lolla.audit_decision_record.v0`` record."""

    run_path = Path(run_dir).expanduser()
    if not run_path.exists():
        raise AuditDecisionRecordInputError("run directory was not found")
    if not run_path.is_dir():
        raise AuditDecisionRecordInputError("run directory is not a directory")

    artifact_records: list[dict[str, Any]] = []
    structured_payloads: dict[str, Mapping[str, Any]] = {}
    malformed_artifacts: list[str] = []
    missing_artifacts: list[str] = []

    for artifact_name, role, read_json in STRUCTURED_ARTIFACTS:
        record, payload = _structured_artifact_record(
            run_path=run_path,
            artifact_name=artifact_name,
            role=role,
            read_json=read_json,
        )
        artifact_records.append(record)
        if record["status"] == "malformed":
            malformed_artifacts.append(artifact_name)
        if record["status"] == "missing":
            missing_artifacts.append(artifact_name)
        if payload is not None:
            structured_payloads[artifact_name] = payload

    review_refs: list[dict[str, Any]] = []
    review_artifact_record: dict[str, Any] | None = None
    if review_json is not None:
        review_artifact_record, review_ref = _review_reference_record(review_json)
        artifact_records.append(review_artifact_record)
        review_refs.append(review_ref)
        if review_artifact_record["status"] == "malformed":
            malformed_artifacts.append("review_json")

    case_id = _case_id(structured_payloads, run_path)
    run_id = _run_id(structured_payloads, run_path)
    record = {
        "schema_version": AUDIT_DECISION_RECORD_SCHEMA_VERSION,
        "case_id": case_id,
        "run_id": run_id,
        "archive_relpath": _archive_relpath(case_id=case_id, run_id=run_id, run_dir=run_path),
        "decision_question": _decision_question(structured_payloads),
        "original_recommendation_summary": _not_measured_field(
            "No safe structured original-recommendation summary source was supplied."
        ),
        "revised_recommendation_summary": _revised_recommendation_summary(
            structured_payloads
        ),
        "actionable_deltas": {label: [] for label in ACTIONABLE_DELTA_LABELS},
        "conflicts_or_unresolved_tensions": [],
        "unresolved_questions": _unresolved_questions(structured_payloads),
        "source_artifacts": artifact_records,
        "review_refs": review_refs,
        "custody_flags": {
            "raw_transcript_included": False,
            "raw_memo_included": False,
            "raw_revised_answer_included": False,
            "provider_text_included": False,
            "private_reasoning_included": False,
            "local_absolute_paths_included": False,
            "secrets_included": False,
            "model_calls": 0,
            "archive_mutated": False,
        },
        "limitations": _limitations(
            missing_artifacts=missing_artifacts,
            malformed_artifacts=malformed_artifacts,
            review_json_present=review_json is not None,
        ),
    }
    return record


def render_audit_decision_record_json(
    record: Mapping[str, Any],
    *,
    pretty: bool = False,
) -> str:
    if pretty:
        return json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return json.dumps(record, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"


def output_path_is_inside_run_dir(*, output_path: Path | str, run_dir: Path | str) -> bool:
    output = Path(output_path).expanduser().resolve(strict=False)
    run_path = Path(run_dir).expanduser().resolve(strict=False)
    return output == run_path or run_path in output.parents


def validate_output_path(*, output_path: Path | str, run_dir: Path | str) -> Path:
    if output_path_is_inside_run_dir(output_path=output_path, run_dir=run_dir):
        raise AuditDecisionRecordInputError("output path must be outside run directory")
    output = Path(output_path).expanduser()
    if output.exists() and output.is_dir():
        raise AuditDecisionRecordInputError("output path is a directory")
    return output


def write_audit_decision_record_output(path: Path | str, payload: str) -> None:
    output = Path(path).expanduser()
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    except OSError as exc:
        raise AuditDecisionRecordInputError(f"output could not be written:{type(exc).__name__}") from exc


def _structured_artifact_record(
    *,
    run_path: Path,
    artifact_name: str,
    role: str,
    read_json: bool,
) -> tuple[dict[str, Any], Mapping[str, Any] | None]:
    path = run_path / artifact_name
    base = {
        "artifact": artifact_name,
        "role": role,
        "relative_path": artifact_name,
        "schema_version": None,
        "byte_count": None,
        "sha256": None,
        "raw_content_read": False,
    }
    if not path.exists():
        return {**base, "status": "missing"}, None
    if not path.is_file():
        return {**base, "status": "unknown"}, None

    stat = path.stat()
    if not read_json:
        return {
            **base,
            "status": "present",
            "byte_count": stat.st_size,
            "schema_version": "not_read",
            "sha256": None,
        }, None

    try:
        text = path.read_text(encoding="utf-8")
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {
            **base,
            "status": "malformed",
            "byte_count": stat.st_size,
            "sha256": _sha256_text(text) if "text" in locals() else None,
            "error": "invalid_json",
        }, None
    except UnicodeDecodeError:
        return {
            **base,
            "status": "malformed",
            "byte_count": stat.st_size,
            "error": "invalid_encoding",
        }, None

    if not isinstance(payload, dict):
        return {
            **base,
            "status": "malformed",
            "byte_count": stat.st_size,
            "sha256": _sha256_text(text),
            "error": "json_root_not_object",
        }, None

    return {
        **base,
        "status": "present",
        "schema_version": _text(payload.get("schema_version")) or None,
        "byte_count": stat.st_size,
        "sha256": _sha256_text(text),
    }, payload


def _review_reference_record(
    review_json: Path | str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    path = Path(review_json).expanduser()
    base_artifact = {
        "artifact": "review_json",
        "role": "human_review_reference",
        "relative_path": path.name,
        "schema_version": None,
        "byte_count": None,
        "sha256": None,
        "raw_content_read": False,
    }
    base_ref = {
        "ref_id": "review_json",
        "relative_path": path.name,
        "status": "unknown",
        "schema_version": None,
        "review_count": 0,
        "labels_created": False,
        "answer_quality_scored": False,
        "raw_content_included": False,
    }
    if not path.exists():
        return {**base_artifact, "status": "missing"}, {**base_ref, "status": "missing"}
    if not path.is_file():
        return {**base_artifact, "status": "unknown"}, {**base_ref, "status": "unknown"}
    stat = path.stat()
    try:
        text = path.read_text(encoding="utf-8")
        payload = json.loads(text)
    except json.JSONDecodeError:
        return (
            {
                **base_artifact,
                "status": "malformed",
                "byte_count": stat.st_size,
                "sha256": _sha256_text(text) if "text" in locals() else None,
                "error": "invalid_json",
            },
            {**base_ref, "status": "malformed"},
        )
    if not isinstance(payload, dict):
        return (
            {
                **base_artifact,
                "status": "malformed",
                "byte_count": stat.st_size,
                "sha256": _sha256_text(text),
                "error": "json_root_not_object",
            },
            {**base_ref, "status": "malformed"},
        )
    schema_version = _text(payload.get("schema_version")) or None
    reviews = payload.get("reviews")
    review_count = len(reviews) if isinstance(reviews, list) else 0
    artifact = {
        **base_artifact,
        "status": "present",
        "schema_version": schema_version,
        "byte_count": stat.st_size,
        "sha256": _sha256_text(text),
    }
    ref = {
        **base_ref,
        "status": "present",
        "schema_version": schema_version,
        "review_count": review_count,
    }
    return artifact, ref


def _decision_question(payloads: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    trace = _mapping(payloads.get("reasoning_trace.json"))
    case = _mapping(trace.get("case"))
    decision_situation = _text(case.get("decision_situation"))
    if decision_situation:
        return {
            "status": "present",
            "summary": decision_situation,
            "grounding": "artifact_present_only",
            "source": "reasoning_trace.json:case.decision_situation",
        }
    return _not_measured_field(
        "No safe structured decision-question source was available."
    )


def _revised_recommendation_summary(
    payloads: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    agent_result = _mapping(payloads.get("agent_result.json"))
    changed = _string_list(agent_result.get("changed_advice_summary"))
    take_backs = _string_list(agent_result.get("take_backs"))
    if changed or take_backs:
        return {
            "status": "partial",
            "summary": "Structured changed-advice metadata is available in agent_result.json; exporter does not score or expand it.",
            "grounding": "artifact_present_only",
            "structured_items": {
                "changed_advice_summary": changed,
                "take_backs": take_backs,
            },
        }
    return _not_measured_field(
        "No safe structured revised-recommendation summary source was available."
    )


def _unresolved_questions(payloads: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    agent_result = _mapping(payloads.get("agent_result.json"))
    questions = _string_list(agent_result.get("human_questions"))
    return [
        {
            "question_id": f"agent_result_human_question_{index + 1}",
            "status": "present",
            "summary": question,
            "owner": "human_reviewer",
            "grounding": "artifact_present_only",
            "source": "agent_result.json:human_questions",
        }
        for index, question in enumerate(questions)
    ]


def _not_measured_field(reason: str) -> dict[str, Any]:
    return {
        "status": "not_measured",
        "summary": "not_included",
        "grounding": "none",
        "reason": reason,
    }


def _case_id(payloads: Mapping[str, Mapping[str, Any]], run_path: Path) -> str:
    for artifact in ("agent_result.json", "evaluation.json"):
        value = _text(_mapping(payloads.get(artifact)).get("case_id"))
        if value:
            return value
    trace_case = _mapping(_mapping(payloads.get("reasoning_trace.json")).get("case"))
    value = _text(trace_case.get("case_id"))
    if value:
        return value
    return run_path.parent.name or "unknown"


def _run_id(payloads: Mapping[str, Mapping[str, Any]], run_path: Path) -> str:
    for artifact in ("agent_result.json", "evaluation.json"):
        value = _text(_mapping(payloads.get(artifact)).get("run_id"))
        if value:
            return value
    trace_case = _mapping(_mapping(payloads.get("reasoning_trace.json")).get("case"))
    value = _text(trace_case.get("run_id"))
    if value:
        return value
    return run_path.name or "unknown"


def _archive_relpath(*, case_id: str, run_id: str, run_dir: Path) -> str:
    if case_id and case_id != "unknown" and run_id and run_id != "unknown":
        return f"{case_id}/{run_id}"
    parent = run_dir.parent.name or "unknown"
    name = run_dir.name or "unknown"
    return f"{parent}/{name}"


def _limitations(
    *,
    missing_artifacts: Sequence[str],
    malformed_artifacts: Sequence[str],
    review_json_present: bool,
) -> list[str]:
    limitations = [
        "This record is an accountability artifact, not answer-quality scoring.",
        "It does not approve the recommendation.",
        "It does not decide safe_for_agent_use.",
        "It does not provide domain approval.",
        "It may contain empty semantic fields when no safe structured source exists.",
        "Human review remains responsible for judging improvement.",
        "The exporter does not infer PR31 actionable-delta labels from prose.",
        "Raw transcript, raw memo, raw revised-answer, provider text, and private reasoning artifacts were intentionally not read.",
    ]
    if missing_artifacts:
        limitations.append(
            "Missing structured artifacts were recorded as missing rather than guessed."
        )
    if malformed_artifacts:
        limitations.append(
            "Malformed structured artifacts were recorded as malformed rather than guessed."
        )
    if not review_json_present:
        limitations.append(
            "No optional review JSON was supplied, so review references remain empty."
        )
    return limitations


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    items = []
    for item in value:
        text = _text(item)
        if text:
            items.append(text)
    return items


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
