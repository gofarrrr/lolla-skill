"""Markdown renderer for Lolla conversation-memory packets."""
from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from typing import Any


CONVERSATION_MEMORY_MARKDOWN_SCHEMA_VERSION = "lolla.conversation_memory_markdown.v0"


def render_conversation_memory_markdown(packet: Mapping[str, Any]) -> str:
    """Render a self-explaining Markdown memory file from a packet."""

    sections = [
        _frontmatter(packet),
        "# Conversation Memory",
        _cold_reader_orientation(packet),
        _claim_verification_checklist(packet),
        _what_this_file_is(packet),
        _what_this_file_is_not(packet),
        _how_to_use(packet),
        _how_produced(packet),
        _source_artifact_map(packet),
        _interpretation_legend(packet),
        _run_summary(packet),
        _privacy_and_non_claims(packet),
        _conversation_interpretation(packet),
        _decision_situation(packet),
        _what_changed(packet),
        _what_still_holds(packet),
        _what_to_revisit(packet),
        _lenses_applied(packet),
        _deterministic_selection_trace(packet),
        _selected_models(packet),
        _suppressed_or_unadjudicated(packet),
        _future_useful_lenses(packet),
        _open_questions(packet),
        _artifact_custody(packet),
        _run_health_and_readiness(packet),
        _agent_instructions(packet),
        _update_rules(packet),
        _appendix_source_excerpts(packet),
    ]
    return "\n\n".join(section for section in sections if section.strip()) + "\n"


def _frontmatter(packet: Mapping[str, Any]) -> str:
    case = _mapping(packet.get("case"))
    privacy = _mapping(packet.get("privacy"))
    title = _text(case.get("decision_situation")) or f"Lolla run {case.get('run_id') or ''}".strip()
    generated_from = [
        "conversation_memory_packet.json",
        "reasoning_trace.json",
        "agent_result.json",
        "evaluation.json",
        "memo.md",
    ]
    lines = [
        "---",
        'type: "Lolla Conversation Memory"',
        f"title: {_yaml_string(title)}",
        'description: "Compiled memory bundle for one completed Lolla run."',
        f"resource: {_yaml_string(case.get('archive_relpath'))}",
        "tags: [lolla, conversation-memory, reasoning-audit]",
        f"timestamp: {_yaml_string(packet.get('created_at'))}",
        'okf_version: "0.1-compatible"',
        f"schema_version: {_yaml_string(CONVERSATION_MEMORY_MARKDOWN_SCHEMA_VERSION)}",
        f"case_id: {_yaml_string(case.get('case_id'))}",
        f"run_id: {_yaml_string(case.get('run_id'))}",
        f"privacy_mode: {_yaml_string(privacy.get('mode'))}",
        'artifact_role: "compiled_memory_view"',
        'created_by: "lolla.conversation_memory_renderer"',
        "generated_from:",
    ]
    lines.extend(f"  - {_yaml_string(item)}" for item in generated_from)
    lines.extend(
        [
            "runtime_source_of_truth: false",
            'source_of_truth: "archive artifacts plus reasoning_trace.json"',
            'interpretation_status: "compiled_from_archived_run"',
            'update_policy: "append changes to log section or companion log.md"',
            "human_validated: false",
            "---",
        ]
    )
    return "\n".join(lines)


