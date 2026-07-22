from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.constitutional_graph_survival import (
    build_constitutional_graph_survival,
)
from engine.system_b.constitutional_pressure_survival import (
    build_constitutional_graph_survival_from_snapshot,
)
from engine.system_b.constitutional_pressure_planner import (
    ConstitutionalPressurePlanner,
    ConstitutionalPressurePolicy,
)
from engine.system_b.pipeline import SystemBPipeline
from engine.system_b.published_knowledge_substrate import PublishedKnowledgeSubstrate


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _candidates(model_ids: list[str]) -> list[dict[str, object]]:
    return [
        {
            "model_id": model_id,
            "model_name": model_id,
            "recall_source": "provider_free_policy_replay",
            "final_rank": index,
        }
        for index, model_id in enumerate(model_ids, start=1)
    ]


def _sha256_value(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def test_checked_in_policy_is_the_exact_named_planner_contract() -> None:
    policy = ConstitutionalPressurePolicy()
    checked_in = _json(ROOT / "data/curation/constitutional_pressure_policy_v1.json")

    assert policy.contract() == checked_in
    assert policy.policy_id == "lolla.constitutional_pressure_planner"
    assert policy.version == "1.0.0"
    assert policy.identity_sha256 == (
        "sha256:829bd0c086610dafabb09b5c941580efcc511396a3ed8c5d3ea3673e17031b10"
    )
    assert policy.direct_active_cap == 6
    assert policy.graph_relation_slots == ("antagonist", "tension", "ally")
    assert policy.expansion_seed_rule == "direct_active_only"
    assert policy.direction == "outgoing_authored_relations"
    assert policy.hop_depth == 1
    assert policy.affinity_used_for_admission is False
    assert policy.probabilistic_prefilter_used is False
    assert policy.provider_calls_allowed == 0


def test_planner_has_no_file_loader_compiler_embedding_or_provider_transport() -> None:
    source = inspect.getsource(sys.modules[ConstitutionalPressurePlanner.__module__])

    assert "PublishedKnowledgeSubstrate.open" not in source
    assert ".read_text(" not in source
    assert "KnowledgeCompiler" not in source
    assert "embeddings.db" not in source
    assert "run_json(" not in source


def test_snapshot_entrypoint_is_exactly_equal_to_legacy_payload_adapter() -> None:
    snapshot = PublishedKnowledgeSubstrate.open(ROOT).require_snapshot()
    knowledge = _json(ROOT / "data/knowledge_graph.json")
    relations = _json(ROOT / "data/relationship_graph.json")
    model_ids = sorted(knowledge["models"])[:60]
    candidates = _candidates(model_ids)

    legacy = build_constitutional_graph_survival(
        candidates=candidates,
        knowledge_graph=knowledge,
        relationship_graph=relations,
    )
    migrated = build_constitutional_graph_survival_from_snapshot(
        candidates=candidates,
        substrate=snapshot,
    )

    assert migrated == legacy
    assert migrated["portfolio_sha256"] == legacy["portfolio_sha256"]


def test_all_frozen_corpus_windows_replay_with_exact_current_policy() -> None:
    baseline = _json(ROOT / "docs/evals/lolla-graph-substrate-baseline-v1.json")
    frozen = baseline["current_portfolio_characterization"]
    snapshot = PublishedKnowledgeSubstrate.open(ROOT).require_snapshot()
    model_ids = sorted(snapshot.models)

    assert frozen["window_count"] == len(model_ids) - frozen["window_size"] + 1
    for expected in frozen["windows"]:
        start = expected["window_index"]
        window = model_ids[start : start + frozen["window_size"]]
        portfolio = build_constitutional_graph_survival_from_snapshot(
            candidates=_candidates(window),
            substrate=snapshot,
        )
        direct_active = [
            row["model_id"]
            for row in portfolio["active_pressure_items"]
            if row["candidate_origin"] == "direct_seed"
        ]
        graph_active = [
            {
                "model_id": row["model_id"],
                "selected_relation_slot": row["selected_relation_slot"],
                "admission_edge": row["graph_path"],
            }
            for row in portfolio["active_pressure_items"]
            if row["candidate_origin"] == "graph_expansion"
        ]
        direct_reserve = [
            row["model_id"]
            for row in portfolio["reserve_custody"]["direct_capacity_reserve"]
        ]
        graph_reserve = [
            row["model_id"]
            for row in portfolio["reserve_custody"]["graph_edge_reserve"]
        ]

        assert portfolio["portfolio_sha256"] == expected["portfolio_sha256"]
        assert direct_active == expected["direct_active_model_ids"]
        assert len(direct_reserve) == expected["direct_reserve_count"]
        assert _sha256_value(direct_reserve) == expected["direct_reserve_model_ids_sha256"]
        assert len(graph_reserve) == expected["graph_reserve_count"]
        assert _sha256_value(graph_reserve) == expected["graph_reserve_model_ids_sha256"]
        assert graph_active == [
            {
                "model_id": row["model_id"],
                "selected_relation_slot": row["selected_relation_slot"],
                "admission_edge": row["admission_edge"],
            }
            for row in expected["graph_active"]
        ]


def test_live_pipeline_builds_constitutional_pressure_before_verification() -> None:
    source = inspect.getsource(SystemBPipeline._run_companion)

    assert source.index("build_constitutional_graph_survival_from_snapshot") < source.index(
        "run_verification_call_with_diagnostics"
    )
