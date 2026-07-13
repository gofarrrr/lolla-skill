"""Shadow-only typed activation input for fact-free reasoning-pattern packets."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .companion import FingerprintMove, FingerprintPayload
from .reasoning_pattern_shadow import lint_routing_projection


class ReasoningPatternActivationShadowError(ValueError):
    pass


def fingerprint_from_reasoning_pattern_packet(packet: Mapping[str, Any]) -> FingerprintPayload:
    """Project controlled pattern nodes into an accepted fact-free typed input.

    This adapter is research-only. It includes controlled enum values only and
    intentionally leaves evidence quotes empty. It does not read pattern source
    refs, conversation text, role prose, or desired outcomes.
    """
    projection = packet.get("routing_projection", {})
    violations = lint_routing_projection(projection)
    if violations:
        raise ReasoningPatternActivationShadowError("reasoning pattern projection is invalid")
    moves = []
    for node in projection.get("pattern_nodes", []):
        mechanism = str(node["mechanism_id"])
        scope = str(node["subject_scope"])
        state = str(node["state"])
        moves.append(FingerprintMove(
            move_id=str(node["pattern_id"]),
            reasoning_move=mechanism.replace("_", " "),
            evidence_quotes=[],
            evidence_rationale=f"subject scope {scope.replace('_', ' ')}; pattern state {state.replace('_', ' ')}",
            confidence="provisional",
        ))
    return FingerprintPayload(raw=list(moves), validated=list(moves), dropped=[])


def fingerprint_fact_boundary(fingerprint: FingerprintPayload) -> dict[str, bool]:
    return {
        "all_evidence_quotes_empty": all(not move.evidence_quotes for move in fingerprint.validated),
        "controlled_reasoning_moves_only": True,
        "raw_role_prose_included": False,
        "entities_included": False,
        "case_quantities_included": False,
        "desired_outcome_included": False,
        "topic_labels_included": False,
    }
