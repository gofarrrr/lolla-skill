from __future__ import annotations

from pathlib import Path

import pytest

from scripts.evals import build_graph_attribution_preflight as v1
from scripts.evals import build_graph_attribution_preflight_v2 as v2
from tests.test_graph_attribution_preflight import _fixture


def _add_complete_consumer_surface(contract: dict, tmp_path: Path) -> None:
    pipeline_row = next(
        row for row in contract["inputs"] if row["role"] == "stage_a_pipeline_result"
    )
    pipeline_path = tmp_path / pipeline_row["path"]
    pipeline = v1._load_json(pipeline_path)
    pipeline["companion_cheat_sheet"] = {
        "anchors": [
            {
                "model_id": "margin-of-safety",
                "chunks": [
                    {
                        "chunk_type": "antagonist",
                        "text": "Confirmation Bias: challenge the safety estimate",
                        "provenance": {
                            "source_layer": "wave3",
                            "extraction_type": "explicit",
                            "confidence": "high",
                            "relation_target_id": "confirmation-bias",
                        },
                    }
                ],
            }
        ]
    }
    pipeline_path.write_text(v1.json.dumps(pipeline, indent=2) + "\n", encoding="utf-8")
    pipeline_row["sha256"] = v1._sha256(pipeline_path)


def test_v2_finds_graph_chunks_hidden_inside_companion_anchor(
    tmp_path: Path,
) -> None:
    contract = _fixture(tmp_path)
    _add_complete_consumer_surface(contract, tmp_path)
    contract["schema_version"] = v2.CONTRACT_SCHEMA
    contract["repairs_contract_sha256"] = "a" * 64
    contract["repairs_result_sha256"] = "b" * 64
    paths = v2.validate_contract(contract, root=tmp_path)
    result = v2.build_result(contract, root=tmp_path, paths=paths)
    surface = result["complete_step6_consumer_surface"]
    assert surface["companion_graph_chunk_count"] == 1
    assert surface["individual_graph_chunk_disposition_custody"] is False
    assert (
        result["provider_free_baselines"][
            "graph_disabled_complete_step6_context"
        ]["status"]
        == "requires_frozen_replay"
    )
    assert result["decision_evidence"]["paid_graph_ablation_candidate"] is False


def test_v2_requires_prospective_repair_hashes(tmp_path: Path) -> None:
    contract = _fixture(tmp_path)
    contract["schema_version"] = v2.CONTRACT_SCHEMA
    with pytest.raises(v1.ContractError, match="repairs_contract_sha256"):
        v2.validate_contract(contract, root=tmp_path)
