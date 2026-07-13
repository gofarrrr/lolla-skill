#!/usr/bin/env python3
"""Build a provider-free attribution report for a frozen Lolla pressure packet.

This tool does not rerun extraction, embeddings, graph traversal, or generation.
It reads frozen artifacts and answers a narrower custody question: which already
recorded pathway made each admitted pressure available to the downstream packet?
"""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


CONTRACT_SCHEMA = "lolla.graph_attribution_preflight_contract.v1"
RESULT_SCHEMA = "lolla.graph_attribution_preflight_result.v1"
REQUIRED_INPUT_ROLES = frozenset(
    {
        "source_conversation",
        "stage_a_pipeline_result",
        "stage_a_private_table_snapshot",
        "stage_a_v60_snapshot",
        "stage_a_preliminary_pressure_review",
        "stage_a_pressure_packet",
        "stage_b_revealed_comparison",
        "stage_b_decision",
    }
)


class ContractError(ValueError):
    """Raised when a frozen attribution contract is incomplete or has drifted."""


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ContractError(f"expected JSON object: {path}")
    return payload


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _resolve(root: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else root / path


def validate_contract(contract: Mapping[str, Any], *, root: Path) -> dict[str, Path]:
    if _text(contract.get("schema_version")) != CONTRACT_SCHEMA:
        raise ContractError(f"schema_version must be {CONTRACT_SCHEMA}")
    if _text(contract.get("status")) != "frozen_before_replay":
        raise ContractError("status must be frozen_before_replay")
    if int(contract.get("provider_call_budget", -1)) != 0:
        raise ContractError("provider_call_budget must be zero")
    if bool(contract.get("runtime_change_authorized")):
        raise ContractError("runtime_change_authorized must be false")

    rows = [_mapping(row) for row in _list(contract.get("inputs"))]
    roles = [_text(row.get("role")) for row in rows]
    if len(roles) != len(set(roles)):
        raise ContractError("input roles must be unique")
    missing = sorted(REQUIRED_INPUT_ROLES - set(roles))
    if missing:
        raise ContractError(f"missing required input roles: {missing}")

    resolved: dict[str, Path] = {}
    for row in rows:
        role = _text(row.get("role"))
        path = _resolve(root, _text(row.get("path")))
        expected = _text(row.get("sha256"))
        if not path.is_file():
            raise ContractError(f"input missing for {role}: {path}")
        actual = _sha256(path)
        if actual != expected:
            raise ContractError(
                f"hash drift for {role}: expected {expected}, observed {actual}"
            )
        resolved[role] = path

    manifest_path = resolved.get("case10_evidence_manifest")
    if manifest_path is not None:
        manifest = _load_json(manifest_path)
        manifest_rows = [_mapping(row) for row in _list(manifest.get("files"))]
        if int(manifest.get("file_count", -1)) != len(manifest_rows):
            raise ContractError("case10 evidence manifest file_count mismatch")
        for row in manifest_rows:
            path = _resolve(root, _text(row.get("path")))
            expected = _text(row.get("sha256"))
            if not path.is_file():
                raise ContractError(f"manifest input missing: {path}")
            actual = _sha256(path)
            if actual != expected:
                raise ContractError(
                    f"manifest hash drift for {path}: expected {expected}, observed {actual}"
                )

    raw_output_path = _text(_mapping(contract.get("output")).get("path"))
    if not raw_output_path:
        raise ContractError("output.path is required")
    output_path = _resolve(root, raw_output_path)
    resolved["output"] = output_path
    return resolved


def _chunk_model_id(chunk_id: str) -> str:
    if chunk_id.startswith("aff::"):
        return chunk_id[len("aff::") :].split(".", 1)[0]
    if chunk_id.startswith("abs::"):
        return chunk_id[len("abs::") :].split("::", 1)[0]
    return ""


def _selected_chunk_index(v60: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for card_value in _list(v60.get("selected_cards")):
        card = _mapping(card_value)
        base = {
            "card_id": _text(card.get("card_id")),
            "model_id": _text(card.get("model_id")),
            "selection_source": _text(card.get("selection_source")),
            "selection_reason": _text(card.get("selection_reason")),
        }
        for field, kind in (
            ("selected_affordance_cards", "affordance"),
            ("selected_absence_records", "absence"),
        ):
            for chunk_value in _list(card.get(field)):
                chunk = _mapping(chunk_value)
                chunk_id = _text(chunk.get("chunk_id"))
                if chunk_id:
                    index[chunk_id] = {
                        **base,
                        "chunk_kind": kind,
                        "chunk_status": _text(chunk.get("status")),
                    }
    return index


def _pressure_rows(packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item_value in _list(packet.get("pressure_items")):
        item = _mapping(item_value)
        chunk_ids = [_text(value) for value in _list(item.get("lineage_chunk_ids"))]
        model_ids = list(dict.fromkeys(_chunk_model_id(value) for value in chunk_ids))
        rows.append(
            {
                "pressure_id": _text(item.get("pressure_id")),
                "challenge": _text(item.get("challenge")),
                "lineage_chunk_ids": chunk_ids,
                "lineage_model_ids": [value for value in model_ids if value],
            }
        )
    return rows


def _coverage(
    pressures: Sequence[Mapping[str, Any]],
    available_models: set[str],
) -> dict[str, Any]:
    rows = []
    fully_covered = 0
    for pressure in pressures:
        required = set(str(value) for value in pressure.get("lineage_model_ids", []))
        present = sorted(required & available_models)
        missing = sorted(required - available_models)
        if required and not missing:
            label = "full_model_coverage"
            fully_covered += 1
        elif present:
            label = "partial_model_coverage"
        else:
            label = "no_model_coverage"
        rows.append(
            {
                "pressure_id": pressure.get("pressure_id"),
                "coverage": label,
                "present_model_ids": present,
                "missing_model_ids": missing,
            }
        )
    return {
        "method": "recorded_model_availability_not_answer_simulation",
        "fully_covered_pressure_count": fully_covered,
        "pressure_count": len(pressures),
        "pressures": rows,
    }


def build_result(
    contract: Mapping[str, Any],
    *,
    root: Path,
    paths: Mapping[str, Path] | None = None,
) -> dict[str, Any]:
    paths = dict(paths or validate_contract(contract, root=root))
    pipeline = _load_json(paths["stage_a_pipeline_result"])
    private_table = _load_json(paths["stage_a_private_table_snapshot"])
    v60_snapshot = _load_json(paths["stage_a_v60_snapshot"])
    preliminary = _load_json(paths["stage_a_preliminary_pressure_review"])
    packet = _load_json(paths["stage_a_pressure_packet"])
    revealed = _load_json(paths["stage_b_revealed_comparison"])
    stage_b_decision = _load_json(paths["stage_b_decision"])

    v60 = _mapping(pipeline.get("v60_enrichment"))
    selected_chunk_index = _selected_chunk_index(v60)
    pressures = _pressure_rows(packet)

    candidate_pool = _mapping(v60.get("candidate_pool"))
    lane_candidates = [_mapping(row) for row in _list(candidate_pool.get("lane_candidates"))]
    direct_anchor_models = {
        _text(row.get("model_id"))
        for row in lane_candidates
        if "lane2_companion_anchor" in _text(row.get("source"))
    }
    frame_route_models = {
        _text(row.get("model_id"))
        for row in lane_candidates
        if "lane3_" in _text(row.get("source"))
    }
    structural_gap_models = {
        _text(row.get("model_id"))
        for row in lane_candidates
        if "lane4_" in _text(row.get("source"))
    }
    embedding_rows = [_mapping(row) for row in _list(candidate_pool.get("embedding_model_hits"))]
    embedding_models = [_text(row.get("model_id")) for row in embedding_rows]
    max_cards = int(_mapping(v60.get("selection_policy")).get("max_cards", 0) or 0)
    embedding_top_cap_models = set(embedding_models[:max_cards])

    companion = _mapping(pipeline.get("companion_card"))
    graph_expansions = []
    for row_value in _list(companion.get("expansions")):
        row = _mapping(row_value)
        graph_expansions.append(
            {
                "source_model_id": _text(row.get("source_model_id")),
                "relation_type": _text(row.get("relation_type")),
                "model_id": _text(row.get("model_id")),
                "substrate_chunk": _text(row.get("substrate_chunk")),
            }
        )
    graph_target_models = {row["model_id"] for row in graph_expansions if row["model_id"]}

    selected_cards = [_mapping(row) for row in _list(v60.get("selected_cards"))]
    selected_models = {_text(row.get("model_id")) for row in selected_cards}
    selected_sources = {_text(row.get("selection_source")) for row in selected_cards}
    candidate_sources = {_text(row.get("source")) for row in lane_candidates}
    graph_named_selected_sources = sorted(
        source for source in selected_sources if "graph" in source or "expansion" in source
    )
    graph_named_candidate_sources = sorted(
        source for source in candidate_sources if "graph" in source or "expansion" in source
    )

    pressure_attribution = []
    graph_specific_pressures = []
    for pressure in pressures:
        models = set(pressure["lineage_model_ids"])
        chunk_rows = []
        for chunk_id in pressure["lineage_chunk_ids"]:
            selected = selected_chunk_index.get(chunk_id)
            chunk_rows.append(
                {
                    "chunk_id": chunk_id,
                    "model_id": _chunk_model_id(chunk_id),
                    "present_in_v60_selected_chunks": selected is not None,
                    "selected_card": selected,
                }
            )
        pathway = {
            "direct_companion_anchor_model_ids": sorted(models & direct_anchor_models),
            "frame_route_model_ids": sorted(models & frame_route_models),
            "structural_gap_model_ids": sorted(models & structural_gap_models),
            "embedding_recalled_model_ids": sorted(models & set(embedding_models)),
            "graph_expansion_target_model_ids": sorted(models & graph_target_models),
            "current_selected_model_ids": sorted(models & selected_models),
        }
        non_graph_availability = (
            direct_anchor_models
            | frame_route_models
            | structural_gap_models
            | set(embedding_models)
        )
        graph_exclusive = sorted((models & graph_target_models) - non_graph_availability)
        selected_via_graph = sorted(
            {
                _text(_mapping(row.get("selected_card")).get("model_id"))
                for row in chunk_rows
                if _text(_mapping(row.get("selected_card")).get("selection_source"))
                in graph_named_selected_sources
            }
            - {""}
        )
        graph_specific = bool(graph_exclusive or selected_via_graph)
        if graph_specific:
            graph_specific_pressures.append(pressure["pressure_id"])
        pressure_attribution.append(
            {
                **pressure,
                "chunks": chunk_rows,
                "all_lineage_chunks_present_in_v60": all(
                    row["present_in_v60_selected_chunks"] for row in chunk_rows
                ),
                "pathway_availability": pathway,
                "graph_exclusive_model_ids": graph_exclusive,
                "selected_via_graph_model_ids": selected_via_graph,
                "graph_specific_at_recorded_handoff": graph_specific,
            }
        )

    source_kind_counts = Counter(
        _text(_mapping(row).get("source_kind"))
        for row in _list(private_table.get("source_items"))
    )
    graph_source_items = [
        _mapping(row)
        for row in _list(private_table.get("source_items"))
        if "graph" in _text(_mapping(row).get("source_kind"))
        or "expansion" in _text(_mapping(row).get("source_kind"))
    ]

    graph_disabled_exact_noop = not (
        graph_named_selected_sources or graph_named_candidate_sources or graph_source_items
    )
    baselines = {
        "direct_labels_only": {
            "available_model_ids": sorted(direct_anchor_models),
            "coverage": _coverage(pressures, direct_anchor_models),
        },
        "frame_routes_only": {
            "available_model_ids": sorted(frame_route_models),
            "coverage": _coverage(pressures, frame_route_models),
        },
        "embedding_only_full_recorded_recall": {
            "available_model_ids": embedding_models,
            "coverage": _coverage(pressures, set(embedding_models)),
            "warning": "This is pool availability, not a fair capped packet.",
        },
        "embedding_only_same_card_cap": {
            "card_cap": max_cards,
            "available_model_ids": embedding_models[:max_cards],
            "coverage": _coverage(pressures, embedding_top_cap_models),
        },
        "graph_expansion_targets_only": {
            "available_model_ids": sorted(graph_target_models),
            "coverage": _coverage(pressures, graph_target_models),
        },
        "graph_disabled_artifact_replay": {
            "status": "exact_noop_at_recorded_handoff" if graph_disabled_exact_noop else "not_exact",
            "selected_models_unchanged": graph_disabled_exact_noop,
            "selected_chunks_unchanged": graph_disabled_exact_noop,
            "basis": (
                "No graph or expansion source appears in the V60 candidate pool, "
                "selected-card sources, or private-table source items."
                if graph_disabled_exact_noop
                else "A graph-derived source is present in the recorded handoff."
            ),
        },
        "shuffled_edges": {
            "status": "non_identifying_noop" if graph_disabled_exact_noop else "requires_frozen_replay",
            "basis": (
                "Shuffling unconsumed graph expansions cannot change this packet."
                if graph_disabled_exact_noop
                else "Recorded graph material entered the handoff and needs a separate replay contract."
            ),
        },
        "transcript_only_strong_control": {
            "source": "completed Stage B blind pair",
            "immediate_action_difference": _mapping(
                revealed.get("blind_read_survived_reveal")
            ).get("immediate_action_difference"),
            "unique_answer_improvement": _mapping(
                revealed.get("claim_classification")
            ).get("unique_answer_improvement"),
            "gate_5_decision": _mapping(stage_b_decision.get("gate_5")).get("decision"),
        },
    }

    main_delta = _mapping(pipeline.get("delta_card"))
    result = {
        "schema_version": RESULT_SCHEMA,
        "status": "complete_provider_free",
        "case_id": _text(contract.get("case_id")),
        "contract_sha256": _sha256(_resolve(root, _text(contract.get("contract_path"))))
        if _text(contract.get("contract_path"))
        and _resolve(root, _text(contract.get("contract_path"))).is_file()
        else "",
        "provider_calls": 0,
        "runtime_mutated": False,
        "source_artifacts": [
            {
                "role": _text(row.get("role")),
                "path": _text(row.get("path")),
                "sha256": _text(row.get("sha256")),
            }
            for row in (_mapping(value) for value in _list(contract.get("inputs")))
        ],
        "recorded_pipeline": {
            "main_delta_finding_count": len(_list(main_delta.get("findings"))),
            "companion_direct_anchor_model_ids": sorted(direct_anchor_models),
            "companion_graph_expansions": graph_expansions,
            "frame_route_model_ids": sorted(frame_route_models),
            "structural_gap_model_ids": sorted(structural_gap_models),
            "embedding_model_hits": embedding_rows,
            "v60_selected_model_ids": sorted(selected_models),
            "v60_selected_sources": sorted(selected_sources),
            "v60_candidate_sources": sorted(candidate_sources),
            "private_table_source_kind_counts": dict(sorted(source_kind_counts.items())),
            "private_table_graph_or_expansion_source_items": graph_source_items,
        },
        "pressure_attribution": pressure_attribution,
        "provider_free_baselines": baselines,
        "decision_evidence": {
            "admitted_pressure_count": len(pressures),
            "graph_specific_admitted_pressure_count": len(graph_specific_pressures),
            "graph_specific_admitted_pressure_ids": graph_specific_pressures,
            "all_admitted_chunks_present_in_v60": all(
                row["all_lineage_chunks_present_in_v60"] for row in pressure_attribution
            ),
            "graph_expansion_count": len(graph_expansions),
            "graph_expansions_entered_v60_candidate_pool": bool(
                graph_named_candidate_sources
            ),
            "graph_expansions_entered_v60_selected_cards": bool(
                graph_named_selected_sources
            ),
            "graph_expansions_entered_private_table": bool(graph_source_items),
            "case10_can_identify_graph_contribution": bool(graph_specific_pressures),
            "paid_graph_ablation_candidate": bool(graph_specific_pressures),
        },
        "interpretation_boundary": {
            "mechanical_conclusion": (
                "The recorded Case 10 downstream packet contains no graph-specific admitted pressure."
                if not graph_specific_pressures
                else "At least one admitted pressure has graph-specific recorded provenance."
            ),
            "does_not_prove": [
                "that direct labels, frame routes, or embeddings would write the same challenge",
                "that graph expansion is never useful in other cases",
                "that any answer is correct",
                "that an unrecorded causal dependency does not exist",
            ],
            "human_or_codex_decision_required": "whether another case can support a fair graph-specific ablation",
        },
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True)
    parser.add_argument("--root", default=".")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    contract_path = _resolve(root, args.contract)
    contract = _load_json(contract_path)
    paths = validate_contract(contract, root=root)
    if args.dry_run:
        print(
            json.dumps(
                {
                    "status": "dry_run_valid",
                    "case_id": contract.get("case_id"),
                    "provider_calls": 0,
                    "validated_input_count": len(paths) - 1,
                },
                indent=2,
            )
        )
        return 0

    result = build_result(contract, root=root, paths=paths)
    output_path = paths["output"]
    if output_path.exists():
        raise ContractError(f"refusing to overwrite existing output: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["decision_evidence"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
