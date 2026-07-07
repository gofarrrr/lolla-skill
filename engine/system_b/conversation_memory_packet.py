"""Offline conversation-memory packet builder for completed Lolla runs.

This module compiles existing archive artifacts into a structured, testable
packet that can be rendered as self-explaining Markdown. It does not run Lolla,
call providers, mutate the input archive, score advice quality, or authorize
action.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


CONVERSATION_MEMORY_PACKET_SCHEMA_VERSION = "lolla.conversation_memory_packet.v0"
CONVERSATION_MEMORY_BUNDLE_WRITE_SCHEMA_VERSION = "lolla.conversation_memory_bundle_write.v0"
CONVERSATION_MEMORY_PACKET_FILENAME = "conversation_memory_packet.json"
CONVERSATION_MEMORY_MARKDOWN_FILENAME = "conversation_memory.md"

PRIVACY_MODES = frozenset({"public_safe", "user_private", "operator_debug"})
REQUIRED_STRUCTURED_ARTIFACTS = (
    "reasoning_trace.json",
    "agent_result.json",
    "evaluation.json",
)

ARTIFACT_ROLES: dict[str, str] = {
    "conversation.txt": "source_conversation",
    "extraction.json": "decision_structure",
    "result.json": "pipeline_result",
    "revised.txt": "reconsidered_position",
    "memo.md": "decision_memo",
    "memo_note.json": "decision_memo_fields",
    "agent_result.json": "agent_handoff",
    "reasoning_trace.json": "artifact_index",
    "evaluation.json": "deterministic_run_readiness",
    "graph_survival_report.json": "graph_survival_report",
    "graph_survival_report.md": "graph_survival_report_markdown",
    "run_events.json": "run_event_ledger",
    "gapcheck.txt": "pressure_check_summary",
    "gapcheck_lanes.json": "pressure_check_state",
    "control_input.json": "control_plane_input",
    "control_result.json": "control_plane_result",
    "extraction_adequacy_report.json": "extraction_adequacy_report",
    "pre_step6_private_table.json": "private_reasoning_table",
    "pre_step6_private_table.md": "private_reasoning_table_markdown",
    "pre_step6_private_table_ledger.json": "private_reasoning_table_ledger",
    "v60_ledger.json": "private_enrichment_ledger",
    "v60_ledger_skeleton.json": "private_enrichment_ledger_skeleton",
    "operator.log": "operator_log",
    "live_transcript.txt": "live_product_surface",
}

ARTIFACT_INVENTORY = tuple(ARTIFACT_ROLES)
PRIVATE_ARTIFACTS = frozenset(
    {
        "pre_step6_private_table.json",
        "pre_step6_private_table.md",
        "pre_step6_private_table_ledger.json",
        "v60_ledger.json",
        "v60_ledger_skeleton.json",
        "operator.log",
        "live_transcript.txt",
    }
)

NON_CLAIMS = (
    "not_runtime_source_of_truth",
    "not_archive_mutation",
    "not_runtime_default",
    "not_model_call",
    "not_answer_quality_scoring",
    "not_advice_correctness",
    "not_answer_correctness",
    "not_action_authorization",
    "not_human_validation",
    "selected_lenses_are_not_proof",
    "suppressed_lenses_are_not_noise",
)

INTERPRETATION_LEGEND = (
    {
        "label": "source",
        "meaning": "Copied directly from a source artifact.",
    },
    {
        "label": "summary",
        "meaning": "Compressed from one source artifact.",
    },
    {
        "label": "synthesis",
        "meaning": "Compiled from multiple artifacts.",
    },
    {
        "label": "inference",
        "meaning": "Renderer or Lolla interpretation beyond one direct source field.",
    },
    {
        "label": "selection_trace",
        "meaning": "Deterministic selection or survival record from run artifacts.",
    },
    {
        "label": "missing",
        "meaning": "Known absent input, artifact, or context.",
    },
    {
        "label": "unknown",
        "meaning": "Not enough evidence was present in the archive.",
    },
    {
        "label": "private",
        "meaning": "Should not be shared without explicit user approval.",
    },
)

UPFLOW_STAGES = (
    {
        "stage": "raw_conversation",
        "role": "Source of what was said.",
        "future_reader_note": "Closest to the user exchange; may be private or absent.",
    },
    {
        "stage": "capture_artifact",
        "role": "Persisted conversation capture.",
        "future_reader_note": "Check artifact presence and capture adequacy before relying on interpretation.",
    },
    {
        "stage": "extraction",
        "role": "System interpretation of the conversation.",
        "future_reader_note": "Useful, but can miss nuance or infer too much.",
    },
    {
        "stage": "system_b_pipeline_result",
        "role": "Lolla analysis and lane output.",
        "future_reader_note": "Rich system output; not all fields are user-facing.",
    },
    {
        "stage": "revised_answer_and_memo",
        "role": "Product-facing synthesis.",
        "future_reader_note": "Useful for reading, not proof of correctness.",
    },
    {
        "stage": "archive_time_sidecars",
        "role": "Custody, readiness, graph survival, and events.",
        "future_reader_note": "Best place to verify artifact status and system behavior.",
    },
    {
        "stage": "conversation_memory_packet",
        "role": "Structured compiled memory.",
        "future_reader_note": "Testable contract for Markdown rendering.",
    },
    {
        "stage": "markdown_or_okf_view",
        "role": "Human/agent reading layer.",
        "future_reader_note": "Portable view, not source of truth.",
    },
)

READING_PROTOCOL = (
    'Read "What This File Is" and "What This File Is Not."',
    "Check privacy mode and non-claims.",
    "Read Run Summary and Conversation Interpretation.",
    "Read What Changed and Open Questions.",
    "Inspect Lenses Applied and Deterministic Selection Trace.",
    "Use Artifact Custody to verify or go deeper.",
    "Do not treat this file as proof of advice correctness.",
)


class ConversationMemoryInputError(ValueError):
    """Sanitized conversation-memory input error."""


def build_conversation_memory_packet(
    *,
    run_dir: Path | str,
    privacy_mode: str = "user_private",
    include_raw_conversation: bool = False,
    created_at: str | None = None,
    strict: bool = True,
) -> dict[str, Any]:
    """Build a structured ``lolla.conversation_memory_packet.v0`` packet."""

    run_path = _validated_run_dir(run_dir)
    privacy_mode = _validated_privacy_mode(privacy_mode)
    if privacy_mode == "public_safe" and include_raw_conversation:
        raise ConversationMemoryInputError("public_safe mode cannot include raw conversation")

    artifact_records = [_artifact_record(run_path, name) for name in ARTIFACT_INVENTORY]
    artifact_status = {record["artifact"]: record["status"] for record in artifact_records}
    missing_required = [
        name
        for name in REQUIRED_STRUCTURED_ARTIFACTS
        if artifact_status.get(name) != "present"
    ]
    malformed_required: list[str] = []

    payloads: dict[str, Mapping[str, Any]] = {}
    for artifact_name in (
        "reasoning_trace.json",
        "agent_result.json",
        "evaluation.json",
        "extraction.json",
        "result.json",
        "memo_note.json",
        "graph_survival_report.json",
        "run_events.json",
    ):
        status, payload = _read_json_artifact(run_path / artifact_name)
        if status == "malformed" and artifact_name in REQUIRED_STRUCTURED_ARTIFACTS:
            malformed_required.append(artifact_name)
        if payload is not None:
            payloads[artifact_name] = payload

    if strict and (missing_required or malformed_required):
        pieces = []
        if missing_required:
            pieces.append("missing required artifact(s): " + ", ".join(missing_required))
        if malformed_required:
            pieces.append("malformed required artifact(s): " + ", ".join(malformed_required))
        raise ConversationMemoryInputError("; ".join(pieces))

    conversation_text = ""
    if include_raw_conversation and privacy_mode in {"user_private", "operator_debug"}:
        conversation_text = _read_text(run_path / "conversation.txt")

    memo_text = _read_text(run_path / "memo.md")
    revised_text = _read_text(run_path / "revised.txt")

    trace = payloads.get("reasoning_trace.json", {})
    agent_result = payloads.get("agent_result.json", {})
    evaluation = payloads.get("evaluation.json", {})
    extraction = payloads.get("extraction.json", {})
    result = payloads.get("result.json", {})
    memo_note = payloads.get("memo_note.json", {})
    graph_survival = payloads.get("graph_survival_report.json", {})
    run_events = payloads.get("run_events.json", {})

    case_id = _case_id(run_path, trace, agent_result, evaluation)
    run_id = _run_id(run_path, trace, agent_result, evaluation)
    source_refs = _source_refs(artifact_records)
    source_ref_artifacts = [ref["artifact"] for ref in source_refs]
    artifact_summary = _artifact_summary(artifact_records)

    packet: dict[str, Any] = {
        "schema_version": CONVERSATION_MEMORY_PACKET_SCHEMA_VERSION,
        "created_at": created_at or _utc_now_iso(),
        "case": {
            "case_id": case_id,
            "run_id": run_id,
            "archive_relpath": f"{case_id}/{run_id}" if case_id and run_id else run_path.name,
            "decision_situation": _decision_situation(trace, extraction),
            "source_refs": _present_source_refs(
                source_ref_artifacts,
                ("reasoning_trace.json", "extraction.json"),
            ),
        },
        "privacy": _privacy_block(
            privacy_mode=privacy_mode,
            include_raw_conversation=bool(conversation_text),
        ),
        "self_description": _self_description(),
        "upflow": {
            "evidence_label": "synthesis",
            "source_refs": _present_source_refs(
                source_ref_artifacts,
                ("conversation.txt", "extraction.json", "result.json", "reasoning_trace.json"),
            ),
            "stages": list(UPFLOW_STAGES),
        },
        "interpretation_legend": list(INTERPRETATION_LEGEND),
        "reading_protocol": list(READING_PROTOCOL),
        "update_policy": _update_policy(),
        "source_refs": source_refs,
        "artifact_status": artifact_summary,
        "source_conversation": _source_conversation(
            artifact_status=artifact_status,
            conversation_text=conversation_text,
            include_raw_conversation=include_raw_conversation,
            privacy_mode=privacy_mode,
        ),
        "conversation_interpretation": _conversation_interpretation(
            trace=trace,
            extraction=extraction,
            result=result,
            source_ref_artifacts=source_ref_artifacts,
        ),
        "decision_summary": _decision_summary(
            memo_text=memo_text,
            revised_text=revised_text,
            result=result,
            memo_note=memo_note,
            source_ref_artifacts=source_ref_artifacts,
        ),
        "advice_delta": _advice_delta(
            agent_result=agent_result,
            result=result,
            source_ref_artifacts=source_ref_artifacts,
        ),
        "lenses": _lenses(trace, result),
        "model_signals": _model_signals(graph_survival),
        "suppressed_or_unadjudicated": _suppressed_or_unadjudicated(
            trace=trace,
            graph_survival=graph_survival,
        ),
        "future_lenses": _future_lenses(
            trace=trace,
            graph_survival=graph_survival,
            result=result,
        ),
        "open_questions": _open_questions(
            agent_result=agent_result,
            result=result,
            source_ref_artifacts=source_ref_artifacts,
        ),
        "run_health": _run_health(
            agent_result=agent_result,
            evaluation=evaluation,
            trace=trace,
            result=result,
        ),
        "run_events": _run_events_summary(run_events),
        "non_claims": list(NON_CLAIMS),
        "agent_use": _agent_use(),
    }
    return packet


def build_conversation_memory_bundle(
    *,
    run_dir: Path | str,
    output_dir: Path | str,
    privacy_mode: str = "user_private",
    include_raw_conversation: bool = False,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Write packet JSON and Markdown into ``output_dir`` without mutating the run."""

    run_path = _validated_run_dir(run_dir)
    output_path = validate_output_dir(output_dir=output_dir, run_dir=run_path)
    packet = build_conversation_memory_packet(
        run_dir=run_path,
        privacy_mode=privacy_mode,
        include_raw_conversation=include_raw_conversation,
        created_at=created_at,
    )

    from .conversation_memory_renderer import render_conversation_memory_markdown

    output_path.mkdir(parents=True, exist_ok=True)
    packet_path = output_path / CONVERSATION_MEMORY_PACKET_FILENAME
    markdown_path = output_path / CONVERSATION_MEMORY_MARKDOWN_FILENAME
    packet_path.write_text(render_conversation_memory_packet_json(packet, pretty=True), encoding="utf-8")
    markdown_path.write_text(render_conversation_memory_markdown(packet), encoding="utf-8")

    return {
        "schema_version": CONVERSATION_MEMORY_BUNDLE_WRITE_SCHEMA_VERSION,
        "status": "generated",
        "case_id": packet["case"]["case_id"],
        "run_id": packet["case"]["run_id"],
        "privacy_mode": packet["privacy"]["mode"],
        "input_archive_mutated": False,
        "model_calls": 0,
        "generated_artifacts": {
            "packet": CONVERSATION_MEMORY_PACKET_FILENAME,
            "markdown": CONVERSATION_MEMORY_MARKDOWN_FILENAME,
        },
        "output_dir": str(output_path),
    }


