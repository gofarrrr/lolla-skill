"""Lossless candidate custody for the offline core-semantic shadow path.

Semantic readers decide meaning by emitting candidates and may optionally
declare a candidate disposition. Validators report mechanical evidence
outcomes directly to this recorder. The ledger never re-reads conversation
prose to infer a semantic result.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from .conversation_context import ConversationContext


SEMANTIC_CANDIDATE_LEDGER_SCHEMA_VERSION = "lolla.semantic_candidate_ledger.v0"
CURRENT_SEMANTIC_VIEW_SCHEMA_VERSION = "lolla.current_semantic_view.v0"

SUPPORTED_CANDIDATE_STATES = (
    "proposed",
    "validated",
    "invalid_evidence",
    "set_aside_semantically",
    "selected_for_current_view",
    "ambiguous_competing_read",
    "not_supported_by_source",
    "not_evaluated_budget",
    "duplicate_identity",
)
CURRENT_VIEW_STATES = {
    "selected_for_current_view",
    "ambiguous_competing_read",
}
SEMANTIC_READER_DISPOSITIONS = {
    "selected_for_current_view",
    "ambiguous_competing_read",
    "set_aside_semantically",
    "not_supported_by_source",
}

STANCE_TRAJECTORY_ADDENDUM = """

SHADOW STANCE TRAJECTORY ADDENDUM:
Return stance events in source-turn order. For a stance that revises,
qualifies, conditions, or defers an earlier stance event in the same returned
array, also return `related_stance_event_index`: the zero-based array index of
that earlier event. When the primary relation is genuinely ambiguous, keep
`relation_ambiguity: true` and add `alternative_relations` using only the base
prompt's relation vocabulary. Do not invent a prior stance reference when none
is present.

The values below illustrate shape only. Do not copy them unless the source and
semantic reading independently support them. Every stance object must use this
expanded key contract:
{
  "text": "exact contiguous substring from one assistant turn",
  "turn_index": 3,
  "relation": "commitment",
  "relation_ambiguity": false,
  "alternative_relations": [],
  "related_stance_event_index": null
}