def _cold_reader_orientation(packet: Mapping[str, Any]) -> str:
    case = _mapping(packet.get("case"))
    interp = _mapping(packet.get("conversation_interpretation"))
    health = _mapping(packet.get("run_health"))
    artifacts = _mapping(packet.get("artifact_status"))
    privacy = _mapping(packet.get("privacy"))

    decision = (
        _text(case.get("decision_situation"))
        or _text(interp.get("decision_situation"))
        or "No decision situation was supplied."
    )

    missing_count = _text(artifacts.get("missing_count")) or "0"
    raw_included = str(bool(privacy.get("raw_conversation_included"))).lower()
    future_ready = str(bool(health.get("future_review_ready"))).lower()

    body = "\n".join(
        [
            "**Orientation, not conclusion.**",
            "",
            (
                "This is a generated memory view over one completed reasoning-audit "
                "run. It contains source material, generated run outputs, telemetry, "
                "custody, missingness, and non-claims."
            ),
            "",
            "**System Synthesis To Verify**",
            "",
            f"- Decision situation: {decision}",
            (
                "- Generated synthesis appears later in `Conversation Interpretation`, "
                "`What Changed`, `Memo`, and `Revised Answer`."
            ),
            "",
            (
                "Treat those synthesis sections as hypotheses to verify, not ground "
                "truth. Do not treat this orientation as the answer."
            ),
            "",
            "**Read Before Relying**",
            "",
            "1. Inspect the full transcript when it is included.",
            "2. Compare the memo and revised answer against the transcript.",
            "3. Use artifact custody and source refs to check where claims came from.",
            "4. Read selected and suppressed lenses as system behavior, not proof.",
            "5. Check run readiness and missing artifacts before relying on the file.",
            "",
            "**Reliance Warnings**",
            "",
            f"- Raw conversation included: `{raw_included}`",
            f"- Missing artifacts: `{missing_count}`",
            f"- Evaluation overall: `{_text(health.get('evaluation_overall')) or 'unknown'}`",
            f"- Caller readiness: `{_text(health.get('caller_readiness')) or 'unknown'}`",
            f"- Trace adequacy: `{_text(health.get('trace_adequacy_status')) or 'unknown'}`",
            f"- Future review ready: `{future_ready}`",
            "",
            (
                "If structured open questions are empty, still inspect the transcript "
                "for practical unresolved questions. Empty structured rows do not mean "
                "the decision has no remaining uncertainty."
            ),
            "",
            "**Key Checks Before Trusting Any Interpretation**",
            "",
            "- Does the transcript support the generated synthesis?",
            "- Does the memo or revised answer sharpen, change, or overstate the transcript?",
            "- Do readiness warnings or missing artifacts limit reliance?",
            "- Are practical open questions still visible even without structured rows?",
            "- Could current business facts have changed since the run?",
        ]
    )
    return _section(
        "Cold Reader Orientation",
        evidence_label="synthesis_to_verify",
        source_refs=[
            "conversation_memory_packet.json",
            "extraction.json",
            "agent_result.json",
            "evaluation.json",
        ],
        body=body,
    )


