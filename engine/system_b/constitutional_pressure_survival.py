"""Current snapshot/planner entrypoint with frozen serializer compatibility.

The historical ``constitutional_graph_survival`` module is an exact frozen R3
input. This module owns the current live entrypoint without rewriting that
evidence. The named planner establishes the candidate policy first; the frozen
serializer then renders the compatible public portfolio and an exact identity
assertion prevents the compatibility adapter from drifting.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .constitutional_graph_survival import build_constitutional_graph_survival
from .constitutional_pressure_planner import ConstitutionalPressurePlanner
from .published_knowledge_substrate import PublishedKnowledgeSnapshot


def build_constitutional_graph_survival_from_snapshot(
    *,
    candidates: Sequence[Mapping[str, Any]],
    substrate: PublishedKnowledgeSnapshot,
    planner: ConstitutionalPressurePlanner | None = None,
) -> dict[str, Any]:
    """Plan from one snapshot, then render through the frozen compatible shape."""

    selected_planner = planner or ConstitutionalPressurePlanner()
    plan = selected_planner.plan(candidates=candidates, substrate=substrate)
    rendered = build_constitutional_graph_survival(
        candidates=plan.canonical_candidates,
        knowledge_graph=substrate.knowledge_graph_payload(),
        relationship_graph=substrate.relationship_graph_payload(),
        direct_active_cap=plan.policy.direct_active_cap,
        relation_slots=plan.policy.graph_relation_slots,
    )
    planned_direct = [
        str(row["model_id"]) for row in plan.direct_ledger["active_candidates"]
    ]
    planned_graph = [
        str(row["model_id"]) for row in plan.graph_ledger["active_candidates"]
    ]
    rendered_direct = [
        str(row["model_id"])
        for row in rendered["active_pressure_items"]
        if row["candidate_origin"] == "direct_seed"
    ]
    rendered_graph = [
        str(row["model_id"])
        for row in rendered["active_pressure_items"]
        if row["candidate_origin"] == "graph_expansion"
    ]
    if (rendered_direct, rendered_graph) != (planned_direct, planned_graph):
        raise RuntimeError("frozen portfolio serializer drifted from the named planner")
    return rendered
