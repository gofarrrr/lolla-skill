"""Read-only Decision Trail specialist packet construction.

This module packetizes Decision Trail review artifacts for future bounded
specialist interpretation. Checked-in safe mode never reads raw/private
content. Local-private include-text mode may read operator-selected local run
artifacts into an unsafe-for-commit packet. Both modes create input scaffolds
only: no Lolla runtime invocation, model calls, archive mutation, specialist
conclusions, fan-in execution, scoring, labels, or action authorization.
"""
from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from engine.system_b.decision_trail_report import (
    RAW_ARTIFACTS_NOT_READ,
    STRUCTURED_ARTIFACTS,
)


DECISION_TRAIL_SPECIALIST_PACKETS_SCHEMA_VERSION = (
    "lolla.decision_trail_specialist_packets.v0"
)
SPECIALIST_CONTRACT_SCHEMA_VERSION = (
    "lolla.decision_trail_specialist_contracts.v0"
)
DEFAULT_CONTRACT_SCHEMA_RELPATH = (
    "docs/conversation-understanding/decision-trail-specialist-contracts-v0.json"
)
DEFAULT_CONTRACT_DOC_RELPATH = (
    "docs/conversation-understanding/decision-trail-specialist-contracts-v0.md"
)
DEFAULT_PR87_DOC_RELPATH = (
    "docs/conversation-understanding/decision-trail-readonly-exporter-v0.md"
)
DEFAULT_PR88_DOC_RELPATH = (
    "docs/conversation-understanding/decision-trail-export-fixture-review-v0.md"
)

INPUT_MODES = ("checked_in_safe_mode", "local_private_mode")
CONTENT_INCLUSION_MODES = ("metadata_only", "include_text")
SPECIALIST_ROLES = (
    "conversation_shape_reader",
    "likely_action_reader",
    "friction_lost_value_reader",
    "conservative_fan_in_reader",
)
LOAD_BEARING_INTERPRETATION_SECTIONS = (
    "vanilla_likely_next_action",
    "revised_likely_next_action",
    "option_map",
    "stakeholders",
    "values_or_priorities",
    "assistant_influence",
    "useful_noisy_friction",
    "lost_value",
)
LOCAL_PRIVATE_ARTIFACTS = tuple(
    (
        artifact_name,
        role,
        activity_kind,
        "structured_json",
    )
    for artifact_name, role, activity_kind in STRUCTURED_ARTIFACTS
) + tuple(
    (
        artifact_name,
        role,
        activity_kind,
        "raw_or_private",
    )
    for artifact_name, role, activity_kind, _status in RAW_ARTIFACTS_NOT_READ
)

BOUNDARY = {
    "human_validated": False,
    "ground_truth": False,
    "judge_calibration_eligible": False,
    "product_proof": False,
    "answer_quality_scored": False,
    "agent_action_authorized": False,
    "model_calls": 0,
    "archive_mutated": False,
    "runtime_invoked": False,
    "skill_invoked": False,
    "raw_private_content_included": False,
    "automatic_labels_created": False,
}

NON_CLAIMS = (
    "not human review",
    "not ground truth",
    "not judge calibration data",
    "not product proof",
    "not agent approval",
    "not answer-quality scoring",
    "not automatic labeling",
    "not runtime integration",
    "not evidence that clean artifacts mean good advice",
)

FORBIDDEN_OUTPUTS = (
    "human-validation claim",
    "ground-truth claim",
    "judge-calibration claim",
    "product-proof claim",
    "answer-quality measurement",
    "agent-action authorization",
    "automatic label creation",
    "runtime integration claim",
    "filled specialist conclusion inside the packet",
)

ROLE_SPECS: dict[str, dict[str, Any]] = {
    "conversation_shape_reader": {
        "doc_ref": (
            f"{DEFAULT_CONTRACT_DOC_RELPATH}#conversation-shape-reader"
        ),
        "expected_fields": (
            "decision_question",
            "live_options",
            "option_status",
            "constraints",
            "stakeholders",
            "values_or_priorities",
            "assistant_influence",
            "assistant_influence_source_status",
            "dropped_threads",
            "unresolved_questions",
            "uncertainty",
            "source_scope_and_truncation_impact",
        ),
        "review_questions": (
            "What conversation-shape fields are visible from the checked-in-safe Decision Trail shell?",
            "Which live options, stakeholders, values, or assistant-influence fields are unavailable without bounded interpretation?",
            "Where is checked-in-safe context too thin to make a candidate read?",
        ),
    },
    "likely_action_reader": {
        "doc_ref": f"{DEFAULT_CONTRACT_DOC_RELPATH}#likely-action-reader",
        "expected_fields": (
            "vanilla_likely_next_action",
            "revised_likely_next_action",
            "vanilla_overlap_read",
            "action_delta",
            "threshold_delta",
            "sequence_delta",
            "evidence_gate_delta",
            "stop_rule_delta",
            "uncertainty",
            "source_scope_and_truncation_impact",
        ),
        "review_questions": (
            "Can a future specialist identify likely next actions from allowed inputs without pretending certainty?",
            "Which action, threshold, sequence, evidence-gate, or stop-rule deltas remain unavailable?",
            "Does the source surface support an unclear read instead of an over-inferred action read?",
        ),
    },
    "friction_lost_value_reader": {
        "doc_ref": (
            f"{DEFAULT_CONTRACT_DOC_RELPATH}#friction-and-lost-value-reader"
        ),
        "expected_fields": (
            "useful_friction",
            "noisy_friction",
            "missing_friction",
            "lost_value",
            "lost_value_severity_read",
            "severity_source_status",
            "value_overwrite_risk",
            "momentum_or_simplicity_loss",
            "overcaution_or_diligence_theater",
            "uncertainty",
            "source_scope_and_truncation_impact",
        ),
        "review_questions": (
            "What would count as useful friction versus noisy friction if a future specialist had enough context?",
            "Which lost-value risks are impossible to read from checked-in-safe fields alone?",
            "Could a populated structural delta make caution look more useful than it is?",
        ),
    },
    "conservative_fan_in_reader": {
        "doc_ref": f"{DEFAULT_CONTRACT_DOC_RELPATH}#conservative-fan-in-reader",
        "expected_fields": (
            "areas_of_agreement",
            "disagreements_preserved",
            "high_uncertainty_fields",
            "fields_ready_for_report",
            "fields_not_ready_for_report",
            "human_followup_questions",
            "overtrust_risks",
            "downgrade_triggers",
            "not_ready_reason",
            "next_review_priority",
            "source_scope_and_truncation_impact",
        ),
        "review_questions": (
            "Which fields are ready for a Decision Trail report and which are not?",
            "Which disagreements, missing fields, or overtrust risks must survive fan-in?",
            "What should a human reviewer or later local-private pass inspect first?",
        ),
    },
}