def _claim_verification_checklist(packet: Mapping[str, Any]) -> str:
    case = _mapping(packet.get("case"))
    interp = _mapping(packet.get("conversation_interpretation"))
    delta = _mapping(packet.get("advice_delta"))
    summary = _mapping(packet.get("decision_summary"))
    questions = _mapping(packet.get("open_questions"))
    health = _mapping(packet.get("run_health"))
    available_anchors = _available_locator_anchors(packet)

    rows: list[list[str]] = []

    decision = _text(case.get("decision_situation")) or _text(
        interp.get("decision_situation")
    )
    if decision:
        rows.append(
            [
                f"Decision situation: {decision}",
                "conversation.txt, extraction.json, reasoning_trace.json",
                _source_locator(
                    available_anchors,
                    ("Transcript", "cm-source-full-transcript"),
                    ("Conversation Interpretation", "cm-section-conversation-interpretation"),
                    ("Decision Situation", "cm-section-decision-situation"),
                ),
                "Confirm the transcript supports this framing and that current facts have not changed.",
            ]
        )

    synthesized = _text(interp.get("synthesized_position"))
    if synthesized:
        rows.append(
            [
                f"Generated synthesized position: {synthesized}",
                "extraction.json, result.json, Conversation Interpretation",
                _source_locator(
                    available_anchors,
                    ("Conversation Interpretation", "cm-section-conversation-interpretation"),
                    ("Transcript", "cm-source-full-transcript"),
                    ("Memo", "cm-source-memo"),
                    ("Revised Answer", "cm-source-revised-answer"),
                ),
                "Compare against the full transcript, memo, and revised answer before relying.",
            ]
        )

    changed = _strings(delta.get("changed_advice_summary"))
    if changed:
        rows.append(
            [
                f"Changed advice summary: {changed[0]}",
                "agent_result.json, result.json, What Changed",
                _source_locator(
                    available_anchors,
                    ("What Changed", "cm-section-what-changed"),
                    ("Transcript", "cm-source-full-transcript"),
                    ("Revised Answer", "cm-source-revised-answer"),
                ),
                "Check whether this is a generated revision, not user acceptance or proof.",
            ]
        )

    counter = _text(delta.get("main_counter_pressure"))
    if counter:
        rows.append(
            [
                f"Main counter-pressure: {counter}",
                "agent_result.json, What Changed",
                _source_locator(
                    available_anchors,
                    ("What Changed", "cm-section-what-changed"),
                    ("Transcript", "cm-source-full-transcript"),
                ),
                "Inspect the transcript for the pressure source and any omitted counter-pressure.",
            ]
        )

    revised = _text(summary.get("revised_answer"))
    if revised:
        rows.append(
            [
                f"Revised answer exists: {_short(revised, 140)}",
                "revised.txt, result.json, Appendix: Revised Answer",
                _source_locator(
                    available_anchors,
                    ("Revised Answer", "cm-source-revised-answer"),
                    ("Memo", "cm-source-memo"),
                    ("Transcript", "cm-source-full-transcript"),
                ),
                "Treat as generated synthesis; verify against source conversation and current context.",
            ]
        )

    open_items = _mappings(questions.get("items"))
    if open_items:
        rows.append(
            [
                f"Open question: {_text(open_items[0].get('question'))}",
                "agent_result.json, result.json, Open Questions",
                _source_locator(
                    available_anchors,
                    ("Open Questions", "cm-section-open-questions"),
                    ("What To Revisit", "cm-section-what-to-revisit"),
                    ("Transcript", "cm-source-full-transcript"),
                ),
                "Resolve before action; do not treat the exported answer as complete.",
            ]
        )
    else:
        rows.append(
            [
                "No structured open-question rows were supplied.",
                "agent_result.json, result.json, Open Questions",
                _source_locator(
                    available_anchors,
                    ("Open Questions", "cm-section-open-questions"),
                    ("What To Revisit", "cm-section-what-to-revisit"),
                    ("Transcript", "cm-source-full-transcript"),
                ),
                "Still inspect the transcript for practical uncertainty; empty rows are not closure.",
            ]
        )

    rows.append(
        [
            (
                "Run readiness: "
                f"evaluation={_text(health.get('evaluation_overall')) or 'unknown'}, "
                f"trace={_text(health.get('trace_adequacy_status')) or 'unknown'}, "
                f"future_review_ready={str(bool(health.get('future_review_ready'))).lower()}"
            ),
            "evaluation.json, reasoning_trace.json, Run Health And Readiness",
            _source_locator(
                available_anchors,
                ("Run Health And Readiness", "cm-section-run-health-and-readiness"),
                ("Artifact Custody", "cm-section-artifact-custody"),
            ),
            "Use warnings and missing artifacts to limit reliance; do not infer advice correctness.",
        ]
    )

    body = "\n".join(
        [
            (
                "Use this as a checking index, not as a conclusion. It does not "
                "prove any claim, certify advice, or replace source inspection."
            ),
            "",
            _table(
                [
                    "Claim / item to verify",
                    "Best evidence in this file",
                    "Source locator",
                    "Still verify before relying",
                ],
                rows[:8],
            ),
        ]
    )
    return _section(
        "Claim Verification Checklist",
        evidence_label="synthesis_to_verify",
        source_refs=[
            "conversation_memory_packet.json",
            "conversation.txt",
            "extraction.json",
            "agent_result.json",
            "evaluation.json",
            "reasoning_trace.json",
            "memo.md",
            "revised.txt",
        ],
        body=body,
    )


def _what_this_file_is(packet: Mapping[str, Any]) -> str:
    self_description = _mapping(packet.get("self_description"))
    body = _text(self_description.get("what_this_file_is"))
    return _section(
        "What This File Is",
        evidence_label="synthesis",
        source_refs=["conversation_memory_packet.json"],
        body=body,
    )


def _what_this_file_is_not(packet: Mapping[str, Any]) -> str:
    self_description = _mapping(packet.get("self_description"))
    bullets = _strings(self_description.get("what_this_file_is_not"))
    return _section(
        "What This File Is Not",
        evidence_label="synthesis",
        source_refs=["conversation_memory_packet.json"],
        body=_bullets(bullets),
    )


