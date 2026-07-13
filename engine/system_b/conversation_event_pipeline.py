"""Provider-free custody and composition for decomposed conversation events.

Probabilistic readers may interpret local meaning and fresh synthesizers may
compose cross-turn state.  This module owns only identity, source resolution,
terminal custody, reference validation, and fail-closed compilation.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict
from typing import Any

from .conversation_event_harvesting import (
    HARVEST_LEDGER_SCHEMA,
    ConstraintClaimEvent,
    ConstraintClaimHarvest,
    ConstraintSynthesis,
    ConstraintSynthesisCandidate,
    ContributionEvent,
    ContributionHarvest,
    PositionSynthesis,
    PositionSynthesisCandidate,
    SpanSelection,
    SynthesizedContribution,
    SynthesizedThreadResponse,
    ThreadEvent,
    ThreadEventHarvest,
    ThreadSynthesis,
    ThreadSynthesisCandidate,
    TurnPairWindow,
    event_snapshot,
)
from .conversation_state_candidate_pipeline import decompose_reviewed_handoff
from .conversation_state_candidates import SourceCatalog
from .conversation_state_handoff import REQUIRED_NON_CLAIMS, SCHEMA_VERSION


SYNTHESIS_LEDGER_SCHEMA = "lolla.conversation_event_synthesis_ledger.v1"
COMPILER_RESULT_SCHEMA = "lolla.conversation_event_compiler_result.v1"
HARVEST_FAMILIES = ("contributions", "thread_events", "constraint_claims")
SYNTHESIS_FAMILIES = ("positions", "threads", "constraints")


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: object) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _event_evidence_ids(event: Any) -> tuple[str, ...]:
    evidence = event.evidence
    if isinstance(evidence, SpanSelection):
        return (evidence.span_id,)
    return tuple(item.span_id for item in evidence)


def build_event_ledger(
    *,
    case_id: str,
    catalog: SourceCatalog,
    windows: Sequence[TurnPairWindow],
    harvests: Mapping[tuple[str, str], Any],
) -> dict[str, Any]:
    """Preserve every harvest proposal and validate only local source custody."""

    records: list[dict[str, Any]] = []
    outcomes: list[dict[str, Any]] = []
    window_by_id = {window.window_id: window for window in windows}
    catalog_ids = set(catalog.by_id())
    sequence = 0
    for family in HARVEST_FAMILIES:
        for window in windows:
            extraction = harvests.get((family, window.window_id))
            if extraction is None:
                outcomes.append(
                    {
                        "family": family,
                        "window_id": window.window_id,
                        "status": "missing",
                        "event_count": 0,
                        "absence_is_observed": False,
                        "ambiguity_is_observed": False,
                    }
                )
                continue
            events = tuple(extraction.events)
            outcomes.append(
                {
                    "family": family,
                    "window_id": window.window_id,
                    "status": extraction.status,
                    "event_count": len(events),
                    "absence_is_observed": extraction.status == "not_found",
                    "ambiguity_is_observed": extraction.status == "unclear",
                }
            )
            for proposal_index, event in enumerate(events, start=1):
                sequence += 1
                raw = asdict(event)
                evidence_ids = _event_evidence_ids(event)
                issues: list[dict[str, str]] = []
                for index, span_id in enumerate(evidence_ids):
                    pointer = f"/evidence/{index}"
                    if span_id not in catalog_ids:
                        issues.append({"code": "source_span_not_found", "path": pointer})
                    elif span_id not in set(window.span_ids):
                        issues.append({"code": "source_span_outside_window", "path": pointer})
                event_id = (
                    f"cevent-{family}-{sequence:03d}-"
                    f"{_sha([case_id, family, window.window_id, proposal_index, raw])[:12]}"
                )
                history = [
                    {
                        "state": "proposed",
                        "actor": "semantic_harvester_or_reviewed_fixture",
                        "reason": "recorded_from_typed_small_window_harvest",
                    }
                ]
                if issues:
                    terminal = "invalid_evidence"
                    reason = ";".join(item["code"] for item in issues)
                    eligible = False
                    snapshot = None
                    actor = "deterministic_harness"
                else:
                    history.append(
                        {
                            "state": "validated",
                            "actor": "deterministic_harness",
                            "reason": "typed_shape_and_window_source_custody_valid",
                        }
                    )
                    terminal = (
                        "ambiguous_candidate"
                        if extraction.status == "unclear"
                        else "preserved_for_synthesis"
                    )
                    reason = (
                        "semantic_harvester_declared_unclear"
                        if extraction.status == "unclear"
                        else "all_valid_harvests_are_preserved_without_relevance_gating"
                    )
                    eligible = True
                    snapshot = event_snapshot(event, catalog=catalog)
                    actor = "semantic_harvester_or_reviewed_fixture"
                history.append({"state": terminal, "actor": actor, "reason": reason})
                records.append(
                    {
                        "event_id": event_id,
                        "family": family,
                        "window_id": window.window_id,
                        "turn_index": window.turn_index,
                        "proposal_index": proposal_index,
                        "raw_proposal": raw,
                        "raw_proposal_sha256": _sha(raw),
                        "state_history": history,
                        "terminal_state": terminal,
                        "terminal_reason": reason,
                        "validation_issues": issues,
                        "synthesis_eligible": eligible,
                        "event_snapshot": snapshot,
                    }
                )
    counts = Counter(row["terminal_state"] for row in records)
    missing = sum(row["status"] == "missing" for row in outcomes)
    return {
        "schema_version": HARVEST_LEDGER_SCHEMA,
        "case_id": case_id,
        "source": {
            "path": catalog.source_path,
            "sha256": catalog.source_sha256,
            "message_count": catalog.message_count,
        },
        "windows": [asdict(window) for window in windows],
        "family_window_outcomes": outcomes,
        "events": records,
        "metrics": {
            "expected_harvest_count": len(windows) * len(HARVEST_FAMILIES),
            "observed_harvest_count": len(outcomes) - missing,
            "missing_harvest_count": missing,
            "proposal_count": len(records),
            "terminal_record_count": len(records),
            "invalid_event_count": counts.get("invalid_evidence", 0),
            "synthesis_eligible_count": sum(row["synthesis_eligible"] for row in records),
            "counts_by_terminal_state": dict(sorted(counts.items())),
            "candidate_custody_complete": len(records) == sum(counts.values()),
        },
        "non_claims": [
            "harvest_validation_is_not_semantic_truth",
            "unreturned_hypotheses_are_not_observed",
            "all_valid_events_are_preserved_without_deterministic_relevance_gating",
            "harvest_events_cannot_seed_graph_directly",
        ],
    }


def _eligible_events(ledger: Mapping[str, Any], family: str) -> list[Mapping[str, Any]]:
    return [
        row
        for row in ledger.get("events", [])
        if isinstance(row, Mapping)
        and row.get("family") == family
        and row.get("synthesis_eligible") is True
        and isinstance(row.get("event_snapshot"), Mapping)
    ]


def _synthesis_candidates(synthesis: Any) -> tuple[Any, ...]:
    if isinstance(synthesis, PositionSynthesis):
        return synthesis.positions
    if isinstance(synthesis, ThreadSynthesis):
        return synthesis.threads
    if isinstance(synthesis, ConstraintSynthesis):
        return synthesis.constraints
    raise TypeError(f"unknown synthesis type: {type(synthesis)!r}")


def _synthesis_refs(family: str, candidate: Any) -> tuple[str, ...]:
    if family == "positions":
        return tuple(item.event_id for item in candidate.contributions)
    if family == "threads":
        return tuple(candidate.event_ids)
    if family == "constraints":
        return tuple(candidate.claim_event_ids)
    raise ValueError(f"unknown synthesis family: {family}")


def build_synthesis_ledger(
    *, case_id: str, event_ledger: Mapping[str, Any], syntheses: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate synthesis references and preserve every synthesis proposal."""

    all_event_ids = {
        str(row["event_id"])
        for row in event_ledger.get("events", [])
        if isinstance(row, Mapping)
        and row.get("synthesis_eligible") is True
        and isinstance(row.get("event_snapshot"), Mapping)
    }
    allowed_by_family = {
        # Harvest families are complementary discovery lenses, not semantic
        # routing silos. Fresh cross-turn synthesis may use any preserved event.
        "positions": all_event_ids,
        "threads": all_event_ids,
        "constraints": {row["event_id"] for row in _eligible_events(event_ledger, "constraint_claims")},
    }
    event_rows = {
        str(row["event_id"]): row
        for row in event_ledger.get("events", [])
        if isinstance(row, Mapping)
        and row.get("synthesis_eligible") is True
        and isinstance(row.get("event_snapshot"), Mapping)
    }
    records: list[dict[str, Any]] = []
    outcomes: dict[str, Any] = {}
    sequence = 0
    for family in SYNTHESIS_FAMILIES:
        synthesis = syntheses.get(family)
        if synthesis is None:
            outcomes[family] = {
                "status": "missing",
                "candidate_count": 0,
                "absence_is_observed": False,
                "ambiguity_is_observed": False,
            }
            continue
        candidates = _synthesis_candidates(synthesis)
        outcomes[family] = {
            "status": synthesis.status,
            "candidate_count": len(candidates),
            "absence_is_observed": synthesis.status == "not_found",
            "ambiguity_is_observed": synthesis.status == "unclear",
        }
        for proposal_index, candidate in enumerate(candidates, start=1):
            sequence += 1
            raw = asdict(candidate)
            refs = _synthesis_refs(family, candidate)
            issues: list[dict[str, str]] = []
            unknown = [ref for ref in refs if ref not in allowed_by_family[family]]
            if unknown:
                issues.append(
                    {
                        "code": "synthesis_event_reference_invalid",
                        "path": "/event_ids",
                        "detail": ",".join(unknown),
                    }
                )
            if len(refs) != len(set(refs)):
                issues.append({"code": "synthesis_event_reference_duplicate", "path": "/event_ids"})
            if family == "positions" and not unknown:
                speakers = {
                    str(source["speaker"])
                    for ref in refs
                    for source in event_rows[ref]["event_snapshot"].get("resolved_source", [])
                }
                if candidate.ownership == "joint" and not {"user", "assistant"} <= speakers:
                    issues.append({"code": "joint_position_requires_both_speakers", "path": "/contributions"})
                if candidate.ownership in {"user", "assistant"} and candidate.ownership not in speakers:
                    issues.append({"code": "owned_position_missing_owner_evidence", "path": "/contributions"})
            if family == "threads":
                if candidate.introduced_event_id not in refs:
                    issues.append({"code": "introduced_event_not_in_trajectory", "path": "/introduced_event_id"})
                if candidate.latest_event_id not in refs:
                    issues.append({"code": "latest_event_not_in_trajectory", "path": "/latest_event_id"})
                response_ids = [item.event_id for item in candidate.responses]
                if any(item not in refs for item in response_ids):
                    issues.append({"code": "response_event_not_in_trajectory", "path": "/responses"})
                if len(response_ids) != len(set(response_ids)):
                    issues.append({"code": "response_event_duplicate", "path": "/responses"})
                engagements = [item.engagement for item in candidate.responses]
                if candidate.disposition == "open_unaddressed" and candidate.responses:
                    issues.append({"code": "unaddressed_thread_cannot_have_responses", "path": "/responses"})
                if candidate.disposition == "addressed_unresolved" and "substantive" not in engagements:
                    issues.append({"code": "addressed_thread_requires_substantive_response", "path": "/responses"})
                if candidate.disposition == "resolved" and "resolved" not in engagements:
                    issues.append({"code": "resolved_thread_requires_resolution_response", "path": "/responses"})
                if candidate.disposition == "genuinely_dropped" and any(item in {"substantive", "resolved"} for item in engagements):
                    issues.append({"code": "dropped_thread_has_material_response", "path": "/responses"})
                if candidate.disposition == "superseded" and not candidate.superseded_by:
                    issues.append({"code": "superseded_thread_requires_replacement", "path": "/superseded_by"})
                if candidate.disposition != "superseded" and candidate.superseded_by is not None:
                    issues.append({"code": "non_superseded_thread_names_replacement", "path": "/superseded_by"})
            synthesis_id = (
                f"csynth-{family}-{sequence:03d}-"
                f"{_sha([case_id, family, proposal_index, raw])[:12]}"
            )
            terminal = "invalid_reference" if issues else (
                "ambiguous_synthesis" if synthesis.status == "unclear" else "selected_for_compilation"
            )
            records.append(
                {
                    "synthesis_id": synthesis_id,
                    "family": family,
                    "proposal_index": proposal_index,
                    "raw_proposal": raw,
                    "raw_proposal_sha256": _sha(raw),
                    "terminal_state": terminal,
                    "terminal_reason": (
                        ";".join(item["code"] for item in issues)
                        if issues
                        else "fresh_synthesis_preserved_for_deterministic_compilation"
                    ),
                    "validation_issues": issues,
                    "compilation_eligible": not issues,
                    "event_snapshot": raw if not issues else None,
                }
            )
    counts = Counter(row["terminal_state"] for row in records)
    return {
        "schema_version": SYNTHESIS_LEDGER_SCHEMA,
        "case_id": case_id,
        "event_ledger_sha256": _sha(event_ledger),
        "family_outcomes": outcomes,
        "decision_summary": (
            syntheses["positions"].decision_summary
            if isinstance(syntheses.get("positions"), PositionSynthesis)
            else None
        ),
        "syntheses": records,
        "metrics": {
            "proposal_count": len(records),
            "terminal_record_count": len(records),
            "invalid_synthesis_count": counts.get("invalid_reference", 0),
            "compilation_eligible_count": sum(row["compilation_eligible"] for row in records),
            "counts_by_terminal_state": dict(sorted(counts.items())),
            "candidate_custody_complete": len(records) == sum(counts.values()),
        },
        "non_claims": [
            "reference_validation_is_not_semantic_truth",
            "fresh_synthesis_is_probabilistic_or_human_interpretation",
            "synthesized_case_state_cannot_seed_graph_directly",
        ],
    }


