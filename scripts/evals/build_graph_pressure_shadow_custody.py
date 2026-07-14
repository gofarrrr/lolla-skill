#!/usr/bin/env python3
"""Build exact, provider-free custody identities for graph-derived companion chunks."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any, Mapping


CONTRACT_SCHEMA = "lolla.graph_pressure_shadow_custody_contract.v1"
RESULT_SCHEMA = "lolla.graph_pressure_shadow_custody.v1"


class ContractError(ValueError):
    pass


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _text_sha256(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ContractError(f"expected JSON object: {path}")
    return payload


def _resolve(root: Path, raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else root / path


def validate_contract(contract: Mapping[str, Any], *, root: Path) -> dict[str, Path]:
    if _text(contract.get("schema_version")) != CONTRACT_SCHEMA:
        raise ContractError(f"schema_version must be {CONTRACT_SCHEMA}")
    if _text(contract.get("status")) != "frozen_before_export":
        raise ContractError("status must be frozen_before_export")
    if int(contract.get("provider_call_budget", -1)) != 0:
        raise ContractError("provider_call_budget must be zero")
    if bool(contract.get("runtime_change_authorized")):
        raise ContractError("runtime_change_authorized must be false")
    if bool(contract.get("include_chunk_text", False)):
        raise ContractError("v1 checked-in shadow custody requires include_chunk_text false")

    for row in (_mapping(item) for item in _list(contract.get("hash_locks"))):
        role = _text(row.get("role"))
        path = _resolve(root, _text(row.get("path")))
        expected = _text(row.get("sha256"))
        if not path.is_file():
            raise ContractError(f"hash lock missing for {role}: {path}")
        actual = _sha256(path)
        if actual != expected:
            raise ContractError(
                f"hash drift for {role}: expected {expected}, observed {actual}"
            )

    resolved = {}
    for role in ("source_conversation", "pipeline_result"):
        row = _mapping(contract.get(role))
        path = _resolve(root, _text(row.get("path")))
        expected = _text(row.get("sha256"))
        if not path.is_file():
            raise ContractError(f"missing {role}: {path}")
        actual = _sha256(path)
        if actual != expected:
            raise ContractError(
                f"hash drift for {role}: expected {expected}, observed {actual}"
            )
        resolved[role] = path
    raw_output = _text(_mapping(contract.get("output")).get("path"))
    if not raw_output:
        raise ContractError("output.path is required")
    resolved["output"] = _resolve(root, raw_output)
    return resolved


def _raw_expansions(pipeline: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for index, value in enumerate(
        _list(_mapping(pipeline.get("companion_card")).get("expansions"))
    ):
        row = _mapping(value)
        rows.append(
            {
                "raw_expansion_index": index,
                "source_model_id": _text(row.get("source_model_id")),
                "relation_type": _text(row.get("relation_type")),
                "target_model_id": _text(row.get("model_id")),
                "substrate_chunk": _text(row.get("substrate_chunk")),
                "affinity_rationale": _text(row.get("affinity_rationale")),
                "activation_condition": _text(row.get("activation_condition")),
                "tension_type": _text(row.get("tension_type")),
            }
        )
    return rows


def build_result(
    contract: Mapping[str, Any],
    *,
    paths: Mapping[str, Path],
) -> dict[str, Any]:
    pipeline = _load_json(paths["pipeline_result"])
    expansions = _raw_expansions(pipeline)
    items = []
    exact_match_failures = []
    anchors = _list(_mapping(pipeline.get("companion_cheat_sheet")).get("anchors"))
    for anchor_index, anchor_value in enumerate(anchors):
        anchor = _mapping(anchor_value)
        source_model_id = _text(anchor.get("model_id"))
        for chunk_index, chunk_value in enumerate(_list(anchor.get("chunks"))):
            chunk = _mapping(chunk_value)
            provenance = _mapping(chunk.get("provenance"))
            target_model_id = _text(provenance.get("relation_target_id"))
            if not target_model_id:
                continue
            text = _text(chunk.get("text"))
            matches = [
                row
                for row in expansions
                if row["source_model_id"] == source_model_id
                and row["target_model_id"] == target_model_id
                and (not row["substrate_chunk"] or row["substrate_chunk"] in text)
            ]
            if len(matches) != 1:
                exact_match_failures.append(
                    {
                        "anchor_index": anchor_index,
                        "chunk_index": chunk_index,
                        "source_model_id": source_model_id,
                        "target_model_id": target_model_id,
                        "match_count": len(matches),
                    }
                )
                continue
            match = matches[0]
            text_hash = _text_sha256(text)
            graph_pressure_id = "graph::{source}::{relation}::{target}::{digest}".format(
                source=_slug(source_model_id),
                relation=_slug(match["relation_type"]),
                target=_slug(target_model_id),
                digest=text_hash[:12],
            )
            items.append(
                {
                    "graph_pressure_id": graph_pressure_id,
                    "source_anchor_model_id": source_model_id,
                    "relation_type": match["relation_type"],
                    "target_model_id": target_model_id,
                    "chunk_type": _text(chunk.get("chunk_type")),
                    "chunk_text_sha256": text_hash,
                    "chunk_text_included": False,
                    "source_layer": _text(provenance.get("source_layer")),
                    "extraction_type": _text(provenance.get("extraction_type")),
                    "confidence": _text(provenance.get("confidence")),
                    "companion_anchor_index": anchor_index,
                    "companion_chunk_index": chunk_index,
                    "raw_expansion_index": match["raw_expansion_index"],
                    "source_json_pointer": (
                        f"/companion_cheat_sheet/anchors/{anchor_index}/chunks/{chunk_index}"
                    ),
                    "raw_expansion_json_pointer": (
                        f"/companion_card/expansions/{match['raw_expansion_index']}"
                    ),
                    "activation_condition": match["activation_condition"],
                    "affinity_rationale": match["affinity_rationale"],
                    "tension_type": match["tension_type"],
                    "disposition": "",
                    "strongest_plausible_application": "",
                    "condition_that_passed_or_failed": "",
                    "why": "",
                    "visible_effect": "",
                    "private_guardrail": "",
                    "risk_if_forced": "",
                    "risk_if_ignored": "",
                    "technical_blocker": "",
                    "source_review_status": "pending",
                }
            )

    ids = [row["graph_pressure_id"] for row in items]
    if len(ids) != len(set(ids)):
        raise ContractError("graph_pressure_id collision")
    return {
        "schema_version": RESULT_SCHEMA,
        "status": "ready" if not exact_match_failures else "partial",
        "case_id": _text(contract.get("case_id")),
        "provider_calls": 0,
        "runtime_mutated": False,
        "source_conversation": {
            "path": _text(_mapping(contract.get("source_conversation")).get("path")),
            "sha256": _text(_mapping(contract.get("source_conversation")).get("sha256")),
        },
        "pipeline_result": {
            "path": _text(_mapping(contract.get("pipeline_result")).get("path")),
            "sha256": _text(_mapping(contract.get("pipeline_result")).get("sha256")),
        },
        "graph_pressure_count": len(items),
        "graph_pressures": items,
        "exact_match_failures": exact_match_failures,
        "individual_identity_complete": not exact_match_failures,
        "semantic_dispositions_complete": False,
        "consumer_injection_authorized": False,
        "non_claims": _list(contract.get("non_claims")),
    }


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
                },
                indent=2,
            )
        )
        return 0
    result = build_result(contract, paths=paths)
    output_path = paths["output"]
    if output_path.exists():
        raise ContractError(f"refusing to overwrite existing output: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": result["status"],
                "graph_pressure_count": result["graph_pressure_count"],
                "individual_identity_complete": result["individual_identity_complete"],
                "provider_calls": 0,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