def _how_to_use(packet: Mapping[str, Any]) -> str:
    body = _numbered(_strings(packet.get("reading_protocol")))
    return _section(
        "How To Use This File",
        evidence_label="synthesis",
        source_refs=["conversation_memory_packet.json"],
        body=body,
    )


def _how_produced(packet: Mapping[str, Any]) -> str:
    upflow = _mapping(packet.get("upflow"))
    rows = [
        [_text(item.get("stage")), _text(item.get("role")), _text(item.get("future_reader_note"))]
        for item in _mappings(upflow.get("stages"))
    ]
    return _section(
        "How This File Was Produced",
        evidence_label=_text(upflow.get("evidence_label")) or "synthesis",
        source_refs=_strings(upflow.get("source_refs")),
        body=_table(["Stage", "Role", "Future reader should think"], rows),
    )


def _source_artifact_map(packet: Mapping[str, Any]) -> str:
    rows = []
    for ref in _mappings(packet.get("source_refs")):
        rows.append(
            [
                f"`{_text(ref.get('artifact'))}`",
                _text(ref.get("role")),
                _text(ref.get("privacy_class")),
                _text(ref.get("byte_count")),
                f"`{_short(_text(ref.get('sha256')), 24)}`",
            ]
        )
    return _section(
        "Source Artifact Map",
        evidence_label="source",
        source_refs=["reasoning_trace.json", "archive directory"],
        body=_table(["Artifact", "Role", "Privacy", "Bytes", "SHA-256"], rows),
    )


def _interpretation_legend(packet: Mapping[str, Any]) -> str:
    rows = [
        [_text(item.get("label")), _text(item.get("meaning"))]
        for item in _mappings(packet.get("interpretation_legend"))
    ]
    return _section(
        "Interpretation Legend",
        evidence_label="synthesis",
        source_refs=["conversation_memory_packet.json"],
        body=_table(["Label", "Meaning"], rows),
    )


def _run_summary(packet: Mapping[str, Any]) -> str:
    case = _mapping(packet.get("case"))
    artifacts = _mapping(packet.get("artifact_status"))
    body = "\n".join(
        [
            f"- Case ID: `{_text(case.get('case_id')) or 'unknown'}`",
            f"- Run ID: `{_text(case.get('run_id')) or 'unknown'}`",
            f"- Archive ref: `{_text(case.get('archive_relpath')) or 'unknown'}`",
            f"- Created at: `{_text(packet.get('created_at')) or 'unknown'}`",
            f"- Present artifacts: {_text(artifacts.get('present_count')) or '0'}",
            f"- Missing artifacts: {_text(artifacts.get('missing_count')) or '0'}",
        ]
    )
    return _section(
        "Run Summary",
        evidence_label="summary",
        source_refs=_strings(case.get("source_refs")),
        body=body,
    )


def _privacy_and_non_claims(packet: Mapping[str, Any]) -> str:
    privacy = _mapping(packet.get("privacy"))
    body = "\n".join(
        [
            f"- Privacy mode: `{_text(privacy.get('mode')) or 'unknown'}`",
            f"- Raw conversation included: `{str(bool(privacy.get('raw_conversation_included'))).lower()}`",
            f"- Private reasoning included: `{str(bool(privacy.get('private_reasoning_included'))).lower()}`",
            f"- Provider raw text included: `{str(bool(privacy.get('provider_raw_text_included'))).lower()}`",
            f"- Sharing boundary: {_text(privacy.get('sharing_boundary'))}",
            "",
            "Non-claims:",
            _bullets(_strings(packet.get("non_claims"))),
        ]
    )
    return _section(
        "Privacy And Non-Claims",
        evidence_label="synthesis",
        source_refs=["conversation_memory_packet.json"],
        body=body,
    )


