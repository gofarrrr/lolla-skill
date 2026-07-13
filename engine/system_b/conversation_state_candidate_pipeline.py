"""Provider-free ledger and compiler for conversation-state micro-candidates."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict
from typing import Any

from .conversation_state_candidates import (
    ConstraintCandidate,
    ConstraintExtraction,
    ContributionCandidate,
    DecisionSummaryCandidate,
    EvidenceRef,
    PositionCandidate,
    PositionExtraction,
    SourceCatalog,
    ThreadCandidate,
    ThreadExtraction,
    ThreadResponseCandidate,
    ValidationIssue,
    evidence_to_handoff,
    parse_typed,
    resolve_evidence,
    validate_extraction_state,
)
from .conversation_state_handoff import REQUIRED_NON_CLAIMS, SCHEMA_VERSION
from .semantic_candidate_ledger import (
    CURRENT_VIEW_STATES,
    SUPPORTED_CANDIDATE_STATES,
)


LEDGER_SCHEMA = "lolla.conversation_state_candidate_ledger.v1"
COMPILER_RESULT_SCHEMA = "lolla.conversation_state_candidate_compiler_result.v1"
FAMILIES = ("decision_summary", "positions", "threads", "constraints")


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: object) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _evidence_ref_from_handoff(
    evidence: Mapping[str, Any], *, catalog: SourceCatalog
) -> dict[str, str]:
    speaker = str(evidence.get("speaker", ""))
    turn_index = int(evidence.get("turn_index", 0))
    quote = str(evidence.get("quote", ""))
    candidates = [
        span
        for span in catalog.spans
        if span.speaker == speaker
        and span.turn_index == turn_index
        and quote
        and quote in span.text
        and span.text.count(quote) == 1
    ]
    if not candidates:
        raise ValueError(
            f"reviewed evidence cannot resolve to catalog: {speaker}/{turn_index}/{quote!r}"
        )
    candidates.sort(key=lambda span: (span.kind != "sentence", len(span.text), span.span_id))
    return {"span_id": candidates[0].span_id, "excerpt": quote}


def _migration_by_constraint(
    migrations: Mapping[str, Any], *, case_id: str
) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for row in migrations.get("migrations", []):
        if not isinstance(row, Mapping) or row.get("case_id") != case_id:
            continue
        result[str(row.get("legacy_constraint_id"))] = [
            dict(item)
            for item in row.get("replacement_candidates", [])
            if isinstance(item, Mapping)
        ]
    return result


def decompose_reviewed_handoff(
    packet: Mapping[str, Any],
    *,
    catalog: SourceCatalog,
    atomic_migrations: Mapping[str, Any],
) -> dict[str, Any]:
    """Project a reviewed handoff into the three shallow typed outputs."""

    decision = packet["decision_summary"]
    positions_payload = {
        "status": "supported",
        "decision_summary": {
            "text": decision["text"],
            "evidence_mode": decision["evidence_mode"],
            "evidence": [
                _evidence_ref_from_handoff(item, catalog=catalog)
                for item in decision["source_evidence"]
            ],
        },
        "positions": [],
    }
    for row in packet["positions"]:
        positions_payload["positions"].append(
            {
                "text": row["text"],
                "ownership": row["ownership"],
                "state": row["state"],
                "evidence_mode": row["evidence_mode"],
                "contributions": [
                    {
                        "role": item["role"],
                        "evidence": _evidence_ref_from_handoff(item, catalog=catalog),
                    }
                    for item in row["contributions"]
                ],
            }
        )

    threads_payload = {"status": "supported", "threads": []}
    for row in packet["threads"]:
        threads_payload["threads"].append(
            {
                "text": row["text"],
                "disposition": row["disposition"],
                "introduced": _evidence_ref_from_handoff(row["introduced"], catalog=catalog),
                "responses": [
                    {
                        "engagement": item["engagement"],
                        "evidence": _evidence_ref_from_handoff(item, catalog=catalog),
                    }
                    for item in row["responses"]
                ],
                "latest": _evidence_ref_from_handoff(row["latest_ref"], catalog=catalog),
                "superseded_by": row["superseded_by"],
                "evidence_mode": row["evidence_mode"],
            }
        )

    migration = _migration_by_constraint(
        atomic_migrations, case_id=str(packet["case_id"])
    )
    constraints_payload = {"status": "supported", "constraints": []}
    for row in packet["constraints"]:
        replacements = migration.get(str(row["constraint_id"]))
        source_rows = replacements if replacements is not None else [row]
        if row["claim_mode"] == "mixed" and replacements is None:
            raise ValueError(f"mixed constraint lacks atomic migration: {row['constraint_id']}")
        for source in source_rows:
            evidence = source.get("source_evidence", [])
            constraints_payload["constraints"].append(
                {
                    "text": source["text"],
                    "state": source["state"],
                    "claim_mode": source["claim_mode"],
                    "evidence_mode": source["evidence_mode"],
                    "evidence": [
                        _evidence_ref_from_handoff(item, catalog=catalog)
                        for item in evidence
                    ],
                }
            )

    parsed: dict[str, Any] = {}
    for family, cls, payload in (
        ("positions", PositionExtraction, positions_payload),
        ("threads", ThreadExtraction, threads_payload),
        ("constraints", ConstraintExtraction, constraints_payload),
    ):
        value, issues = parse_typed(cls, payload)
        if issues or value is None:
            raise ValueError(
                {family: [issue.to_dict() for issue in issues]}
            )
        state_issues = validate_extraction_state(value)
        if state_issues:
            raise ValueError(
                {family: [issue.to_dict() for issue in state_issues]}
            )
        parsed[family] = value
    return parsed


def _evidence_issues(
    refs: Sequence[EvidenceRef], *, catalog: SourceCatalog, path: str
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for index, ref in enumerate(refs):
        _span, found = resolve_evidence(
            ref, catalog=catalog, path=f"{path}/{index}"
        )
        issues.extend(found)
    return issues


def _candidate_issues(
    family: str, candidate: Any, *, catalog: SourceCatalog, path: str
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if family == "decision_summary":
        return _evidence_issues(candidate.evidence, catalog=catalog, path=path + "/evidence")
    if family == "positions":
        speakers: set[str] = set()
        for index, contribution in enumerate(candidate.contributions):
            span, found = resolve_evidence(
                contribution.evidence,
                catalog=catalog,
                path=f"{path}/contributions/{index}/evidence",
            )
            issues.extend(found)
            if span is not None and not found:
                speakers.add(span.speaker)
        if candidate.ownership == "joint" and not {"user", "assistant"} <= speakers:
            issues.append(ValidationIssue("joint_position_requires_both_speakers", path))
        if candidate.ownership in {"user", "assistant"} and candidate.ownership not in speakers:
            issues.append(ValidationIssue("owned_position_missing_owner_evidence", path))
        return issues
    if family == "threads":
        refs = [candidate.introduced, candidate.latest]
        refs.extend(item.evidence for item in candidate.responses)
        issues.extend(_evidence_issues(refs, catalog=catalog, path=path + "/evidence"))
        engagements = [item.engagement for item in candidate.responses]
        if candidate.disposition == "open_unaddressed" and candidate.responses:
            issues.append(ValidationIssue("unaddressed_thread_cannot_have_responses", path))
        if candidate.disposition == "addressed_unresolved" and "substantive" not in engagements:
            issues.append(ValidationIssue("addressed_thread_requires_substantive_response", path))
        if candidate.disposition == "resolved" and "resolved" not in engagements:
            issues.append(ValidationIssue("resolved_thread_requires_resolution_response", path))
        if candidate.disposition == "genuinely_dropped" and any(
            item in {"substantive", "resolved"} for item in engagements
        ):
            issues.append(ValidationIssue("dropped_thread_has_material_response", path))
        if candidate.disposition == "superseded" and not candidate.superseded_by:
            issues.append(ValidationIssue("superseded_thread_requires_replacement", path))
        if candidate.disposition != "superseded" and candidate.superseded_by is not None:
            issues.append(ValidationIssue("non_superseded_thread_names_replacement", path))
        return issues
    if family == "constraints":
        issues.extend(
            _evidence_issues(candidate.evidence, catalog=catalog, path=path + "/evidence")
        )
        if candidate.claim_mode == "mixed":
            issues.append(ValidationIssue("mixed_constraint_forbidden", path + "/claim_mode"))
        return issues
    return [ValidationIssue("unknown_candidate_family", path, family)]


def _record(
    *,
    case_id: str,
    family: str,
    index: int,
    candidate: Any,
    extraction_status: str,
    issues: Sequence[ValidationIssue],
) -> dict[str, Any]:
    snapshot = asdict(candidate)
    candidate_id = f"cstate-{family}-{index:03d}-{_sha([case_id, family, index, snapshot])[:12]}"
    state_history = [
        {
            "state": "proposed",
            "reason": "recorded_from_typed_micro_extraction",
            "actor": "semantic_reader_or_reviewed_fixture",
        }
    ]
    if issues:
        terminal = "invalid_evidence"
        reason = ";".join(issue.code for issue in issues)
        eligible = False
        actor = "deterministic_harness"
    else:
        state_history.append(
            {
                "state": "validated",
                "reason": "typed_shape_and_source_custody_valid",
                "actor": "deterministic_harness",
            }
        )
        terminal = (
            "ambiguous_competing_read"
            if extraction_status == "unclear"
            else "selected_for_current_view"
        )
        reason = (
            "semantic_reader_declared_unclear"
            if extraction_status == "unclear"
            else "source_reviewed_or_reader_selected_candidate"
        )
        eligible = True
        actor = "semantic_reader_or_source_review"
    state_history.append({"state": terminal, "reason": reason, "actor": actor})
    return {
        "candidate_id": candidate_id,
        "family": family,
        "proposal_index": index,
        "raw_proposal": snapshot,
        "raw_proposal_sha256": _sha(snapshot),
        "state_history": state_history,
        "terminal_state": terminal,
        "terminal_reason": reason,
        "validation_issues": [issue.to_dict() for issue in issues],
        "current_view_eligible": eligible,
        "event_snapshot": snapshot if eligible else None,
    }


def build_candidate_ledger(
    *, case_id: str, catalog: SourceCatalog, extractions: Mapping[str, Any]
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    outcomes: dict[str, Any] = {}
    positions: PositionExtraction = extractions["positions"]
    groups = {
        "decision_summary": (
            positions.status,
            (positions.decision_summary,) if positions.decision_summary is not None else (),
        ),
        "positions": (positions.status, positions.positions),
        "threads": (extractions["threads"].status, extractions["threads"].threads),
        "constraints": (
            extractions["constraints"].status,
            extractions["constraints"].constraints,
        ),
    }
    for family, (status, candidates) in groups.items():
        outcomes[family] = {
            "extraction_status": status,
            "candidate_count": len(candidates),
            "absence_is_observed": status == "not_found",
            "ambiguity_is_observed": status == "unclear",
        }
        for index, candidate in enumerate(candidates, start=1):
            issues = _candidate_issues(
                family, candidate, catalog=catalog, path=f"/{family}/{index - 1}"
            )
            records.append(
                _record(
                    case_id=case_id,
                    family=family,
                    index=index,
                    candidate=candidate,
                    extraction_status=status,
                    issues=issues,
                )
            )
    terminal_counts = Counter(row["terminal_state"] for row in records)
    return {
        "schema_version": LEDGER_SCHEMA,
        "case_id": case_id,
        "source": {
            "path": catalog.source_path,
            "sha256": catalog.source_sha256,
            "message_count": catalog.message_count,
            "catalog_schema_version": catalog.schema_version,
        },
        "supported_candidate_states": list(SUPPORTED_CANDIDATE_STATES),
        "family_outcomes": outcomes,
        "candidates": records,
        "metrics": {
            "proposal_count": len(records),
            "terminal_record_count": len(records),
            "invalid_candidate_count": terminal_counts.get("invalid_evidence", 0),
            "current_view_candidate_count": sum(
                terminal_counts.get(state, 0) for state in CURRENT_VIEW_STATES
            ),
            "counts_by_terminal_state": dict(sorted(terminal_counts.items())),
            "candidate_custody_complete": True,
        },
        "non_claims": [
            "candidate_validation_is_not_semantic_truth",
            "unreturned_hypotheses_are_not_observed",
            "source_grounding_is_not_semantic_correctness",
            "candidate_records_cannot_seed_graph_directly",
        ],
    }


def _current(ledger: Mapping[str, Any], family: str) -> list[Mapping[str, Any]]:
    return [
        row
        for row in ledger.get("candidates", [])
        if isinstance(row, Mapping)
        and row.get("family") == family
        and row.get("terminal_state") in CURRENT_VIEW_STATES
        and row.get("current_view_eligible") is True
        and isinstance(row.get("event_snapshot"), Mapping)
    ]


def _ref(value: Mapping[str, Any]) -> EvidenceRef:
    return EvidenceRef(span_id=str(value["span_id"]), excerpt=str(value["excerpt"]))


def compile_handoff_from_ledger(
    *, ledger: Mapping[str, Any], catalog: SourceCatalog
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    invalid = [
        row
        for row in ledger.get("candidates", [])
        if isinstance(row, Mapping) and row.get("terminal_state") == "invalid_evidence"
    ]
    decisions = _current(ledger, "decision_summary")
    positions = _current(ledger, "positions")
    if invalid or len(decisions) != 1 or not positions:
        reason = (
            "invalid_candidates_present"
            if invalid
            else "decision_or_position_projection_incomplete"
        )
        return None, {
            "schema_version": COMPILER_RESULT_SCHEMA,
            "status": "quarantined",
            "reason": reason,
            "accepted_observed_path_allowed": False,
            "invalid_candidate_ids": [str(row.get("candidate_id")) for row in invalid],
            "graph_routing_allowed": False,
        }

    decision = decisions[0]["event_snapshot"]
    packet_positions: list[dict[str, Any]] = []
    for index, record in enumerate(positions, start=1):
        row = record["event_snapshot"]
        packet_positions.append(
            {
                "position_id": str(record["candidate_id"]),
                "text": row["text"],
                "ownership": row["ownership"],
                "state": row["state"],
                "evidence_mode": row["evidence_mode"],
                "contributions": [
                    {
                        **evidence_to_handoff(_ref(item["evidence"]), catalog=catalog),
                        "role": item["role"],
                    }
                    for item in row["contributions"]
                ],
                "graph_routing_eligible": False,
            }
        )

    packet_threads: list[dict[str, Any]] = []
    for record in _current(ledger, "threads"):
        row = record["event_snapshot"]
        packet_threads.append(
            {
                "thread_id": str(record["candidate_id"]),
                "text": row["text"],
                "disposition": row["disposition"],
                "introduced": evidence_to_handoff(_ref(row["introduced"]), catalog=catalog),
                "responses": [
                    {
                        **evidence_to_handoff(_ref(item["evidence"]), catalog=catalog),
                        "engagement": item["engagement"],
                    }
                    for item in row["responses"]
                ],
                "latest_ref": evidence_to_handoff(_ref(row["latest"]), catalog=catalog),
                "superseded_by": row["superseded_by"],
                "evidence_mode": row["evidence_mode"],
                "graph_routing_eligible": False,
            }
        )

    packet_constraints: list[dict[str, Any]] = []
    for record in _current(ledger, "constraints"):
        row = record["event_snapshot"]
        packet_constraints.append(
            {
                "constraint_id": str(record["candidate_id"]),
                "text": row["text"],
                "state": row["state"],
                "claim_mode": row["claim_mode"],
                "evidence_mode": row["evidence_mode"],
                "source_evidence": [
                    evidence_to_handoff(_ref(item), catalog=catalog)
                    for item in row["evidence"]
                ],
                "graph_routing_eligible": False,
            }
        )

    packet = {
        "schema_version": SCHEMA_VERSION,
        "status": "reviewed_shadow",
        "case_id": ledger["case_id"],
        "source": {
            "path": catalog.source_path,
            "sha256": catalog.source_sha256,
            "message_count": catalog.message_count,
        },
        "decision_summary": {
            "text": decision["text"],
            "evidence_mode": decision["evidence_mode"],
            "source_evidence": [
                evidence_to_handoff(_ref(item), catalog=catalog)
                for item in decision["evidence"]
            ],
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
        "reason": "all_projected_candidates_validated",
        "accepted_observed_path_allowed": True,
        "invalid_candidate_ids": [],
        "graph_routing_allowed": False,
        "compiled_packet_sha256": _sha(packet),
    }