def render_conversation_memory_packet_json(
    packet: Mapping[str, Any],
    *,
    pretty: bool = False,
) -> str:
    if pretty:
        return json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return json.dumps(packet, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"


def render_bundle_write_result_json(
    result: Mapping[str, Any],
    *,
    pretty: bool = False,
) -> str:
    if pretty:
        return json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return json.dumps(result, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"


def validate_output_dir(*, output_dir: Path | str, run_dir: Path | str) -> Path:
    output = Path(output_dir).expanduser().resolve(strict=False)
    run_path = Path(run_dir).expanduser().resolve(strict=False)
    if output == run_path or run_path in output.parents:
        raise ConversationMemoryInputError("output directory must be outside run directory")
    return output


def _validated_run_dir(run_dir: Path | str) -> Path:
    run_path = Path(run_dir).expanduser()
    if not run_path.exists():
        raise ConversationMemoryInputError("run directory was not found")
    if not run_path.is_dir():
        raise ConversationMemoryInputError("run directory is not a directory")
    return run_path


def _validated_privacy_mode(privacy_mode: str) -> str:
    mode = str(privacy_mode or "").strip()
    if mode not in PRIVACY_MODES:
        allowed = ", ".join(sorted(PRIVACY_MODES))
        raise ConversationMemoryInputError(f"unsupported privacy mode; expected one of: {allowed}")
    return mode


def _artifact_record(run_path: Path, artifact_name: str) -> dict[str, Any]:
    path = run_path / artifact_name
    base = {
        "artifact": artifact_name,
        "role": ARTIFACT_ROLES.get(artifact_name, "archived_artifact"),
        "relative_path": artifact_name,
        "privacy_class": "private_or_debug" if artifact_name in PRIVATE_ARTIFACTS else "run_artifact",
        "byte_count": None,
        "sha256": None,
        "raw_content_read": False,
    }
    if not path.exists():
        return {**base, "status": "missing"}
    if not path.is_file():
        return {**base, "status": "unknown"}
    stat = path.stat()
    return {
        **base,
        "status": "present",
        "byte_count": stat.st_size,
        "sha256": _sha256_uri(path),
    }


def _artifact_summary(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_artifact = {
        _text(record.get("artifact")): _text(record.get("status")) or "unknown"
        for record in records
        if _text(record.get("artifact"))
    }
    present = sum(1 for status in by_artifact.values() if status == "present")
    missing = sum(1 for status in by_artifact.values() if status == "missing")
    return {
        "evidence_label": "source",
        "present_count": present,
        "missing_count": missing,
        "by_artifact": by_artifact,
        "required_structured_artifacts": list(REQUIRED_STRUCTURED_ARTIFACTS),
    }


def _source_refs(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    for record in records:
        if record.get("status") != "present":
            continue
        refs.append(
            {
                "artifact": _text(record.get("artifact")),
                "role": _text(record.get("role")),
                "relative_path": _text(record.get("relative_path")),
                "privacy_class": _text(record.get("privacy_class")),
                "byte_count": record.get("byte_count"),
                "sha256": _text(record.get("sha256")),
            }
        )
    return refs


def _read_json_artifact(path: Path) -> tuple[str, Mapping[str, Any] | None]:
    if not path.exists():
        return "missing", None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "malformed", None
    except OSError:
        return "unreadable", None
    if not isinstance(value, Mapping):
        return "malformed", None
    return "present", value


def _read_text(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def _case_id(
    run_path: Path,
    trace: Mapping[str, Any],
    agent_result: Mapping[str, Any],
    evaluation: Mapping[str, Any],
) -> str:
    return (
        _text(agent_result.get("case_id"))
        or _text(evaluation.get("case_id"))
        or _text(_mapping(trace.get("case")).get("case_id"))
        or run_path.parent.name
    )


def _run_id(
    run_path: Path,
    trace: Mapping[str, Any],
    agent_result: Mapping[str, Any],
    evaluation: Mapping[str, Any],
) -> str:
    return (
        _text(agent_result.get("run_id"))
        or _text(evaluation.get("run_id"))
        or _text(_mapping(trace.get("case")).get("run_id"))
        or run_path.name
    )


def _decision_situation(trace: Mapping[str, Any], extraction: Mapping[str, Any]) -> str:
    trace_value = _text(_mapping(trace.get("case")).get("decision_situation"))
    if trace_value:
        return trace_value
    nested = _mapping(extraction.get("extraction"))
    return _text(nested.get("decision_situation")) or _text(extraction.get("decision_situation"))


def _privacy_block(*, privacy_mode: str, include_raw_conversation: bool) -> dict[str, Any]:
    return {
        "mode": privacy_mode,
        "raw_conversation_included": include_raw_conversation,
        "private_reasoning_included": False,
        "operator_logs_included": False,
        "provider_raw_text_included": False,
        "local_absolute_paths_included": False,
        "sharing_boundary": _sharing_boundary(privacy_mode),
    }


def _sharing_boundary(privacy_mode: str) -> str:
    if privacy_mode == "public_safe":
        return "Designed to omit raw conversation and private/debug artifacts."
    if privacy_mode == "operator_debug":
        return "Local maintainer mode; still excludes private artifact bodies in v0."
    return "Local user-owned export; raw conversation appears only with explicit flag."


def _self_description() -> dict[str, Any]:
    return {
        "what_this_file_is": (
            "A compiled, self-explaining memory view over one completed Lolla run."
        ),
        "what_this_file_is_not": [
            "It is not the runtime source of truth.",
            "It is not proof that the advice or revised answer is correct.",
            "It is not an action authorization.",
            "It is not a replacement for reasoning_trace.json, agent_result.json, or evaluation.json.",
            "It is not evidence that suppressed lenses were noise.",
        ],
        "safe_to_reuse_for": [
            "Orienting a future agent or coder to the completed run.",
            "Finding the source artifacts that should be inspected next.",
            "Continuing analysis with explicit source, synthesis, inference, missing, and unknown labels.",
        ],
        "not_safe_to_reuse_for": [
            "Approving action without user/human review.",
            "Claiming answer correctness.",
            "Treating a generated Markdown view as canonical archive truth.",
        ],
    }


def _update_policy() -> dict[str, Any]:
    return {
        "evidence_label": "synthesis",
        "markdown_is_generated_view": True,
        "source_of_truth": "archive artifacts plus reasoning_trace.json",
        "append_material_edits_to_log": True,
        "preserve_source_refs": True,
        "do_not_delete_open_questions_without_note": True,
        "label_later_edits_as_human_edit_or_agent_edit": True,
    }


def _source_conversation(
    *,
    artifact_status: Mapping[str, str],
    conversation_text: str,
    include_raw_conversation: bool,
    privacy_mode: str,
) -> dict[str, Any]:
    status = artifact_status.get("conversation.txt", "missing")
    if include_raw_conversation and not conversation_text and status == "present":
        evidence_label = "missing"
        note = "Raw conversation inclusion was requested, but text could not be read."
    elif conversation_text:
        evidence_label = "private"
        note = "Raw conversation text included by explicit request."
    elif status == "present":
        evidence_label = "source"
        note = "Raw conversation artifact is present but not copied into this packet."
    else:
        evidence_label = "missing"
        note = "Raw conversation artifact is missing."
    return {
        "evidence_label": evidence_label,
        "artifact": "conversation.txt",
        "artifact_status": status,
        "included": bool(conversation_text),
        "privacy_mode": privacy_mode,
        "note": note,
        **({"text": conversation_text} if conversation_text else {}),
    }


def _conversation_interpretation(
    *,
    trace: Mapping[str, Any],
    extraction: Mapping[str, Any],
    result: Mapping[str, Any],
    source_ref_artifacts: Sequence[str],
) -> dict[str, Any]:
    nested = _mapping(extraction.get("extraction"))
    capture = _mapping(trace.get("capture"))
    capture_adequacy = _mapping(capture.get("capture_adequacy"))
    decision_structure = _mapping(capture.get("decision_structure"))
    live_constraints = _text_items(nested.get("live_constraints"), keys=("text", "constraint", "summary"))
    dropped_threads = _text_items(nested.get("dropped_threads"), keys=("text", "thread", "summary"))
    assumptions = _text_items(nested.get("assumptions"), keys=("text", "assumption", "summary"))
    original_framing = _text(nested.get("original_framing"))
    synthesized_position = _text(nested.get("synthesized_position"))
    result_extraction = _mapping(result.get("extraction"))
    if not original_framing:
        original_framing = _text(result_extraction.get("original_framing"))
    if not synthesized_position:
        synthesized_position = _text(result_extraction.get("synthesized_position"))

    return {
        "evidence_label": "synthesis",
        "source_refs": _present_source_refs(
            source_ref_artifacts,
            ("extraction.json", "reasoning_trace.json", "result.json"),
        ),
        "decision_situation": _decision_situation(trace, extraction),
        "capture_status": _text(capture_adequacy.get("status")) or _text(capture.get("capture_health")) or "unknown",
        "capture_strategy": _text(capture_adequacy.get("capture_strategy")) or "unknown",
        "decision_structure_counts": {
            "live_constraint_count": _safe_int(decision_structure.get("live_constraint_count") or len(live_constraints)),
            "reasoning_passage_count": _safe_int(decision_structure.get("reasoning_passage_count")),
            "dropped_thread_count": _safe_int(decision_structure.get("dropped_thread_count") or len(dropped_threads)),
        },
        "original_framing": original_framing,
        "synthesized_position": synthesized_position,
        "known_constraints": live_constraints[:12],
        "dropped_threads": dropped_threads[:12],
        "assumptions": assumptions[:12],
    }


def _decision_summary(
    *,
    memo_text: str,
    revised_text: str,
    result: Mapping[str, Any],
    memo_note: Mapping[str, Any],
    source_ref_artifacts: Sequence[str],
) -> dict[str, Any]:
    title = _text(result.get("memo_substantive_title")) or _text(memo_note.get("memo_substantive_title"))
    return {
        "evidence_label": "summary",
        "source_refs": _present_source_refs(
            source_ref_artifacts,
            ("memo.md", "revised.txt", "result.json", "memo_note.json"),
        ),
        "title": title,
        "orientation": _first_text(
            result,
            memo_note,
            ("memo_orientation_note", "memo_orientation_narrative"),
        ),
        "memo_markdown": memo_text,
        "revised_answer": revised_text or _text(result.get("revised_answer")),
        "what_still_holds": _first_text(result, memo_note, ("memo_what_still_holds",)),
        "pressure_check": _first_text(result, memo_note, ("memo_pressure_check",)),
    }


def _advice_delta(
    *,
    agent_result: Mapping[str, Any],
    result: Mapping[str, Any],
    source_ref_artifacts: Sequence[str],
) -> dict[str, Any]:
    changed = _strings(agent_result.get("changed_advice_summary"))
    if not changed:
        changed = _text_items(result.get("memo_what_changed"))
    take_backs = _strings(agent_result.get("take_backs"))
    if not take_backs:
        take_backs = _text_items(result.get("memo_take_back_or_set_aside"))
    return {
        "evidence_label": "summary",
        "source_refs": _present_source_refs(
            source_ref_artifacts,
            ("agent_result.json", "result.json"),
        ),
        "position_changed": bool(agent_result.get("position_changed")) if "position_changed" in agent_result else bool(changed or take_backs),
        "changed_advice_summary": changed[:8],
        "take_backs": take_backs[:8],
        "main_counter_pressure": _text(agent_result.get("main_counter_pressure")),
        "caller_action": _text(agent_result.get("caller_action")),
    }


def _lenses(trace: Mapping[str, Any], result: Mapping[str, Any]) -> dict[str, Any]:
    raw_lenses = [_mapping(item) for item in _list(trace.get("reasoning_lenses"))]
    if not raw_lenses:
        raw_lenses = _fallback_lenses(result)
    selected = [item for item in raw_lenses if item.get("selected")]
    surfaced = [item for item in raw_lenses if item.get("surfaced")]
    return {
        "evidence_label": "selection_trace",
        "source_refs": ["reasoning_trace.json", "result.json"],
        "total_count": len(raw_lenses),
        "selected_count": len(selected),
        "surfaced_count": len(surfaced),
        "items": [
            _compact_lens(item)
            for item in raw_lenses[:40]
        ],
    }


def _fallback_lenses(result: Mapping[str, Any]) -> list[dict[str, Any]]:
    companion = _mapping(result.get("companion_cheat_sheet"))
    items: list[dict[str, Any]] = []
    for key in ("model_id", "selected_model_id", "companion_model_id"):
        value = _text(companion.get(key))
        if value:
            items.append(
                {
                    "model_id": value,
                    "lane": "lane2",
                    "role": "companion_anchor",
                    "selected": True,
                    "surfaced": True,
                    "disposition": "fallback_from_result",
                    "source_ref": "result.json#/companion_cheat_sheet",
                }
            )
    return items


def _compact_lens(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "model_id": _text(item.get("model_id")) or _text(item.get("lens_id")),
        "lane": _text(item.get("lane")),
        "role": _text(item.get("role")),
        "selected": bool(item.get("selected")),
        "surfaced": bool(item.get("surfaced")),
        "disposition": _text(item.get("disposition")) or "unknown",
        "source_ref": _text(item.get("source_ref")),
    }


def _model_signals(graph_survival: Mapping[str, Any]) -> dict[str, Any]:
    summary = _mapping(graph_survival.get("summary"))
    rows = [_mapping(item) for item in _list(graph_survival.get("candidate_survival"))]
    return {
        "evidence_label": "selection_trace",
        "source_refs": ["graph_survival_report.json"],
        "status": _text(graph_survival.get("status")) or ("missing" if not graph_survival else "unknown"),
        "noise_policy": _mapping(graph_survival.get("noise_policy")),
        "summary": {
            "lane_candidate_count": _safe_int(summary.get("lane_candidate_count")),
            "embedding_hit_count": _safe_int(summary.get("embedding_hit_count")),
            "selected_card_count": _safe_int(summary.get("selected_card_count")),
            "suppressed_signal_count": _safe_int(summary.get("suppressed_signal_count")),
        },
        "candidate_survival": [
            {
                "model_id": _text(row.get("model_id")),
                "survival_state": _text(row.get("survival_state")),
                "sources": _strings(row.get("sources")),
                "visible_effects": _strings(row.get("visible_effects")),
                "private_guardrails": _strings(row.get("private_guardrails")),
            }
            for row in rows[:40]
        ],
    }


def _suppressed_or_unadjudicated(
    *,
    trace: Mapping[str, Any],
    graph_survival: Mapping[str, Any],
) -> dict[str, Any]:
    suppressed = [_mapping(item) for item in _list(graph_survival.get("suppressed_signals"))]
    budget_suppressed = [_mapping(item) for item in _list(trace.get("budget_suppressed_lenses"))]
    rows: list[dict[str, Any]] = []
    for item in suppressed[:40]:
        rows.append(
            {
                "model_id": _text(item.get("model_id")),
                "reason": _text(item.get("reason")),
                "source": _text(item.get("source")),
                "research_status": _text(item.get("research_status")) or "unknown",
                "status": "suppressed_or_unadjudicated",
            }
        )
    for item in budget_suppressed[:20]:
        rows.append(
            {
                "model_id": _text(item.get("model_id")),
                "reason": _text(item.get("reason")) or "budget_suppressed",
                "source": _text(item.get("source")) or "reasoning_trace",
                "research_status": "unknown_not_noise",
                "status": "budget_suppressed",
            }
        )
    return {
        "evidence_label": "selection_trace",
        "source_refs": ["graph_survival_report.json", "reasoning_trace.json"],
        "unknown_noise_status": True,
        "items": _dedupe_by_model_reason(rows),
    }


def _future_lenses(
    *,
    trace: Mapping[str, Any],
    graph_survival: Mapping[str, Any],
    result: Mapping[str, Any],
) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    suppressed = _mapping(
        _suppressed_or_unadjudicated(trace=trace, graph_survival=graph_survival)
    )
    for item in _list(suppressed.get("items"))[:8]:
        row = _mapping(item)
        model_id = _text(row.get("model_id"))
        if not model_id:
            continue
        candidates.append(
            {
                "model_id": model_id,
                "why": "Preserved as suppressed or unadjudicated; not proven noise.",
                "status": _text(row.get("status")) or "unknown",
                "source_refs": ["graph_survival_report.json", "reasoning_trace.json"],
            }
        )
    for question in _open_questions(
        agent_result={},
        result=result,
        source_ref_artifacts=("result.json",),
    ).get("items", [])[:4]:
        candidates.append(
            {
                "model_id": "",
                "why": _text(_mapping(question).get("question")),
                "status": "question_suggests_future_lens",
                "source_refs": ["result.json"],
            }
        )
    return {
        "evidence_label": "inference",
        "source_refs": ["graph_survival_report.json", "reasoning_trace.json", "result.json"],
        "items": candidates[:12],
    }


def _open_questions(
    *,
    agent_result: Mapping[str, Any],
    result: Mapping[str, Any],
    source_ref_artifacts: Sequence[str],
) -> dict[str, Any]:
    questions = []
    for question in _strings(agent_result.get("human_questions")):
        questions.append(
            {
                "question": question,
                "source_refs": ["agent_result.json"],
                "evidence_label": "source",
            }
        )
    structural = _mapping(result.get("structural_coverage_card"))
    for gap in _list(structural.get("gap_questions")):
        item = _mapping(gap)
        for question in _text_items(item.get("questions")):
            questions.append(
                {
                    "question": question,
                    "source_refs": ["result.json"],
                    "evidence_label": "source",
                }
            )
        single = _text(item.get("question"))
        if single:
            questions.append(
                {
                    "question": single,
                    "source_refs": ["result.json"],
                    "evidence_label": "source",
                }
            )
    return {
        "evidence_label": "synthesis",
        "source_refs": _present_source_refs(
            source_ref_artifacts,
            ("agent_result.json", "result.json"),
        ),
        "items": _dedupe_questions(questions)[:16],
    }


def _run_health(
    *,
    agent_result: Mapping[str, Any],
    evaluation: Mapping[str, Any],
    trace: Mapping[str, Any],
    result: Mapping[str, Any],
) -> dict[str, Any]:
    run_health = _mapping(result.get("run_health")) or _mapping(_mapping(trace.get("process")).get("run_health"))
    trace_adequacy = _mapping(trace.get("trace_adequacy"))
    return {
        "evidence_label": "summary",
        "source_refs": ["agent_result.json", "evaluation.json", "reasoning_trace.json", "result.json"],
        "agent_result_status": _text(agent_result.get("status")) or "unknown",
        "caller_action": _text(agent_result.get("caller_action")) or "unknown",
        "run_health_overall": _text(agent_result.get("run_health_overall")) or _text(run_health.get("overall")) or "unknown",
        "product_output_health": _text(agent_result.get("product_output_health")) or _text(run_health.get("product_output_health")) or "unknown",
        "evaluation_overall": _text(evaluation.get("overall")) or "unknown",
        "caller_readiness": _text(evaluation.get("caller_readiness")) or "unknown",
        "trace_adequacy_status": _text(trace_adequacy.get("status")) or "unknown",
        "future_review_ready": bool(trace_adequacy.get("future_review_ready")),
    }


def _run_events_summary(run_events: Mapping[str, Any]) -> dict[str, Any]:
    events = [_mapping(item) for item in _list(run_events.get("events"))]
    return {
        "evidence_label": "summary",
        "source_refs": ["run_events.json"],
        "event_count": len(events),
        "first_event": _text(events[0].get("event_type")) if events else "",
        "last_event": _text(events[-1].get("event_type")) if events else "",
    }


def _agent_use() -> dict[str, Any]:
    return {
        "evidence_label": "synthesis",
        "source_refs": ["agent_result.json", "evaluation.json", "reasoning_trace.json"],
        "recommended_use": [
            "Use this packet to orient to a completed Lolla run.",
            "Inspect source_refs before relying on a claim.",
            "Preserve open questions and unknown statuses.",
            "Use reasoning_trace.json for custody verification.",
        ],
        "do_not_use_for": [
            "Do not approve actions from this packet alone.",
            "Do not infer answer correctness from clean artifacts.",
            "Do not treat suppressed lenses as discarded noise.",
        ],
    }


def _first_text(
    primary: Mapping[str, Any],
    secondary: Mapping[str, Any],
    keys: Sequence[str],
) -> str:
    for key in keys:
        value = _text(primary.get(key))
        if value:
            return value
        value = _text(secondary.get(key))
        if value:
            return value
    return ""


def _present_source_refs(available_artifacts: Sequence[str], wanted: Sequence[str]) -> list[str]:
    available = set(available_artifacts)
    return [artifact for artifact in wanted if artifact in available]


def _dedupe_questions(items: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in items:
        question = _text(item.get("question"))
        key = question.lower()
        if not question or key in seen:
            continue
        seen.add(key)
        rows.append(dict(item))
    return rows


def _dedupe_by_model_reason(items: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for item in items:
        model_id = _text(item.get("model_id"))
        reason = _text(item.get("reason"))
        key = (model_id, reason)
        if key in seen:
            continue
        seen.add(key)
        rows.append(dict(item))
    return rows


def _text_items(value: Any, *, keys: Sequence[str] = ("text", "question", "summary")) -> list[str]:
    if isinstance(value, str):
        return [part.strip() for part in value.splitlines() if part.strip()]
    items: list[str] = []
    for raw in _list(value):
        if isinstance(raw, str):
            text = raw.strip()
        else:
            item = _mapping(raw)
            text = ""
            for key in keys:
                text = _text(item.get(key))
                if text:
                    break
        if text and text not in items:
            items.append(text)
    return items


def _strings(value: Any) -> list[str]:
    return [_text(item) for item in _list(value) if _text(item)]


def _list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return []


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _sha256_uri(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return f"sha256:{digest}"


def _utc_now_iso() -> str:
    return _dt.datetime.now(tz=_dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
