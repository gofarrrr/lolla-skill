from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.evals import build_graph_ablation_candidate_inventory as inventory


def _write(path: Path, payload: object, *, raw: bool = False) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    value = str(payload) if raw else json.dumps(payload, indent=2) + "\n"
    path.write_text(value, encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact(tmp_path: Path, role: str, payload: object, *, raw: bool = False) -> dict:
    suffix = ".txt" if raw else ".json"
    path = tmp_path / f"{role}{suffix}"
    return {
        "role": role,
        "path": path.name,
        "sha256": _write(path, payload, raw=raw),
    }


def _contract(tmp_path: Path, *, eligible: bool) -> dict:
    pipeline = {
        "companion_card": {
            "expansions": [
                {
                    "source_model_id": "inversion",
                    "relation_type": "antagonist",
                    "model_id": "commitment-bias",
                    "substrate_chunk": "challenge prior commitment",
                }
            ]
        },
        "companion_cheat_sheet": {
            "anchors": [
                {
                    "model_id": "inversion",
                    "chunks": [
                        {
                            "chunk_type": "antagonist",
                            "text": "Commitment Bias: challenge prior commitment",
                            "provenance": {
                                "source_layer": "wave3",
                                "relation_target_id": "commitment-bias",
                            },
                        }
                    ],
                }
            ]
        },
    }
    artifacts = [
        _artifact(tmp_path, "source", "source", raw=True),
        _artifact(tmp_path, "stage_a_gate", {"status": "passed"}),
        _artifact(tmp_path, "pipeline_result", pipeline),
        _artifact(tmp_path, "strong_control", {"status": "ok"}),
        _artifact(
            tmp_path,
            "treatment_packet",
            {"trace_ids": ["graph::inversion::antagonist::commitment-bias"]}
            if eligible
            else {"trace_ids": ["aff::inversion.test"]},
        ),
        _artifact(
            tmp_path,
            "graph_source_review",
            {
                "decision": {
                    "graph_chunks_admitted_for_paid_ablation": 1 if eligible else 0
                }
            },
        ),
    ]
    return {
        "schema_version": inventory.CONTRACT_SCHEMA,
        "status": "frozen_before_inventory",
        "provider_call_budget": 0,
        "runtime_change_authorized": False,
        "scope": {"name": "test"},
        "cases": [
            {
                "case_id": "case-test",
                "case_role": "fixture",
                "individual_graph_disposition_contract": eligible,
                "risk_excluded": False,
                "artifacts": artifacts,
            }
        ],
        "output": {"path": "result.json"},
        "non_claims": ["not product proof"],
    }


def test_eligible_case_requires_full_chain(tmp_path: Path) -> None:
    contract = _contract(tmp_path, eligible=True)
    paths = inventory.validate_contract(contract, root=tmp_path)
    result = inventory.build_result(contract, root=tmp_path, paths_by_case=paths)
    assert result["eligible_case_ids"] == ["case-test"]
    assert result["decision"]["paid_graph_ablation_authorized"] is False


def test_non_graph_treatment_and_zero_review_block_candidate(tmp_path: Path) -> None:
    contract = _contract(tmp_path, eligible=False)
    paths = inventory.validate_contract(contract, root=tmp_path)
    result = inventory.build_result(contract, root=tmp_path, paths_by_case=paths)
    case = result["cases"][0]
    assert case["eligible"] is False
    assert "no_exact_graph_lineage_in_frozen_treatment" in case["ineligibility_reasons"]
    assert "source_first_graph_chunk_review_admitted_zero" in case["ineligibility_reasons"]


def test_hash_drift_fails_closed(tmp_path: Path) -> None:
    contract = _contract(tmp_path, eligible=True)
    source = next(
        row for row in contract["cases"][0]["artifacts"] if row["role"] == "source"
    )
    (tmp_path / source["path"]).write_text("drift", encoding="utf-8")
    with pytest.raises(inventory.ContractError, match="hash drift"):
        inventory.validate_contract(contract, root=tmp_path)
