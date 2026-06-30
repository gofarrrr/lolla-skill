"""Read-only Decision Trail report exporter for archived Lolla runs.

The exporter builds a sparse, custody-first ``lolla.decision_trail_report.v0``
shell from completed run artifacts. It reads only structured JSON artifacts in
checked-in safe mode, does not run Lolla, does not call models, does not mutate
archives, and does not infer messy semantic fields from prose.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


DECISION_TRAIL_REPORT_SCHEMA_VERSION = "lolla.decision_trail_report.v0"

STATUS_VALUES = (
    "not_supplied",
    "not_measured",
    "not_applicable",
    "available_from_structured_artifact",
    "available_from_review_artifact",
    "available_but_redacted_in_safe_mode",
    "available_in_private_artifact_not_exported",
    "requires_llm_interpretation",
    "unavailable_missing_artifact",
    "unavailable_malformed_artifact",
    "unclear",
)

OWNER_VALUES = (
    "deterministic_exporter",
    "existing_llm_runtime_artifact",
    "product_delta_review_artifact",
    "future_llm_specialist",
    "future_human_review",
    "mixed_sources",
    "not_supplied",
)

REPORT_MODES = (
    "checked_in_safe_mode",
    "local_private_mode",
    "future_runtime_mode_not_implemented",
)

STRUCTURED_ARTIFACTS = (
    ("evaluation.json", "evaluation_artifact", "deterministic_evaluation"),
    ("agent_result.json", "structured_runtime_artifact", "agent_handoff"),
    ("reasoning_trace.json", "structured_runtime_artifact", "reasoning_trace"),
    (
        "extraction_adequacy_report.json",
        "evaluation_artifact",
        "extraction_adequacy",
    ),
    ("extraction.json", "structured_runtime_artifact", "extraction"),
    ("result.json", "audit_artifact", "audit_pipeline"),
)

RAW_ARTIFACTS_NOT_READ = (
    (
        "conversation.txt",
        "runtime_source",
        "conversation_capture",
        "available_but_redacted_in_safe_mode",
    ),
    (
        "memo.md",
        "audit_artifact",
        "memo_rendering",
        "available_but_redacted_in_safe_mode",
    ),
    (
        "revised.txt",
        "audit_artifact",
        "revised_answer_persistence",
        "available_but_redacted_in_safe_mode",
    ),
    (
        "live_transcript.txt",
        "runtime_source",
        "conversation_capture",
        "available_but_redacted_in_safe_mode",
    ),
    (
        "operator.log",
        "not_read",
        "unknown",
        "available_in_private_artifact_not_exported",
    ),
    (
        "pre_step6_private_table.json",
        "not_read",
        "audit_pipeline",
        "available_in_private_artifact_not_exported",
    ),
    (
        "pre_step6_private_table.md",
        "not_read",
        "audit_pipeline",
        "available_in_private_artifact_not_exported",
    ),
    (
        "pre_step6_private_table_ledger.json",
        "not_read",
        "audit_pipeline",
        "available_in_private_artifact_not_exported",
    ),
    (
        "v60_ledger.json",
        "not_read",
        "audit_pipeline",
        "available_in_private_artifact_not_exported",
    ),
    (
        "v60_ledger_skeleton.json",
        "not_read",
        "audit_pipeline",
        "available_in_private_artifact_not_exported",
    ),
)

SEMANTIC_SECTION_NAMES = (
    "conversation_understanding_summary",
    "decision_question",
    "vanilla_likely_next_action",
    "revised_likely_next_action",
    "option_map",
    "constraints",
    "stakeholders",
    "values_or_priorities",
    "assistant_influence",
    "audit_pressure_summary",
    "structural_delta",
    "useful_noisy_friction",
    "lost_value",
    "unresolved_questions",
)


class DecisionTrailReportInputError(ValueError):
    """Sanitized exporter input error."""


def build_decision_trail_report(
    *,
    run_dir: Path | str,
    report_mode: str = "checked_in_safe_mode",
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build a read-only ``lolla.decision_trail_report.v0`` report."""

    if report_mode not in REPORT_MODES:
        raise DecisionTrailReportInputError("unsupported report mode")
    if report_mode != "checked_in_safe_mode":
        raise DecisionTrailReportInputError(
            "only checked_in_safe_mode is implemented in PR87"
        )

    run_path = Path(run_dir).expanduser()
    if not run_path.exists():
        raise DecisionTrailReportInputError("run directory was not found")
    if not run_path.is_dir():
        raise DecisionTrailReportInputError("run directory is not a directory")

    source_artifacts: list[dict[str, Any]] = []
    payloads: dict[str, Mapping[str, Any]] = {}

    for artifact_name, role, activity_kind in STRUCTURED_ARTIFACTS:
        record, payload = _structured_artifact_record(
            run_path=run_path,
            artifact_name=artifact_name,
            role=role,
            activity_kind=activity_kind,
        )
        source_artifacts.append(record)
        if payload is not None:
            payloads[artifact_name] = payload

    for artifact_name, role, activity_kind, redacted_status in RAW_ARTIFACTS_NOT_READ:
        source_artifacts.append(
            _not_read_artifact_record(
                run_path=run_path,
                artifact_name=artifact_name,
                role=role,
                activity_kind=activity_kind,
                redacted_status=redacted_status,
            )
        )

    artifact_statuses = {
        record["artifact"]: record["status"]
        for record in source_artifacts
    }
    case_id = _case_id(payloads, run_path)
    run_id = _run_id(payloads, run_path)
    archive_relpath = _archive_relpath(
        case_id=case_id,
        run_id=run_id,
        run_dir=run_path,
    )

    report = {
        "schema_version": DECISION_TRAIL_REPORT_SCHEMA_VERSION,
        "report_metadata": {
            "report_id": _report_id(case_id=case_id, run_id=run_id),
            "created_at": created_at or _utc_now_iso(),
            "case_id": case_id,
            "run_id": run_id,
            "archive_relpath": archive_relpath,
            "report_mode": report_mode,
            "generated_by": "decision_trail_exporter",
            "schema_version": DECISION_TRAIL_REPORT_SCHEMA_VERSION,
            "notes": [
                "PR87 implements the read-only exporter for the PR86 report contract.",
            ],
        },
        "source_artifacts": source_artifacts,
        "custody_flags": _custody_flags(),
        "trace_context": _trace_context(payloads=payloads, artifact_statuses=artifact_statuses),
        "report_mode": report_mode,
        "conversation_understanding_summary": _conversation_understanding_summary(
            payloads=payloads,
            artifact_statuses=artifact_statuses,
        ),
        "decision_question": _decision_question(
            payloads=payloads,
            artifact_statuses=artifact_statuses,
        ),
        "vanilla_likely_next_action": _requires_llm_section(
            empty_meaning=(
                "not populated in checked-in safe mode; vanilla likely next "
                "action requires a review artifact or LLM interpretation"
            ),
            notes=[
                "The exporter does not infer the original likely action from conversation prose."
            ],
        ),
        "revised_likely_next_action": _revised_likely_next_action(
            artifact_statuses=artifact_statuses
        ),
        "option_map": _requires_llm_section(
            empty_meaning=(
                "not populated in checked-in safe mode; absence is not evidence "
                "that no live options existed"
            ),
            notes=["Live options and option status are not first-class structured runtime fields in PR87."],
        ),
        "constraints": _constraints(
            payloads=payloads,
            artifact_statuses=artifact_statuses,
        ),
        "stakeholders": _requires_llm_section(
            empty_meaning=(
                "not populated in checked-in safe mode; absence is not evidence "
                "that no stakeholders or obligations existed"
            )
        ),
        "values_or_priorities": _requires_llm_section(
            empty_meaning=(
                "not populated in checked-in safe mode; user values and "
                "priorities require LLM interpretation or human review"
            )
        ),
        "assistant_influence": _requires_llm_section(
            empty_meaning=(
                "not populated in checked-in safe mode; assistant influence "
                "requires a bounded interpretive read"
            )
        ),
        "audit_pressure_summary": _audit_pressure_summary(
            payloads=payloads,
            artifact_statuses=artifact_statuses,
        ),
        "structural_delta": _structural_delta(
            payloads=payloads,
            artifact_statuses=artifact_statuses,
        ),
        "useful_noisy_friction": _requires_llm_section(
            empty_meaning=(
                "not populated in checked-in safe mode; useful versus noisy "
                "friction requires review interpretation"
            )
        ),
        "lost_value": _requires_llm_section(
            empty_meaning=(
                "not populated in checked-in safe mode; absence is not evidence "
                "that the revised answer lost no value"
            )
        ),
        "unresolved_questions": _unresolved_questions(
            payloads=payloads,
            artifact_statuses=artifact_statuses,
        ),
        "artifact_health": _artifact_health(source_artifacts),
        "field_population_policy": _field_population_policy(),
        "limitations": _limitations(
            source_artifacts=source_artifacts,
            report_mode=report_mode,
        ),
        "non_claims": _non_claims(),
    }
    return report