def _conversation_interpretation(packet: Mapping[str, Any]) -> str:
    interp = _mapping(packet.get("conversation_interpretation"))
    lines = [
        f"- Capture status: `{_text(interp.get('capture_status')) or 'unknown'}`",
        f"- Capture strategy: `{_text(interp.get('capture_strategy')) or 'unknown'}`",
    ]
    counts = _mapping(interp.get("decision_structure_counts"))
    if counts:
        lines.extend(
            [
                f"- Live constraints captured: {_text(counts.get('live_constraint_count')) or '0'}",
                f"- Reasoning passages captured: {_text(counts.get('reasoning_passage_count')) or '0'}",
                f"- Dropped threads captured: {_text(counts.get('dropped_thread_count')) or '0'}",
            ]
        )
    original = _text(interp.get("original_framing"))
    synthesized = _text(interp.get("synthesized_position"))
    if original:
        lines.extend(["", "**Original Framing**", original])
    if synthesized:
        lines.extend(["", "**Synthesized Position**", synthesized])
    constraints = _strings(interp.get("known_constraints"))
    if constraints:
        lines.extend(["", "**Known Constraints**", _bullets(constraints)])
    dropped = _strings(interp.get("dropped_threads"))
    if dropped:
        lines.extend(["", "**Dropped Threads**", _bullets(dropped)])
    assumptions = _strings(interp.get("assumptions"))
    if assumptions:
        lines.extend(["", "**Assumptions**", _bullets(assumptions)])
    return _section(
        "Conversation Interpretation",
        evidence_label=_text(interp.get("evidence_label")) or "synthesis",
        source_refs=_strings(interp.get("source_refs")),
        body="\n".join(lines),
    )


def _decision_situation(packet: Mapping[str, Any]) -> str:
    case = _mapping(packet.get("case"))
    interp = _mapping(packet.get("conversation_interpretation"))
    body = _text(case.get("decision_situation")) or _text(interp.get("decision_situation")) or "Unknown."
    return _section(
        "Decision Situation",
        evidence_label="summary",
        source_refs=_strings(case.get("source_refs")),
        body=body,
    )


def _what_changed(packet: Mapping[str, Any]) -> str:
    delta = _mapping(packet.get("advice_delta"))
    lines = [
        f"- Position changed: `{str(bool(delta.get('position_changed'))).lower()}`",
        f"- Caller action: `{_text(delta.get('caller_action')) or 'unknown'}`",
    ]
    counter = _text(delta.get("main_counter_pressure"))
    if counter:
        lines.extend(["", "**Main Counter-Pressure**", counter])
    changed = _strings(delta.get("changed_advice_summary"))
    if changed:
        lines.extend(["", "**Changed Advice Summary**", _bullets(changed)])
    take_backs = _strings(delta.get("take_backs"))
    if take_backs:
        lines.extend(["", "**Take Backs / Set Aside**", _bullets(take_backs)])
    if not changed and not take_backs:
        lines.append("\nNo structured advice delta was supplied.")
    return _section(
        "What Changed",
        evidence_label=_text(delta.get("evidence_label")) or "summary",
        source_refs=_strings(delta.get("source_refs")),
        body="\n".join(lines),
    )


def _what_still_holds(packet: Mapping[str, Any]) -> str:
    summary = _mapping(packet.get("decision_summary"))
    body = _text(summary.get("what_still_holds")) or "No structured `what still holds` field was supplied."
    return _section(
        "What Still Holds",
        evidence_label=_text(summary.get("evidence_label")) or "summary",
        source_refs=_strings(summary.get("source_refs")),
        body=body,
    )


def _what_to_revisit(packet: Mapping[str, Any]) -> str:
    questions = _mappings(_mapping(packet.get("open_questions")).get("items"))
    if questions:
        body = _bullets(_text(item.get("question")) for item in questions)
    else:
        body = "No structured open questions were supplied."
    return _section(
        "What To Revisit",
        evidence_label="synthesis",
        source_refs=_strings(_mapping(packet.get("open_questions")).get("source_refs")),
        body=body,
    )


def _lenses_applied(packet: Mapping[str, Any]) -> str:
    lenses = _mapping(packet.get("lenses"))
    body = "\n".join(
        [
            f"- Total lenses: {_text(lenses.get('total_count')) or '0'}",
            f"- Selected lenses: {_text(lenses.get('selected_count')) or '0'}",
            f"- Surfaced lenses: {_text(lenses.get('surfaced_count')) or '0'}",
            "",
            _lens_table(_mappings(lenses.get("items"))[:20]),
        ]
    )
    return _section(
        "Lenses Applied",
        evidence_label=_text(lenses.get("evidence_label")) or "selection_trace",
        source_refs=_strings(lenses.get("source_refs")),
        body=body,
    )


