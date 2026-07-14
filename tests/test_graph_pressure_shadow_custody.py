from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.evals import build_graph_pressure_shadow_custody as custody


def _write(path: Path, value: str) -> str:
    path.write_text(value, encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fixture(tmp_path: Path) -> dict:
    source = tmp_path / "source.txt"
    source_hash = _write(source, "conversation")
    pipeline = {
        "companion_card": {
            "expansions": [
                {
                    "source_model_id": "inversion",
                    "relation_type": "antagonist",
                    "model_id": "commitment-bias",
                    "substrate_chunk": "challenge prior commitment",
                    "activation_condition": "when commitment blocks reconsideration",
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
                                "extraction_type": "explicit",
                                "confidence": "high",
                                "relation_target_id": "commitment-bias",
                            },
                        }
                    ],
                }
            ]
        },
    }
    pipeline_path = tmp_path / "pipeline.json"
    pipeline_hash = _write(pipeline_path, json.dumps(pipeline))
    return {
        "schema_version": custody.CONTRACT_SCHEMA,
        "status": "frozen_before_export",
        "case_id": "case-test",
        "provider_call_budget": 0,
        "runtime_change_authorized": False,
        "include_chunk_text": False,
        "source_conversation": {"path": "source.txt", "sha256": source_hash},
        "pipeline_result": {"path": "pipeline.json", "sha256": pipeline_hash},
        "output": {"path": "result.json"},
        "non_claims": ["not relevance proof"],
    }


def test_builds_stable_exact_graph_pressure_identity_without_text(tmp_path: Path) -> None:
    contract = _fixture(tmp_path)
    paths = custody.validate_contract(contract, root=tmp_path)
    result = custody.build_result(contract, paths=paths)
    assert result["status"] == "ready"
    assert result["graph_pressure_count"] == 1
    row = result["graph_pressures"][0]
    assert row["graph_pressure_id"].startswith(
        "graph::inversion::antagonist::commitment-bias::"
    )
    assert row["chunk_text_included"] is False
    assert "text" not in row
    assert row["source_review_status"] == "pending"
    assert result["consumer_injection_authorized"] is False


def test_unmatched_chunk_is_partial_and_not_silently_laundered(tmp_path: Path) -> None:
    contract = _fixture(tmp_path)
    pipeline_path = tmp_path / "pipeline.json"
    pipeline = json.loads(pipeline_path.read_text(encoding="utf-8"))
    pipeline["companion_cheat_sheet"]["anchors"][0]["chunks"][0]["text"] = "different"
    pipeline_path.write_text(json.dumps(pipeline), encoding="utf-8")
    contract["pipeline_result"]["sha256"] = hashlib.sha256(
        pipeline_path.read_bytes()
    ).hexdigest()
    paths = custody.validate_contract(contract, root=tmp_path)
    result = custody.build_result(contract, paths=paths)
    assert result["status"] == "partial"
    assert result["graph_pressure_count"] == 0
    assert result["exact_match_failures"][0]["match_count"] == 0


def test_contract_refuses_raw_text_or_provider_calls(tmp_path: Path) -> None:
    contract = _fixture(tmp_path)
    contract["include_chunk_text"] = True
    with pytest.raises(custody.ContractError, match="include_chunk_text"):
        custody.validate_contract(contract, root=tmp_path)
    contract["include_chunk_text"] = False
    contract["provider_call_budget"] = 1
    with pytest.raises(custody.ContractError, match="provider_call_budget"):
        custody.validate_contract(contract, root=tmp_path)