class DecisionTrailSpecialistPacketInputError(ValueError):
    """Deterministic, sanitized input error."""


def load_json_object(path: Path | str) -> dict[str, Any]:
    input_path = Path(path)
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DecisionTrailSpecialistPacketInputError(
            "input JSON is not valid JSON"
        ) from exc
    except OSError as exc:
        raise DecisionTrailSpecialistPacketInputError(
            f"input JSON could not be read:{type(exc).__name__}"
        ) from exc
    if not isinstance(payload, dict):
        raise DecisionTrailSpecialistPacketInputError("input JSON is not an object")
    return payload


def build_decision_trail_specialist_packets(
    *,
    fixture_review: Mapping[str, Any],
    contract_schema: Mapping[str, Any],
    fixture_review_relpath: str,
    contract_schema_relpath: str = DEFAULT_CONTRACT_SCHEMA_RELPATH,
    contract_doc_relpath: str = DEFAULT_CONTRACT_DOC_RELPATH,
    mode: str = "checked_in_safe_mode",
    limit: int | None = None,
    report_ids: Sequence[str] | None = None,
    local_run_dirs: Sequence[Path | str] | None = None,
    content_inclusion_mode: str = "metadata_only",
    output_path: Path | str | None = None,
    repo_root: Path | str | None = None,
    max_text_chars: int = 12000,
) -> dict[str, Any]:
    """Build Decision Trail specialist input packets."""

    if mode not in INPUT_MODES:
        raise DecisionTrailSpecialistPacketInputError("unsupported input mode")
    if content_inclusion_mode not in CONTENT_INCLUSION_MODES:
        raise DecisionTrailSpecialistPacketInputError(
            "unsupported content inclusion mode"
        )
    if limit is not None and limit < 1:
        raise DecisionTrailSpecialistPacketInputError("limit must be positive")
    if max_text_chars < 1:
        raise DecisionTrailSpecialistPacketInputError("max text chars must be positive")
    _validate_contract_schema(contract_schema)
    if mode == "local_private_mode":
        return _build_local_private_packets(
            fixture_review_relpath=fixture_review_relpath,
            contract_schema_relpath=contract_schema_relpath,
            contract_doc_relpath=contract_doc_relpath,
            local_run_dirs=local_run_dirs,
            content_inclusion_mode=content_inclusion_mode,
            output_path=output_path,
            repo_root=repo_root,
            max_text_chars=max_text_chars,
            limit=limit,
        )
    if local_run_dirs:
        raise DecisionTrailSpecialistPacketInputError(
            "local run directories require local_private_mode"
        )

    selected_report_ids = {report_id for report_id in (report_ids or []) if report_id}
    source_report_index = _index_source_reports(
        fixture_review.get("source_reports"),
        path=fixture_review_relpath,
    )
    review_records: list[tuple[int, Mapping[str, Any]]] = []
    for review_index, review in enumerate(_items(fixture_review.get("report_reviews"))):
        report_id = _text(review.get("report_id"))
        if selected_report_ids and report_id not in selected_report_ids:
            continue
        review_records.append((review_index, review))
    if limit is not None:
        review_records = review_records[:limit]

    reports: list[dict[str, Any]] = []
    for review_index, review in review_records:
        report_id = _text(review.get("report_id"))
        source_report_ref = source_report_index.get(report_id)
        reports.append(
            _build_report_packet_bundle(
                review=review,
                review_index=review_index,
                source_report_ref=source_report_ref,
                fixture_review_relpath=fixture_review_relpath,
                contract_schema_relpath=contract_schema_relpath,
                contract_doc_relpath=contract_doc_relpath,
                evidence_scope=_text(fixture_review.get("evidence_scope")),
                local_private_shadow_status=_local_private_shadow_status(fixture_review),
                mode=mode,
            )
        )

    return {
        "schema_version": DECISION_TRAIL_SPECIALIST_PACKETS_SCHEMA_VERSION,
        "generated_by": "decision_trail_specialist_packets",
        "mode": mode,
        "input_refs": {
            "fixture_review": fixture_review_relpath,
            "contract_schema": contract_schema_relpath,
            "contract_doc": contract_doc_relpath,
            "decision_trail_exporter_doc": DEFAULT_PR87_DOC_RELPATH,
            "decision_trail_fixture_review_doc": DEFAULT_PR88_DOC_RELPATH,
        },
        "boundary": _boundary(raw_private_content_included=False),
        "packet_policy": {
            "packet_type": "input_scaffold_only",
            "specialist_reads_filled": False,
            "fan_in_executed": False,
            "checked_in_safe_mode_only": True,
            "local_private_mode_enabled": False,
            "commit_safety": "safe_for_checked_in_fixture_if_lint_passes",
            "requires_operator_review_before_share": False,
            "content_inclusion_mode": "metadata_only",
            "raw_transcripts_included": False,
            "raw_revised_answers_included": False,
            "raw_memos_included": False,
            "provider_private_text_included": False,
            "local_absolute_paths_included": False,
            "source_report_policy": (
                "PR91 packetizes PR88 durable fixture-review findings. PR88 "
                "did not check in generated Decision Trail reports, so packets "
                "record source-report thinness instead of pretending full report "
                "content is present."
            ),
            "source_scope_policy": {
                "source_scope_summary_required": True,
                "truncation_summary_required": True,
                "local_private_retention_status_required_in_review": True,
            },
            "local_private_retention_policy": _local_private_retention_policy(
                mode="checked_in_safe_mode"
            ),
        },
        "report_count": len(reports),
        "reports": reports,
        "non_claims": list(NON_CLAIMS),
    }


