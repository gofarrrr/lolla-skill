"""Bounded local turn records for the post-A–E conversation redesign.

Probabilistic readers own local semantic compression. Deterministic code owns
shape, source/window identity, budgets, complete disposition custody, and the
fact-free graph boundary.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

from .conversation_event_harvesting import SpanSelection, TurnPairWindow
from .conversation_state_candidates import (
    EXTRACTION_STATUSES,
    SourceCatalog,
    ValidationIssue,
    parse_typed,
    schema_for_dataclass,
    schema_metrics,
)
from .conversation_state_handoff import CLAIM_MODES


TURN_RECORD_SCHEMA = "lolla.conversation_turn_record.v1"
TURN_RECORD_LEDGER_SCHEMA = "lolla.conversation_turn_record_ledger.v1"
ARCHITECTURES = ("single_reader", "three_lens_consolidation")
LOCAL_THREAD_MOVES = (
    "raised",
    "engaged",
    "qualified",
    "resolution_claim",
    "unresolved_signal",
    "superseding_signal",
)
INPUT_DISPOSITIONS = ("preserved", "merged", "set_aside_redundant", "unclear")
MAX_DIRECTIONAL_MOVES = 2
MAX_THREAD_SIGNALS = 2
MAX_LOCAL_CLAIMS = 4
MAX_ITEMS_PER_WINDOW = 8
MAX_ITEMS_PER_CONVERSATION = 56
TARGET_ITEMS_PER_CONVERSATION = 42
MAX_SYNTHESIS_INPUT_BYTES = 32_000


def _meta(
    description: str,
    *,
    enum: Optional[tuple[str, ...]] = None,
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
    allow_empty: bool = False,
) -> dict[str, Any]:
    result: dict[str, Any] = {"description": description, "allow_empty": allow_empty}
    if enum is not None:
        result["enum"] = enum
    if min_items is not None:
        result["min_items"] = min_items
    if max_items is not None:
        result["max_items"] = max_items
    return result


@dataclass(frozen=True)
class LocalDirectionalMove:
    text: str = field(metadata=_meta("One local decision direction, condition, objection, or refinement."))
    evidence: tuple[SpanSelection, ...] = field(
        metadata=_meta("One or two current-window source IDs.", min_items=1, max_items=2)
    )


@dataclass(frozen=True)
class LocalThreadSignal:
    text: str = field(metadata=_meta("Neutral local substantive question or concern."))
    local_move: str = field(metadata=_meta("Locally observable move only.", enum=LOCAL_THREAD_MOVES))
    evidence: tuple[SpanSelection, ...] = field(
        metadata=_meta("One or two current-window source IDs.", min_items=1, max_items=2)
    )


@dataclass(frozen=True)
class LocalAtomicClaim:
    text: str = field(metadata=_meta("One atomic claim that may constrain the decision."))
    claim_mode: str = field(
        metadata=_meta("Strength visible in the local source wording.", enum=tuple(sorted(CLAIM_MODES - {"mixed"})))
    )
    evidence: SpanSelection = field(metadata=_meta("The one source ID carrying this atomic claim."))


@dataclass(frozen=True)
class InputDisposition:
    input_event_id: str = field(metadata=_meta("One input event from this window."))
    disposition: str = field(metadata=_meta("Semantic consolidation disposition.", enum=INPUT_DISPOSITIONS))
    normalized_item_keys: tuple[str, ...] = field(
        metadata=_meta("Temporary normalized item keys, empty only when set aside or unclear.", min_items=0, max_items=4, allow_empty=True)
    )


@dataclass(frozen=True)
class ConversationTurnRecord:
    status: str = field(metadata=_meta("supported, unclear, or not_found.", enum=EXTRACTION_STATUSES))
    directional_moves: tuple[LocalDirectionalMove, ...] = field(
        metadata=_meta("Bounded local directional moves.", min_items=0, max_items=MAX_DIRECTIONAL_MOVES, allow_empty=True)
    )
    thread_signals: tuple[LocalThreadSignal, ...] = field(
        metadata=_meta("Bounded local thread signals.", min_items=0, max_items=MAX_THREAD_SIGNALS, allow_empty=True)
    )
    claims: tuple[LocalAtomicClaim, ...] = field(
        metadata=_meta("Bounded atomic claims with local strength.", min_items=0, max_items=MAX_LOCAL_CLAIMS, allow_empty=True)
    )
    input_dispositions: tuple[InputDisposition, ...] = field(
        metadata=_meta("Required only for three-lens consolidation.", min_items=0, max_items=24, allow_empty=True)
    )


def turn_record_schema(
    *, window: TurnPairWindow, input_event_ids: Sequence[str] = ()
) -> dict[str, Any]:
    schema = schema_for_dataclass(ConversationTurnRecord, use_references=True)
    schema["$defs"]["SpanSelection"]["properties"]["span_id"]["enum"] = list(window.span_ids)
    schema["$defs"]["InputDisposition"]["properties"]["input_event_id"]["enum"] = list(input_event_ids)
    return schema


def build_single_reader_contract(*, window: TurnPairWindow) -> dict[str, Any]:
    schema = turn_record_schema(window=window)
    system = (
        "Read one user/assistant turn pair and return one bounded local record. Identify at most two directional moves, "
        "two substantive thread signals, and four atomic claims. Classify claim strength only from local wording: "
        "stated_condition is directly stated, reported_statement is attributed to another source, possibility uses may/might/could, "
        "preference expresses a desired direction, concern expresses worry or risk, and inference is not directly asserted. "
        "The schema maxima are safety caps, not quotas. Target three to five total items: normally one direction, one thread signal, and up to three claims. "
        "Add a second direction or thread only when materially independent. Include only claims that could affect the decision; do not convert every assistant observation into a claim. "
        "Do not decide global ownership, acceptance, first introduction, final relevance, or thread disposition. "
        "Use stable source IDs only and return exactly one JSON object matching the schema. input_dispositions must be empty."
    )
    user = window.source_text + "\n\nOUTPUT SCHEMA\n" + json.dumps(schema, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return _contract("single_reader", window, system, user, schema, ())


def build_consolidator_contract(
    *, window: TurnPairWindow, input_events: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    input_ids = tuple(str(row["event_id"]) for row in input_events)
    schema = turn_record_schema(window=window, input_event_ids=input_ids)
    lines = [window.source_text, "", "LOCAL LENS PROPOSALS"]
    for row in input_events:
        lines.append(
            f"[{row['event_id']}] family={row['family']} proposal="
            + json.dumps(row.get("event_snapshot"), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        )
    system = (
        "Consolidate overlapping local lens proposals for one turn pair into one bounded record: at most two directional moves, "
        "two thread signals, and four atomic claims. This is a semantic task. Preserve minority signals when material, merge duplicates, "
        "and classify claim strength from the visible local wording. The schema maxima are safety caps, not quotas. Target three to five total normalized items and reduce overlapping proposals by at least forty percent when the inputs permit it. "
        "Normally keep one direction, one thread signal, and up to three load-bearing claims; use set_aside_redundant for commentary or duplicates that add no local decision information. Account for every input event exactly once with preserved, merged, "
        "set_aside_redundant, or unclear. Do not decide global ownership, acceptance, first introduction, final relevance, or disposition. "
        "Use only listed source and input event IDs and return exactly one JSON object matching the schema."
    )
    user = "\n".join(lines) + "\n\nOUTPUT SCHEMA\n" + json.dumps(schema, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return _contract("three_lens_consolidation", window, system, user, schema, input_ids)


def _contract(
    architecture: str,
    window: TurnPairWindow,
    system: str,
    user: str,
    schema: Mapping[str, Any],
    input_ids: Sequence[str],
) -> dict[str, Any]:
    return {
        "architecture": architecture,
        "window_id": window.window_id,
        "input_event_ids": list(input_ids),
        "system_prompt": system,
        "user_prompt": user,
        "schema": dict(schema),
        "schema_metrics": schema_metrics(schema),
        "system_prompt_sha256": hashlib.sha256(system.encode()).hexdigest(),
        "user_prompt_sha256": hashlib.sha256(user.encode()).hexdigest(),
        "provider_calls": 0,
    }


def parse_turn_record(payload: object) -> tuple[Optional[ConversationTurnRecord], list[ValidationIssue]]:
    return parse_typed(ConversationTurnRecord, payload)


def _selections(item: Any) -> tuple[str, ...]:
    evidence = item.evidence
    if isinstance(evidence, SpanSelection):
        return (evidence.span_id,)
    return tuple(ref.span_id for ref in evidence)


def build_turn_record_ledger(
    *,
    architecture: str,
    case_id: str,
    catalog: SourceCatalog,
    windows: Sequence[TurnPairWindow],
    records: Mapping[str, ConversationTurnRecord],
    input_events_by_window: Optional[Mapping[str, Sequence[Mapping[str, Any]]]] = None,
) -> dict[str, Any]:
    if architecture not in ARCHITECTURES:
        raise ValueError(f"unknown architecture: {architecture}")
    input_events_by_window = input_events_by_window or {}
    by_span = catalog.by_id()
    items: list[dict[str, Any]] = []
    record_rows: list[dict[str, Any]] = []
    input_custody: list[dict[str, Any]] = []
    for window in windows:
        record = records.get(window.window_id)
        if record is None:
            record_rows.append({
                "window_id": window.window_id,
                "status": "missing",
                "item_count": 0,
                "input_custody_invalid": architecture == "three_lens_consolidation"
                and bool(input_events_by_window.get(window.window_id)),
            })
            continue
        groups = (
            ("directional_move", record.directional_moves),
            ("thread_signal", record.thread_signals),
            ("claim", record.claims),
        )
        record_item_count = sum(len(group) for _kind, group in groups)
        record_rows.append({
            "window_id": window.window_id,
            "status": record.status,
            "item_count": record_item_count,
            "absence_is_observed": record.status == "not_found",
            "ambiguity_is_observed": record.status == "unclear",
        })
        for kind, group in groups:
            for index, item in enumerate(group, start=1):
                raw = asdict(item)
                span_ids = _selections(item)
                issues = []
                for span_id in span_ids:
                    if span_id not in by_span:
                        issues.append({"code": "source_span_not_found", "path": "/evidence"})
                    elif span_id not in window.span_ids:
                        issues.append({"code": "source_span_outside_window", "path": "/evidence"})
                item_id = f"turnitem-{window.turn_index:03d}-{kind}-{index:02d}-{hashlib.sha256(json.dumps(raw,sort_keys=True).encode()).hexdigest()[:10]}"
                snapshot = None if issues else {
                    **raw,
                    "resolved_source": [
                        {"span_id": span_id, "speaker": by_span[span_id].speaker, "turn_index": by_span[span_id].turn_index, "text": by_span[span_id].text}
                        for span_id in span_ids
                    ],
                }
                items.append({
                    "item_id": item_id,
                    "window_id": window.window_id,
                    "turn_index": window.turn_index,
                    "kind": kind,
                    "raw_proposal": raw,
                    "terminal_state": "invalid_evidence" if issues else ("ambiguous_item" if record.status == "unclear" else "preserved_for_global_synthesis"),
                    "validation_issues": issues,
                    "synthesis_eligible": not issues,
                    "event_snapshot": snapshot,
                    "graph_routing_eligible": False,
                })
        expected_inputs = {str(row["event_id"]) for row in input_events_by_window.get(window.window_id, ())}
        observed_inputs = [row.input_event_id for row in record.input_dispositions]
        for disposition in record.input_dispositions:
            input_custody.append({"window_id": window.window_id, **asdict(disposition)})
        if architecture == "three_lens_consolidation" and (set(observed_inputs) != expected_inputs or len(observed_inputs) != len(set(observed_inputs))):
            record_rows[-1]["input_custody_invalid"] = True
        else:
            record_rows[-1]["input_custody_invalid"] = False
    counts = Counter(row["terminal_state"] for row in items)
    serialized = json.dumps(items, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    compact_for_synthesis = [
        {
            "item_id": row["item_id"],
            "turn_index": row["turn_index"],
            "kind": row["kind"],
            "event_snapshot": row["event_snapshot"],
        }
        for row in items
        if row["synthesis_eligible"]
    ]
    synthesis_bytes = len(
        json.dumps(compact_for_synthesis, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    )
    return {
        "schema_version": TURN_RECORD_LEDGER_SCHEMA,
        "architecture": architecture,
        "case_id": case_id,
        "source": {"path": catalog.source_path, "sha256": catalog.source_sha256, "message_count": catalog.message_count},
        "records": record_rows,
        "items": items,
        "input_candidate_custody": input_custody,
        "metrics": {
            "window_count": len(windows),
            "observed_record_count": len(records),
            "missing_record_count": sum(row["status"] == "missing" for row in record_rows),
            "item_count": len(items),
            "invalid_item_count": counts.get("invalid_evidence", 0),
            "terminal_item_count": sum(counts.values()),
            "input_candidate_count": sum(len(rows) for rows in input_events_by_window.values()),
            "input_disposition_count": len(input_custody),
            "input_custody_invalid_window_count": sum(row["input_custody_invalid"] for row in record_rows),
            "serialized_item_bytes": len(serialized),
            "synthesis_payload_bytes": synthesis_bytes,
            "within_hard_item_budget": len(items) <= MAX_ITEMS_PER_CONVERSATION,
            "within_target_item_budget": len(items) <= TARGET_ITEMS_PER_CONVERSATION,
            "within_synthesis_byte_budget": synthesis_bytes <= MAX_SYNTHESIS_INPUT_BYTES,
            "candidate_custody_complete": len(items) == sum(counts.values()),
        },
        "non_claims": [
            "local_semantic_compression_is_probabilistic_or_human_interpretation",
            "deterministic_budget_validation_is_not_relevance_judgment",
            "turn_records_cannot_seed_graph_directly",
        ],
    }
