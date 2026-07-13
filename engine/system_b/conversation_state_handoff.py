"""Minimal, source-linked conversation-state handoff (research shadow only).

The handoff preserves case-local position ownership, thread disposition, and
load-bearing claims for audit/navigation.  It deliberately cannot route facts
to the deterministic graph.  Semantic interpretation belongs to an LLM or
human; deterministic code validates only shape, identity, controlled
vocabularies, source references, and the routing boundary.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from typing import Any


SCHEMA_VERSION = "lolla.conversation_state_handoff.v1"
PROJECTION_SCHEMA_VERSION = "lolla.conversation_state_routing_boundary.v1"
HANDOFF_STATUSES = {"reviewed_shadow", "model_probe_unreviewed"}

OWNERSHIP = {"user", "assistant", "joint", "unclear"}
POSITION_STATES = {
    "proposed",
    "conditional",
    "accepted",
    "rejected",
    "deferred",
    "unresolved",
}
CONTRIBUTION_ROLES = {
    "originated",
    "developed",
    "qualified",
    "challenged",
    "accepted",
}
THREAD_DISPOSITIONS = {
    "open_unaddressed",
    "addressed_unresolved",
    "resolved",
    "superseded",
    "genuinely_dropped",
    "unclear",
}
THREAD_ENGAGEMENTS = {"acknowledged", "substantive", "resolved"}
CONSTRAINT_STATES = {"active", "modified", "resolved", "unclear"}
CLAIM_MODES = {
    "stated_condition",
    "reported_statement",
    "possibility",
    "preference",
    "concern",
    "inference",
    "mixed",
}
EVIDENCE_MODES = {"exact_span", "multi_turn_derivation"}

REQUIRED_NON_CLAIMS = {
    "state_items_are_probabilistic_or_human_interpretations",
    "source_grounding_is_not_semantic_correctness",
    "conversation_state_is_not_reasoning_pattern",
    "facts_cannot_seed_graph_directly",
    "not_runtime_integration_authority",
}

_TOP_FIELDS = {
    "schema_version",
    "status",
    "case_id",
    "source",
    "decision_summary",
    "positions",
    "threads",
    "constraints",
    "routing_boundary",
    "non_claims",
}
_SOURCE_FIELDS = {"path", "sha256", "message_count"}
_DECISION_FIELDS = {"text", "evidence_mode", "source_evidence"}
_EVIDENCE_FIELDS = {"speaker", "turn_index", "quote"}
_POSITION_FIELDS = {
    "position_id",
    "text",
    "ownership",
    "state",
    "evidence_mode",
    "contributions",
    "graph_routing_eligible",
}
_CONTRIBUTION_FIELDS = {"speaker", "turn_index", "role", "quote"}
_THREAD_FIELDS = {
    "thread_id",
    "text",
    "disposition",
    "introduced",
    "responses",
    "latest_ref",
    "superseded_by",
    "evidence_mode",
    "graph_routing_eligible",
}
_RESPONSE_FIELDS = {"speaker", "turn_index", "engagement", "quote"}
_CONSTRAINT_FIELDS = {
    "constraint_id",
    "text",
    "state",
    "claim_mode",
    "evidence_mode",
    "source_evidence",
    "graph_routing_eligible",
}
_ROUTING_BOUNDARY = {
    "contains_case_context": True,
    "direct_graph_routing_allowed": False,
    "reasoning_pattern_abstraction_required": True,
    "runtime_integration": False,
}

_TURN_PATTERN = re.compile(
    r"\[Turn\s+(\d+)\]\s+(USER|ASSISTANT):\s*\n(.*?)(?=\n\[Turn\s+\d+\]\s+(?:USER|ASSISTANT):|\Z)",
    re.DOTALL,
)


class ConversationStateHandoffError(ValueError):
    """Raised when a shadow handoff violates deterministic custody rules."""


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _turn_map(source_text: str) -> dict[tuple[int, str], str]:
    turns: dict[tuple[int, str], str] = {}
    for match in _TURN_PATTERN.finditer(source_text):
        key = (int(match.group(1)), match.group(2).lower())
        turns[key] = match.group(3).strip()
    return turns


def _issue(code: str, pointer: str, detail: str = "") -> dict[str, str]:
    result = {"code": code, "json_pointer": pointer}
    if detail:
        result["detail"] = detail
    return result


def _is_array(value: object) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes))


def _validate_evidence(
    value: object,
    *,
    pointer: str,
    turns: Mapping[tuple[int, str], str],
    violations: list[dict[str, str]],
) -> None:
    if not isinstance(value, Mapping) or set(value) != _EVIDENCE_FIELDS:
        violations.append(_issue("source_evidence_shape_invalid", pointer))
        return
    speaker = str(value.get("speaker", ""))
    try:
        turn_index = int(value.get("turn_index", -1))
    except (TypeError, ValueError):
        turn_index = -1
    quote = str(value.get("quote", ""))
    source_turn = turns.get((turn_index, speaker))
    if source_turn is None:
        violations.append(_issue("source_turn_not_found", pointer))
    elif not quote or quote not in source_turn:
        violations.append(_issue("source_quote_not_exact", pointer + "/quote"))


def _validate_evidence_array(
    value: object,
    *,
    pointer: str,
    turns: Mapping[tuple[int, str], str],
    violations: list[dict[str, str]],
    require_nonempty: bool = True,
) -> None:
    if not _is_array(value):
        violations.append(_issue("source_evidence_not_array", pointer))
        return
    if require_nonempty and not value:
        violations.append(_issue("source_evidence_empty", pointer))
    for index, item in enumerate(value):
        _validate_evidence(
            item,
            pointer=f"{pointer}/{index}",
            turns=turns,
            violations=violations,
        )


def validate_conversation_state_handoff(
    payload: object,
    *,
    source_text: str,
) -> list[dict[str, str]]:
    """Return deterministic custody violations without judging semantics."""

    violations: list[dict[str, str]] = []
    if not isinstance(payload, Mapping):
        return [_issue("handoff_not_object", "")]
    if set(payload) != _TOP_FIELDS:
        violations.append(_issue("handoff_fields_invalid", ""))
    if payload.get("schema_version") != SCHEMA_VERSION:
        violations.append(_issue("schema_version_invalid", "/schema_version"))
    if payload.get("status") not in HANDOFF_STATUSES:
        violations.append(_issue("status_invalid", "/status"))
    if not str(payload.get("case_id", "")).strip():
        violations.append(_issue("case_id_missing", "/case_id"))

    turns = _turn_map(source_text)
    source = payload.get("source")
    if not isinstance(source, Mapping) or set(source) != _SOURCE_FIELDS:
        violations.append(_issue("source_shape_invalid", "/source"))
    else:
        if source.get("sha256") != _sha256_text(source_text):
            violations.append(_issue("source_hash_mismatch", "/source/sha256"))
        if int(source.get("message_count", -1) or -1) != len(turns):
            violations.append(_issue("source_message_count_mismatch", "/source/message_count"))
        if not str(source.get("path", "")).strip():
            violations.append(_issue("source_path_missing", "/source/path"))

    decision = payload.get("decision_summary")
    if not isinstance(decision, Mapping) or set(decision) != _DECISION_FIELDS:
        violations.append(_issue("decision_summary_shape_invalid", "/decision_summary"))
    else:
        if not str(decision.get("text", "")).strip():
            violations.append(_issue("decision_summary_missing", "/decision_summary/text"))
        if decision.get("evidence_mode") not in EVIDENCE_MODES:
            violations.append(_issue("evidence_mode_invalid", "/decision_summary/evidence_mode"))
        _validate_evidence_array(
            decision.get("source_evidence"),
            pointer="/decision_summary/source_evidence",
            turns=turns,
            violations=violations,
        )

    positions = payload.get("positions")
    position_ids: list[str] = []
    if not _is_array(positions):
        violations.append(_issue("positions_not_array", "/positions"))
    else:
        for index, row in enumerate(positions):
            pointer = f"/positions/{index}"
            if not isinstance(row, Mapping) or set(row) != _POSITION_FIELDS:
                violations.append(_issue("position_shape_invalid", pointer))
                continue
            position_id = str(row.get("position_id", ""))
            position_ids.append(position_id)
            if not position_id or not str(row.get("text", "")).strip():
                violations.append(_issue("position_identity_or_text_missing", pointer))
            ownership = row.get("ownership")
            if ownership not in OWNERSHIP:
                violations.append(_issue("position_ownership_invalid", pointer + "/ownership"))
            if row.get("state") not in POSITION_STATES:
                violations.append(_issue("position_state_invalid", pointer + "/state"))
            if row.get("evidence_mode") not in EVIDENCE_MODES:
                violations.append(_issue("evidence_mode_invalid", pointer + "/evidence_mode"))
            if row.get("graph_routing_eligible") is not False:
                violations.append(_issue("case_state_graph_routing_forbidden", pointer + "/graph_routing_eligible"))
            contributions = row.get("contributions")
            speakers: set[str] = set()
            if not _is_array(contributions) or not contributions:
                violations.append(_issue("position_contributions_missing", pointer + "/contributions"))
                continue
            for c_index, contribution in enumerate(contributions):
                c_pointer = f"{pointer}/contributions/{c_index}"
                if not isinstance(contribution, Mapping) or set(contribution) != _CONTRIBUTION_FIELDS:
                    violations.append(_issue("contribution_shape_invalid", c_pointer))
                    continue
                speaker = str(contribution.get("speaker", ""))
                speakers.add(speaker)
                if contribution.get("role") not in CONTRIBUTION_ROLES:
                    violations.append(_issue("contribution_role_invalid", c_pointer + "/role"))
                _validate_evidence(
                    {key: contribution.get(key) for key in _EVIDENCE_FIELDS},
                    pointer=c_pointer,
                    turns=turns,
                    violations=violations,
                )
            if ownership == "joint" and not {"user", "assistant"} <= speakers:
                violations.append(_issue("joint_position_requires_both_speakers", pointer + "/contributions"))
            if ownership in {"user", "assistant"} and ownership not in speakers:
                violations.append(_issue("owned_position_missing_owner_evidence", pointer + "/contributions"))
    if len(position_ids) != len(set(position_ids)):
        violations.append(_issue("position_ids_not_unique", "/positions"))

    threads = payload.get("threads")
    thread_ids: list[str] = []
    if not _is_array(threads):
        violations.append(_issue("threads_not_array", "/threads"))
    else:
        for index, row in enumerate(threads):
            pointer = f"/threads/{index}"
            if not isinstance(row, Mapping) or set(row) != _THREAD_FIELDS:
                violations.append(_issue("thread_shape_invalid", pointer))
                continue
            thread_id = str(row.get("thread_id", ""))
            thread_ids.append(thread_id)
            if not thread_id or not str(row.get("text", "")).strip():
                violations.append(_issue("thread_identity_or_text_missing", pointer))
            disposition = row.get("disposition")
            if disposition not in THREAD_DISPOSITIONS:
                violations.append(_issue("thread_disposition_invalid", pointer + "/disposition"))
            if row.get("evidence_mode") not in EVIDENCE_MODES:
                violations.append(_issue("evidence_mode_invalid", pointer + "/evidence_mode"))
            if row.get("graph_routing_eligible") is not False:
                violations.append(_issue("case_state_graph_routing_forbidden", pointer + "/graph_routing_eligible"))
            _validate_evidence(
                row.get("introduced"), pointer=pointer + "/introduced", turns=turns, violations=violations
            )
            _validate_evidence(
                row.get("latest_ref"), pointer=pointer + "/latest_ref", turns=turns, violations=violations
            )
            responses = row.get("responses")
            engagements: list[str] = []
            if not _is_array(responses):
                violations.append(_issue("thread_responses_not_array", pointer + "/responses"))
                responses = []
            for r_index, response in enumerate(responses):
                r_pointer = f"{pointer}/responses/{r_index}"
                if not isinstance(response, Mapping) or set(response) != _RESPONSE_FIELDS:
                    violations.append(_issue("thread_response_shape_invalid", r_pointer))
                    continue
                engagement = str(response.get("engagement", ""))
                engagements.append(engagement)
                if engagement not in THREAD_ENGAGEMENTS:
                    violations.append(_issue("thread_engagement_invalid", r_pointer + "/engagement"))
                _validate_evidence(
                    {key: response.get(key) for key in _EVIDENCE_FIELDS},
                    pointer=r_pointer,
                    turns=turns,
                    violations=violations,
                )
            if disposition == "open_unaddressed" and responses:
                violations.append(_issue("unaddressed_thread_cannot_have_responses", pointer + "/responses"))
            if disposition == "addressed_unresolved" and "substantive" not in engagements:
                violations.append(_issue("addressed_thread_requires_substantive_response", pointer + "/responses"))
            if disposition == "resolved" and "resolved" not in engagements:
                violations.append(_issue("resolved_thread_requires_resolution_response", pointer + "/responses"))
            if disposition == "genuinely_dropped" and any(
                item in {"substantive", "resolved"} for item in engagements
            ):
                violations.append(_issue("dropped_thread_cannot_have_substantive_response", pointer + "/responses"))
            superseded_by = row.get("superseded_by")
            if disposition == "superseded" and not str(superseded_by or "").strip():
                violations.append(_issue("superseded_thread_requires_replacement", pointer + "/superseded_by"))
            if disposition != "superseded" and superseded_by is not None:
                violations.append(_issue("non_superseded_thread_cannot_name_replacement", pointer + "/superseded_by"))
    if len(thread_ids) != len(set(thread_ids)):
        violations.append(_issue("thread_ids_not_unique", "/threads"))

    constraints = payload.get("constraints")
    constraint_ids: list[str] = []
    if not _is_array(constraints):
        violations.append(_issue("constraints_not_array", "/constraints"))
    else:
        for index, row in enumerate(constraints):
            pointer = f"/constraints/{index}"
            if not isinstance(row, Mapping) or set(row) != _CONSTRAINT_FIELDS:
                violations.append(_issue("constraint_shape_invalid", pointer))
                continue
            constraint_id = str(row.get("constraint_id", ""))
            constraint_ids.append(constraint_id)
            if not constraint_id or not str(row.get("text", "")).strip():
                violations.append(_issue("constraint_identity_or_text_missing", pointer))
            if row.get("state") not in CONSTRAINT_STATES:
                violations.append(_issue("constraint_state_invalid", pointer + "/state"))
            if row.get("claim_mode") not in CLAIM_MODES:
                violations.append(_issue("constraint_claim_mode_invalid", pointer + "/claim_mode"))
            if row.get("evidence_mode") not in EVIDENCE_MODES:
                violations.append(_issue("evidence_mode_invalid", pointer + "/evidence_mode"))
            if row.get("graph_routing_eligible") is not False:
                violations.append(_issue("case_state_graph_routing_forbidden", pointer + "/graph_routing_eligible"))
            _validate_evidence_array(
                row.get("source_evidence"),
                pointer=pointer + "/source_evidence",
                turns=turns,
                violations=violations,
            )
    if len(constraint_ids) != len(set(constraint_ids)):
        violations.append(_issue("constraint_ids_not_unique", "/constraints"))

    if payload.get("routing_boundary") != _ROUTING_BOUNDARY:
        violations.append(_issue("routing_boundary_invalid", "/routing_boundary"))
    non_claims = payload.get("non_claims")
    if not _is_array(non_claims) or not REQUIRED_NON_CLAIMS <= set(non_claims):
        violations.append(_issue("required_non_claims_missing", "/non_claims"))
    return violations


def assert_valid_conversation_state_handoff(
    payload: object,
    *,
    source_text: str,
) -> None:
    violations = validate_conversation_state_handoff(payload, source_text=source_text)
    if violations:
        raise ConversationStateHandoffError(_canonical_json(violations))


def build_fact_free_routing_boundary(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Seal an empty graph projection; semantic abstraction is still required."""

    if payload.get("routing_boundary") != _ROUTING_BOUNDARY:
        raise ConversationStateHandoffError("invalid routing boundary")
    return {
        "schema_version": PROJECTION_SCHEMA_VERSION,
        "state_packet_sha256": _sha256_text(_canonical_json(payload)),
        "direct_graph_seed_count": 0,
        "reasoning_pattern_inputs": [],
        "contains_case_context": False,
        "reasoning_pattern_abstraction_required": True,
        "runtime_integration": False,
        "non_claims": [
            "empty_projection_is_not_semantic_stand_down",
            "conversation_state_is_not_graph_applicability",
            "not_runtime_integration_authority",
        ],
    }
