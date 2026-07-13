"""Typed small-window event harvesting and fresh synthesis contracts.

Models select source IDs and interpret local events. Deterministic code owns
window identity, exact text retrieval, candidate custody, and schema assembly.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional

from .conversation_state_candidates import (
    EXTRACTION_STATUSES,
    SourceCatalog,
    ValidationIssue,
    parse_typed,
    schema_for_dataclass,
    schema_metrics,
)
from .conversation_state_handoff import (
    CLAIM_MODES,
    CONSTRAINT_STATES,
    CONTRIBUTION_ROLES,
    OWNERSHIP,
    POSITION_STATES,
    THREAD_DISPOSITIONS,
)


HARVEST_LEDGER_SCHEMA = "lolla.conversation_event_harvest_ledger.v1"
WINDOW_SCHEMA = "lolla.conversation_turn_pair_window.v1"
FAMILIES = ("contributions", "thread_events", "constraint_claims")
THREAD_LOCAL_MOVES = (
    "raised",
    "engaged",
    "qualification",
    "resolution_claim",
    "unresolved_signal",
    "superseding_signal",
)


def _meta(
    description: str,
    *,
    enum: Optional[tuple[str, ...]] = None,
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
    allow_empty: bool = False,
) -> dict[str, Any]:
    value: dict[str, Any] = {"description": description, "allow_empty": allow_empty}
    if enum is not None:
        value["enum"] = enum
    if min_items is not None:
        value["min_items"] = min_items
    if max_items is not None:
        value["max_items"] = max_items
    return value


@dataclass(frozen=True)
class SpanSelection:
    span_id: str = field(
        metadata=_meta("Select one complete source ID from this window.")
    )


@dataclass(frozen=True)
class ContributionEvent:
    position_fragment: str = field(
        metadata=_meta("Neutral local position fragment this contribution affects.")
    )
    evidence: tuple[SpanSelection, ...] = field(
        metadata=_meta("One or two local source IDs.", min_items=1, max_items=2)
    )


@dataclass(frozen=True)
class ContributionHarvest:
    status: str = field(
        metadata=_meta("supported, unclear, or not_found.", enum=EXTRACTION_STATUSES)
    )
    events: tuple[ContributionEvent, ...] = field(
        metadata=_meta(
            "Local contribution events; empty is valid for not_found.",
            min_items=0,
            max_items=6,
            allow_empty=True,
        )
    )


@dataclass(frozen=True)
class ThreadEvent:
    thread_hint: str = field(
        metadata=_meta("Local neutral label for the substantive thread.")
    )
    local_move: str = field(
        metadata=_meta("Locally observable move; global trajectory is decided later.", enum=THREAD_LOCAL_MOVES)
    )
    evidence: tuple[SpanSelection, ...] = field(
        metadata=_meta("One or two local source IDs.", min_items=1, max_items=2)
    )


@dataclass(frozen=True)
class ThreadEventHarvest:
    status: str = field(
        metadata=_meta("supported, unclear, or not_found.", enum=EXTRACTION_STATUSES)
    )
    events: tuple[ThreadEvent, ...] = field(
        metadata=_meta(
            "Local thread events; empty is valid for not_found.",
            min_items=0,
            max_items=8,
            allow_empty=True,
        )
    )


@dataclass(frozen=True)
class ConstraintClaimEvent:
    claim_text: str = field(
        metadata=_meta("One atomic local claim that may constrain the decision.")
    )
    evidence: SpanSelection = field(
        metadata=_meta("The single local source ID carrying this claim.")
    )


@dataclass(frozen=True)
class ConstraintClaimHarvest:
    status: str = field(
        metadata=_meta("supported, unclear, or not_found.", enum=EXTRACTION_STATUSES)
    )
    events: tuple[ConstraintClaimEvent, ...] = field(
        metadata=_meta(
            "Atomic local claim candidates; empty is valid for not_found.",
            min_items=0,
            max_items=10,
            allow_empty=True,
        )
    )


@dataclass(frozen=True)
class PositionSynthesisCandidate:
    text: str = field(metadata=_meta("One composed current position."))
    ownership: str = field(
        metadata=_meta("Material conversational ownership.", enum=tuple(sorted(OWNERSHIP)))
    )
    state: str = field(
        metadata=_meta("Current position state.", enum=tuple(sorted(POSITION_STATES)))
    )
    contributions: tuple["SynthesizedContribution", ...] = field(
        metadata=_meta("Ordered harvested events with cross-turn contribution roles.", min_items=1, max_items=12)
    )


@dataclass(frozen=True)
class SynthesizedContribution:
    event_id: str = field(metadata=_meta("One harvested contribution event."))
    role: str = field(
        metadata=_meta("Role after full-trajectory synthesis.", enum=tuple(sorted(CONTRIBUTION_ROLES)))
    )


@dataclass(frozen=True)
class PositionSynthesis:
    status: str = field(metadata=_meta("supported, unclear, or not_found.", enum=EXTRACTION_STATUSES))
    decision_summary: Optional[str] = field(
        metadata=_meta("Current decision state, or null for not_found.", allow_empty=True)
    )
    positions: tuple[PositionSynthesisCandidate, ...] = field(
        metadata=_meta("Composed current positions.", min_items=0, max_items=4, allow_empty=True)
    )


@dataclass(frozen=True)
class ThreadSynthesisCandidate:
    text: str = field(metadata=_meta("One synthesized focal thread."))
    disposition: str = field(
        metadata=_meta("Full ordered trajectory disposition.", enum=tuple(sorted(THREAD_DISPOSITIONS)))
    )
    event_ids: tuple[str, ...] = field(
        metadata=_meta("All ordered events used for this trajectory.", min_items=1, max_items=20)
    )
    introduced_event_id: str = field(metadata=_meta("Event where the thread was introduced."))
    latest_event_id: str = field(metadata=_meta("Latest material event for the thread."))
    responses: tuple["SynthesizedThreadResponse", ...] = field(
        metadata=_meta("Cross-turn response classifications.", min_items=0, max_items=12, allow_empty=True)
    )
    superseded_by: Optional[str] = field(
        metadata=_meta("Replacement label only for superseded threads.", allow_empty=True)
    )


@dataclass(frozen=True)
class SynthesizedThreadResponse:
    event_id: str = field(metadata=_meta("One harvested thread event."))
    engagement: str = field(
        metadata=_meta(
            "How this event engaged the focal thread after full-context synthesis.",
            enum=("acknowledged", "substantive", "resolved"),
        )
    )


@dataclass(frozen=True)
class ThreadSynthesis:
    status: str = field(metadata=_meta("supported, unclear, or not_found.", enum=EXTRACTION_STATUSES))
    threads: tuple[ThreadSynthesisCandidate, ...] = field(
        metadata=_meta("Synthesized focal threads.", min_items=0, max_items=6, allow_empty=True)
    )


@dataclass(frozen=True)
class ConstraintSynthesisCandidate:
    text: str = field(metadata=_meta("One atomic load-bearing constraint."))
    state: str = field(
        metadata=_meta("Current constraint state.", enum=tuple(sorted(CONSTRAINT_STATES)))
    )
    claim_mode: str = field(
        metadata=_meta(
            "Source strength after narrow classification.",
            enum=tuple(sorted(CLAIM_MODES - {"mixed"})),
        )
    )
    claim_event_ids: tuple[str, ...] = field(
        metadata=_meta("Harvested local claims supporting this atomic constraint.", min_items=1, max_items=6)
    )


@dataclass(frozen=True)
class ConstraintSynthesis:
    status: str = field(metadata=_meta("supported, unclear, or not_found.", enum=EXTRACTION_STATUSES))
    constraints: tuple[ConstraintSynthesisCandidate, ...] = field(
        metadata=_meta("Synthesized atomic constraints.", min_items=0, max_items=20, allow_empty=True)
    )


@dataclass(frozen=True)
class TurnPairWindow:
    schema_version: str
    window_id: str
    turn_index: int
    span_ids: tuple[str, ...]
    source_text: str


def build_turn_pair_windows(catalog: SourceCatalog) -> tuple[TurnPairWindow, ...]:
    by_turn: dict[int, list[Any]] = {}
    for span in catalog.spans:
        by_turn.setdefault(span.turn_index, []).append(span)
    windows: list[TurnPairWindow] = []
    for turn_index in sorted(by_turn):
        spans = sorted(
            by_turn[turn_index],
            key=lambda item: (item.speaker != "user", item.kind != "turn", item.char_start),
        )
        lines = [f"TURN PAIR {turn_index}"]
        current_speaker = None
        for span in spans:
            if span.speaker != current_speaker:
                current_speaker = span.speaker
                turn_span = next(
                    item for item in spans
                    if item.speaker == span.speaker and item.kind == "turn"
                )
                lines.append(
                    f"{span.speaker.upper()} [{turn_span.span_id} is the complete speaker turn]:"
                )
            if span.kind == "sentence":
                lines.append(f"[{span.span_id}] {span.text}")
        windows.append(
            TurnPairWindow(
                schema_version=WINDOW_SCHEMA,
                window_id=f"window-{turn_index:03d}",
                turn_index=turn_index,
                span_ids=tuple(span.span_id for span in spans),
                source_text="\n".join(lines),
            )
        )
    return tuple(windows)


_HARVEST_CLASSES = {
    "contributions": ContributionHarvest,
    "thread_events": ThreadEventHarvest,
    "constraint_claims": ConstraintClaimHarvest,
}
_SYNTHESIS_CLASSES = {
    "positions": PositionSynthesis,
    "threads": ThreadSynthesis,
    "constraints": ConstraintSynthesis,
}


def _schema_with_enum(cls: type[Any], *, definition: str, field_name: str, values: list[str]) -> dict[str, Any]:
    schema = schema_for_dataclass(cls, use_references=True)
    target = schema["$defs"][definition]["properties"][field_name]
    target["enum"] = values
    return schema


def harvest_schema(family: str, *, window: TurnPairWindow) -> dict[str, Any]:
    if family not in _HARVEST_CLASSES:
        raise ValueError(f"unknown harvest family: {family}")
    return _schema_with_enum(
        _HARVEST_CLASSES[family],
        definition="SpanSelection",
        field_name="span_id",
        values=list(window.span_ids),
    )


def synthesis_schema(family: str, *, event_ids: list[str]) -> dict[str, Any]:
    if family not in _SYNTHESIS_CLASSES:
        raise ValueError(f"unknown synthesis family: {family}")
    mapping = {
        "positions": ("SynthesizedContribution", "event_id"),
        "threads": ("ThreadSynthesisCandidate", "event_ids"),
        "constraints": ("ConstraintSynthesisCandidate", "claim_event_ids"),
    }
    definition, field_name = mapping[family]
    schema = schema_for_dataclass(_SYNTHESIS_CLASSES[family], use_references=True)
    target = schema["$defs"][definition]["properties"][field_name]
    if target.get("type") == "array":
        target["items"]["enum"] = event_ids
    else:
        target["enum"] = event_ids
    if family == "threads":
        for name in ("introduced_event_id", "latest_event_id"):
            schema["$defs"][definition]["properties"][name]["enum"] = event_ids
        schema["$defs"]["SynthesizedThreadResponse"]["properties"]["event_id"]["enum"] = event_ids
    return schema


_HARVEST_JOBS = {
    "contributions": "Identify only local speaker contributions to possible decision directions. Do not decide contribution role, final ownership, relevance to the current plan, or compose the final position.",
    "thread_events": "Identify only local substantive thread moves. Describe the locally observable move; do not decide where the thread began, response quality, relevance to the focal trajectory, or final disposition.",
    "constraint_claims": "Identify only atomic local claims that might constrain the decision. Do not decide final importance or source-strength classification.",
}


def build_harvest_contract(family: str, *, window: TurnPairWindow) -> dict[str, Any]:
    schema = harvest_schema(family, window=window)
    system = (
        _HARVEST_JOBS[family]
        + "\nReturn stable span IDs only; never copy or paraphrase source text. "
        "Favor recall, preserve uncertainty, and use not_found rather than invention. "
        "Return exactly one JSON object matching the schema."
    )
    user = window.source_text + "\n\nOUTPUT SCHEMA\n" + json.dumps(
        schema, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return {
        "family": family,
        "window_id": window.window_id,
        "system_prompt": system,
        "user_prompt": user,
        "schema": schema,
        "schema_metrics": schema_metrics(schema),
        "system_prompt_sha256": hashlib.sha256(system.encode()).hexdigest(),
        "user_prompt_sha256": hashlib.sha256(user.encode()).hexdigest(),
        "provider_calls": 0,
    }


_SYNTHESIS_JOBS = {
    "positions": (
        "Reconstruct the current decision state and the smallest set of materially developed positions from the complete ordered event ledger. "
        "Return one composed focal current direction when its conditions, thresholds, implementation details, and later qualifications are compatible parts of the same plan. "
        "Split only materially independent or competing positions. A provisional plan, leaning, future review, or unresolved decision rule is conditional rather than accepted; accepted requires unequivocal adoption. "
        "Ownership is joint whenever both speakers materially originated, developed, or qualified the composed direction. Assign each contribution role only now, using the full trajectory."
    ),
    "threads": (
        "Reconstruct only focal substantive thread trajectories from the complete ordered event ledger. "
        "Do not collapse a specific unresolved concern into the broad decision topic. Scan from the end backward for narrow questions that remain consequential. "
        "A later general policy may engage an earlier specific thread. Decide introduction, responses, latest material state, and disposition only from the full trajectory. "
        "Reference only the minimal decisive events: introduction, material response or responses, and latest governing state; do not list every related event."
    ),
    "constraints": (
        "Select only atomic load-bearing conditions whose removal could change the decision. Split combined claims, preserve the source's epistemic strength, and classify each claim separately. "
        "Sweep all turns so later plan details do not crowd out earlier capacity, commitment, timing, and dependency constraints. "
        "Use stated_condition when the speaker directly states a present case fact or adopted plan condition; reported_statement only when the speaker attributes the claim to another person or organization; "
        "possibility for may/might/could, preference for wants or desired direction, concern for a worry or risk, and inference only for a synthesis not directly asserted. "
        "Assistant advice, warnings, and hypotheticals are not case constraints unless the user accepts them or they become part of the current decision state."
    ),
}


def build_synthesis_contract(
    family: str, *, event_ledger: Mapping[str, Any]
) -> dict[str, Any]:
    """Build a fresh-context synthesis contract over the preserved event ledger."""

    if family not in _SYNTHESIS_CLASSES:
        raise ValueError(f"unknown synthesis family: {family}")
    eligible = [
        row
        for row in event_ledger.get("events", [])
        if isinstance(row, Mapping)
        and row.get("synthesis_eligible") is True
        and isinstance(row.get("event_snapshot"), Mapping)
        and (family != "constraints" or row.get("family") == "constraint_claims")
    ]
    event_ids = [str(row["event_id"]) for row in eligible]
    schema = synthesis_schema(family, event_ids=event_ids)
    lines = ["ORDERED PRESERVED EVENTS"]
    for row in eligible:
        snapshot = dict(row["event_snapshot"])
        sources = snapshot.pop("resolved_source", [])
        snapshot.pop("evidence", None)
        lines.append(
            f"[{row['event_id']}] family={row['family']} window={row['window_id']} turn={row['turn_index']}"
        )
        for source in sources:
            lines.append(
                f"  source={source['span_id']} speaker={source['speaker']} turn={source['turn_index']} text={json.dumps(source['text'], ensure_ascii=False)}"
            )
        lines.append(
            "  local_interpretation="
            + json.dumps(snapshot, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        )
    system = (
        _SYNTHESIS_JOBS[family]
        + "\nTreat harvest candidates as noisy proposals, not truth. Use only listed event IDs; do not invent source IDs or source text. "
        "Preserve uncertainty and use not_found when the ledger does not support a result. Return exactly one JSON object matching the schema."
    )
    user = "\n".join(lines) + "\n\nOUTPUT SCHEMA\n" + json.dumps(
        schema, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return {
        "family": family,
        "event_ids": event_ids,
        "event_count": len(event_ids),
        "system_prompt": system,
        "user_prompt": user,
        "schema": schema,
        "schema_metrics": schema_metrics(schema),
        "system_prompt_sha256": hashlib.sha256(system.encode()).hexdigest(),
        "user_prompt_sha256": hashlib.sha256(user.encode()).hexdigest(),
        "provider_calls": 0,
    }


def parse_harvest(family: str, payload: object) -> tuple[Any, list[ValidationIssue]]:
    if family not in _HARVEST_CLASSES:
        raise ValueError(f"unknown harvest family: {family}")
    return parse_typed(_HARVEST_CLASSES[family], payload)


def parse_synthesis(family: str, payload: object) -> tuple[Any, list[ValidationIssue]]:
    if family not in _SYNTHESIS_CLASSES:
        raise ValueError(f"unknown synthesis family: {family}")
    return parse_typed(_SYNTHESIS_CLASSES[family], payload)


def canonical_sha(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode()).hexdigest()


def event_snapshot(event: Any, *, catalog: SourceCatalog) -> dict[str, Any]:
    raw = asdict(event)
    selections: list[str]
    evidence = getattr(event, "evidence")
    if isinstance(evidence, SpanSelection):
        selections = [evidence.span_id]
    else:
        selections = [item.span_id for item in evidence]
    by_id = catalog.by_id()
    raw["resolved_source"] = [
        {
            "span_id": span_id,
            "speaker": by_id[span_id].speaker,
            "turn_index": by_id[span_id].turn_index,
            "text": by_id[span_id].text,
        }
        for span_id in selections
        if span_id in by_id
    ]
    return raw