def _event_map(ledger: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        str(row["event_id"]): row
        for row in ledger.get("events", [])
        if isinstance(row, Mapping) and isinstance(row.get("event_snapshot"), Mapping)
    }


def _compiled_syntheses(ledger: Mapping[str, Any], family: str) -> list[Mapping[str, Any]]:
    return [
        row
        for row in ledger.get("syntheses", [])
        if isinstance(row, Mapping)
        and row.get("family") == family
        and row.get("compilation_eligible") is True
        and isinstance(row.get("event_snapshot"), Mapping)
    ]


def _source_rows(event_ids: Sequence[str], events: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for event_id in event_ids:
        event = events[event_id]["event_snapshot"]
        for source in event.get("resolved_source", []):
            span_id = str(source["span_id"])
            if span_id in seen:
                continue
            seen.add(span_id)
            rows.append(
                {
                    "speaker": source["speaker"],
                    "turn_index": source["turn_index"],
                    "quote": source["text"],
                }
            )
    return rows


def compile_handoff_from_event_ledgers(
    *,
    event_ledger: Mapping[str, Any],
    synthesis_ledger: Mapping[str, Any],
    catalog: SourceCatalog,
    handoff_status: str = "reviewed_shadow",
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """Fail closed and compile source-linked conversation state without graph seeds."""

    invalid_events = [
        row for row in event_ledger.get("events", [])
        if isinstance(row, Mapping) and row.get("terminal_state") == "invalid_evidence"
    ]
    invalid_syntheses = [
        row for row in synthesis_ledger.get("syntheses", [])
        if isinstance(row, Mapping) and row.get("terminal_state") == "invalid_reference"
    ]
    positions = _compiled_syntheses(synthesis_ledger, "positions")
    decision_summary = synthesis_ledger.get("decision_summary")
    missing_synthesis_families = [
        family
        for family in SYNTHESIS_FAMILIES
        if synthesis_ledger.get("family_outcomes", {}).get(family, {}).get("status") == "missing"
    ]
    if (
        invalid_events
        or invalid_syntheses
        or event_ledger.get("metrics", {}).get("missing_harvest_count")
        or missing_synthesis_families
        or not positions
        or not isinstance(decision_summary, str)
        or not decision_summary.strip()
    ):
        if invalid_events:
            reason = "invalid_harvest_events_present"
        elif invalid_syntheses:
            reason = "invalid_synthesis_references_present"
        elif event_ledger.get("metrics", {}).get("missing_harvest_count"):
            reason = "harvest_matrix_incomplete"
        elif missing_synthesis_families:
            reason = "synthesis_matrix_incomplete"
        else:
            reason = "decision_or_position_projection_incomplete"
        return None, {
            "schema_version": COMPILER_RESULT_SCHEMA,
            "status": "quarantined",
            "reason": reason,
            "accepted_observed_path_allowed": False,
            "graph_routing_allowed": False,
            "invalid_event_ids": [str(row.get("event_id")) for row in invalid_events],
            "invalid_synthesis_ids": [str(row.get("synthesis_id")) for row in invalid_syntheses],
        }

    events = _event_map(event_ledger)
    packet_positions: list[dict[str, Any]] = []
    all_position_event_ids: list[str] = []
    for record in positions:
        row = record["event_snapshot"]
        event_ids = [item["event_id"] for item in row["contributions"]]
        all_position_event_ids.extend(event_ids)
        contributions: list[dict[str, Any]] = []
        for contribution in row["contributions"]:
            event_id = contribution["event_id"]
            event = events[event_id]["event_snapshot"]
            for source in event["resolved_source"]:
                contributions.append(
                    {
                        "speaker": source["speaker"],
                        "turn_index": source["turn_index"],
                        "role": contribution["role"],
                        "quote": source["text"],
                    }
                )
        packet_positions.append(
            {
                "position_id": record["synthesis_id"],
                "text": row["text"],
                "ownership": row["ownership"],
                "state": row["state"],
                "evidence_mode": "exact_span" if len(contributions) == 1 else "multi_turn_derivation",
                "contributions": contributions,
                "graph_routing_eligible": False,
            }
        )

    packet_threads: list[dict[str, Any]] = []
    for record in _compiled_syntheses(synthesis_ledger, "threads"):
        row = record["event_snapshot"]
        introduced = _source_rows([row["introduced_event_id"]], events)[0]
        latest = _source_rows([row["latest_event_id"]], events)[-1]
        responses: list[dict[str, Any]] = []
        if row["disposition"] != "open_unaddressed":
            for response in row["responses"]:
                event_id = response["event_id"]
                event = events[event_id]["event_snapshot"]
                for source in event["resolved_source"]:
                    responses.append(
                        {
                            "speaker": source["speaker"],
                            "turn_index": source["turn_index"],
                            "engagement": response["engagement"],
                            "quote": source["text"],
                        }
                    )
        packet_threads.append(
            {
                "thread_id": record["synthesis_id"],
                "text": row["text"],
                "disposition": row["disposition"],
                "introduced": introduced,
                "responses": responses,
                "latest_ref": latest,
                "superseded_by": row["superseded_by"],
                "evidence_mode": "exact_span" if len(set(row["event_ids"])) == 1 else "multi_turn_derivation",
                "graph_routing_eligible": False,
            }
        )

    packet_constraints: list[dict[str, Any]] = []
    for record in _compiled_syntheses(synthesis_ledger, "constraints"):
        row = record["event_snapshot"]
        source = _source_rows(row["claim_event_ids"], events)
        packet_constraints.append(
            {
                "constraint_id": record["synthesis_id"],
                "text": row["text"],
                "state": row["state"],
                "claim_mode": row["claim_mode"],
                "evidence_mode": "exact_span" if len(source) == 1 else "multi_turn_derivation",
                "source_evidence": source,
                "graph_routing_eligible": False,
            }
        )

    decision_source = _source_rows(all_position_event_ids, events)
    if not decision_source:
        return None, {
            "schema_version": COMPILER_RESULT_SCHEMA,
            "status": "quarantined",
            "reason": "decision_source_projection_incomplete",
            "accepted_observed_path_allowed": False,
            "graph_routing_allowed": False,
            "invalid_event_ids": [],
            "invalid_synthesis_ids": [],
        }
    packet = {
        "schema_version": SCHEMA_VERSION,
        "status": handoff_status,
        "case_id": event_ledger["case_id"],
        "source": {
            "path": catalog.source_path,
            "sha256": catalog.source_sha256,
            "message_count": catalog.message_count,
        },
        "decision_summary": {
            "text": decision_summary,
            "evidence_mode": "exact_span" if len(decision_source) == 1 else "multi_turn_derivation",
            "source_evidence": decision_source[:4],
        },
        "positions": packet_positions,
        "threads": packet_threads,
        "constraints": packet_constraints,
        "routing_boundary": {
            "contains_case_context": True,
            "direct_graph_routing_allowed": False,
            "reasoning_pattern_abstraction_required": True,
            "runtime_integration": False,
        },
        "non_claims": sorted(REQUIRED_NON_CLAIMS),
    }
    return packet, {
        "schema_version": COMPILER_RESULT_SCHEMA,
        "status": "compiled",
        "reason": "all_harvest_and_synthesis_records_validated",
        "accepted_observed_path_allowed": True,
        "graph_routing_allowed": False,
        "invalid_event_ids": [],
        "invalid_synthesis_ids": [],
    }


def reviewed_event_projection(
    *,
    packet: Mapping[str, Any],
    catalog: SourceCatalog,
    windows: Sequence[TurnPairWindow],
    atomic_migrations: Mapping[str, Any],
) -> tuple[dict[tuple[str, str], Any], dict[str, Any]]:
    """Provider-free reviewed projection used only to test representation loss."""

    extracted = decompose_reviewed_handoff(
        packet, catalog=catalog, atomic_migrations=atomic_migrations
    )
    span_to_window = {
        span_id: window.window_id for window in windows for span_id in window.span_ids
    }
    staged: dict[tuple[str, str], list[Any]] = {
        (family, window.window_id): []
        for family in HARVEST_FAMILIES
        for window in windows
    }
    groups: dict[str, list[dict[str, Any]]] = {
        "positions": [], "threads": [], "constraints": []
    }

    def add(family: str, span_id: str, event: Any) -> tuple[str, str, int]:
        window_id = span_to_window[span_id]
        key = (family, window_id)
        staged[key].append(event)
        return family, window_id, len(staged[key])

    positions = extracted["positions"]
    for position in positions.positions:
        locators = []
        for contribution in position.contributions:
            ref = contribution.evidence
            locators.append(
                add(
                    "contributions",
                    ref.span_id,
                    ContributionEvent(
                        position_fragment=position.text,
                        evidence=(SpanSelection(ref.span_id),),
                    ),
                )
            )
        groups["positions"].append(
            {
                "text": position.text,
                "ownership": position.ownership,
                "state": position.state,
                "contributions": [
                    {"locator": locator, "role": contribution.role}
                    for locator, contribution in zip(locators, position.contributions)
                ],
            }
        )

    for thread in extracted["threads"].threads:
        locators: list[tuple[str, str, int]] = []
        introduced = add(
            "thread_events",
            thread.introduced.span_id,
            ThreadEvent(
                thread_hint=thread.text,
                local_move="raised",
                evidence=(SpanSelection(thread.introduced.span_id),),
            ),
        )
        locators.append(introduced)
        by_span = {thread.introduced.span_id: introduced}
        response_groups = []
        for response in thread.responses:
            locator = add(
                "thread_events",
                response.evidence.span_id,
                ThreadEvent(
                    thread_hint=thread.text,
                    local_move="engaged",
                    evidence=(SpanSelection(response.evidence.span_id),),
                ),
            )
            locators.append(locator)
            by_span[response.evidence.span_id] = locator
            response_groups.append({"locator": locator, "engagement": response.engagement})
        latest = by_span.get(thread.latest.span_id)
        if latest is None:
            latest_kind = {
                "resolved": "resolution_claim",
                "superseded": "superseding_signal",
                "addressed_unresolved": "unresolved_signal",
            }.get(thread.disposition, "qualification")
            latest = add(
                "thread_events",
                thread.latest.span_id,
                ThreadEvent(
                    thread_hint=thread.text,
                    local_move=latest_kind,
                    evidence=(SpanSelection(thread.latest.span_id),),
                ),
            )
            locators.append(latest)
        groups["threads"].append(
            {
                "text": thread.text,
                "disposition": thread.disposition,
                "superseded_by": thread.superseded_by,
                "locators": locators,
                "introduced": introduced,
                "latest": latest,
                "responses": response_groups,
            }
        )

    for constraint in extracted["constraints"].constraints:
        locators = []
        for ref in constraint.evidence:
            locators.append(
                add(
                    "constraint_claims",
                    ref.span_id,
                    ConstraintClaimEvent(
                        claim_text=constraint.text,
                        evidence=SpanSelection(ref.span_id),
                    ),
                )
            )
        groups["constraints"].append(
            {
                "text": constraint.text,
                "state": constraint.state,
                "claim_mode": constraint.claim_mode,
                "locators": locators,
            }
        )

    harvests: dict[tuple[str, str], Any] = {}
    classes = {
        "contributions": ContributionHarvest,
        "thread_events": ThreadEventHarvest,
        "constraint_claims": ConstraintClaimHarvest,
    }
    for key, events in staged.items():
        family, _window_id = key
        harvests[key] = classes[family](
            status="supported" if events else "not_found", events=tuple(events)
        )
    return harvests, {
        "decision_summary": positions.decision_summary.text if positions.decision_summary else None,
        "groups": groups,
    }


def reviewed_fresh_syntheses(
    *, event_ledger: Mapping[str, Any], projection: Mapping[str, Any]
) -> dict[str, Any]:
    """Recreate reviewed syntheses solely through stable harvested event IDs."""

    locator_to_id = {
        (str(row["family"]), str(row["window_id"]), int(row["proposal_index"])): str(row["event_id"])
        for row in event_ledger.get("events", [])
        if isinstance(row, Mapping)
    }

    def ids(locators: Sequence[Sequence[Any]]) -> tuple[str, ...]:
        return tuple(locator_to_id[(str(a), str(b), int(c))] for a, b, c in locators)

    groups = projection["groups"]
    position_rows = tuple(
        PositionSynthesisCandidate(
            text=row["text"],
            ownership=row["ownership"],
            state=row["state"],
            contributions=tuple(
                SynthesizedContribution(
                    event_id=ids([item["locator"]])[0], role=item["role"]
                )
                for item in row["contributions"]
            ),
        )
        for row in groups["positions"]
    )
    thread_rows = tuple(
        ThreadSynthesisCandidate(
            text=row["text"],
            disposition=row["disposition"],
            event_ids=ids(row["locators"]),
            introduced_event_id=ids([row["introduced"]])[0],
            latest_event_id=ids([row["latest"]])[0],
            responses=tuple(
                SynthesizedThreadResponse(
                    event_id=ids([item["locator"]])[0], engagement=item["engagement"]
                )
                for item in row["responses"]
            ),
            superseded_by=row["superseded_by"],
        )
        for row in groups["threads"]
    )
    constraint_rows = tuple(
        ConstraintSynthesisCandidate(
            text=row["text"],
            state=row["state"],
            claim_mode=row["claim_mode"],
            claim_event_ids=ids(row["locators"]),
        )
        for row in groups["constraints"]
    )
    return {
        "positions": PositionSynthesis(
            status="supported" if position_rows else "not_found",
            decision_summary=projection["decision_summary"],
            positions=position_rows,
        ),
        "threads": ThreadSynthesis(
            status="supported" if thread_rows else "not_found", threads=thread_rows
        ),
        "constraints": ConstraintSynthesis(
            status="supported" if constraint_rows else "not_found",
            constraints=constraint_rows,
        ),
    }