def _deterministic_selection_trace(packet: Mapping[str, Any]) -> str:
    model_signals = _mapping(packet.get("model_signals"))
    summary = _mapping(model_signals.get("summary"))
    body = "\n".join(
        [
            f"- Graph survival status: `{_text(model_signals.get('status')) or 'unknown'}`",
            f"- Lane candidates: {_text(summary.get('lane_candidate_count')) or '0'}",
            f"- Embedding hits: {_text(summary.get('embedding_hit_count')) or '0'}",
            f"- Selected cards: {_text(summary.get('selected_card_count')) or '0'}",
            f"- Suppressed signals: {_text(summary.get('suppressed_signal_count')) or '0'}",
            "",
            "Unselected or suppressed signals are preserved as unknown, not labeled as noise.",
        ]
    )
    return _section(
        "Deterministic Selection Trace",
        evidence_label=_text(model_signals.get("evidence_label")) or "selection_trace",
        source_refs=_strings(model_signals.get("source_refs")),
        body=body,
    )


def _selected_models(packet: Mapping[str, Any]) -> str:
    model_signals = _mapping(packet.get("model_signals"))
    rows = []
    for item in _mappings(model_signals.get("candidate_survival")):
        state = _text(item.get("survival_state"))
        if "selected" not in state and not _strings(item.get("visible_effects")):
            continue
        rows.append(
            [
                _text(item.get("model_id")),
                state,
                ", ".join(_strings(item.get("sources"))),
                "; ".join(_strings(item.get("visible_effects")))[:180],
            ]
        )
    body = _table(["Model", "State", "Sources", "Visible Effect"], rows)
    return _section(
        "Selected Models",
        evidence_label="selection_trace",
        source_refs=_strings(model_signals.get("source_refs")),
        body=body,
    )


def _suppressed_or_unadjudicated(packet: Mapping[str, Any]) -> str:
    suppressed = _mapping(packet.get("suppressed_or_unadjudicated"))
    rows = [
        [
            _text(item.get("model_id")),
            _text(item.get("status")),
            _text(item.get("reason")),
            _text(item.get("research_status")),
        ]
        for item in _mappings(suppressed.get("items"))
    ]
    return _section(
        "Suppressed Or Unadjudicated Signals",
        evidence_label=_text(suppressed.get("evidence_label")) or "selection_trace",
        source_refs=_strings(suppressed.get("source_refs")),
        body=_table(["Model", "Status", "Reason", "Research Status"], rows),
    )


def _future_useful_lenses(packet: Mapping[str, Any]) -> str:
    future = _mapping(packet.get("future_lenses"))
    rows = [
        [
            _text(item.get("model_id")) or "(no model id)",
            _text(item.get("status")),
            _text(item.get("why")),
        ]
        for item in _mappings(future.get("items"))
    ]
    body = _table(["Model", "Status", "Why It May Matter Later"], rows)
    return _section(
        "Future Useful Lenses",
        evidence_label=_text(future.get("evidence_label")) or "inference",
        source_refs=_strings(future.get("source_refs")),
        body=body,
    )


def _open_questions(packet: Mapping[str, Any]) -> str:
    questions = _mapping(packet.get("open_questions"))
    rows = [
        [
            _text(item.get("question")),
            _text(item.get("evidence_label")),
            ", ".join(_strings(item.get("source_refs"))),
        ]
        for item in _mappings(questions.get("items"))
    ]
    return _section(
        "Open Questions",
        evidence_label=_text(questions.get("evidence_label")) or "synthesis",
        source_refs=_strings(questions.get("source_refs")),
        body=_table(["Question", "Evidence", "Source Refs"], rows),
    )


def _artifact_custody(packet: Mapping[str, Any]) -> str:
    artifact_status = _mapping(packet.get("artifact_status"))
    rows = [
        [f"`{artifact}`", status]
        for artifact, status in sorted(_mapping(artifact_status.get("by_artifact")).items())
    ]
    return _section(
        "Artifact Custody",
        evidence_label=_text(artifact_status.get("evidence_label")) or "source",
        source_refs=["reasoning_trace.json", "archive directory"],
        body=_table(["Artifact", "Status"], rows),
    )