def render_decision_trail_report_json(
    report: Mapping[str, Any],
    *,
    pretty: bool = False,
) -> str:
    if pretty:
        return json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return json.dumps(report, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"


def output_path_is_inside_run_dir(*, output_path: Path | str, run_dir: Path | str) -> bool:
    output = Path(output_path).expanduser().resolve(strict=False)
    run_path = Path(run_dir).expanduser().resolve(strict=False)
    return output == run_path or run_path in output.parents


def validate_output_path(*, output_path: Path | str, run_dir: Path | str) -> Path:
    if output_path_is_inside_run_dir(output_path=output_path, run_dir=run_dir):
        raise DecisionTrailReportInputError("output path must be outside run directory")
    output = Path(output_path).expanduser()
    if output.exists() and output.is_dir():
        raise DecisionTrailReportInputError("output path is a directory")
    return output


def write_decision_trail_report_output(path: Path | str, payload: str) -> None:
    output = Path(path).expanduser()
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    except OSError as exc:
        raise DecisionTrailReportInputError(
            f"output could not be written:{type(exc).__name__}"
        ) from exc


def _structured_artifact_record(
    *,
    run_path: Path,
    artifact_name: str,
    role: str,
    activity_kind: str,
) -> tuple[dict[str, Any], Mapping[str, Any] | None]:
    path = run_path / artifact_name
    base = {
        "artifact": artifact_name,
        "role": role,
        "relative_path": artifact_name,
        "schema_version": None,
        "sha256": None,
        "byte_count": None,
        "raw_content_read": False,
        "content_included": False,
        "activity_kind": activity_kind,
        "generated_by": ["lolla_runtime"],
        "used_by": ["decision_trail_report_exporter"],
    }
    if not path.exists():
        status = "unavailable_missing_artifact"
        return {**base, "status": status, "source_status": status}, None
    if not path.is_file():
        status = "unclear"
        return {
            **base,
            "status": status,
            "source_status": status,
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
            "byte_count": stat.st_size,
            "notes": ["Structured JSON artifact was not valid UTF-8."],
        }, None
    except OSError as exc:
        status = "unclear"
        return {
            **base,
            "status": status,
            "source_status": status,
            "byte_count": stat.st_size,
            "notes": [f"Structured JSON artifact could not be read:{type(exc).__name__}"],
        }, None

    if not isinstance(payload, dict):
        status = "unavailable_malformed_artifact"
        return {
            **base,
            "status": status,
            "source_status": status,
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
    }, payload


def _not_read_artifact_record(
    *,
    run_path: Path,
    artifact_name: str,
    role: str,
    activity_kind: str,
    redacted_status: str,
) -> dict[str, Any]:
    path = run_path / artifact_name
    base = {
        "artifact": artifact_name,
        "role": role,
        "relative_path": artifact_name,
        "schema_version": None,
        "sha256": None,
        "byte_count": None,
        "raw_content_read": False,
        "content_included": False,
        "activity_kind": activity_kind,
        "generated_by": ["lolla_runtime"],
        "used_by": ["decision_trail_report_exporter"],
    }
    if not path.exists():
        status = "unavailable_missing_artifact"
        return {**base, "status": status, "source_status": status}
    if not path.is_file():
        status = "unclear"
        return {
            **base,
            "status": status,
            "source_status": status,
            "notes": ["Path exists but is not a file; no content was read."],
        }
    status = redacted_status
    return {
        **base,
        "status": status,
        "source_status": status,
        "byte_count": path.stat().st_size,
        "notes": [
            "Artifact existence was recorded, but content was not read in checked-in safe mode."
        ],
    }


def _conversation_understanding_summary(
    *,
    payloads: Mapping[str, Mapping[str, Any]],
    artifact_statuses: Mapping[str, str],
) -> dict[str, Any]:
    extraction_payload = _mapping(payloads.get("extraction.json"))
    extraction = _extraction_body(extraction_payload)
    if extraction:
        value = {
            "decision_situation_present": bool(_text(extraction.get("decision_situation"))),
            "live_constraints_count": len(_list(extraction.get("live_constraints"))),
            "dropped_threads_count": len(_list(extraction.get("dropped_threads"))),
            "reasoning_passages_count": len(_list(extraction.get("reasoning_passages"))),
            "synthesized_position_present": bool(_text(extraction.get("synthesized_position"))),
            "original_framing_present": bool(_text(extraction.get("original_framing"))),
        }
        return _section_value(
            status="available_from_structured_artifact",
            source_status="available_from_structured_artifact",
            source_refs=[
                _source_ref(
                    artifact="extraction.json",
                    field="extraction",
                    json_pointer="/extraction",
                    content_included=False,
                )
            ],
            value=value,
            empty_meaning="not applicable; structured extraction metadata was available",
            owner="existing_llm_runtime_artifact",
            requires_llm_interpretation=False,
            notes=[
                "Counts and presence flags are copied from structured extraction metadata; raw conversation text is not read."
            ],
        )
    status = _status_for_artifact(artifact_statuses.get("extraction.json"))
    return _section_items(
        status=status,
        source_status=status,
        source_refs=[],
        items=[],
        empty_meaning=(
            "conversation understanding summary was not supplied by a readable "
            "structured extraction artifact"
        ),
        owner="not_supplied",
        requires_llm_interpretation=False,
    )


def _decision_question(
    *,
    payloads: Mapping[str, Mapping[str, Any]],
    artifact_statuses: Mapping[str, str],
) -> dict[str, Any]:
    extraction_payload = _mapping(payloads.get("extraction.json"))
    extraction = _extraction_body(extraction_payload)
    decision = _text(extraction.get("decision_situation"))
    if decision:
        return _section_value(
            status="available_from_structured_artifact",
            source_status="available_from_structured_artifact",
            source_refs=[
                _source_ref(
                    artifact="extraction.json",
                    field="extraction.decision_situation",
                    json_pointer=_extraction_pointer(extraction_payload, "decision_situation"),
                    content_included=True,
                )
            ],
            value=decision,
            empty_meaning="not applicable; value was supplied from structured extraction",
            owner="existing_llm_runtime_artifact",
            requires_llm_interpretation=False,
            notes=["The exporter copied this field from extraction metadata and did not infer it from prose."],
        )

    trace_case = _mapping(_mapping(payloads.get("reasoning_trace.json")).get("case"))
    trace_decision = _text(trace_case.get("decision_situation"))
    if trace_decision:
        return _section_value(
            status="available_from_structured_artifact",
            source_status="available_from_structured_artifact",
            source_refs=[
                _source_ref(
                    artifact="reasoning_trace.json",
                    field="case.decision_situation",
                    json_pointer="/case/decision_situation",
                    content_included=True,
                )
            ],
            value=trace_decision,
            empty_meaning="not applicable; value was supplied from structured trace case metadata",
            owner="existing_llm_runtime_artifact",
            requires_llm_interpretation=False,
            notes=[
                "reasoning_trace.json carries extraction-derived case metadata; exporter did not inspect raw conversation text."
            ],
        )

    status = _status_for_artifact(artifact_statuses.get("extraction.json"))
    if status == "not_supplied":
        status = _status_for_artifact(artifact_statuses.get("reasoning_trace.json"))
    if status == "not_supplied":
        status = "not_supplied"
    return _section_items(
        status=status,
        source_status=status,
        source_refs=[],
        items=[],
        empty_meaning=(
            "no safe structured decision question was supplied; this is not "
            "evidence that the run lacked a decision question"
        ),
        owner="not_supplied",
        requires_llm_interpretation=False,
    )


def _revised_likely_next_action(
    *,
    artifact_statuses: Mapping[str, str],
) -> dict[str, Any]:
    revised_status = artifact_statuses.get("revised.txt")
    refs = []
    if revised_status in {
        "available_but_redacted_in_safe_mode",
        "available_in_private_artifact_not_exported",
    }:
        refs.append(
            _source_ref(
                artifact="revised.txt",
                field="raw_revised_answer_not_read",
                source_status=revised_status,
                content_included=False,
            )
        )
    return _requires_llm_section(
        source_refs=refs,
        source_status=revised_status or "not_supplied",
        empty_meaning=(
            "not populated in checked-in safe mode; revised likely next action "
            "requires a safe structured review artifact or LLM interpretation"
        ),
        notes=["The exporter does not read revised.txt or infer likely action from revised-answer prose."],
    )


def _constraints(
    *,
    payloads: Mapping[str, Mapping[str, Any]],
    artifact_statuses: Mapping[str, str],
) -> dict[str, Any]:
    extraction_payload = _mapping(payloads.get("extraction.json"))
    extraction = _extraction_body(extraction_payload)
    constraints = [
        item for item in _list(extraction.get("live_constraints"))
        if isinstance(item, Mapping)
    ]
    if constraints:
        items = []
        for index, constraint in enumerate(constraints):
            summary = _text(constraint.get("constraint"))
            if not summary:
                continue
            items.append(
                {
                    "item_id": f"constraint_{index + 1}",
                    "status": "available_from_structured_artifact",
                    "summary": summary,
                    "source_refs": [
                        _source_ref(
                            artifact="extraction.json",
                            field="extraction.live_constraints",
                            json_pointer=_extraction_pointer(
                                extraction_payload,
                                f"live_constraints/{index}",
                            ),
                            content_included=True,
                        )
                    ],
                    "owner": "existing_llm_runtime_artifact",
                    "requires_llm_interpretation": False,
                    "exporter_inferred_from_prose": False,
                    "constraint_status": _text(constraint.get("status")) or "unclear",
                    "weight": _text(constraint.get("weight")) or "unclear",
                    "introduced_turn": constraint.get("introduced_turn")
                    if isinstance(constraint.get("introduced_turn"), int)
                    else None,
                }
            )
        if items:
            return _section_items(
                status="available_from_structured_artifact",
                source_status="available_from_structured_artifact",
                source_refs=[
                    _source_ref(
                        artifact="extraction.json",
                        field="extraction.live_constraints",
                        json_pointer=_extraction_pointer(extraction_payload, "live_constraints"),
                        content_included=True,
                    )
                ],
                items=items,
                empty_meaning="not applicable; structured constraints were supplied",
                owner="existing_llm_runtime_artifact",
                requires_llm_interpretation=False,
                notes=["The exporter copied structured extraction constraints and did not infer new constraints."],
            )

    status = _status_for_artifact(artifact_statuses.get("extraction.json"))
    if status == "not_supplied":
        status = "not_supplied"
    return _section_items(
        status=status,
        source_status=status,
        source_refs=[],
        items=[],
        empty_meaning=(
            "no structured live constraints were supplied; this is not evidence "
            "that no constraints existed"
        ),
        owner="not_supplied",
        requires_llm_interpretation=False,
    )


def _audit_pressure_summary(
    *,
    payloads: Mapping[str, Mapping[str, Any]],
    artifact_statuses: Mapping[str, str],
) -> dict[str, Any]:
    agent = _mapping(payloads.get("agent_result.json"))
    value = _text(agent.get("main_counter_pressure"))
    if value:
        return _section_value(
            status="available_from_structured_artifact",
            source_status="available_from_structured_artifact",
            source_refs=[
                _source_ref(
                    artifact="agent_result.json",
                    field="main_counter_pressure",
                    json_pointer="/main_counter_pressure",
                    content_included=True,
                )
            ],
            value=value,
            empty_meaning="not applicable; structured audit pressure summary was supplied",
            owner="existing_llm_runtime_artifact",
            requires_llm_interpretation=False,
        )

    result = _mapping(payloads.get("result.json"))
    for field in ("main_counter_pressure", "strongest_counter_pressure", "counter_pressure"):
        value = _text(result.get(field))
        if value:
            return _section_value(
                status="available_from_structured_artifact",
                source_status="available_from_structured_artifact",
                source_refs=[
                    _source_ref(
                        artifact="result.json",
                        field=field,
                        json_pointer=f"/{field}",
                        content_included=True,
                    )
                ],
                value=value,
                empty_meaning="not applicable; structured audit pressure summary was supplied",
                owner="existing_llm_runtime_artifact",
                requires_llm_interpretation=False,
            )

    status = _status_for_artifact(artifact_statuses.get("agent_result.json"))
    if status == "not_supplied":
        status = _status_for_artifact(artifact_statuses.get("result.json"))
    if status == "not_supplied":
        status = "not_supplied"
    return _section_items(
        status=status,
        source_status=status,
        source_refs=[],
        items=[],
        empty_meaning=(
            "no compact structured audit-pressure summary was supplied; this "
            "is not evidence that no audit pressure was applied"
        ),
        owner="not_supplied",
        requires_llm_interpretation=False,
    )


def _structural_delta(
    *,
    payloads: Mapping[str, Mapping[str, Any]],
    artifact_statuses: Mapping[str, str],
) -> dict[str, Any]:
    agent = _mapping(payloads.get("agent_result.json"))
    changed = _string_list(agent.get("changed_advice_summary"))
    take_backs = _string_list(agent.get("take_backs"))
    items: list[dict[str, Any]] = []
    for index, summary in enumerate(changed):
        items.append(
            _semantic_item(
                item_id=f"changed_advice_{index + 1}",
                summary=summary,
                owner="existing_llm_runtime_artifact",
                source_ref=_source_ref(
                    artifact="agent_result.json",
                    field="changed_advice_summary",
                    json_pointer=f"/changed_advice_summary/{index}",
                    content_included=True,
                ),
            )
        )
    for index, summary in enumerate(take_backs):
        items.append(
            _semantic_item(
                item_id=f"take_back_{index + 1}",
                summary=summary,
                owner="existing_llm_runtime_artifact",
                source_ref=_source_ref(
                    artifact="agent_result.json",
                    field="take_backs",
                    json_pointer=f"/take_backs/{index}",
                    content_included=True,
                ),
            )
        )
    if items:
        return _section_items(
            status="available_from_structured_artifact",
            source_status="available_from_structured_artifact",
            source_refs=[
                _source_ref(
                    artifact="agent_result.json",
                    field="changed_advice_summary|take_backs",
                    content_included=True,
                )
            ],
            items=items,
            empty_meaning="not applicable; structured delta items were supplied",
            owner="existing_llm_runtime_artifact",
            requires_llm_interpretation=False,
            notes=["The exporter copies compact structured delta items; it does not infer Product Delta labels."],
        )

    status = _status_for_artifact(artifact_statuses.get("agent_result.json"))
    return _section_items(
        status=status,
        source_status=status,
        source_refs=[],
        items=[],
        empty_meaning=(
            "no structured changed-advice or take-back items were supplied; "
            "this is not evidence that no structural delta existed"
        ),
        owner="not_supplied",
        requires_llm_interpretation=False,
    )


def _unresolved_questions(
    *,
    payloads: Mapping[str, Mapping[str, Any]],
    artifact_statuses: Mapping[str, str],
) -> dict[str, Any]:
    agent = _mapping(payloads.get("agent_result.json"))
    questions = _string_list(agent.get("human_questions"))
    if questions:
        items = [
            _semantic_item(
                item_id=f"human_question_{index + 1}",
                summary=question,
                owner="future_human_review",
                source_ref=_source_ref(
                    artifact="agent_result.json",
                    field="human_questions",
                    json_pointer=f"/human_questions/{index}",
                    content_included=True,
                ),
            )
            for index, question in enumerate(questions)
        ]
        return _section_items(
            status="available_from_structured_artifact",
            source_status="available_from_structured_artifact",
            source_refs=[
                _source_ref(
                    artifact="agent_result.json",
                    field="human_questions",
                    content_included=True,
                )
            ],
            items=items,
            empty_meaning="not applicable; unresolved questions were supplied",
            owner="future_human_review",
            requires_llm_interpretation=False,
        )
    status = _status_for_artifact(artifact_statuses.get("agent_result.json"))
    return _section_items(
        status=status,
        source_status=status,
        source_refs=[],
        items=[],
        empty_meaning=(
            "no structured unresolved questions were supplied; this is not "
            "evidence that no questions remain"
        ),
        owner="not_supplied",
        requires_llm_interpretation=False,
    )


def _artifact_health(source_artifacts: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    items = []
    for artifact in source_artifacts:
        name = _text(artifact.get("artifact")) or "unknown"
        status = _text(artifact.get("status")) or "unclear"
        items.append(
            {
                "item_id": f"artifact_{_slug_fragment(name)}",
                "status": status,
                "summary": f"{name}: {status}",
                "source_refs": [
                    _source_ref(
                        artifact=name,
                        field="artifact_status",
                        source_status=status,
                        content_included=False,
                    )
                ],
                "owner": "deterministic_exporter",
                "requires_llm_interpretation": False,
                "exporter_inferred_from_prose": False,
            }
        )
    return {
        "status": "available_from_structured_artifact",
        "source_status": "available_from_structured_artifact",
        "source_refs": [],
        "items": items,
        "empty_meaning": "not applicable; artifact health items are generated deterministically",
        "owner": "deterministic_exporter",
        "requires_llm_interpretation": False,
        "exporter_inferred_from_prose": False,
        "notes": [
            "Artifact health records presence, parsing, redaction, and not-read status only.",
            "Clean artifact health is not a claim that the advice was good.",
        ],
    }


def _trace_context(
    *,
    payloads: Mapping[str, Mapping[str, Any]],
    artifact_statuses: Mapping[str, str],
) -> dict[str, Any]:
    refs = []
    trace = _mapping(payloads.get("reasoning_trace.json"))
    if _text(trace.get("trace_id")):
        refs.append(
            _source_ref(
                artifact="reasoning_trace.json",
                field="trace_id",
                json_pointer="/trace_id",
                content_included=False,
            )
        )
    status = "future_compatible"
    if artifact_statuses.get("reasoning_trace.json") == "unavailable_missing_artifact":
        status = "not_used"
    return {
        "status": status,
        "source_refs": refs,
        "external_trace_id": None,
        "otel_genai_semconv_status": "not_used",
        "external_trace_dependency_added": False,
        "notes": [
            "PR87 records only future-compatible trace metadata.",
            "No external tracing package or semantic convention dependency is used.",
        ],
    }


def _field_population_policy() -> dict[str, Any]:
    return {
        "status_vocabulary": list(STATUS_VALUES),
        "owner_vocabulary": list(OWNER_VALUES),
        "deterministic_exporter_may": [
            "read structured JSON artifacts in checked-in safe mode",
            "record artifact presence, missingness, malformedness, byte counts, and hashes for structured artifacts",
            "copy safe structured values already present in extraction, trace, result, evaluation, or agent-result artifacts",
            "record redaction and private-artifact availability without reading excluded content",
        ],
        "deterministic_exporter_must_not": [
            "infer user values, live options, friction usefulness, lost value, stakeholder obligations, likely next action, or answer quality from prose",
            "read raw transcript, raw memo, raw revised-answer, operator, provider, or private-ledger content in checked-in safe mode",
            "create Product Delta labels, answer-quality scores, judge outputs, product proof, or agent authorization",
        ],
        "redaction_policy": (
            "available_but_redacted_in_safe_mode and "
            "available_in_private_artifact_not_exported are distinct from missing artifacts"
        ),
        "missingness_policy": (
            "empty arrays and null values are non-claims; every empty semantic "
            "section must explain its empty meaning"
        ),
        "messy_interpretation_policy": (
            "messy semantic interpretation belongs to existing LLM runtime "
            "artifacts, future bounded specialists, or human review, not to "
            "this deterministic exporter"
        ),
    }


def _limitations(
    *,
    source_artifacts: Sequence[Mapping[str, Any]],
    report_mode: str,
) -> dict[str, Any]:
    missing = [
        _text(item.get("artifact"))
        for item in source_artifacts
        if item.get("status") == "unavailable_missing_artifact"
    ]
    malformed = [
        _text(item.get("artifact"))
        for item in source_artifacts
        if item.get("status") == "unavailable_malformed_artifact"
    ]
    items = [
        "This report is a sparse Decision Trail shell, not a product-usefulness review.",
        "It does not judge answer quality or authorize an agent to act.",
        "It does not read raw transcript, raw memo, raw revised-answer, provider text, operator log, or private ledger content in checked-in safe mode.",
        "It does not infer live options, values, stakeholders, useful friction, noisy friction, lost value, or likely next action from prose.",
        "Clean custody and artifact health do not prove good advice.",
        "local_private_mode is deferred in PR87; only checked_in_safe_mode is implemented.",
        f"Generated in report mode: {report_mode}.",
    ]
    if missing:
        items.append("Missing artifacts were recorded as missing rather than guessed.")
    if malformed:
        items.append("Malformed structured artifacts were recorded as malformed rather than guessed.")
    return {
        "items": items,
        "empty_meaning": "not applicable; limitations are always populated",
    }


def _non_claims() -> dict[str, Any]:
    return {
        "items": [
            "This report does not claim the advice is good.",
            "This report does not claim a human reviewed the run.",
            "This report does not provide ground truth.",
            "This report does not provide judge calibration data.",
            "This report does not claim Product Delta proof.",
            "This report does not score answer quality.",
            "This report does not use an LLM judge.",
            "This report does not create automatic labels.",
            "This report does not authorize agent action.",
            "Empty semantic sections are non-claims, not evidence of absence.",
        ],
        "human_validated": False,
        "ground_truth": False,
        "judge_calibration_eligible": False,
        "product_proof": False,
        "answer_quality_scored": False,
        "llm_judge_used": False,
        "automatic_labels_created": False,
        "agent_action_authorized": False,
    }


def _custody_flags() -> dict[str, Any]:
    return {
        "raw_transcript_included": False,
        "raw_memo_included": False,
        "raw_revised_answer_included": False,
        "provider_text_included": False,
        "private_reasoning_included": False,
        "local_absolute_paths_included": False,
        "secrets_included": False,
        "raw_private_content_included": False,
        "model_calls": 0,
        "archive_mutated": False,
        "runtime_invoked": False,
        "skill_invoked": False,
        "human_validated": False,
        "ground_truth": False,
        "judge_calibration_eligible": False,
        "product_proof": False,
        "answer_quality_scored": False,
        "llm_judge_used": False,
        "automatic_labels_created": False,
        "agent_action_authorized": False,
    }


def _requires_llm_section(
    *,
    empty_meaning: str,
    source_refs: Sequence[Mapping[str, Any]] = (),
    source_status: str = "not_supplied",
    notes: Sequence[str] = (),
) -> dict[str, Any]:
    return _section_items(
        status="requires_llm_interpretation",
        source_status=source_status if source_status in STATUS_VALUES else "not_supplied",
        source_refs=list(source_refs),
        items=[],
        empty_meaning=empty_meaning,
        owner="future_llm_specialist",
        requires_llm_interpretation=True,
        notes=notes,
    )


def _section_value(
    *,
    status: str,
    source_status: str,
    source_refs: Sequence[Mapping[str, Any]],
    value: Any,
    empty_meaning: str,
    owner: str,
    requires_llm_interpretation: bool,
    notes: Sequence[str] = (),
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "status": status,
        "source_status": source_status,
        "source_refs": list(source_refs),
        "value": value,
        "empty_meaning": empty_meaning,
        "owner": owner,
        "requires_llm_interpretation": requires_llm_interpretation,
        "exporter_inferred_from_prose": False,
    }
    if notes:
        payload["notes"] = list(notes)
    return payload


def _section_items(
    *,
    status: str,
    source_status: str,
    source_refs: Sequence[Mapping[str, Any]],
    items: Sequence[Mapping[str, Any]],
    empty_meaning: str,
    owner: str,
    requires_llm_interpretation: bool,
    notes: Sequence[str] = (),
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "status": status,
        "source_status": source_status,
        "source_refs": list(source_refs),
        "items": list(items),
        "empty_meaning": empty_meaning,
        "owner": owner,
        "requires_llm_interpretation": requires_llm_interpretation,
        "exporter_inferred_from_prose": False,
    }
    if notes:
        payload["notes"] = list(notes)
    return payload


def _semantic_item(
    *,
    item_id: str,
    summary: str,
    owner: str,
    source_ref: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "item_id": item_id,
        "status": "available_from_structured_artifact",
        "summary": summary,
        "source_refs": [dict(source_ref)],
        "owner": owner,
        "requires_llm_interpretation": False,
        "exporter_inferred_from_prose": False,
    }


def _source_ref(
    *,
    artifact: str,
    field: str,
    json_pointer: str | None = None,
    source_status: str = "available_from_structured_artifact",
    content_included: bool,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "artifact": artifact,
        "field": field,
        "source_status": source_status,
        "content_included": content_included,
    }
    if json_pointer is not None:
        payload["json_pointer"] = json_pointer
    return payload


def _status_for_artifact(status: str | None) -> str:
    if status in {
        "unavailable_missing_artifact",
        "unavailable_malformed_artifact",
        "available_but_redacted_in_safe_mode",
        "available_in_private_artifact_not_exported",
        "unclear",
    }:
        return status
    return "not_supplied"


def _extraction_body(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    nested = _mapping(payload.get("extraction"))
    if nested:
        return nested
    return payload


def _extraction_pointer(payload: Mapping[str, Any], field: str) -> str:
    if isinstance(payload.get("extraction"), Mapping):
        return f"/extraction/{field}"
    return f"/{field}"


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


def _report_id(*, case_id: str, run_id: str) -> str:
    return f"decision_trail_{_slug_fragment(case_id)}_{_slug_fragment(run_id)}"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if not isinstance(value, list):
        return []
    items = []
    for item in value:
        text = _text(item).strip()
        if text:
            items.append(text)
    return items


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _slug_fragment(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_.-]+", "_", value.strip())
    return slug.strip("._-") or "unknown"


def _utc_now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
