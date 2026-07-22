from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.system_b.constitutional_graph_survival import (  # noqa: E402
    build_constitutional_graph_survival,
)
from engine.system_b.source_custody import build_source_custody_report  # noqa: E402


SCHEMA_VERSION = "lolla.graph_substrate_baseline.v1"
DEFAULT_REGISTER = Path("docs/evals/lolla-graph-substrate-baseline-v1.json")
ARTIFACT_PATHS = {
    "knowledge_graph": Path("data/knowledge_graph.json"),
    "relationship_graph": Path("data/relationship_graph.json"),
    "source_manifest": Path("data/model_sources/manifest.json"),
    "activation_embeddings": Path("data/embeddings.db"),
    "v60_affordances": Path(
        "data/compiled/model_affordances/affordances_v60.json"
    ),
}
RELATION_TYPE_TO_COMPACT_TYPE = {
    "ally": "ally",
    "antagonist": "antagonist",
    "tension": "structured_tension",
}
WINDOW_SIZE = 60


class GraphSubstrateBaselineError(RuntimeError):
    pass


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _sha256_value(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _relation_identity(edge: Mapping[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("source_model_id", "")).strip(),
        str(edge.get("target_model_id", "")).strip(),
        str(edge.get("edge_type", "")).strip(),
    )


def _compact_relation_identity(edge: Mapping[str, Any]) -> tuple[str, str, str] | None:
    edge_type = str(edge.get("type", "")).strip()
    rich_type = next(
        (
            relation_type
            for relation_type, compact_type in RELATION_TYPE_TO_COMPACT_TYPE.items()
            if compact_type == edge_type
        ),
        None,
    )
    if rich_type is None:
        return None
    return (
        str(edge.get("source", "")).strip(),
        str(edge.get("target", "")).strip(),
        rich_type,
    )


def _baseline_candidates(model_ids: Sequence[str]) -> list[dict[str, Any]]:
    return [
        {
            "model_id": model_id,
            "model_name": model_id,
            "recall_source": "provider_free_graph_substrate_baseline",
            "final_rank": index,
        }
        for index, model_id in enumerate(model_ids, start=1)
    ]


def _portfolio_sweep(
    *,
    model_ids: list[str],
    knowledge_graph: Mapping[str, Any],
    relationship_graph: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    if len(model_ids) < WINDOW_SIZE:
        raise GraphSubstrateBaselineError("model registry is smaller than sweep window")

    windows: list[dict[str, Any]] = []
    total_graph_active = 0
    active_with_multiple_paths = 0
    additional_paths_not_on_outer_active_item = 0

    for start in range(len(model_ids) - WINDOW_SIZE + 1):
        window_ids = model_ids[start : start + WINDOW_SIZE]
        portfolio = build_constitutional_graph_survival(
            candidates=_baseline_candidates(window_ids),
            knowledge_graph=knowledge_graph,
            relationship_graph=relationship_graph,
        )
        active_items = list(portfolio["active_pressure_items"])
        direct_active_ids = [
            str(item["model_id"])
            for item in active_items
            if item["candidate_origin"] == "direct_seed"
        ]
        direct_active_set = set(direct_active_ids)
        graph_active_items = [
            item for item in active_items if item["candidate_origin"] == "graph_expansion"
        ]

        graph_rows: list[dict[str, Any]] = []
        for item in graph_active_items:
            model_id = str(item["model_id"])
            exact_paths = sorted(
                (
                    {
                        "source_model_id": str(edge.get("source_model_id", "")),
                        "target_model_id": str(edge.get("target_model_id", "")),
                        "edge_type": str(edge.get("edge_type", "")),
                    }
                    for edge in relationship_graph
                    if str(edge.get("source_model_id", "")) in direct_active_set
                    and str(edge.get("target_model_id", "")) == model_id
                    and str(edge.get("edge_type", ""))
                    in RELATION_TYPE_TO_COMPACT_TYPE
                ),
                key=lambda edge: (
                    edge["edge_type"],
                    edge["source_model_id"],
                    edge["target_model_id"],
                ),
            )
            path_count = len(exact_paths)
            if path_count < 1:
                raise GraphSubstrateBaselineError(
                    f"active graph target {model_id} has no exact source path"
                )
            total_graph_active += 1
            if path_count > 1:
                active_with_multiple_paths += 1
            additional_paths_not_on_outer_active_item += path_count - 1
            graph_rows.append(
                {
                    "model_id": model_id,
                    "selected_relation_slot": item["selected_relation_slot"],
                    "admission_edge": item["graph_path"],
                    "exact_path_count": path_count,
                    "exact_paths_sha256": _sha256_value(exact_paths),
                }
            )

        reserve = portfolio["reserve_custody"]
        direct_reserve_ids = [
            str(item["model_id"])
            for item in reserve["direct_capacity_reserve"]
        ]
        graph_reserve_ids = [
            str(item["model_id"])
            for item in reserve["graph_edge_reserve"]
        ]
        windows.append(
            {
                "window_index": start,
                "input_first_model_id": window_ids[0],
                "input_last_model_id": window_ids[-1],
                "input_model_ids_sha256": _sha256_value(window_ids),
                "portfolio_sha256": portfolio["portfolio_sha256"],
                "direct_active_model_ids": direct_active_ids,
                "direct_reserve_count": len(direct_reserve_ids),
                "direct_reserve_model_ids_sha256": _sha256_value(direct_reserve_ids),
                "graph_active": graph_rows,
                "graph_reserve_count": len(graph_reserve_ids),
                "graph_reserve_model_ids_sha256": _sha256_value(graph_reserve_ids),
            }
        )

    return {
        "window_size": WINDOW_SIZE,
        "window_count": len(windows),
        "ordering": "canonical_model_id_ascending_contiguous_windows",
        "graph_active_count": total_graph_active,
        "graph_active_with_multiple_exact_paths_count": active_with_multiple_paths,
        "additional_exact_paths_not_on_outer_active_item_count": (
            additional_paths_not_on_outer_active_item
        ),
        "windows": windows,
    }


def build_graph_substrate_baseline(root: Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(root).resolve()
    resolved_artifacts = {
        role: root / relative_path for role, relative_path in ARTIFACT_PATHS.items()
    }
    missing = [
        str(ARTIFACT_PATHS[role])
        for role, path in resolved_artifacts.items()
        if not path.is_file()
    ]
    if missing:
        raise GraphSubstrateBaselineError(
            "required baseline artifacts are missing: " + ", ".join(missing)
        )

    knowledge_graph = _load_json(resolved_artifacts["knowledge_graph"])
    relationship_graph = _load_json(resolved_artifacts["relationship_graph"])
    if not isinstance(knowledge_graph, Mapping):
        raise GraphSubstrateBaselineError("knowledge graph must be an object")
    if not isinstance(relationship_graph, list) or not all(
        isinstance(item, Mapping) for item in relationship_graph
    ):
        raise GraphSubstrateBaselineError("relationship graph must be an edge list")

    models = knowledge_graph.get("models")
    tendencies = knowledge_graph.get("tendencies")
    compact_edges = knowledge_graph.get("edges")
    if not isinstance(models, Mapping) or not isinstance(tendencies, Mapping):
        raise GraphSubstrateBaselineError("knowledge graph registries are invalid")
    if not isinstance(compact_edges, list) or not all(
        isinstance(item, Mapping) for item in compact_edges
    ):
        raise GraphSubstrateBaselineError("knowledge graph edges are invalid")

    model_ids = sorted(str(model_id) for model_id in models)
    canonical_ids = set(model_ids)
    rich_identities = [_relation_identity(edge) for edge in relationship_graph]
    if any(not all(identity) for identity in rich_identities):
        raise GraphSubstrateBaselineError("relationship graph has blank identity fields")
    if len(rich_identities) != len(set(rich_identities)):
        raise GraphSubstrateBaselineError("relationship graph identities are duplicated")
    noncanonical = sorted(
        {
            endpoint
            for source, target, _ in rich_identities
            for endpoint in (source, target)
            if endpoint not in canonical_ids
        }
    )
    if noncanonical:
        raise GraphSubstrateBaselineError(
            "relationship graph has noncanonical endpoints: " + ", ".join(noncanonical)
        )
    self_edges = sorted(
        f"{source}->{target}:{edge_type}"
        for source, target, edge_type in rich_identities
        if source == target
    )
    if self_edges:
        raise GraphSubstrateBaselineError("relationship graph contains self-edges")

    compact_relation_identities = {
        identity
        for edge in compact_edges
        if (identity := _compact_relation_identity(edge)) is not None
    }
    if compact_relation_identities != set(rich_identities):
        raise GraphSubstrateBaselineError(
            "compact and rich relationship projections do not reconcile"
        )

    source_report = build_source_custody_report(root)
    if any(
        source_report[field]
        for field in (
            "missing_manifest_model_ids",
            "manifest_model_ids_outside_runtime_graph",
            "duplicate_manifest_model_ids",
            "missing_local_source_model_ids",
            "source_file_mismatch_model_ids",
            "local_sha256_mismatch_model_ids",
            "local_byte_mismatch_model_ids",
            "missing_canonical_source_model_ids",
            "canonical_sha256_mismatch_model_ids",
        )
    ):
        raise GraphSubstrateBaselineError("repository-local source custody is invalid")

    relation_type_counts = Counter(identity[2] for identity in rich_identities)
    compact_type_counts = Counter(str(edge.get("type", "")) for edge in compact_edges)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "complete",
        "created_date": "2026-07-22",
        "evidence_type": "provider_free_local_structural_baseline",
        "repository_authority": {
            "status": "sole_active_authority",
            "canonical_source_root": "data/model_sources",
            "canonical_source_authority": source_report[
                "canonical_source_authority"
            ],
            "external_runtime_dependency": False,
        },
        "artifacts": {
            role: {
                "path": str(ARTIFACT_PATHS[role]),
                "sha256": _sha256_file(path),
                "bytes": path.stat().st_size,
            }
            for role, path in sorted(resolved_artifacts.items())
        },
        "source_custody": source_report,
        "graph_inventory": {
            "canonical_model_count": len(model_ids),
            "canonical_model_ids_sha256": _sha256_value(model_ids),
            "tendency_count": len(tendencies),
            "compact_edge_count": len(compact_edges),
            "compact_edge_type_counts": dict(sorted(compact_type_counts.items())),
            "rich_relation_count": len(relationship_graph),
            "rich_relation_type_counts": dict(sorted(relation_type_counts.items())),
            "unique_rich_relation_identity_count": len(set(rich_identities)),
            "self_edge_count": 0,
            "noncanonical_endpoint_count": 0,
            "compact_rich_relation_identity_match": True,
        },
        "current_portfolio_characterization": _portfolio_sweep(
            model_ids=model_ids,
            knowledge_graph=knowledge_graph,
            relationship_graph=relationship_graph,
        ),
        "non_claims": [
            "structural_validity_is_not_semantic_correctness",
            "graph_reachability_is_not_relevance",
            "convergent_paths_are_not_truth_or_importance",
            "portfolio_admission_is_not_best_model_selection",
            "this_baseline_is_not_real_user_usefulness_evidence",
        ],
    }


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build or validate the provider-free graph substrate baseline."
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_REGISTER)
    parser.add_argument("--register", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    payload = build_graph_substrate_baseline(root)
    register = args.register or args.output
    register = register if register.is_absolute() else root / register
    if args.validate_only:
        if not register.is_file():
            raise GraphSubstrateBaselineError(f"baseline register is missing: {register}")
        observed = _load_json(register)
        if observed != payload:
            raise GraphSubstrateBaselineError(
                "baseline register differs from the current provider-free build"
            )
    else:
        output = args.output if args.output.is_absolute() else root / args.output
        _write_json(output, payload)

    summary = payload["current_portfolio_characterization"]
    print(
        json.dumps(
            {
                "status": "valid" if args.validate_only else "written",
                "register": str(register.relative_to(root)),
                "model_count": payload["graph_inventory"]["canonical_model_count"],
                "relation_count": payload["graph_inventory"]["rich_relation_count"],
                "window_count": summary["window_count"],
                "graph_active_count": summary["graph_active_count"],
                "active_with_multiple_paths": summary[
                    "graph_active_with_multiple_exact_paths_count"
                ],
                "additional_outer_unpreserved_paths": summary[
                    "additional_exact_paths_not_on_outer_active_item_count"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