def _run_health_and_readiness(packet: Mapping[str, Any]) -> str:
    health = _mapping(packet.get("run_health"))
    body = "\n".join(
        [
            f"- Agent result status: `{_text(health.get('agent_result_status')) or 'unknown'}`",
            f"- Caller action: `{_text(health.get('caller_action')) or 'unknown'}`",
            f"- Run health overall: `{_text(health.get('run_health_overall')) or 'unknown'}`",
            f"- Product output health: `{_text(health.get('product_output_health')) or 'unknown'}`",
            f"- Evaluation overall: `{_text(health.get('evaluation_overall')) or 'unknown'}`",
            f"- Caller readiness: `{_text(health.get('caller_readiness')) or 'unknown'}`",
            f"- Trace adequacy: `{_text(health.get('trace_adequacy_status')) or 'unknown'}`",
            f"- Future review ready: `{str(bool(health.get('future_review_ready'))).lower()}`",
        ]
    )
    return _section(
        "Run Health And Readiness",
        evidence_label=_text(health.get("evidence_label")) or "summary",
        source_refs=_strings(health.get("source_refs")),
        body=body,
    )


def _agent_instructions(packet: Mapping[str, Any]) -> str:
    agent_use = _mapping(packet.get("agent_use"))
    body = "\n".join(
        [
            "**Recommended Use**",
            _bullets(_strings(agent_use.get("recommended_use"))),
            "",
            "**Do Not Use For**",
            _bullets(_strings(agent_use.get("do_not_use_for"))),
        ]
    )
    return _section(
        "Agent Instructions For Future Use",
        evidence_label=_text(agent_use.get("evidence_label")) or "synthesis",
        source_refs=_strings(agent_use.get("source_refs")),
        body=body,
    )


def _update_rules(packet: Mapping[str, Any]) -> str:
    update = _mapping(packet.get("update_policy"))
    body = "\n".join(
        [
            f"- Markdown is generated view: `{str(bool(update.get('markdown_is_generated_view'))).lower()}`",
            f"- Source of truth: {_text(update.get('source_of_truth'))}",
            f"- Append material edits to log: `{str(bool(update.get('append_material_edits_to_log'))).lower()}`",
            f"- Preserve source refs: `{str(bool(update.get('preserve_source_refs'))).lower()}`",
            f"- Do not delete open questions without note: `{str(bool(update.get('do_not_delete_open_questions_without_note'))).lower()}`",
            f"- Label later edits: `{str(bool(update.get('label_later_edits_as_human_edit_or_agent_edit'))).lower()}`",
        ]
    )
    return _section(
        "Update Rules",
        evidence_label=_text(update.get("evidence_label")) or "synthesis",
        source_refs=["conversation_memory_packet.json"],
        body=body,
    )


def _appendix_source_excerpts(packet: Mapping[str, Any]) -> str:
    source = _mapping(packet.get("source_conversation"))
    summary = _mapping(packet.get("decision_summary"))
    parts = []
    conversation_text = _text(source.get("text"))
    if conversation_text:
        parts.extend(
            [
                '<a id="cm-source-full-transcript"></a>',
                "",
                "### Full 1:1 Conversation Transcript",
                "_Evidence label: private. Source refs: conversation.txt._",
                "",
                "This is the full archived `conversation.txt` transcript included by "
                "explicit private export request. Preserve it as the primary source "
                "for future-session context.",
                "",
                _fenced(conversation_text),
            ]
        )
    memo = _text(summary.get("memo_markdown"))
    if memo:
        parts.extend(
            [
                '<a id="cm-source-memo"></a>',
                "",
                "### Memo",
                "_Evidence label: source. Source refs: memo.md._",
                "",
                memo,
            ]
        )
    revised = _text(summary.get("revised_answer"))
    if revised:
        parts.extend(
            [
                '<a id="cm-source-revised-answer"></a>',
                "",
                "### Revised Answer",
                "_Evidence label: source. Source refs: revised.txt or result.json._",
                "",
                revised,
            ]
        )
    if not parts:
        parts.append("No source excerpts were included in this privacy mode.")
    return "## Appendix: Source Excerpts\n\n" + "\n\n".join(parts)


