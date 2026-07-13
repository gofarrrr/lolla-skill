#!/usr/bin/env python3
"""Inventory frozen cases for a fair graph-specific ablation candidate."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping

from scripts.evals import build_graph_attribution_preflight as attribution_v1
from scripts.evals import build_graph_attribution_preflight_v2 as attribution_v2


CONTRACT_SCHEMA = "lolla.graph_ablation_candidate_inventory_contract.v1"
RESULT_SCHEMA = "lolla.graph_ablation_candidate_inventory_result.v1"


class ContractError(ValueError):
    pass


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ContractError(f"expected JSON object: {path}")
    return payload


def _resolve(root: Path, raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else root / path


def validate_contract(
    contract: Mapping[str, Any], *, root: Path
) -> dict[str, dict[str, Path]]:
    if _text(contract.get("schema_version")) != CONTRACT_SCHEMA:
        raise ContractError(f"schema_version must be {CONTRACT_SCHEMA}")
    if _text(contract.get("status")) != "frozen_before_inventory":
        raise ContractError("status must be frozen_before_inventory")
    if int(contract.get("provider_call_budget", -1)) != 0:
        raise ContractError("provider_call_budget must be zero")
    if bool(contract.get("runtime_change_authorized")):
        raise ContractError("runtime_change_authorized must be false")

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

    cases = [_mapping(row) for row in _list(contract.get("cases"))]
    case_ids = [_text(row.get("case_id")) for row in cases]
    if not case_ids or any(not value for value in case_ids):
        raise ContractError("at least one non-empty case_id is required")
    if len(case_ids) != len(set(case_ids)):
        raise ContractError("case_id values must be unique")

    resolved: dict[str, dict[str, Path]] = {}
    for case in cases:
        case_id = _text(case.get("case_id"))
        artifacts = [_mapping(row) for row in _list(case.get("artifacts"))]
        roles = [_text(row.get("role")) for row in artifacts]
        if "source" not in roles or "stage_a_gate" not in roles:
            raise ContractError(f"{case_id} requires source and stage_a_gate")
        if len(roles) != len(set(roles)):
            raise ContractError(f"{case_id} artifact roles must be unique")
        paths: dict[str, Path] = {}
        for row in artifacts:
            role = _text(row.get("role"))
            path = _resolve(root, _text(row.get("path")))
            expected = _text(row.get("sha256"))
            if not path.is_file():
                raise ContractError(f"{case_id} missing {role}: {path}")
            actual = _sha256(path)
            if actual != expected:
                raise ContractError(
                    f"{case_id} hash drift for {role}: expected {expected}, observed {actual}"
                )
            paths[role] = path
        resolved[case_id] = paths

    raw_output = _text(_mapping(contract.get("output")).get("path"))
    if not raw_output:
        raise ContractError("output.path is required")
    resolved["__output__"] = {"path": _resolve(root, raw_output)}
    return resolved


def _walk_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, Mapping):
        rows: list[str] = []
        for child in value.values():
            rows.extend(_walk_strings(child))
        return rows
    if isinstance(value, list):
        rows = []
        for child in value:
            rows.extend(_walk_strings(child))
        return rows
    return []


def _explicit_graph_lineage_ids(packet: Mapping[str, Any]) -> list[str]:
    return sorted(
        {
            value
            for value in _walk_strings(packet)
            if value.startswith("graph::") or "relation_target_id=" in value
        }
    )


def _source_review_admitted_count(review: Mapping[str, Any]) -> int | None:
    decision = _mapping(review.get("decision"))
    for key in (
        "graph_chunks_admitted_for_paid_ablation",
        "graph_chunks_admitted_for_case10_paid_ablation",
    ):
        if key in decision:
            return int(decision[key])
    return None


def build_result(
    contract: Mapping[str, Any],
    *,
    root: Path,
    paths_by_case: Mapping[str, Mapping[str, Path]] | None = None,
) -> dict[str, Any]:
    paths_by_case = dict(paths_by_case or validate_contract(contract, root=root))
    case_results = []
    eligible_ids = []

    for case in (_mapping(row) for row in _list(contract.get("cases"))):
        case_id = _text(case.get("case_id"))
        paths = paths_by_case[case_id]
        gate = _load_json(paths["stage_a_gate"])
        stage_a_passed = _text(gate.get("status")) == "passed"

        graph_chunks: list[dict[str, Any]] | None = None
        if "pipeline_result" in paths:
            graph_chunks = attribution_v2._companion_graph_chunks(
                _load_json(paths["pipeline_result"])
            )

        explicit_graph_lineage_ids: list[str] = []
        if "treatment_packet" in paths:
            explicit_graph_lineage_ids = _explicit_graph_lineage_ids(
                _load_json(paths["treatment_packet"])
            )

        attribution_graph_lineage_count: int | None = None
        if "graph_attribution" in paths:
            evidence = _mapping(
                _load_json(paths["graph_attribution"]).get("decision_evidence")
            )
            if "stage_b_pressure_with_graph_target_lineage_count" in evidence:
                attribution_graph_lineage_count = int(
                    evidence["stage_b_pressure_with_graph_target_lineage_count"]
                )

        source_review_count: int | None = None
        if "graph_source_review" in paths:
            source_review_count = _source_review_admitted_count(
                _load_json(paths["graph_source_review"])
            )

        control_present = "strong_control" in paths or "blind_pair" in paths
        treatment_present = "treatment_packet" in paths
        exact_graph_lineage_count = max(
            len(explicit_graph_lineage_ids), attribution_graph_lineage_count or 0
        )
        individual_custody = bool(
            case.get("individual_graph_disposition_contract", False)
        )
        risk_excluded = bool(case.get("risk_excluded", False))
        reasons = []
        if not stage_a_passed:
            reasons.append("stage_a_not_formally_passed")
        if graph_chunks is None:
            reasons.append("complete_companion_graph_surface_not_preserved")
        elif not graph_chunks:
            reasons.append("no_graph_chunk_reached_complete_consumer_surface")
        if not control_present:
            reasons.append("strong_control_not_preserved")
        if not treatment_present:
            reasons.append("frozen_treatment_packet_not_preserved")
        if exact_graph_lineage_count == 0:
            reasons.append("no_exact_graph_lineage_in_frozen_treatment")
        if source_review_count is None:
            reasons.append("source_first_graph_chunk_review_missing")
        elif source_review_count == 0:
            reasons.append("source_first_graph_chunk_review_admitted_zero")
        if not individual_custody:
            reasons.append("individual_graph_chunk_disposition_contract_missing")
        if risk_excluded:
            reasons.append("case_excluded_by_frozen_risk_scope")

        eligible = not reasons
        if eligible:
            eligible_ids.append(case_id)
        case_results.append(
            {
                "case_id": case_id,
                "case_role": _text(case.get("case_role")),
                "stage_a_status": _text(gate.get("status")),
                "complete_companion_graph_surface_preserved": graph_chunks is not None,
                "companion_graph_chunk_count": (
                    len(graph_chunks) if graph_chunks is not None else None
                ),
                "strong_control_present": control_present,
                "frozen_treatment_packet_present": treatment_present,
                "explicit_graph_lineage_ids": explicit_graph_lineage_ids,
                "exact_graph_lineage_count": exact_graph_lineage_count,
                "source_first_graph_chunks_admitted": source_review_count,
                "individual_graph_disposition_contract": individual_custody,
                "risk_excluded": risk_excluded,
                "eligible": eligible,
                "ineligibility_reasons": reasons,
            }
        )

    return {
        "schema_version": RESULT_SCHEMA,
        "status": "complete_provider_free",
        "scope": _mapping(contract.get("scope")),
        "provider_calls": 0,
        "runtime_mutated": False,
        "case_count": len(case_results),
        "eligible_case_count": len(eligible_ids),
        "eligible_case_ids": eligible_ids,
        "cases": case_results,
        "decision": {
            "paid_graph_ablation_candidate_found": bool(eligible_ids),
            "paid_graph_ablation_authorized": False,
            "next_step": (
                "source-review and freeze the smallest eligible candidate"
                if eligible_ids
                else "keep paid Gate 6 blocked; design exact graph-chunk shadow custody before a new holdout"
            ),
        },
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
                    "case_count": len(_list(contract.get("cases"))),
                    "provider_calls": 0,
                },
                indent=2,
            )
        )
        return 0

    result = build_result(contract, root=root, paths_by_case=paths)
    output_path = paths["__output__"]["path"]
    if output_path.exists():
        raise ContractError(f"refusing to overwrite existing output: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["decision"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
