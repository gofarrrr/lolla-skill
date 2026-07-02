"""Offline Decision Work conversation interpretation packet construction.

PR130 prepares a contract-shaped dossier for future bounded LLM or human
interpretation. It is deterministic and read-only: it preserves source refs,
source status, missingness, redaction/private availability, custody flags,
future questions, and non-claims. It does not run Lolla, call models, mutate
archives, implement runtime extraction, or semantically fill PR128 fields.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import re
import string
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from engine.system_b.decision_work_brief_packets import (
    DecisionWorkBriefPacketInputError,
    build_decision_work_brief_packets,
    output_path_is_inside_run_dir,
)


DECISION_WORK_CONVERSATION_INTERPRETATION_PACKETS_SCHEMA_VERSION = (
    "lolla.decision_work_conversation_interpretation_packets.v0"
)
DECISION_WORK_CONVERSATION_INTERPRETATION_CONTRACT_SCHEMA_VERSION = (
    "lolla.decision_work_conversation_interpretation_contract.v0"
)
FUTURE_INTERPRETATION_READ_SCHEMA_VERSION = (
    "lolla.decision_work_conversation_interpretation_read.v0"
)
DEFAULT_CONTRACT_RELPATH = (
    "docs/conversation-understanding/"
    "decision-work-conversation-interpretation-contract-v0.json"
)
DEFAULT_PACKET_REVIEW_RELPATH = (
    "docs/conversation-understanding/"
    "decision-work-conversation-interpretation-contract-packet-review-v0.md"
)

PACKET_MODES = ("checked_in_safe", "local_private_metadata")
CONTRACT_FIELD_PACKET_STATUSES = (
    "status_only_ready",
    "requires_llm_interpretation",
    "requires_human_review",
    "local_private_metadata_only",
    "not_currently_captured",
    "unclear",
)
CONTRACT_SOURCE_STATUSES = (
    "source_refs_available",
    "source_refs_available_with_private_or_redacted_limits",
    "local_private_or_redacted_only",
    "missing_source",
    "not_currently_captured",
    "unclear",
)
NON_CLAIMS = (
    "packet_is_not_interpretation",
    "packet_is_not_a_decision_work_brief",
    "packet_is_not_product_proof",
    "packet_does_not_score_answer_quality",
    "packet_does_not_authorize_agent_action",
    "packet_does_not_validate_decision_correctness",
    "packet_does_not_run_lolla",
    "packet_does_not_call_models",
    "packet_does_not_change_runtime",
    "packet_does_not_fill_pr128_fields",
    "clean_artifacts_do_not_imply_good_advice",
    "future_interpretation_required",
)

GROUP_FUTURE_QUESTIONS = {
    "decision_shape": (
        "What decision was being made, what direction did the work appear to "
        "start from, and what action consequence should be tested later?"
    ),
    "options_and_paths": (
        "Which options were live, abandoned, rejected, deferred, gated, or "
        "conditioned by thresholds and stop rules?"
    ),
    "conversation_process": (
        "What did the conversation process add, drop, pressure, or leave "
        "unresolved?"
    ),
    "provided_context_and_evidence": (
        "What context or external evidence was provided, and which parts must "
        "remain local/private?"
    ),
    "stakeholders_and_values": (
        "Which values, stakeholder obligations, relationships, or political "
        "constraints require interpretation or human review?"
    ),
    "constraints_and_unknowns": (
        "Which timing, capacity, legal, compliance, safety, and real-world "
        "unknowns constrain the decision?"
    ),
    "audit_pressure_and_change": (
        "What did Lolla press on, and what changed for action, threshold, "
        "sequence, gate, stop rule, or scope?"
    ),
    "losses_and_overcorrection": (
        "What useful friction, noisy friction, lost value, overcorrection, "
        "false precision, or generic caution risk should a later interpreter "
        "test?"
    ),
    "evidence_and_custody": (
        "Which source refs, private-context availability, and redaction status "
        "back or limit the interpretation?"
    ),
    "handoff_for_brief": (
        "What can later feed a Decision Work Brief, and what must the brief not "
        "claim?"
    ),
    "handoff_for_agent_inspection": (
        "What can later orient agent inspection without authorizing agent "
        "action?"
    ),
}

FIELD_ALLOWED_SOURCES: dict[str, tuple[str, ...]] = {
    "decision_question": (
        "extraction.json",
        "reasoning_trace.json",
        "agent_result.json",
        "decision_work_brief",
        "rendered_decision_work_brief",
    ),
    "likely_starting_direction": (
        "conversation.txt",
        "extraction.json",
        "reasoning_trace.json",
        "decision_work_brief_packet",
    ),
    "revised_direction_or_action_consequence": (
        "revised.txt",
        "memo.md",
        "agent_result.json",
        "result.json",
        "decision_work_brief",
        "rendered_decision_work_brief",
    ),
    "live_options": ("conversation.txt", "extraction.json", "result.json"),
    "abandoned_or_rejected_options": (
        "conversation.txt",
        "extraction.json",
        "result.json",
        "memo.md",
    ),
    "option_status": ("conversation.txt", "extraction.json", "result.json"),
    "decision_thresholds": ("result.json", "agent_result.json", "memo_note.json"),
    "stop_rules": ("result.json", "agent_result.json", "memo_note.json"),
    "evidence_gates": (
        "result.json",
        "agent_result.json",
        "memo_note.json",
        "graph_survival_report.json",
    ),
    "conversation_turn_depth": (
        "extraction.json",
        "result.json",
        "reasoning_trace.json",
    ),
    "assistant_influence_on_user_framing": (
        "conversation.txt",
        "live_transcript.txt",
        "extraction.json",
    ),
    "user_changed_mind_during_conversation": (
        "conversation.txt",
        "live_transcript.txt",
        "extraction.json",
    ),
    "assistant_sycophancy_or_over-accommodation_risk": (
        "conversation.txt",
        "live_transcript.txt",
        "result.json",
    ),
    "unresolved_threads": ("extraction.json", "result.json", "reasoning_trace.json"),
    "dropped_threads": ("extraction.json", "result.json", "reasoning_trace.json"),
    "premortem_or_counterfactual_pressure": (
        "result.json",
        "agent_result.json",
        "graph_survival_report.json",
    ),
    "alternative_frames_considered": (
        "extraction.json",
        "result.json",
        "reasoning_trace.json",
    ),
    "user_provided_context": ("conversation.txt", "extraction.json"),
    "pasted_documents_or_external_context": (
        "conversation.txt",
        "operator.log",
        "extraction.json",
    ),
    "user_values_or_priorities": ("conversation.txt", "extraction.json"),
    "stakeholder_obligations": ("conversation.txt", "extraction.json", "result.json"),
    "relationship_or_political_constraints": (
        "conversation.txt",
        "extraction.json",
        "memo.md",
    ),
    "timing_or_runway_constraints": ("extraction.json", "result.json", "memo.md"),
    "operational_capacity_constraints": (
        "extraction.json",
        "result.json",
        "memo.md",
    ),
    "legal_compliance_or_safety_constraints": (
        "extraction.json",
        "result.json",
        "memo.md",
    ),
    "real_world_unknowns": (
        "extraction.json",
        "result.json",
        "reasoning_trace.json",
    ),
    "unknown_unknowns_or_context_not_available_to_model": (
        "evaluation.json",
        "result.json",
        "operator.log",
    ),
    "what_lolla_pressed_on": (
        "result.json",
        "agent_result.json",
        "graph_survival_report.json",
    ),
    "what_changed": ("revised.txt", "result.json", "agent_result.json", "memo.md"),
    "useful_friction": (
        "result.json",
        "agent_result.json",
        "pre_step6_private_table_ledger.json",
    ),
    "noisy_friction": (
        "result.json",
        "agent_result.json",
        "pre_step6_private_table_ledger.json",
    ),
    "lost_value": (
        "conversation.txt",
        "revised.txt",
        "memo.md",
        "v60_ledger.json",
    ),
    "overcorrection_risk": ("result.json", "memo.md", "v60_ledger.json"),
    "false_precision_risk": ("result.json", "evaluation.json", "memo.md"),
    "generic_caution_risk": ("result.json", "evaluation.json", "memo.md"),
    "momentum_or_ambition_loss": (
        "conversation.txt",
        "revised.txt",
        "memo.md",
        "v60_ledger.json",
    ),
    "source_refs": ("*source_inventory*",),
    "private_context_available": ("*source_inventory*",),
    "redacted_or_not_checked_in": ("*source_inventory*",),
    "what_the_final_answer_does_not_prove": (
        "decision_work_brief",
        "rendered_decision_work_brief",
        "evaluation.json",
    ),
    "safe_to_show_user": (
        "decision_work_brief",
        "rendered_decision_work_brief",
        "evaluation.json",
    ),
    "safe_for_agent_inspection_only": ("*source_inventory*",),
    "requires_human_review": ("*source_inventory*",),
    "requires_llm_interpretation": ("*source_inventory*",),
    "deterministic_only_metadata": ("*source_inventory*",),
    "local_private_only": ("*source_inventory*",),
}

NOT_CURRENTLY_CAPTURED_FIELDS = {
    "option_status",
    "user_changed_mind_during_conversation",
    "unknown_unknowns_or_context_not_available_to_model",
    "safe_to_show_user",
    "safe_for_agent_inspection_only",
}


class DecisionWorkConversationInterpretationPacketInputError(ValueError):
    """Deterministic, sanitized offline-packet input error."""


def build_decision_work_conversation_interpretation_packets(
    *,
    run_dir: Path | str,
    contract_path: Path | str = DEFAULT_CONTRACT_RELPATH,
    mode: str = "checked_in_safe",
    decision_work_brief_packet_path: Path | str | None = None,
    decision_work_brief_path: Path | str | None = None,
    rendered_decision_work_brief_path: Path | str | None = None,
    decision_work_receipt_path: Path | str | None = None,
    decision_trail_report_path: Path | str | None = None,
    product_delta_report_path: Path | str | None = None,
    created_at: str | None = None,
    limit_fields: int | None = None,
) -> dict[str, Any]:
    """Build a PR128 contract-shaped offline interpretation packet."""

    if mode not in PACKET_MODES:
        raise DecisionWorkConversationInterpretationPacketInputError(
            "unsupported packet mode"
        )
    if limit_fields is not None and limit_fields < 1:
        raise DecisionWorkConversationInterpretationPacketInputError(
            "limit fields must be positive"
        )

    run_path = Path(run_dir).expanduser()
    if not run_path.exists():
        raise DecisionWorkConversationInterpretationPacketInputError(
            "run directory was not found"
        )
    if not run_path.is_dir():
        raise DecisionWorkConversationInterpretationPacketInputError(
            "run directory is not a directory"
        )

    contract, contract_record = _load_contract(contract_path)
    if contract["schema_version"] != (
        DECISION_WORK_CONVERSATION_INTERPRETATION_CONTRACT_SCHEMA_VERSION
    ):
        raise DecisionWorkConversationInterpretationPacketInputError(
            "unsupported contract schema version"
        )

    try:
        brief_packet = build_decision_work_brief_packets(
            run_dir=run_path,
            mode="metadata_only",
            include_private_text=False,
            decision_work_receipt_path=decision_work_receipt_path,
            decision_trail_report_path=decision_trail_report_path,
            product_delta_report_path=product_delta_report_path,
            created_at=created_at,
        )
    except DecisionWorkBriefPacketInputError as exc:
        raise DecisionWorkConversationInterpretationPacketInputError(
            str(exc)
        ) from exc

    source_inventory = [_source_inventory_record(record) for record in brief_packet["input_refs"]]
    optional_records = [
        _optional_supporting_artifact_record(
            input_id="decision_work_brief_packet",
            source_kind="decision_work_brief_packet",
            path=decision_work_brief_packet_path,
            expected_schema="lolla.decision_work_brief_packets.v0",
        ),
        _optional_supporting_artifact_record(
            input_id="decision_work_brief",
            source_kind="decision_work_brief",
            path=decision_work_brief_path,
            expected_schema="lolla.decision_work_brief.v0",
        ),
        _optional_supporting_artifact_record(
            input_id="rendered_decision_work_brief",
            source_kind="rendered_decision_work_brief",
            path=rendered_decision_work_brief_path,
            expected_schema=None,
        ),
    ]
    source_inventory.extend(optional_records)

    field_groups = _contract_field_groups(
        contract=contract,
        source_inventory=source_inventory,
        limit_fields=limit_fields,
    )
    future_tasks = _future_interpretation_tasks(
        field_groups=field_groups,
        source_inventory=source_inventory,
    )

    case_id = _text(brief_packet["packet_metadata"].get("case_id")) or "unknown_case"
    run_id = _text(brief_packet["packet_metadata"].get("run_id")) or "unknown_run"
    checked_in_safe = mode == "checked_in_safe"

    return {
        "schema_version": (
            DECISION_WORK_CONVERSATION_INTERPRETATION_PACKETS_SCHEMA_VERSION
        ),
        "packet_metadata": {
            "packet_id": (
                f"decision_work_conversation_interpretation_packets:{case_id}:{run_id}"
            ),
            "created_at": created_at or _utc_now_iso(),
            "case_id": case_id,
            "run_id": run_id,
            "archive_relpath": f"{case_id}/{run_id}",
            "mode": mode,
            "generated_by": "decision_work_conversation_interpretation_packet_builder",
            "schema_version": (
                DECISION_WORK_CONVERSATION_INTERPRETATION_PACKETS_SCHEMA_VERSION
            ),
            "notes": [
                "PR130 prepares a source/status packet only; it does not interpret conversation meaning."
            ],
        },
        "mode": mode,
        "source_run": brief_packet["source_run"],
        "source_contract": {
            "schema_version": contract["schema_version"],
            "contract_ref": _safe_relative_or_name(contract_record["artifact"]),
            "contract_doc_ref": (
                "docs/conversation-understanding/"
                "decision-work-conversation-interpretation-contract-v0.md"
            ),
            "content_included": False,
            "raw_private_content_included": False,
            "provider_text_included": False,
        },
        "source_inventory": source_inventory,
        "custody_flags": _custody_flags(mode=mode, checked_in_safe=checked_in_safe),
        "contract_field_groups": field_groups,
        "future_interpretation_tasks": future_tasks,
        "required_future_output": {
            "schema_version": FUTURE_INTERPRETATION_READ_SCHEMA_VERSION,
            "source_contract_schema_version": contract["schema_version"],
            "semantic_fields_filled": False,
            "future_interpreter_required": True,
            "must_preserve_source_refs": True,
            "must_not_score_answer_quality": True,
            "must_not_authorize_agent_action": True,
            "must_not_claim_product_proof": True,
        },
        "non_claims": list(NON_CLAIMS),
    }


def render_decision_work_conversation_interpretation_packets_json(
    packet: Mapping[str, Any],
    *,
    pretty: bool = False,
) -> str:
    """Render an offline interpretation packet as JSON."""

    if pretty:
        return json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return json.dumps(
        packet,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ) + "\n"


def validate_output_path(
    *,
    output_path: Path | str,
    run_dir: Path | str,
) -> Path:
    """Validate output location without touching the run archive."""

    if output_path_is_inside_run_dir(output_path=output_path, run_dir=run_dir):
        raise DecisionWorkConversationInterpretationPacketInputError(
            "output path must be outside run directory"
        )
    output = Path(output_path).expanduser()
    if output.exists() and output.is_dir():
        raise DecisionWorkConversationInterpretationPacketInputError(
            "output path is a directory"
        )
    return output


def write_decision_work_conversation_interpretation_packets_output(
    path: Path | str,
    payload: str,
) -> None:
    """Write rendered packet JSON."""

    output = Path(path).expanduser()
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    except OSError as exc:
        raise DecisionWorkConversationInterpretationPacketInputError(
            f"output could not be written:{type(exc).__name__}"
        ) from exc


def _load_contract(path: Path | str) -> tuple[dict[str, Any], dict[str, Any]]:
    contract_path = Path(path).expanduser()
    if not contract_path.exists():
        raise DecisionWorkConversationInterpretationPacketInputError(
            "contract file was not found"
        )
    if not contract_path.is_file():
        raise DecisionWorkConversationInterpretationPacketInputError(
            "contract path is not a file"
        )
    try:
        text = contract_path.read_text(encoding="utf-8")
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DecisionWorkConversationInterpretationPacketInputError(
            "contract JSON could not be parsed"
        ) from exc
    except UnicodeDecodeError as exc:
        raise DecisionWorkConversationInterpretationPacketInputError(
            "contract JSON was not valid UTF-8"
        ) from exc
    if not isinstance(payload, dict):
        raise DecisionWorkConversationInterpretationPacketInputError(
            "contract JSON root was not an object"
        )
    return payload, {
        "artifact": _display_artifact_ref(contract_path),
        "schema_version": _text(payload.get("schema_version")) or None,
        "sha256": _sha256_text(text),
        "byte_count": len(text.encode("utf-8")),
    }


def _source_inventory_record(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "ref_id": _text(record.get("ref_id")),
        "artifact": _text(record.get("artifact")),
        "relative_path": record.get("relative_path"),
        "source_kind": _text(record.get("source_kind")),
        "source_status": _contract_source_status(record),
        "packet_source_status": _text(record.get("source_status")),
        "read_status": _text(record.get("read_status")),
        "schema_version": record.get("schema_version"),
        "sha256": record.get("sha256"),
        "byte_count": record.get("byte_count"),
        "content_included": False,
        "raw_private_content_included": False,
        "provider_text_included": False,
        "local_absolute_path_included": False,
        "status_only": True,
        "notes": list(record.get("notes") or []),
    }


def _optional_supporting_artifact_record(
    *,
    input_id: str,
    source_kind: str,
    path: Path | str | None,
    expected_schema: str | None,
) -> dict[str, Any]:
    base = {
        "ref_id": input_id,
        "artifact": f"{input_id}:not_supplied",
        "relative_path": None,
        "source_kind": source_kind,
        "source_status": "missing_artifact",
        "packet_source_status": "not_supplied",
        "read_status": "not_supplied",
        "schema_version": None,
        "sha256": None,
        "byte_count": None,
        "content_included": False,
        "raw_private_content_included": False,
        "provider_text_included": False,
        "local_absolute_path_included": False,
        "status_only": True,
        "notes": [
            "Optional supporting artifact was not supplied; this is source status, not a semantic finding."
        ],
    }
    if path is None:
        return base

    artifact_path = Path(path).expanduser()
    artifact_ref = _display_artifact_ref(artifact_path)
    base.update(
        {
            "artifact": artifact_ref,
            "relative_path": artifact_ref if not artifact_path.is_absolute() else None,
            "read_status": "metadata_only",
            "notes": [
                "Optional supporting artifact was referenced by metadata only; content was not copied."
            ],
        }
    )
    if not artifact_path.exists():
        base["source_status"] = "missing_artifact"
        base["packet_source_status"] = "unavailable_missing_artifact"
        return base
    if not artifact_path.is_file():
        base["source_status"] = "unclear"
        base["packet_source_status"] = "unclear"
        return base

    stat = artifact_path.stat()
    base["byte_count"] = stat.st_size
    if expected_schema is None:
        base["source_status"] = "available_from_checked_in_safe_artifact"
        base["packet_source_status"] = "available_from_structured_artifact"
        return base

    try:
        text = artifact_path.read_text(encoding="utf-8")
        payload = json.loads(text)
    except (json.JSONDecodeError, UnicodeDecodeError):
        base["source_status"] = "malformed_artifact"
        base["packet_source_status"] = "unavailable_malformed_artifact"
        return base
    if not isinstance(payload, dict):
        base["source_status"] = "malformed_artifact"
        base["packet_source_status"] = "unavailable_malformed_artifact"
        return base
    base["schema_version"] = _text(payload.get("schema_version")) or None
    base["sha256"] = _sha256_text(text)
    base["source_status"] = "available_from_checked_in_safe_artifact"
    base["packet_source_status"] = (
        "available_from_structured_artifact"
        if base["schema_version"] == expected_schema
        else "unclear"
    )
    return base


def _contract_field_groups(
    *,
    contract: Mapping[str, Any],
    source_inventory: list[dict[str, Any]],
    limit_fields: int | None,
) -> dict[str, Any]:
    groups: dict[str, Any] = {}
    fields_left = limit_fields
    for group_id, raw_fields in _mapping(contract.get("field_groups")).items():
        if fields_left is not None and fields_left <= 0:
            break
        group_fields = []
        for field in _sequence(raw_fields):
            if fields_left is not None and fields_left <= 0:
                break
            field_mapping = _mapping(field)
            field_name = _text(field_mapping.get("field_name"))
            group_fields.append(
                _field_packet(
                    group_id=group_id,
                    field=field_mapping,
                    source_inventory=source_inventory,
                )
            )
            if fields_left is not None:
                fields_left -= 1
        groups[group_id] = {
            "field_group": group_id,
            "future_question": GROUP_FUTURE_QUESTIONS.get(
                group_id,
                "What should a future interpreter answer for this field group?",
            ),
            "interpretation_task_id": f"{group_id}_read",
            "fields": group_fields,
            "packet_builder_filled_semantics": False,
            "notes": [
                "Fields are prepared for future interpretation; values are not filled by deterministic code."
            ],
        }
    return groups


def _field_packet(
    *,
    group_id: str,
    field: Mapping[str, Any],
    source_inventory: list[dict[str, Any]],
) -> dict[str, Any]:
    field_name = _text(field.get("field_name"))
    source_refs = _field_source_refs(
        field_name=field_name,
        source_inventory=source_inventory,
    )
    status = _field_packet_status(field=field, field_name=field_name)
    source_status = _field_source_status(
        field_name=field_name,
        source_refs=source_refs,
    )
    return {
        "field_group": group_id,
        "field_name": field_name,
        "purpose": _text(field.get("purpose")),
        "owner": _text(field.get("owner")),
        "interpretation_required": _text(field.get("interpretation_required")),
        "deterministic_allowed": bool(field.get("deterministic_allowed")),
        "human_review_required_when": _text(field.get("human_review_required_when")),
        "source_refs_required": bool(field.get("source_refs_required")),
        "empty_meaning": _text(field.get("empty_meaning")),
        "privacy_handling": _text(field.get("privacy_handling")),
        "checked_in_safe_policy": _text(field.get("checked_in_safe_policy")),
        "local_private_policy": _text(field.get("local_private_policy")),
        "should_feed_brief": bool(field.get("should_feed_brief")),
        "should_feed_agent_inspection": bool(
            field.get("should_feed_agent_inspection")
        ),
        "must_not_be_used_as_quality_label": True,
        "current_packet_status": status,
        "source_status": source_status,
        "source_refs": source_refs,
        "unavailable_or_redacted_sources": [
            ref
            for ref in source_refs
            if ref["source_status"]
            in {
                "available_but_redacted",
                "available_from_local_private_artifact",
                "missing_artifact",
                "malformed_artifact",
                "not_captured",
                "unclear",
            }
        ],
        "future_interpretation_question": _future_question(
            field_name=field_name,
            purpose=_text(field.get("purpose")),
        ),
        "interpretation_task_status": "not_answered",
        "semantic_field_filled": False,
        "value": None,
        "required_output_contract_ref": {
            "schema_version": (
                DECISION_WORK_CONVERSATION_INTERPRETATION_CONTRACT_SCHEMA_VERSION
            ),
            "schema_path": DEFAULT_CONTRACT_RELPATH,
            "field_group": group_id,
            "field_name": field_name,
        },
        "known_limits": _field_known_limits(status=status, source_status=source_status),
    }


def _field_source_refs(
    *,
    field_name: str,
    source_inventory: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    allowed_sources = FIELD_ALLOWED_SOURCES.get(field_name, ("*source_inventory*",))
    if allowed_sources == ("*source_inventory*",):
        records = source_inventory
    else:
        records = [
            record
            for record in source_inventory
            if record["artifact"] in allowed_sources
            or record["source_kind"] in allowed_sources
        ]
    return [
        {
            "ref_id": record["ref_id"],
            "artifact": record["artifact"],
            "source_kind": record["source_kind"],
            "source_status": record["source_status"],
            "read_status": record["read_status"],
            "content_included": False,
            "raw_private_content_included": False,
            "provider_text_included": False,
            "local_absolute_path_included": False,
        }
        for record in records
    ]


def _field_packet_status(*, field: Mapping[str, Any], field_name: str) -> str:
    if field_name in NOT_CURRENTLY_CAPTURED_FIELDS:
        return "not_currently_captured"
    owner = _text(field.get("owner"))
    privacy = _text(field.get("privacy_handling"))
    interpretation_required = _text(field.get("interpretation_required"))
    if owner == "human_review":
        return "requires_human_review"
    if privacy in {"local_private_only", "redacted_in_checked_in_safe_mode"}:
        return "local_private_metadata_only"
    if interpretation_required == "yes":
        return "requires_llm_interpretation"
    return "status_only_ready"


def _field_source_status(*, field_name: str, source_refs: list[dict[str, Any]]) -> str:
    if field_name in NOT_CURRENTLY_CAPTURED_FIELDS:
        return "not_currently_captured"
    if not source_refs:
        return "missing_source"
    statuses = {ref["source_status"] for ref in source_refs}
    if statuses <= {"missing_artifact", "not_captured", "unclear"}:
        return "missing_source"
    if statuses & {"available_but_redacted", "available_from_local_private_artifact"}:
        if statuses & {"available_from_checked_in_safe_artifact"}:
            return "source_refs_available_with_private_or_redacted_limits"
        return "local_private_or_redacted_only"
    if statuses & {"available_from_checked_in_safe_artifact"}:
        return "source_refs_available"
    return "unclear"


def _future_interpretation_tasks(
    *,
    field_groups: Mapping[str, Mapping[str, Any]],
    source_inventory: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    tasks = []
    for group_id, group in field_groups.items():
        fields = list(_sequence(group.get("fields")))
        tasks.append(
            {
                "task_id": f"{group_id}_read",
                "field_group": group_id,
                "status": "not_answered",
                "future_question": _text(group.get("future_question")),
                "target_fields": [_text(field.get("field_name")) for field in fields],
                "allowed_source_refs": _dedupe_task_source_refs(fields),
                "known_unavailable_or_redacted_sources": [
                    _source_ref_summary(record)
                    for record in source_inventory
                    if record["source_status"]
                    in {
                        "available_but_redacted",
                        "available_from_local_private_artifact",
                        "missing_artifact",
                        "malformed_artifact",
                        "unclear",
                    }
                ],
                "required_future_output_schema": FUTURE_INTERPRETATION_READ_SCHEMA_VERSION,
                "must_preserve_source_refs": True,
                "must_not_score_answer_quality": True,
                "must_not_authorize_agent_action": True,
                "must_not_claim_product_proof": True,
                "semantic_output_filled_by_packet_builder": False,
            }
        )
    return tasks


def _dedupe_task_source_refs(fields: Sequence[Any]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    refs = []
    for field in fields:
        for ref in _sequence(_mapping(field).get("source_refs")):
            ref_mapping = _mapping(ref)
            key = (_text(ref_mapping.get("ref_id")), _text(ref_mapping.get("artifact")))
            if key in seen:
                continue
            seen.add(key)
            refs.append(
                {
                    "ref_id": key[0],
                    "artifact": key[1],
                    "source_kind": _text(ref_mapping.get("source_kind")),
                    "source_status": _text(ref_mapping.get("source_status")),
                }
            )
    return refs


def _field_known_limits(*, status: str, source_status: str) -> list[str]:
    limits = [
        "packet_builder_did_not_interpret_field",
        "field_value_is_unfilled",
        "future_interpreter_must_cite_source_refs",
        "must_not_be_used_as_quality_label",
    ]
    if status in {"requires_llm_interpretation", "local_private_metadata_only"}:
        limits.append("future_llm_or_human_interpretation_required")
    if status == "requires_human_review":
        limits.append("human_review_required_before_user_facing_claim")
    if source_status in {
        "source_refs_available_with_private_or_redacted_limits",
        "local_private_or_redacted_only",
        "missing_source",
    }:
        limits.append(
            "missing_redacted_or_private_sources_are_availability_status_not_semantic_evidence"
        )
    return limits


def _future_question(*, field_name: str, purpose: str) -> str:
    if purpose:
        return f"What should a future interpreter record for {field_name}: {purpose}"
    return f"What should a future interpreter record for {field_name}?"


def _custody_flags(*, mode: str, checked_in_safe: bool) -> dict[str, Any]:
    return {
        "runtime_invoked": False,
        "skill_invoked": False,
        "archive_mutated": False,
        "model_calls": 0,
        "provider_calls": 0,
        "semantic_fields_filled": False,
        "semantic_interpretation_performed": False,
        "human_validated": False,
        "product_proof": False,
        "answer_quality_scored": False,
        "agent_action_authorized": False,
        "brief_generated": False,
        "runtime_extraction_implemented": False,
        "raw_private_content_included": False,
        "provider_text_included": False,
        "raw_transcript_included": False,
        "raw_revised_answer_included": False,
        "raw_memo_included": False,
        "private_ledger_content_included": False,
        "local_absolute_paths_included": False,
        "secrets_included": False,
        "automatic_labels_created": False,
        "broad_judge_used": False,
        "checked_in_safe": checked_in_safe,
        "unsafe_for_commit": False,
        "requires_operator_review_before_share": mode == "local_private_metadata",
    }


def _contract_source_status(record: Mapping[str, Any]) -> str:
    status = _text(record.get("source_status")) or _text(record.get("status"))
    if status == "available_from_structured_artifact":
        return "available_from_checked_in_safe_artifact"
    if status == "available_but_redacted_in_safe_mode":
        return "available_but_redacted"
    if status == "available_in_private_artifact_not_exported":
        return "available_from_local_private_artifact"
    if status in {"not_supplied", "unavailable_missing_artifact"}:
        return "missing_artifact"
    if status == "unavailable_malformed_artifact":
        return "malformed_artifact"
    if status == "explicit_in_source":
        return "available_from_local_private_artifact"
    return "unclear"


def _source_ref_summary(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "ref_id": _text(record.get("ref_id")),
        "artifact": _text(record.get("artifact")),
        "source_kind": _text(record.get("source_kind")),
        "source_status": _text(record.get("source_status")),
    }


def _display_artifact_ref(path: Path) -> str:
    if path.is_absolute():
        return _safe_token(path.name)
    return str(path)


def _safe_relative_or_name(value: str) -> str:
    if value.startswith("/"):
        return _safe_token(Path(value).name)
    return value


def _safe_token(value: str) -> str:
    allowed = set(string.ascii_letters + string.digits + "._-")
    cleaned = "".join(char if char in allowed else "_" for char in value.strip())
    return cleaned.strip("._-") or "artifact"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> Sequence[Any]:
    return value if isinstance(value, Sequence) and not isinstance(value, str) else ()


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _utc_now_iso() -> str:
    return _dt.datetime.now(tz=_dt.UTC).replace(microsecond=0).isoformat()