def _section(
    title: str,
    *,
    evidence_label: str,
    source_refs: Sequence[str],
    body: str,
) -> str:
    source = ", ".join(f"`{item}`" for item in source_refs if item) or "none supplied"
    header = f"## {title}\n\n_Evidence label: `{evidence_label}`. Source refs: {source}._"
    anchor = f'<a id="{_section_anchor(title)}"></a>'
    return f"{anchor}\n\n{header}\n\n{body.strip() if body.strip() else 'No data supplied.'}"


def _lens_table(items: Sequence[Mapping[str, Any]]) -> str:
    rows = [
        [
            _text(item.get("model_id")),
            _text(item.get("lane")),
            _text(item.get("role")),
            str(bool(item.get("selected"))).lower(),
            str(bool(item.get("surfaced"))).lower(),
            _text(item.get("disposition")),
        ]
        for item in items
    ]
    return _table(["Model", "Lane", "Role", "Selected", "Surfaced", "Disposition"], rows)


def _table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    if not rows:
        return "No rows supplied."
    lines = [
        "| " + " | ".join(_md_cell(header) for header in headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        padded = list(row)[: len(headers)]
        padded.extend("" for _ in range(len(headers) - len(padded)))
        lines.append("| " + " | ".join(_md_cell(cell) for cell in padded) + " |")
    return "\n".join(lines)


def _bullets(items: Sequence[Any]) -> str:
    rows = [_text(item) for item in items if _text(item)]
    if not rows:
        return "- None supplied."
    return "\n".join(f"- {row}" for row in rows)


def _numbered(items: Sequence[Any]) -> str:
    rows = [_text(item) for item in items if _text(item)]
    if not rows:
        return "1. None supplied."
    return "\n".join(f"{index}. {row}" for index, row in enumerate(rows, start=1))


def _fenced(text: str) -> str:
    return "```text\n" + text.replace("```", "` ` `") + "\n```"


def _md_cell(value: Any) -> str:
    text = _text(value)
    text = text.replace("|", "\\|")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _source_locator(available_anchors: set[str], *items: tuple[str, str]) -> str:
    links = []
    for label, anchor in items:
        if label and anchor and anchor in available_anchors:
            links.append(f"[{label}](#{anchor})")
        elif label:
            links.append(f"{label} (artifact not embedded)")
    return "; ".join(links) or "No locator supplied."


def _available_locator_anchors(packet: Mapping[str, Any]) -> set[str]:
    anchors = {
        _section_anchor(title)
        for title in (
            "Cold Reader Orientation",
            "Claim Verification Checklist",
            "What This File Is",
            "What This File Is Not",
            "How To Use This File",
            "How This File Was Produced",
            "Source Artifact Map",
            "Interpretation Legend",
            "Run Summary",
            "Privacy And Non-Claims",
            "Conversation Interpretation",
            "Decision Situation",
            "What Changed",
            "What Still Holds",
            "What To Revisit",
            "Lenses Applied",
            "Deterministic Selection Trace",
            "Selected Models",
            "Suppressed Or Unadjudicated Signals",
            "Future Useful Lenses",
            "Open Questions",
            "Artifact Custody",
            "Run Health And Readiness",
            "Agent Instructions For Future Use",
            "Update Rules",
        )
    }
    source = _mapping(packet.get("source_conversation"))
    summary = _mapping(packet.get("decision_summary"))
    if _text(source.get("text")):
        anchors.add("cm-source-full-transcript")
    if _text(summary.get("memo_markdown")):
        anchors.add("cm-source-memo")
    if _text(summary.get("revised_answer")):
        anchors.add("cm-source-revised-answer")
    return anchors


def _section_anchor(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return f"cm-section-{slug or 'section'}"


def _yaml_string(value: Any) -> str:
    return json.dumps(_text(value), ensure_ascii=False)


def _short(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)] + "..."


def _mappings(value: Any) -> list[Mapping[str, Any]]:
    return [_mapping(item) for item in _list(value) if isinstance(item, Mapping)]


def _strings(value: Any) -> list[str]:
    return [_text(item) for item in _list(value) if _text(item)]


def _list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if hasattr(value, "__iter__") and not isinstance(value, (str, bytes, Mapping)):
        return list(value)
    return []


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _text(value: Any) -> str:
    return str(value or "").strip()