Use null when the stance has no relationship to an earlier emitted stance.
Never insert `...` or otherwise shorten text inside `text`. The turn_index must
be the number printed immediately above the assistant source quote.
"""

_FAMILY_SPECS: dict[str, tuple[str, str]] = {
    "live_constraint_events": ("live_constraints", "live_constraints"),
    "assistant_stance_events": ("assistant_stances", "stance_events"),
    "dropped_thread_events": ("dropped_threads", "dropped_threads"),
    "question_events": ("question_trajectory", "question_events"),
    "user_pressure_events": ("user_pressure", "user_pressure_events"),
    "option_events": ("option_evidence", "option_events"),
    "evidence_boundary_events": ("option_evidence", "evidence_boundary_events"),
}
_RAW_CANDIDATE_KEYS = {raw_key for _, raw_key in _FAMILY_SPECS.values()}


@runtime_checkable
class BoundaryClient(Protocol):
    def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]: ...


@dataclass(frozen=True)
class SemanticReaderCall:
    call_id: str
    ordinal: int
    reader_role: str
    client_type: str
    provider_client_type: str
    provider_name: str
    model: str
    system_prompt_sha256: str
    user_prompt_sha256: str
    raw_payload: dict[str, object]

    def public_dict(self) -> dict[str, Any]:
        return {
            "call_id": self.call_id,
            "ordinal": self.ordinal,
            "reader_role": self.reader_role,
            "client_type": self.client_type,
            "provider_client_type": self.provider_client_type,
            "provider_name": self.provider_name,
            "model": self.model,
            "system_prompt_sha256": self.system_prompt_sha256,
            "user_prompt_sha256": self.user_prompt_sha256,
            "prompt_text_persisted": False,
            "raw_candidate_counts": {
                key: len(value) if isinstance(value, list) else 0
                for key, value in sorted(self.raw_payload.items())
                if key in _RAW_CANDIDATE_KEYS
            },
        }


class SemanticCandidateLedgerRecorder:
    """Boundary wrapper plus append-only candidate outcome recorder."""

    def __init__(self, boundary: BoundaryClient) -> None:
        self.boundary = boundary
        self.calls: list[SemanticReaderCall] = []
        self.records: list[dict[str, Any]] = []

    def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
        role = _reader_role(system_prompt)
        effective_system_prompt = system_prompt
        if role == "assistant_stances":
            effective_system_prompt += STANCE_TRAJECTORY_ADDENDUM
        raw_payload = self.boundary.run_json(effective_system_prompt, user_prompt)
        payload = _json_copy(raw_payload) if isinstance(raw_payload, dict) else {}
        ordinal = len(self.calls) + 1
        system_hash = _sha256_text(effective_system_prompt)
        user_hash = _sha256_text(user_prompt)
        call_hash = _sha256_text(
            f"{ordinal}|{role}|{system_hash}|{user_hash}"
        )[:12]
        identity = _boundary_identity(self.boundary)
        self.calls.append(
            SemanticReaderCall(
                call_id=f"semantic_reader_call_{ordinal:02d}_{call_hash}",
                ordinal=ordinal,
                reader_role=role,
                client_type=identity["client_type"],
                provider_client_type=identity["provider_client_type"],
                provider_name=identity["provider_name"],
                model=identity["model"],
                system_prompt_sha256=system_hash,
                user_prompt_sha256=user_hash,
                raw_payload=payload,
            )
        )
        return raw_payload

    def record_candidate(
        self,
        *,
        reader_role: str,
        family: str,
        proposal_index: int,
        raw_proposal: Any,
        mechanical_state: str,
        mechanical_reason: str,
        event: Any = None,
    ) -> None:
        """Append one proposal and its mechanical validation outcome."""

        call = _call_for_role(self.calls, reader_role)
        call_id = call.call_id if call else "missing_reader_call"
        candidate_id = _candidate_id(
            call_id=call_id,
            family=family,
            proposal_index=proposal_index,
            raw=raw_proposal,
        )
        snapshot = _event_snapshot(event)
        record: dict[str, Any] = {
            "candidate_id": candidate_id,
            "family": family,
            "reader_call_id": call_id,
            "proposal_index": proposal_index,
            "raw_proposal": _json_copy(raw_proposal),
            "raw_proposal_sha256": _sha256_json(raw_proposal),
            "state_history": [
                {
                    "state": "proposed",
                    "reason": "recorded_from_semantic_reader_output",
                    "actor": "semantic_reader",
                }
            ],
            "terminal_state": "",
            "terminal_reason": "",
            "current_view_eligible": False,
            "event_snapshot": snapshot,
        }

        if mechanical_state != "validated":
            _terminate(
                record,
                state=mechanical_state,
                reason=mechanical_reason,
                actor="deterministic_harness",
                eligible=False,
            )
            self.records.append(record)
            return

        if snapshot is None:
            _terminate(
                record,
                state="invalid_evidence",
                reason="validator_reported_success_without_event_snapshot",
                actor="deterministic_harness",
                eligible=False,
            )
            self.records.append(record)
            return

        if snapshot.get("routing_eligible", True) is not True:
            provenance = snapshot.get("provenance")
            reasons = (
                provenance.get("rejection_reasons", [])
                if isinstance(provenance, Mapping)
                else []
            )
            reason = ";".join(str(item) for item in reasons) or str(
                snapshot.get("provenance_status") or mechanical_reason
            )
            _terminate(
                record,
                state="not_supported_by_source",
                reason=reason,
                actor="deterministic_harness",
                eligible=False,
            )
            self.records.append(record)
            return

        _transition(
            record,
            state="validated",
            reason=mechanical_reason,
            actor="deterministic_harness",
        )
        terminal, reason, eligible, actor = _semantic_disposition(
            raw_proposal,
            snapshot,
        )
        _terminate(
            record,
            state=terminal,
            reason=reason,
            actor=actor,
            eligible=eligible,
        )
        self.records.append(record)

    def build_ledger(self, *, context: ConversationContext) -> dict[str, Any]:
        self._backfill_unrecorded_proposals()
        _mark_exact_duplicate_events(self.records)
        _mark_multiple_current_questions(self.records)
        expected = _expected_proposal_count(self.calls)
        metrics = _ledger_metrics(context, self.records, expected=expected)
        return {
            "schema_version": SEMANTIC_CANDIDATE_LEDGER_SCHEMA_VERSION,
            "authoritative_source": {
                "conversation_sha256": _conversation_sha256(context),
                "turn_count": len(context.turns),
                "contains_raw_conversation": False,
                "contains_source_excerpts": True,
            },
            "supported_candidate_states": list(SUPPORTED_CANDIDATE_STATES),
            "reader_calls": [call.public_dict() for call in self.calls],
            "candidates": self.records,
            "metrics": metrics,
            "non_claims": [
                "candidate_state_is_not_semantic_truth",
                "ledger_does_not_observe_unreturned_hypotheses",
                "missing_explicit_disposition_is_not_semantic_rejection",
                "validation_is_not_reasoning_quality_proof",
                "source_turn_coverage_is_not_semantic_completeness",
                "reader_agreement_is_not_correctness",
            ],
        }

    def _backfill_unrecorded_proposals(self) -> None:
        """Fail closed if a validator forgot to report a raw list item."""

        for family, (reader_role, raw_key) in _FAMILY_SPECS.items():
            call = _call_for_role(self.calls, reader_role)
            if call is None:
                continue
            raw_items = call.raw_payload.get(raw_key)
            if not isinstance(raw_items, list):
                continue
            recorded_hashes = Counter(
                str(record.get("raw_proposal_sha256") or "")
                for record in self.records
                if record.get("family") == family
                and record.get("reader_call_id") == call.call_id
            )
            for proposal_index, raw in enumerate(raw_items):
                raw_hash = _sha256_json(raw)
                if recorded_hashes[raw_hash] > 0:
                    recorded_hashes[raw_hash] -= 1
                    continue
                self.record_candidate(
                    reader_role=reader_role,
                    family=family,
                    proposal_index=proposal_index,
                    raw_proposal=raw,
                    mechanical_state="invalid_evidence",
                    mechanical_reason="validator_did_not_record_raw_proposal",
                )


def reconstruct_current_semantic_view(
    ledger: Mapping[str, Any],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    """Reconstruct the current view solely from terminal ledger records."""

    current = {family: [] for family in _FAMILY_SPECS}
    selected_ids = {family: [] for family in _FAMILY_SPECS}
    ambiguous_ids = {family: [] for family in _FAMILY_SPECS}
    for record in ledger.get("candidates", []):
        if not isinstance(record, Mapping):
            continue
        family = str(record.get("family") or "")
        terminal = str(record.get("terminal_state") or "")
        snapshot = record.get("event_snapshot")
        if (
            family not in current
            or terminal not in CURRENT_VIEW_STATES
            or record.get("current_view_eligible") is not True
            or not isinstance(snapshot, Mapping)
        ):
            continue
        event = _json_copy(snapshot)
        event["candidate_id"] = str(record.get("candidate_id") or "")
        event["candidate_state"] = terminal
        current[family].append(event)
        selected_ids[family].append(str(record.get("candidate_id") or ""))
        if terminal == "ambiguous_competing_read":
            ambiguous_ids[family].append(str(record.get("candidate_id") or ""))

    manifest = {
        "schema_version": CURRENT_SEMANTIC_VIEW_SCHEMA_VERSION,
        "reconstructible_from_candidate_ledger": True,
        "invalid_candidates_excluded": True,
        "selected_candidate_ids_by_family": selected_ids,
        "ambiguous_candidate_ids_by_family": ambiguous_ids,
        "event_count": sum(len(items) for items in current.values()),
        "view_sha256": _sha256_json(current),
    }
    return current, manifest


def _semantic_disposition(
    raw: Any,
    event: Mapping[str, Any],
) -> tuple[str, str, bool, str]:
    if isinstance(raw, Mapping):
        disposition = _text(raw.get("candidate_disposition")).lower()
        reason = _text(raw.get("disposition_reason"))
        if disposition and disposition not in SEMANTIC_READER_DISPOSITIONS:
            return (
                "invalid_evidence",
                "candidate_disposition_is_invalid",
                False,
                "deterministic_harness",
            )
        if disposition:
            return (
                disposition,
                reason or "semantic_reader_declared_candidate_disposition",
                disposition in CURRENT_VIEW_STATES,
                "semantic_reader",
            )
    if bool(event.get("kind_ambiguity")) or bool(event.get("relation_ambiguity")):
        return (
            "ambiguous_competing_read",
            "semantic_reader_marked_relation_or_kind_ambiguity",
            True,
            "semantic_reader",
        )
    return (
        "selected_for_current_view",
        "semantic_reader_emitted_validated_candidate_without_disposition",
        True,
        "semantic_reader",
    )


def _event_snapshot(event: Any) -> dict[str, Any] | None:
    if event is None:
        return None
    if hasattr(event, "to_dict"):
        payload = event.to_dict()
        provenance = getattr(event, "provenance", None)
        status = getattr(provenance, "evidence_status", None)
        eligible = getattr(provenance, "routing_eligible", None)
        if status is not None:
            payload["provenance_status"] = str(status)
            if isinstance(payload.get("provenance"), dict):
                payload["provenance"]["provenance_status"] = str(status)
        if eligible is not None:
            payload["routing_eligible"] = bool(eligible)
        else:
            payload.setdefault("routing_eligible", True)
        return _json_copy(payload)
    if isinstance(event, Mapping):
        return _json_copy(event)
    return None


def _transition(
    record: dict[str, Any], *, state: str, reason: str, actor: str
) -> None:
    if state not in SUPPORTED_CANDIDATE_STATES:
        raise ValueError(f"unsupported semantic candidate state: {state}")
    record["state_history"].append(
        {"state": state, "reason": reason, "actor": actor}
    )


def _terminate(
    record: dict[str, Any],
    *,
    state: str,
    reason: str,
    actor: str,
    eligible: bool,
) -> None:
    _transition(record, state=state, reason=reason, actor=actor)
    record["terminal_state"] = state
    record["terminal_reason"] = reason
    record["current_view_eligible"] = eligible


def _mark_multiple_current_questions(records: list[dict[str, Any]]) -> None:
    current = [
        record
        for record in records
        if record.get("family") == "question_events"
        and record.get("terminal_state") in CURRENT_VIEW_STATES
        and isinstance(record.get("event_snapshot"), Mapping)
        and record["event_snapshot"].get("kind") == "current"
    ]
    if len(current) < 2:
        return
    for record in current:
        if record.get("terminal_state") == "ambiguous_competing_read":
            continue
        _transition(
            record,
            state="ambiguous_competing_read",
            reason="multiple_reader_designated_current_questions",
            actor="deterministic_harness",
        )
        record["terminal_state"] = "ambiguous_competing_read"
        record["terminal_reason"] = "multiple_reader_designated_current_questions"
        record["current_view_eligible"] = True


def _mark_exact_duplicate_events(records: list[dict[str, Any]]) -> None:
    """Exclude repeated event identities without merging semantic roles."""

    seen: set[tuple[str, str]] = set()
    for record in records:
        if (
            record.get("terminal_state") not in CURRENT_VIEW_STATES
            or record.get("current_view_eligible") is not True
        ):
            continue
        snapshot = record.get("event_snapshot")
        if not isinstance(snapshot, Mapping):
            continue
        event_id = _text(snapshot.get("event_id"))
        if not event_id:
            continue
        identity = (_text(record.get("family")), event_id)
        if identity not in seen:
            seen.add(identity)
            continue
        _transition(
            record,
            state="duplicate_identity",
            reason="exact_event_identity_already_selected",
            actor="deterministic_harness",
        )
        record["terminal_state"] = "duplicate_identity"
        record["terminal_reason"] = "exact_event_identity_already_selected"
        record["current_view_eligible"] = False


def _ledger_metrics(
    context: ConversationContext,
    records: list[dict[str, Any]],
    *,
    expected: int,
) -> dict[str, Any]:
    terminal_counts = Counter(
        _text(record.get("terminal_state")) or "unterminated" for record in records
    )
    family_counts = Counter(_text(record.get("family")) or "unknown" for record in records)
    disposition_observability = _disposition_observability(records)
    referenced_turns: set[tuple[int, str]] = set()
    for record in records:
        snapshot = record.get("event_snapshot")
        if isinstance(snapshot, Mapping):
            referenced_turns.update(_event_turn_refs(snapshot))
    all_turns = {(turn.turn_index, turn.speaker) for turn in context.turns}
    return {
        "expected_proposal_count": expected,
        "proposal_count": len(records),
        "candidate_custody_complete": len(records) == expected,
        "terminal_record_count": sum(
            1 for record in records if _text(record.get("terminal_state"))
        ),
        "unterminated_record_count": terminal_counts.get("unterminated", 0),
        "current_view_candidate_count": sum(
            terminal_counts.get(state, 0) for state in CURRENT_VIEW_STATES
        ),
        "ambiguous_candidate_count": terminal_counts.get(
            "ambiguous_competing_read", 0
        ),
        "counts_by_terminal_state": dict(sorted(terminal_counts.items())),
        "counts_by_family": dict(sorted(family_counts.items())),
        "semantic_disposition_observability": disposition_observability,
        "source_turn_reference_coverage": (
            len(referenced_turns) / len(all_turns) if all_turns else 0.0
        ),
        "referenced_source_turns": [
            {"turn_index": turn, "speaker": speaker}
            for turn, speaker in sorted(referenced_turns)
        ],
        "unreferenced_source_turns": [
            {"turn_index": turn, "speaker": speaker}
            for turn, speaker in sorted(all_turns - referenced_turns)
        ],
    }


def _disposition_observability(records: list[dict[str, Any]]) -> dict[str, Any]:
    declared = Counter()
    observed = 0
    for record in records:
        raw = record.get("raw_proposal")
        value = (
            _text(raw.get("candidate_disposition")).lower()
            if isinstance(raw, Mapping)
            else ""
        )
        if not value:
            continue
        observed += 1
        declared[value] += 1
    total = len(records)
    return {
        "explicit_disposition_is_optional": True,
        "proposal_count": total,
        "explicit_disposition_count": observed,
        "unobserved_disposition_count": total - observed,
        "explicit_disposition_rate": observed / total if total else 0.0,
        "counts_by_declared_disposition": dict(sorted(declared.items())),
        "emitted_candidates_are_not_a_complete_hypothesis_set": True,
        "must_not_be_used_as_quality_label": True,
    }


def _event_turn_refs(event: Mapping[str, Any]) -> set[tuple[int, str]]:
    refs: set[tuple[int, str]] = set()
    source = event.get("source")
    if isinstance(source, Mapping):
        refs.add((int(source.get("turn_index") or 0), _text(source.get("speaker"))))
        return refs
    provenance = event.get("provenance")
    if not isinstance(provenance, Mapping):
        return refs
    span_ref = provenance.get("span_ref")
    if isinstance(span_ref, Mapping):
        refs.add((int(span_ref.get("turn_index") or 0), _text(span_ref.get("speaker"))))
    components = provenance.get("components")
    if isinstance(components, list):
        for component in components:
            span = component.get("span_ref") if isinstance(component, Mapping) else None
            if isinstance(span, Mapping):
                refs.add((int(span.get("turn_index") or 0), _text(span.get("speaker"))))
    return refs


def _expected_proposal_count(calls: list[SemanticReaderCall]) -> int:
    total = 0
    for family, (reader_role, raw_key) in _FAMILY_SPECS.items():
        del family
        call = _call_for_role(calls, reader_role)
        raw = call.raw_payload.get(raw_key) if call else None
        total += len(raw) if isinstance(raw, list) else 0
    return total


def _call_for_role(
    calls: list[SemanticReaderCall], role: str
) -> SemanticReaderCall | None:
    return next((call for call in calls if call.reader_role == role), None)


def _reader_role(system_prompt: str) -> str:
    if "LIVE CONSTRAINTS" in system_prompt:
        return "live_constraints"
    if "STANCE EVENT" in system_prompt:
        return "assistant_stances"
    if "DROPPED THREADS" in system_prompt:
        return "dropped_threads"
    if "QUESTION TRAJECTORY SEMANTICS" in system_prompt:
        return "question_trajectory"
    if "USER COUNTER-PRESSURE TEMPORAL SEMANTICS" in system_prompt:
        return "user_pressure"
    if "USER COUNTER-PRESSURE SEMANTICS" in system_prompt:
        return "user_pressure"
    if "USER PRESSURE SEMANTICS" in system_prompt:
        return "user_pressure"
    if "OPTION AND EVIDENCE SEMANTICS" in system_prompt:
        return "option_evidence"
    return "unknown"


def _boundary_identity(boundary: object) -> dict[str, str]:
    outer_type = f"{boundary.__class__.__module__}.{boundary.__class__.__qualname__}"
    provider = getattr(boundary, "boundary", boundary)
    provider_type = f"{provider.__class__.__module__}.{provider.__class__.__qualname__}"
    return {
        "client_type": outer_type,
        "provider_client_type": provider_type,
        "provider_name": _text(getattr(provider, "provider_name", ""))
        or "not_exposed_by_boundary_client",
        "model": _text(getattr(provider, "model", ""))
        or "not_exposed_by_boundary_client",
    }


def _candidate_id(
    *, call_id: str, family: str, proposal_index: int, raw: Any
) -> str:
    digest = _sha256_text(
        f"{call_id}|{family}|{proposal_index}|{_canonical_json(raw)}"
    )[:12]
    return f"candidate_{family}_{proposal_index:03d}_{digest}"


def _conversation_sha256(context: ConversationContext) -> str:
    body = "\n".join(
        f"{turn.turn_index}|{turn.speaker}|{turn.text}" for turn in context.turns
    )
    return _sha256_text(body)


def _sha256_json(value: Any) -> str:
    return _sha256_text(_canonical_json(value))


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def _json_copy(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False, default=str))


def _text(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""
