"""The named, versioned policy for Lolla's live constitutional pressure set.

The planner consumes an already loaded published substrate. It owns direct
active allocation, the exact one-hop outgoing seed scope, graph slots, order,
deduplication, and reserve allocation. It does not load files, compile, rank by
affinity, interpret conversation meaning, call a provider, or disposition the
result.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
from typing import Any

from .published_knowledge_substrate import PublishedKnowledgeSnapshot
from .simulated_reliability_v1 import build_direct_ledger, build_graph_ledger


POLICY_ID = "lolla.constitutional_pressure_planner"
POLICY_VERSION = "1.0.0"
DEFAULT_DIRECT_ACTIVE_CAP = 6
DEFAULT_GRAPH_RELATION_SLOTS = ("antagonist", "tension", "ally")


@dataclass(frozen=True)
class ConstitutionalPressurePolicy:
    policy_id: str = POLICY_ID
    version: str = POLICY_VERSION
    direct_active_cap: int = DEFAULT_DIRECT_ACTIVE_CAP
    graph_relation_slots: tuple[str, ...] = DEFAULT_GRAPH_RELATION_SLOTS
    expansion_seed_rule: str = "direct_active_only"
    direction: str = "outgoing_authored_relations"
    hop_depth: int = 1
    direct_order: str = "input_recall_order_via_zero_padded_rank_mechanisms"
    graph_order: str = "relation_slot_then_source_id_then_target_id_ascending"
    direct_deduplication: str = "first_canonical_input_occurrence"
    graph_deduplication: str = "one_active_target_across_relation_slots"
    affinity_used_for_admission: bool = False
    probabilistic_prefilter_used: bool = False
    provider_calls_allowed: int = 0

    def contract(self) -> dict[str, Any]:
        return {
            "schema_version": "lolla.constitutional_pressure_policy.v1",
            "policy_id": self.policy_id,
            "version": self.version,
            "direct_active_cap": self.direct_active_cap,
            "graph_relation_slots": list(self.graph_relation_slots),
            "expansion_seed_rule": self.expansion_seed_rule,
            "direction": self.direction,
            "hop_depth": self.hop_depth,
            "direct_order": self.direct_order,
            "graph_order": self.graph_order,
            "direct_deduplication": self.direct_deduplication,
            "graph_deduplication": self.graph_deduplication,
            "affinity_used_for_admission": self.affinity_used_for_admission,
            "probabilistic_prefilter_used": self.probabilistic_prefilter_used,
            "provider_calls_allowed": self.provider_calls_allowed,
            "reserve_policy": {
                "direct_capacity_overflow_preserved": True,
                "graph_capacity_and_direct_duplicates_preserved": True,
                "semantic_rejection_performed": False,
            },
            "non_claims": [
                "active_admission_is_not_relevance_proof",
                "reserve_is_not_semantic_rejection",
                "one_hop_path_is_not_transitive_meaning",
            ],
        }

    @property
    def identity_sha256(self) -> str:
        payload = json.dumps(
            self.contract(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return "sha256:" + hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class ConstitutionalPressurePlan:
    policy: ConstitutionalPressurePolicy
    policy_sha256: str
    substrate_release_id: str
    models: Mapping[str, Any]
    relationship_edges: tuple[Mapping[str, Any], ...]
    canonical_candidates: tuple[Mapping[str, Any], ...]
    first_input_index: Mapping[str, int]
    malformed_candidates: tuple[Mapping[str, Any], ...]
    duplicate_candidates: tuple[Mapping[str, Any], ...]
    direct_ledger: Mapping[str, Any]
    graph_ledger: Mapping[str, Any]
    provider_calls: int = 0


class ConstitutionalPressurePlanner:
    def __init__(self, policy: ConstitutionalPressurePolicy | None = None) -> None:
        self.policy = policy or ConstitutionalPressurePolicy()

    def plan(
        self,
        *,
        candidates: Sequence[Mapping[str, Any]],
        substrate: PublishedKnowledgeSnapshot,
    ) -> ConstitutionalPressurePlan:
        return self.plan_records(
            candidates=candidates,
            models={model_id: model.payload for model_id, model in substrate.models.items()},
            relationship_edges=tuple(relation.payload for relation in substrate.relations),
            substrate_release_id=substrate.release_id,
        )

    def plan_records(
        self,
        *,
        candidates: Sequence[Mapping[str, Any]],
        models: Mapping[str, Any],
        relationship_edges: Sequence[Mapping[str, Any]],
        substrate_release_id: str = "legacy_raw_payload_adapter",
    ) -> ConstitutionalPressurePlan:
        if not isinstance(models, Mapping) or not models:
            raise ValueError("canonical model registry is unavailable")
        if self.policy.direct_active_cap < 1:
            raise ValueError("direct_active_cap must be positive")

        canonical_ids = set(models)
        malformed: list[dict[str, Any]] = []
        duplicates: list[dict[str, Any]] = []
        canonical_candidates: list[dict[str, Any]] = []
        first_index: dict[str, int] = {}
        for index, raw in enumerate(candidates):
            model_id = _text(raw.get("model_id")) if isinstance(raw, Mapping) else ""
            if not model_id or model_id not in canonical_ids:
                malformed.append(
                    {
                        "input_index": index,
                        "raw_model_id": model_id,
                        "custody_status": "malformed_or_noncanonical_before_admission",
                        "semantic_rejection_performed": False,
                    }
                )
                continue
            if model_id in first_index:
                duplicates.append(
                    {
                        "model_id": model_id,
                        "input_index": index,
                        "first_input_index": first_index[model_id],
                        "custody_status": "duplicate_of_direct_candidate",
                        "semantic_rejection_performed": False,
                    }
                )
                continue
            first_index[model_id] = index
            canonical_candidates.append(dict(raw))

        mechanism_ids = [
            f"lane2_recall_rank:{index:03d}" for index in range(len(canonical_candidates))
        ]
        mechanism_models = {
            mechanism_id: [_text(candidate.get("model_id"))]
            for mechanism_id, candidate in zip(mechanism_ids, canonical_candidates)
        }
        direct = build_direct_ledger(
            unresolved_mechanism_ids=mechanism_ids,
            mechanism_seed_models=mechanism_models,
            canonical_model_ids=canonical_ids,
            active_cap=self.policy.direct_active_cap,
        )
        graph = build_graph_ledger(
            direct_ledger=direct,
            relation_graph=relationship_edges,
            canonical_model_ids=canonical_ids,
            slot_order=self.policy.graph_relation_slots,
        )
        return ConstitutionalPressurePlan(
            policy=self.policy,
            policy_sha256=self.policy.identity_sha256,
            substrate_release_id=substrate_release_id,
            models=models,
            relationship_edges=tuple(relationship_edges),
            canonical_candidates=tuple(canonical_candidates),
            first_input_index=dict(first_index),
            malformed_candidates=tuple(malformed),
            duplicate_candidates=tuple(duplicates),
            direct_ledger=direct,
            graph_ledger=graph,
            provider_calls=0,
        )


def _text(value: Any) -> str:
    return str(value or "").strip()