def render_decision_trail_specialist_packets_json(report: Mapping[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def validate_local_private_output_path(
    *,
    output_path: Path | str,
    local_run_dirs: Sequence[Path | str],
    repo_root: Path | str | None = None,
) -> Path:
    output = Path(output_path).expanduser()
    resolved_output = output.resolve(strict=False)
    if output.exists() and output.is_dir():
        raise DecisionTrailSpecialistPacketInputError("output path is a directory")
    for run_dir in local_run_dirs:
        resolved_run = Path(run_dir).expanduser().resolve(strict=False)
        if resolved_output == resolved_run or resolved_run in resolved_output.parents:
            raise DecisionTrailSpecialistPacketInputError(
                "local-private output path must be outside local run directory"
            )
    if repo_root is not None:
        resolved_repo = Path(repo_root).expanduser().resolve(strict=False)
        if resolved_output == resolved_repo or resolved_repo in resolved_output.parents:
            raise DecisionTrailSpecialistPacketInputError(
                "local-private output path must be outside repository"
            )
    return output


def write_text(path: Path | str, payload: str) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(payload, encoding="utf-8")


def _boundary(*, raw_private_content_included: bool) -> dict[str, Any]:
    boundary = dict(BOUNDARY)
    boundary["raw_private_content_included"] = raw_private_content_included
    return boundary


def _build_local_private_packets(
    *,
    fixture_review_relpath: str,
    contract_schema_relpath: str,
    contract_doc_relpath: str,
    local_run_dirs: Sequence[Path | str] | None,
    content_inclusion_mode: str,
    output_path: Path | str | None,
    repo_root: Path | str | None,
    max_text_chars: int,
    limit: int | None,
) -> dict[str, Any]:
    if not local_run_dirs:
        raise DecisionTrailSpecialistPacketInputError(
            "local_private_mode requires at least one local run directory"
        )
    if output_path is None:
        raise DecisionTrailSpecialistPacketInputError(
            "local_private_mode requires an explicit output path"
        )
    run_paths = [Path(run_dir).expanduser() for run_dir in local_run_dirs]
    validate_local_private_output_path(
        output_path=output_path,
        local_run_dirs=run_paths,
        repo_root=repo_root,
    )
    for run_path in run_paths:
        if not run_path.exists():
            raise DecisionTrailSpecialistPacketInputError(
                "local run directory was not found"
            )
        if not run_path.is_dir():
            raise DecisionTrailSpecialistPacketInputError(
                "local run directory is not a directory"
            )
    if limit is not None:
        run_paths = run_paths[:limit]

    reports = [
        _build_local_private_report_packet_bundle(
            run_path=run_path,
            run_index=run_index,
            fixture_review_relpath=fixture_review_relpath,
            contract_schema_relpath=contract_schema_relpath,
            contract_doc_relpath=contract_doc_relpath,
            content_inclusion_mode=content_inclusion_mode,
            max_text_chars=max_text_chars,
        )
        for run_index, run_path in enumerate(run_paths)
    ]
    raw_private_content_included = _reports_include_any_content(reports)

    return {
        "schema_version": DECISION_TRAIL_SPECIALIST_PACKETS_SCHEMA_VERSION,
        "generated_by": "decision_trail_specialist_packets",
        "mode": "local_private_mode",
        "input_refs": {
            "fixture_review": fixture_review_relpath,
            "contract_schema": contract_schema_relpath,
            "contract_doc": contract_doc_relpath,
            "decision_trail_exporter_doc": DEFAULT_PR87_DOC_RELPATH,
            "decision_trail_fixture_review_doc": DEFAULT_PR88_DOC_RELPATH,
        },
        "boundary": _boundary(
            raw_private_content_included=raw_private_content_included
        ),
        "packet_policy": {
            "packet_type": "input_scaffold_only",
            "specialist_reads_filled": False,
            "fan_in_executed": False,
            "checked_in_safe_mode_only": False,
            "local_private_mode_enabled": True,
            "commit_safety": "unsafe_for_commit_by_default",
            "requires_operator_review_before_share": True,
            "content_inclusion_mode": content_inclusion_mode,
            "content_excerpt_policy": {
                "max_text_chars_per_artifact": max_text_chars,
                "truncation_indicator": "text_truncated",
            },
            "raw_transcripts_included": _reports_include_artifacts(
                reports,
                ("conversation.txt", "live_transcript.txt"),
            ),
            "raw_revised_answers_included": _reports_include_artifacts(
                reports,
                ("revised.txt",),
            ),
            "raw_memos_included": _reports_include_artifacts(
                reports,
                ("memo.md",),
            ),
            "provider_private_text_included": False,
            "local_absolute_paths_included": False,
            "source_report_policy": (
                "PR95 local-private mode packetizes operator-selected local "
                "run artifacts for future offline specialist reads. Output is "
                "not safe for commit by default and does not create specialist "
                "answers."
            ),
            "source_scope_policy": {
                "source_scope_summary_required": True,
                "truncation_summary_required": True,
                "local_private_retention_status_required_in_review": True,
            },
            "local_private_retention_policy": _local_private_retention_policy(
                mode="local_private_mode"
            ),
        },
        "report_count": len(reports),
        "reports": reports,
        "non_claims": list(NON_CLAIMS),
    }


def _reports_include_any_content(reports: Sequence[Mapping[str, Any]]) -> bool:
    return any(
        bool(record.get("content_included"))
        for report in reports
        for record in _local_private_artifact_records(report)
    )


def _reports_include_artifacts(
    reports: Sequence[Mapping[str, Any]],
    artifact_names: Sequence[str],
) -> bool:
    target_names = set(artifact_names)
    return any(
        _text(record.get("artifact")) in target_names
        and bool(record.get("content_included"))
        for report in reports
        for record in _local_private_artifact_records(report)
    )


def _local_private_artifact_records(
    report: Mapping[str, Any],
) -> list[Mapping[str, Any]]:
    context = _mapping(report.get("available_context"))
    return _items(context.get("local_private_artifacts_read"))


def _local_private_retention_policy(*, mode: str) -> dict[str, Any]:
    if mode == "local_private_mode":
        return {
            "local_include_text_output_retention_status": (
                "operator_managed_not_tracked_by_builder"
            ),
            "checked_in_review_must_record": [
                "deleted_after_review",
                "retained_locally",
                "never_created",
            ],
            "retention_status_source": "future_checked_in_review_summary",
            "builder_deletes_local_output": False,
        }
    return {
        "local_include_text_output_retention_status": (
            "not_created_by_checked_in_safe_mode"
        ),
        "checked_in_review_must_record": [
            "not_applicable_checked_in_safe_mode",
        ],
        "retention_status_source": "packet_policy",
        "builder_deletes_local_output": False,
    }


def _local_private_source_scope_summary(
    *,
    artifact_records: Sequence[Mapping[str, Any]],
    content_inclusion_mode: str,
) -> dict[str, Any]:
    scope_counts: dict[str, int] = {}
    artifact_refs_by_scope: dict[str, list[str]] = {}
    for record in artifact_records:
        scope_status = _artifact_scope_status(record)
        scope_counts[scope_status] = scope_counts.get(scope_status, 0) + 1
        artifact_refs_by_scope.setdefault(scope_status, []).append(
            _text(record.get("artifact_ref"))
        )
    return {
        "scope_mode": "local_private_mode",
        "content_inclusion_mode": content_inclusion_mode,
        "artifact_scope_status_counts": dict(sorted(scope_counts.items())),
        "artifact_refs_by_scope_status": {
            key: value
            for key, value in sorted(artifact_refs_by_scope.items())
        },
        "specialists_must_cite_scope_status": True,
    }


def _local_private_truncation_summary(
    *,
    artifact_records: Sequence[Mapping[str, Any]],
    max_text_chars: int,
) -> dict[str, Any]:
    truncated_refs = [
        _text(record.get("artifact_ref"))
        for record in artifact_records
        if bool(record.get("text_truncated"))
    ]
    return {
        "max_text_chars_per_artifact": max_text_chars,
        "artifact_records_truncated": len(truncated_refs),
        "truncated_artifact_refs": truncated_refs,
        "truncation_impact": (
            "must_be_cited_by_specialists"
            if truncated_refs
            else "no_truncation_observed"
        ),
    }


def _artifact_scope_status(record: Mapping[str, Any]) -> str:
    status = _text(record.get("status"))
    if status == "unavailable_missing_artifact":
        return "absent"
    if status == "unavailable_malformed_artifact":
        return "malformed"
    if bool(record.get("content_included")):
        if bool(record.get("text_truncated")):
            return "read_text_truncated"
        return "read_text_complete"
    if _safe_int(record.get("byte_count")) > 0:
        return "read_metadata"
    if status:
        return "present_not_read"
    return "present_not_read"


def _build_local_private_report_packet_bundle(
    *,
    run_path: Path,
    run_index: int,
    fixture_review_relpath: str,
    contract_schema_relpath: str,
    contract_doc_relpath: str,
    content_inclusion_mode: str,
    max_text_chars: int,
) -> dict[str, Any]:
    run_ref = _local_run_ref(run_path=run_path, run_index=run_index)
    artifact_records = [
        _local_private_artifact_record(
            run_path=run_path,
            run_ref=run_ref,
            artifact_name=artifact_name,
            role=role,
            activity_kind=activity_kind,
            artifact_kind=artifact_kind,
            content_inclusion_mode=content_inclusion_mode,
            max_text_chars=max_text_chars,
        )
        for artifact_name, role, activity_kind, artifact_kind in LOCAL_PRIVATE_ARTIFACTS
    ]
    raw_private_content_included = any(
        bool(record.get("content_included")) for record in artifact_records
    )
    source_refs = _local_private_source_refs(
        run_ref=run_ref,
        artifact_records=artifact_records,
        fixture_review_relpath=fixture_review_relpath,
        contract_schema_relpath=contract_schema_relpath,
    )
    available_context = _local_private_available_context(
        run_ref=run_ref,
        artifact_records=artifact_records,
        content_inclusion_mode=content_inclusion_mode,
        raw_private_content_included=raw_private_content_included,
        max_text_chars=max_text_chars,
    )
    missing_or_thin_context = _local_private_missing_or_thin_context(
        artifact_records=artifact_records,
        content_inclusion_mode=content_inclusion_mode,
        raw_private_content_included=raw_private_content_included,
    )
    packets = {
        role: _build_specialist_packet(
            role=role,
            report_id=run_ref,
            mode="local_private_mode",
            source_refs=source_refs,
            available_context=available_context,
            missing_or_thin_context=missing_or_thin_context,
            contract_schema_relpath=contract_schema_relpath,
            contract_doc_relpath=contract_doc_relpath,
        )
        for role in SPECIALIST_ROLES
    }
    return {
        "report_id": run_ref,
        "report_ref": f"local_private_run:{run_ref}",
        "source_run_ref": run_ref,
        "report_mode": "local_private_mode",
        "source_refs": source_refs,
        "available_context": available_context,
        "missing_or_thin_context": missing_or_thin_context,
        "packets": packets,
        "packetization_notes": [
            "PR95 prepared local-private input packets only.",
            "Specialist reads remain unfilled until a later provisional review slice.",
            "This local-private packet output is unsafe for commit by default.",
        ],
    }


def _local_run_ref(*, run_path: Path, run_index: int) -> str:
    name = _slug_text(run_path.name) or f"local-run-{run_index + 1}"
    return f"{name}-{run_index + 1}"


def _local_private_artifact_record(
    *,
    run_path: Path,
    run_ref: str,
    artifact_name: str,
    role: str,
    activity_kind: str,
    artifact_kind: str,
    content_inclusion_mode: str,
    max_text_chars: int,
) -> dict[str, Any]:
    path = run_path / artifact_name
    base: dict[str, Any] = {
        "artifact": artifact_name,
        "artifact_ref": f"local_private_run:{run_ref}/{artifact_name}",
        "role": role,
        "relative_path": artifact_name,
        "activity_kind": activity_kind,
        "artifact_kind": artifact_kind,
        "status": "not_supplied",
        "source_status": "not_supplied",
        "byte_count": None,
        "sha256": None,
        "raw_content_read": False,
        "content_included": False,
        "text_truncated": False,
        "content_text": None,
        "notes": [],
    }
    if not path.exists():
        status = "unavailable_missing_artifact"
        return {
            **base,
            "status": status,
            "source_status": status,
            "notes": ["Artifact was not present in the local run directory."],
        }
    if not path.is_file():
        status = "unavailable_malformed_artifact"
        return {
            **base,
            "status": status,
            "source_status": status,
            "notes": ["Artifact path exists but is not a file."],
        }

    stat = path.stat()
    if content_inclusion_mode == "metadata_only":
        status = "available_in_private_artifact_not_exported"
        return {
            **base,
            "status": status,
            "source_status": status,
            "byte_count": stat.st_size,
            "notes": [
                "Artifact exists locally, but content was not read in metadata-only local-private mode."
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
            "byte_count": stat.st_size,
            "notes": ["Artifact was not valid UTF-8 and content was not included."],
        }
    except OSError as exc:
        status = "unavailable_malformed_artifact"
        return {
            **base,
            "status": status,
            "source_status": status,
            "byte_count": stat.st_size,
            "notes": [f"Artifact could not be read:{type(exc).__name__}"],
        }

    truncated = len(text) > max_text_chars
    status = "explicit_in_source"
    return {
        **base,
        "status": status,
        "source_status": status,
        "byte_count": stat.st_size,
        "sha256": _sha256_text(text),
        "raw_content_read": True,
        "content_included": True,
        "text_truncated": truncated,
        "content_text": text[:max_text_chars],
        "notes": [
            "Artifact text is included because local-private include-text mode was explicitly requested.",
            "Output is unsafe for commit by default.",
        ],
    }


def _local_private_source_refs(
    *,
    run_ref: str,
    artifact_records: Sequence[Mapping[str, Any]],
    fixture_review_relpath: str,
    contract_schema_relpath: str,
) -> list[dict[str, Any]]:
    refs = [
        {
            "artifact_ref": fixture_review_relpath,
            "source_status": "not_supplied",
            "content_policy": (
                "Input reference retained for lineage only; local-private "
                "packet content is built from the operator-selected run "
                "artifacts and PR90 contract schema, not from PR88 review "
                "findings."
            ),
        },
        {
            "artifact_ref": contract_schema_relpath,
            "source_status": "explicit_in_source",
            "content_policy": "PR90 output contract definitions",
        },
    ]
    for record in artifact_records:
        if _text(record.get("status")) == "unavailable_missing_artifact":
            continue
        policy = (
            "local-private artifact text included for offline specialist packet use"
            if record.get("content_included")
            else "local-private artifact presence metadata only"
        )
        refs.append(
            {
                "artifact_ref": _text(record.get("artifact_ref")),
                "source_status": _text(record.get("source_status")),
                "content_policy": policy,
            }
        )
    refs.append(
        {
            "artifact_ref": f"local_private_run:{run_ref}",
            "source_status": "explicit_in_source",
            "content_policy": "operator-selected local run directory; absolute path omitted",
        }
    )
    return _dedupe_dicts(refs)


def _local_private_available_context(
    *,
    run_ref: str,
    artifact_records: Sequence[Mapping[str, Any]],
    content_inclusion_mode: str,
    raw_private_content_included: bool,
    max_text_chars: int,
) -> dict[str, Any]:
    read_records = [
        dict(record)
        for record in artifact_records
        if _text(record.get("status")) != "unavailable_missing_artifact"
    ]
    missing_records = [
        {
            "artifact": _text(record.get("artifact")),
            "artifact_ref": _text(record.get("artifact_ref")),
            "status": _text(record.get("status")),
            "source_status": _text(record.get("source_status")),
        }
        for record in artifact_records
        if _text(record.get("status")) == "unavailable_missing_artifact"
    ]
    return {
        "evidence_scope": "local_private_operator_selected",
        "local_private_shadow_review_status": "local_private_packet_mode",
        "source_report_checked_in": False,
        "source_report_available_in_repo": False,
        "source_report_kind": "local_private_run_artifacts",
        "local_private_context_available": True,
        "private_context_policy": {
            "mode": "local_private_mode",
            "run_ref": run_ref,
            "content_inclusion_mode": content_inclusion_mode,
            "raw_private_content_included": raw_private_content_included,
            "commit_safety": "unsafe_for_commit_by_default",
            "requires_operator_review_before_share": True,
            "local_absolute_paths_included": False,
            "max_text_chars_per_artifact": max_text_chars,
        },
        "field_population_summary": {
            "local_private_artifacts_available": len(read_records),
            "local_private_artifacts_missing": len(missing_records),
            "load_bearing_interpretation_sections": len(
                LOAD_BEARING_INTERPRETATION_SECTIONS
            ),
        },
        "source_scope_summary": _local_private_source_scope_summary(
            artifact_records=artifact_records,
            content_inclusion_mode=content_inclusion_mode,
        ),
        "truncation_summary": _local_private_truncation_summary(
            artifact_records=artifact_records,
            max_text_chars=max_text_chars,
        ),
        "local_private_retention_policy": _local_private_retention_policy(
            mode="local_private_mode"
        ),
        "populated_sections": [],
        "interpretation_needed_sections": list(LOAD_BEARING_INTERPRETATION_SECTIONS),
        "redacted_or_private_refs": [
            {
                "ref": _text(record.get("artifact")),
                "classification": "local_private_available",
                "source_status": _text(record.get("source_status")),
            }
            for record in read_records
        ],
        "missing_or_malformed_artifacts": missing_records,
        "overtrust_risk_sections": [
            "local_private_content_access",
            "future_specialist_interpretation",
        ],
        "behavioral_usefulness_summary": {
            "what_changed_answerable": "not_by_packet_builder",
            "evidence_support_answerable": "source_context_available_for_future_specialist",
            "missingness_answerable": "yes",
            "non_claims_answerable": "yes",
            "more_careful_or_more_impressed": "more_careful_if_unsafe_commit_status_is_preserved",
        },
        "report_readability": "local_private_packet_scaffold_only",
        "artifact_custody_read": "local_private_manifest_available",
        "semantic_interpretation_adequacy_read": "not_run",
        "product_delta_usefulness_read": "not_reviewed",
        "human_validation_read": "not_human_validated",
        "human_followup_questions": [
            "Which local-private artifacts should future specialists read first?",
            "Does including raw text create too much commit-safety risk?",
            "Can future specialists fill likely action and lost value without overclaiming?",
        ],
        "local_private_artifacts_read": read_records,
        "local_private_artifacts_not_read": missing_records,
    }


def _local_private_missing_or_thin_context(
    *,
    artifact_records: Sequence[Mapping[str, Any]],
    content_inclusion_mode: str,
    raw_private_content_included: bool,
) -> list[str]:
    notes = [
        "evidence_scope:local_private_operator_selected",
        "local_private_output_unsafe_for_commit_by_default",
        "specialist_reads_not_filled",
        "fan_in_not_executed",
    ]
    if raw_private_content_included:
        notes.append("raw_private_content_included")
    else:
        notes.append(f"content_inclusion_mode:{content_inclusion_mode}")
    missing_count = sum(
        1
        for record in artifact_records
        if _text(record.get("status")) == "unavailable_missing_artifact"
    )
    if missing_count:
        notes.append(f"local_private_artifacts_missing:{missing_count}")
    notes.append(
        f"requires_interpretation_sections:{len(LOAD_BEARING_INTERPRETATION_SECTIONS)}"
    )
    return list(dict.fromkeys(notes))


def _build_report_packet_bundle(
    *,
    review: Mapping[str, Any],
    review_index: int,
    source_report_ref: Mapping[str, Any] | None,
    fixture_review_relpath: str,
    contract_schema_relpath: str,
    contract_doc_relpath: str,
    evidence_scope: str,
    local_private_shadow_status: str,
    mode: str,
) -> dict[str, Any]:
    report_id = _text(review.get("report_id"))
    source_refs = _report_source_refs(
        review_index=review_index,
        source_report_ref=source_report_ref,
        fixture_review_relpath=fixture_review_relpath,
        contract_schema_relpath=contract_schema_relpath,
    )
    available_context = _available_context(
        review=review,
        source_report_ref=source_report_ref,
        evidence_scope=evidence_scope,
        local_private_shadow_status=local_private_shadow_status,
    )
    missing_or_thin_context = _missing_or_thin_context(
        review=review,
        source_report_ref=source_report_ref,
        evidence_scope=evidence_scope,
        local_private_shadow_status=local_private_shadow_status,
    )
    packets = {
        role: _build_specialist_packet(
            role=role,
            report_id=report_id,
            mode=mode,
            source_refs=source_refs,
            available_context=available_context,
            missing_or_thin_context=missing_or_thin_context,
            contract_schema_relpath=contract_schema_relpath,
            contract_doc_relpath=contract_doc_relpath,
        )
        for role in SPECIALIST_ROLES
    }
    return {
        "report_id": report_id,
        "report_ref": _text(review.get("report_ref")),
        "source_run_ref": _text(review.get("source_run_ref")),
        "report_mode": _text(review.get("report_mode")) or "checked_in_safe_mode",
        "source_refs": source_refs,
        "available_context": available_context,
        "missing_or_thin_context": missing_or_thin_context,
        "packets": packets,
        "packetization_notes": [
            "PR91 prepared input packets only.",
            "Specialist reads remain unfilled until a later provisional review slice.",
        ],
    }


def _build_specialist_packet(
    *,
    role: str,
    report_id: str,
    mode: str,
    source_refs: Sequence[Mapping[str, Any]],
    available_context: Mapping[str, Any],
    missing_or_thin_context: Sequence[str],
    contract_schema_relpath: str,
    contract_doc_relpath: str,
) -> dict[str, Any]:
    role_spec = ROLE_SPECS[role]
    schema_ref = (
        f"{contract_schema_relpath}#/properties/specialist_roles/properties/{role}"
    )
    context = {
        "report_id": report_id,
        "evidence_scope": _text(available_context.get("evidence_scope")),
        "local_private_shadow_review_status": _text(
            available_context.get("local_private_shadow_review_status")
        ),
        "source_report_checked_in": bool(
            available_context.get("source_report_checked_in")
        ),
        "source_report_available_in_repo": bool(
            available_context.get("source_report_available_in_repo")
        ),
        "populated_sections": list(available_context.get("populated_sections", [])),
        "interpretation_needed_sections": list(
            available_context.get("interpretation_needed_sections", [])
        ),
        "overtrust_risk_sections": list(
            available_context.get("overtrust_risk_sections", [])
        ),
        "source_scope_summary": _source_scope_summary_from_context(
            available_context=available_context,
            mode=mode,
        ),
        "truncation_summary": _truncation_summary_from_context(
            available_context=available_context,
            mode=mode,
        ),
        "local_private_retention_policy": _retention_policy_from_context(
            available_context=available_context,
            mode=mode,
        ),
        "prior_fixture_review_use": (
            "source context only; not a specialist answer and not truth"
        ),
    }
    private_policy = _mapping(available_context.get("private_context_policy"))
    if private_policy:
        context.update(
            {
                "local_private_context_available": bool(
                    available_context.get("local_private_context_available")
                ),
                "private_context_policy": dict(private_policy),
                "local_private_artifact_count": len(
                    available_context.get("local_private_artifacts_read", [])
                ),
                "local_private_missing_artifact_count": len(
                    available_context.get("local_private_artifacts_not_read", [])
                ),
            }
        )
    return {
        "specialist_role": role,
        "contract_ref": {
            "schema_ref": schema_ref,
            "contract_schema_version": SPECIALIST_CONTRACT_SCHEMA_VERSION,
            "doc_ref": role_spec["doc_ref"].replace(
                DEFAULT_CONTRACT_DOC_RELPATH,
                contract_doc_relpath,
            ),
        },
        "mode": mode,
        "allowed_inputs": _allowed_inputs(
            source_refs=source_refs,
            contract_schema_relpath=contract_schema_relpath,
            contract_doc_relpath=contract_doc_relpath,
            role=role,
        ),
        "forbidden_outputs": list(FORBIDDEN_OUTPUTS),
        "review_questions": list(role_spec["review_questions"]),
        "source_refs": list(source_refs),
        "context": context,
        "known_limits": _packet_known_limits(
            role=role,
            missing_or_thin_context=missing_or_thin_context,
            available_context=available_context,
        ),
        "required_non_claims": list(NON_CLAIMS),
        "expected_output_contract": {
            "schema_ref": schema_ref,
            "required_field_names": list(role_spec["expected_fields"]),
            "pr99_patch_fields": _pr99_patch_fields_for_role(role),
            "filled_by_packet_builder": False,
            "must_be_filled_by_future_specialist": True,
            "candidate_only": True,
        },
    }


def _allowed_inputs(
    *,
    source_refs: Sequence[Mapping[str, Any]],
    contract_schema_relpath: str,
    contract_doc_relpath: str,
    role: str,
) -> list[dict[str, Any]]:
    allowed = [
        {
            "artifact_ref": ref["artifact_ref"],
            "content_policy": ref["content_policy"],
        }
        for ref in source_refs
    ]
    allowed.extend(
        [
            {
                "artifact_ref": contract_schema_relpath,
                "content_policy": f"Use only the PR90 contract for `{role}` output shape.",
            },
            {
                "artifact_ref": contract_doc_relpath,
                "content_policy": "Human-readable PR90 contract explanation.",
            },
        ]
    )
    return _dedupe_dicts(allowed)


def _source_scope_summary_from_context(
    *,
    available_context: Mapping[str, Any],
    mode: str,
) -> dict[str, Any]:
    summary = _mapping(available_context.get("source_scope_summary"))
    if summary:
        return dict(summary)
    return {
        "scope_mode": mode,
        "content_inclusion_mode": "metadata_only",
        "artifact_scope_status_counts": {
            "checked_in_safe_summary_only": 1,
        },
        "artifact_refs_by_scope_status": {},
        "specialists_must_cite_scope_status": True,
    }


def _truncation_summary_from_context(
    *,
    available_context: Mapping[str, Any],
    mode: str,
) -> dict[str, Any]:
    summary = _mapping(available_context.get("truncation_summary"))
    if summary:
        return dict(summary)
    return {
        "max_text_chars_per_artifact": None,
        "artifact_records_truncated": 0,
        "truncated_artifact_refs": [],
        "truncation_impact": (
            "not_applicable_checked_in_safe_mode"
            if mode == "checked_in_safe_mode"
            else "not_supplied"
        ),
    }


def _retention_policy_from_context(
    *,
    available_context: Mapping[str, Any],
    mode: str,
) -> dict[str, Any]:
    policy = _mapping(available_context.get("local_private_retention_policy"))
    if policy:
        return dict(policy)
    return _local_private_retention_policy(mode=mode)


def _pr99_patch_fields_for_role(role: str) -> list[str]:
    fields = ["source_scope_and_truncation_impact"]
    if role == "conversation_shape_reader":
        fields.append("assistant_influence_source_status")
    elif role == "likely_action_reader":
        fields.append("vanilla_overlap_read")
    elif role == "friction_lost_value_reader":
        fields.extend(["lost_value_severity_read", "severity_source_status"])
    elif role == "conservative_fan_in_reader":
        fields.extend(["downgrade_triggers", "not_ready_reason"])
    return fields


def _report_source_refs(
    *,
    review_index: int,
    source_report_ref: Mapping[str, Any] | None,
    fixture_review_relpath: str,
    contract_schema_relpath: str,
) -> list[dict[str, Any]]:
    refs = [
        {
            "artifact_ref": f"{fixture_review_relpath}#/report_reviews/{review_index}",
            "source_status": "explicit_in_source",
            "content_policy": (
                "PR88 report-review findings: field population, missingness, "
                "redaction, readability, and overtrust risk only"
            ),
        }
    ]
    if source_report_ref:
        refs.append(
            {
                "artifact_ref": (
                    f"{source_report_ref['path']}#/source_reports/"
                    f"{source_report_ref['index']}"
                ),
                "source_status": "explicit_in_source",
                "content_policy": (
                    "PR88 source-report metadata only; generated report JSON "
                    "may not be checked in"
                ),
            }
        )
    else:
        refs.append(
            {
                "artifact_ref": "missing:pr88_source_report_metadata",
                "source_status": "unavailable_missing_artifact",
                "content_policy": "source report metadata unavailable",
            }
        )
    refs.append(
        {
            "artifact_ref": contract_schema_relpath,
            "source_status": "explicit_in_source",
            "content_policy": "PR90 output contract definitions",
        }
    )
    return refs


def _available_context(
    *,
    review: Mapping[str, Any],
    source_report_ref: Mapping[str, Any] | None,
    evidence_scope: str,
    local_private_shadow_status: str,
) -> dict[str, Any]:
    source_report = _mapping(source_report_ref.get("source_report")) if source_report_ref else {}
    return {
        "evidence_scope": evidence_scope or "not_supplied",
        "local_private_shadow_review_status": local_private_shadow_status,
        "source_report_checked_in": bool(source_report.get("checked_in")),
        "source_report_available_in_repo": bool(source_report.get("checked_in")),
        "source_report_kind": _text(source_report.get("source_run_kind")),
        "field_population_summary": _mapping(review.get("field_population_summary")),
        "source_scope_summary": {
            "scope_mode": "checked_in_safe_mode",
            "content_inclusion_mode": "metadata_only",
            "artifact_scope_status_counts": {
                "checked_in_safe_summary_only": 1,
            },
            "artifact_refs_by_scope_status": {},
            "specialists_must_cite_scope_status": True,
        },
        "truncation_summary": {
            "max_text_chars_per_artifact": None,
            "artifact_records_truncated": 0,
            "truncated_artifact_refs": [],
            "truncation_impact": "not_applicable_checked_in_safe_mode",
        },
        "local_private_retention_policy": _local_private_retention_policy(
            mode="checked_in_safe_mode"
        ),
        "populated_sections": _section_names(review.get("populated_sections")),
        "interpretation_needed_sections": _section_names(
            review.get("interpretation_needed_sections")
        ),
        "redacted_or_private_refs": _artifact_status_refs(
            review.get("redacted_or_private_sections")
        ),
        "missing_or_malformed_artifacts": _artifact_status_refs(
            review.get("missing_or_malformed_artifacts")
        ),
        "overtrust_risk_sections": _section_names(review.get("overtrust_risk_sections")),
        "behavioral_usefulness_summary": _behavioral_usefulness_summary(
            review.get("behavioral_usefulness")
        ),
        "report_readability": _text(review.get("report_readability")),
        "artifact_custody_read": _text(review.get("artifact_custody_read")),
        "semantic_interpretation_adequacy_read": _text(
            review.get("semantic_interpretation_adequacy_read")
        ),
        "product_delta_usefulness_read": _text(
            review.get("product_delta_usefulness_read")
        ),
        "human_validation_read": _text(review.get("human_validation_read")),
        "human_followup_questions": _strings(review.get("human_followup_questions")),
    }


def _missing_or_thin_context(
    *,
    review: Mapping[str, Any],
    source_report_ref: Mapping[str, Any] | None,
    evidence_scope: str,
    local_private_shadow_status: str,
) -> list[str]:
    notes: list[str] = []
    if evidence_scope:
        notes.append(f"evidence_scope:{evidence_scope}")
    if local_private_shadow_status and local_private_shadow_status != "completed":
        notes.append(f"local_private_shadow_review:{local_private_shadow_status}")
    source_report = _mapping(source_report_ref.get("source_report")) if source_report_ref else {}
    if not source_report:
        notes.append("source_report_metadata_missing")
    elif not source_report.get("checked_in"):
        notes.append("source_report_not_checked_in")
    field_population = _mapping(review.get("field_population_summary"))
    if _safe_int(field_population.get("clear_and_populated")) == 0:
        notes.append("no_populated_semantic_sections_in_fixture_review")
    required_count = _safe_int(field_population.get("requires_llm_interpretation"))
    if required_count:
        notes.append(f"requires_llm_interpretation_sections:{required_count}")
    if _section_names(review.get("overtrust_risk_sections")):
        notes.append("overtrust_risk_present")
    if not notes:
        notes.append("checked_in_safe_fixture_context_available_with_caveats")
    return list(dict.fromkeys(notes))


def _packet_known_limits(
    *,
    role: str,
    missing_or_thin_context: Sequence[str],
    available_context: Mapping[str, Any],
) -> list[str]:
    private_policy = _mapping(available_context.get("private_context_policy"))
    if private_policy:
        limits = [
            "local-private packet output is unsafe for commit by default",
            "packet builder does not infer conversation shape, likely actions, friction, lost value, or fan-in conclusions",
            "local-private access is not human validation and not product proof",
        ]
        if private_policy.get("content_inclusion_mode") == "metadata_only":
            limits.append(
                "artifact existence metadata is available, but private text was not included"
            )
        else:
            limits.append(
                "private artifact text may be included only because local-private include-text mode was explicitly requested"
            )
    else:
        limits = [
            "checked-in packet excludes raw transcript, raw revised answer, raw memo, provider text, private ledgers, and private local content",
            "packet builder does not infer conversation shape, likely actions, friction, lost value, or fan-in conclusions",
            "PR88 reviewed fixture outputs only; no local-private shadow review was run",
        ]
    limits.extend(
        [
        "packet builder does not infer conversation shape, likely actions, friction, lost value, or fan-in conclusions",
        ]
    )
    limits.extend(missing_or_thin_context)
    if not available_context.get("source_report_available_in_repo"):
        limits.append("generated Decision Trail report JSON is not checked in for this review target")
    if role in {"likely_action_reader", "friction_lost_value_reader"}:
        limits.append("role requires bounded interpretation before any candidate field can be filled")
    if role == "conservative_fan_in_reader":
        limits.append("fan-in must preserve disagreement and cannot vote or score")
    return list(dict.fromkeys(limits))


def _validate_contract_schema(contract_schema: Mapping[str, Any]) -> None:
    if _text(contract_schema.get("$id")) != SPECIALIST_CONTRACT_SCHEMA_VERSION:
        raise DecisionTrailSpecialistPacketInputError(
            "contract schema version is unsupported"
        )
    role_schema = _mapping(_mapping(contract_schema.get("properties")).get("specialist_roles"))
    required_roles = set(_strings(role_schema.get("required")))
    if set(SPECIALIST_ROLES) - required_roles:
        raise DecisionTrailSpecialistPacketInputError(
            "contract schema is missing required specialist roles"
        )


def _index_source_reports(value: Any, *, path: str) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for report_index, source_report in enumerate(_items(value)):
        report_id = _text(source_report.get("report_id"))
        if report_id:
            index[report_id] = {
                "source_report": source_report,
                "index": report_index,
                "path": path,
            }
    return index


def _local_private_shadow_status(fixture_review: Mapping[str, Any]) -> str:
    status = _mapping(fixture_review.get("local_private_shadow_review_status"))
    return _text(status.get("status")) or "not_supplied"


def _section_names(value: Any) -> list[str]:
    names: list[str] = []
    for item in _items(value):
        name = _text(item.get("section"))
        if name:
            names.append(name)
    return names


def _artifact_status_refs(value: Any) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for item in _items(value):
        artifact = _text(item.get("artifact"))
        section = _text(item.get("section"))
        if not artifact and not section:
            continue
        refs.append(
            {
                "ref": artifact or section,
                "classification": _text(item.get("classification")) or "not_supplied",
                "source_status": _text(item.get("source_status")) or "not_supplied",
            }
        )
    return refs


def _behavioral_usefulness_summary(value: Any) -> dict[str, str]:
    summary: dict[str, str] = {}
    behavior = _mapping(value)
    for key in (
        "what_changed_answerable",
        "evidence_support_answerable",
        "missingness_answerable",
        "non_claims_answerable",
        "more_careful_or_more_impressed",
    ):
        item = _mapping(behavior.get(key))
        answer = _text(item.get("answer"))
        if answer:
            summary[key] = answer
    return summary


def _items(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_text(item) for item in value if _text(item)]


def _text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""


def _safe_int(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    return 0


def _sha256_text(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _slug_text(value: str) -> str:
    chars = [
        char.lower() if char.isalnum() else "-"
        for char in value
    ]
    return "-".join(part for part in "".join(chars).split("-") if part)[:80]


def _dedupe_dicts(items: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for item in items:
        key = json.dumps(item, sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        result.append(dict(item))
    return result
