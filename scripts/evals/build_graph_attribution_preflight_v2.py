#!/usr/bin/env python3
"""Repair Gate 6 attribution by inspecting the complete Step 6 consumer context."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from scripts.evals import build_graph_attribution_preflight as v1


CONTRACT_SCHEMA = "lolla.graph_attribution_preflight_contract.v2"
RESULT_SCHEMA = "lolla.graph_attribution_preflight_result.v2"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _v1_shape(contract: Mapping[str, Any]) -> dict[str, Any]:
    shaped = dict(contract)
    shaped["schema_version"] = v1.CONTRACT_SCHEMA
    return shaped


def validate_contract(contract: Mapping[str, Any], *, root: Path) -> dict[str, Path]:
    if _text(contract.get("schema_version")) != CONTRACT_SCHEMA:
        raise v1.ContractError(f"schema_version must be {CONTRACT_SCHEMA}")
    if _text(contract.get("repairs_contract_sha256")) == "":
        raise v1.ContractError("repairs_contract_sha256 is required")
    if _text(contract.get("repairs_result_sha256")) == "":
        raise v1.ContractError("repairs_result_sha256 is required")
    return v1.validate_contract(_v1_shape(contract), root=root)


def _companion_graph_chunks(pipeline: Mapping[str, Any]) -> list[dict[str, Any]]:
    raw_expansions = []
    for row_value in _list(_mapping(pipeline.get("companion_card")).get("expansions")):
        row = _mapping(row_value)
        raw_expansions.append(
            {
                "source_model_id": _text(row.get("source_model_id")),
                "relation_type": _text(row.get("relation_type")),
                "target_model_id": _text(row.get("model_id")),
                "substrate_chunk": _text(row.get("substrate_chunk")),
            }
        )

    rows = []
    cheat_sheet = _mapping(pipeline.get("companion_cheat_sheet"))
    for anchor_value in _list(cheat_sheet.get("anchors")):
        anchor = _mapping(anchor_value)
        anchor_model_id = _text(anchor.get("model_id"))
        for chunk_value in _list(anchor.get("chunks")):
            chunk = _mapping(chunk_value)
            provenance = _mapping(chunk.get("provenance"))
            target_model_id = _text(provenance.get("relation_target_id"))
            if not target_model_id:
                continue
            text = _text(chunk.get("text"))
            matches = [
                row
                for row in raw_expansions
                if row["source_model_id"] == anchor_model_id
                and row["target_model_id"] == target_model_id
                and (not row["substrate_chunk"] or row["substrate_chunk"] in text)
            ]
            rows.append(
                {
                    "anchor_model_id": anchor_model_id,
                    "relation_target_id": target_model_id,
                    "chunk_type": _text(chunk.get("chunk_type")),
                    "text": text,
                    "source_layer": _text(provenance.get("source_layer")),
                    "extraction_type": _text(provenance.get("extraction_type")),
                    "confidence": _text(provenance.get("confidence")),
                    "raw_expansion_match_count": len(matches),
                    "raw_expansion_matches": matches,
                    "exact_raw_expansion_match": len(matches) == 1,
                }
            )
    return rows


def build_result(
    contract: Mapping[str, Any],
    *,
    root: Path,
    paths: Mapping[str, Path] | None = None,
) -> dict[str, Any]:
    paths = dict(paths or validate_contract(contract, root=root))
    base = v1.build_result(_v1_shape(contract), root=root, paths=paths)
    pipeline = v1._load_json(paths["stage_a_pipeline_result"])
    private_table = v1._load_json(paths["stage_a_private_table_snapshot"])
    packet = v1._load_json(paths["stage_a_pressure_packet"])

    graph_chunks = _companion_graph_chunks(pipeline)
    graph_target_ids = {
        row["relation_target_id"] for row in graph_chunks if row["relation_target_id"]
    }
    pressure_rows = v1._pressure_rows(packet)
    stage_b_graph_target_pressure_ids = [
        row["pressure_id"]
        for row in pressure_rows
        if set(row["lineage_model_ids"]) & graph_target_ids
    ]

    source_items = [
        _mapping(row) for row in _list(private_table.get("source_items"))
    ]
    ledger_items = [
        _mapping(row)
        for row in _list(
            _mapping(private_table.get("consideration_ledger_skeleton")).get("items")
        )
    ]
    parent_anchor_ids = {
        f"lane2::{row['anchor_model_id']}" for row in graph_chunks
    }
    parent_anchor_source_items = sorted(
        {
            _text(row.get("source_id"))
            for row in source_items
            if _text(row.get("source_id")) in parent_anchor_ids
        }
    )
    parent_anchor_ledger_items = [
        {
            "source_id": _text(row.get("source_id")),
            "source_kind": _text(row.get("source_kind")),
            "disposition": _text(row.get("disposition")),
            "why": _text(row.get("why")),
        }
        for row in ledger_items
        if _text(row.get("source_id")) in parent_anchor_ids
    ]

    exact_graph_chunk_ids = {
        _text(row.get("chunk_id"))
        for row in ledger_items
        if _text(row.get("chunk_id"))
        and (
            "graph" in _text(row.get("source_kind"))
            or "expansion" in _text(row.get("source_kind"))
        )
    }
    complete_context_changes_if_graph_disabled = bool(graph_chunks)

    base["schema_version"] = RESULT_SCHEMA
    base["repairs"] = {
        "v1_contract_sha256": _text(contract.get("repairs_contract_sha256")),
        "v1_result_sha256": _text(contract.get("repairs_result_sha256")),
        "repair_reason": (
            "v1 inspected V60 and private-table graph sources but omitted graph-derived "
            "chunks embedded inside companion_cheat_sheet anchor cards."
        ),
    }
    base["complete_step6_consumer_surface"] = {
        "companion_graph_chunk_count": len(graph_chunks),
        "companion_graph_chunks": graph_chunks,
        "graph_relation_target_model_ids": sorted(graph_target_ids),
        "parent_anchor_source_items": parent_anchor_source_items,
        "parent_anchor_ledger_items": parent_anchor_ledger_items,
        "individual_graph_chunk_ledger_ids": sorted(exact_graph_chunk_ids),
        "individual_graph_chunk_disposition_custody": bool(exact_graph_chunk_ids),
        "custody_read": (
            "Graph relationship chunks reach Step 6 inside companion anchors, but the "
            "recorded private-table ledger dispositions the parent anchor rather than each "
            "relationship chunk."
            if graph_chunks and not exact_graph_chunk_ids
            else "No graph relationship chunk reached the consumer."
            if not graph_chunks
            else "Graph relationship chunks have individual ledger identity."
        ),
    }

    base["provider_free_baselines"]["graph_disabled_v60_packet"] = dict(
        base["provider_free_baselines"].pop("graph_disabled_artifact_replay")
    )
    base["provider_free_baselines"]["shuffled_edges_v60_packet"] = dict(
        base["provider_free_baselines"].pop("shuffled_edges")
    )
    base["provider_free_baselines"]["graph_disabled_complete_step6_context"] = {
        "status": (
            "requires_frozen_replay"
            if complete_context_changes_if_graph_disabled
            else "exact_noop"
        ),
        "recorded_companion_chunks_removed": len(graph_chunks),
        "basis": (
            "Disabling graph relationships would remove recorded relationship chunks from "
            "the companion cheat sheet even though V60 cards remain unchanged."
            if graph_chunks
            else "No graph relationship chunk appears in the complete consumer surface."
        ),
    }
    base["provider_free_baselines"]["shuffled_edges_complete_step6_context"] = {
        "status": (
            "requires_frozen_replay"
            if complete_context_changes_if_graph_disabled
            else "non_identifying_noop"
        ),
        "basis": (
            "A shuffle could change which relationship chunks appear inside companion anchors; "
            "the current frozen artifacts cannot simulate the resulting card selection or prose."
            if graph_chunks
            else "No relationship chunk reached the consumer surface."
        ),
    }

    v1_decision = dict(_mapping(base.get("decision_evidence")))
    base["decision_evidence"] = {
        **v1_decision,
        "companion_graph_chunks_entered_complete_step6_context": bool(graph_chunks),
        "companion_graph_chunk_count": len(graph_chunks),
        "individual_graph_chunk_disposition_custody": bool(exact_graph_chunk_ids),
        "stage_b_pressure_with_graph_target_lineage_count": len(
            stage_b_graph_target_pressure_ids
        ),
        "stage_b_pressure_with_graph_target_lineage_ids": stage_b_graph_target_pressure_ids,
        "case10_stage_b_can_identify_graph_contribution": bool(
            stage_b_graph_target_pressure_ids
        ),
        "paid_graph_ablation_candidate": False,
    }
    base["interpretation_boundary"] = {
        "mechanical_conclusion": (
            "Graph relationships reached the normal Step 6 consumer indirectly inside three "
            "companion-anchor chunks, but none had exact lineage in the frozen Case 10 Stage B "
            "pressure packet and none had individual disposition custody. The completed pair "
            "therefore cannot identify graph contribution."
        ),
        "does_not_prove": [
            "that the three graph chunks changed or did not change an ordinary live Step 6 answer",
            "that graph expansion is generally useful or useless",
            "that a parent-anchor disposition is semantic proof about every embedded relation",
            "that another case cannot support a graph-specific ablation",
        ],
        "required_before_paid_ablation": [
            "one source-reviewed graph relationship chunk absent from simpler baselines",
            "exact graph-chunk identity in the treatment contract",
            "separate individual disposition custody",
            "a graph-disabled or shuffled-edge arm frozen before generation",
            "public-revision and private-receipt fields measured separately",
        ],
    }
    return base


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True)
    parser.add_argument("--root", default=".")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    contract_path = v1._resolve(root, args.contract)
    contract = v1._load_json(contract_path)
    paths = validate_contract(contract, root=root)
    if args.dry_run:
        print(
            json.dumps(
                {
                    "status": "dry_run_valid",
                    "schema_version": CONTRACT_SCHEMA,
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
        raise v1.ContractError(f"refusing to overwrite existing output: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["decision_evidence"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
