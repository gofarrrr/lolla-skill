from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.evals import build_graph_attribution_preflight as preflight


def _write(path: Path, value: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: object) -> str:
    return _write(path, json.dumps(value, indent=2) + "\n")


def _card(
    card_id: str,
    model_id: str,
    source: str,
    chunks: list[str],
) -> dict:
    affordances = []
    absences = []
    for chunk_id in chunks:
        row = {"chunk_id": chunk_id, "status": "supported"}
        if chunk_id.startswith("aff::"):
            affordances.append(row)
        else:
            absences.append(row)
    return {
        "card_id": card_id,
        "model_id": model_id,
        "selection_source": source,
        "selection_reason": source,
        "selected_affordance_cards": affordances,
        "selected_absence_records": absences,
    }


def _fixture(tmp_path: Path, *, graph_selected: bool = False) -> dict:
    packet_items = [
        {
            "pressure_id": "evidence-buffer",
            "lineage_chunk_ids": [
                "aff::margin-of-safety.evidence-buffer",
                "aff::prospect-theory.loss-frame-check",
            ],
            "challenge": "Verify the buffer and frame.",
        }
    ]
    cards = [
        _card(
            "card-margin",
            "margin-of-safety",
            "lane_preserved",
            ["aff::margin-of-safety.evidence-buffer"],
        ),
        _card(
            "card-prospect",
            "prospect-theory",
            "embedding_model_recall",
            ["aff::prospect-theory.loss-frame-check"],
        ),
    ]
    lane_candidates = [
        {
            "model_id": "margin-of-safety",
            "source": "lane2_companion_anchor",
        },
        {
            "model_id": "inversion",
            "source": "lane3_frame_route_candidate",
        },
    ]
    private_sources = [
        {"source_kind": "lane2_anchor"},
        {"source_kind": "v60_selected_card"},
    ]
    if graph_selected:
        packet_items.append(
            {
                "pressure_id": "graph-pressure",
                "lineage_chunk_ids": ["aff::confirmation-bias.adversarial-check"],
                "challenge": "Check the adversarial estimate.",
            }
        )
        cards.append(
            _card(
                "card-confirmation",
                "confirmation-bias",
                "graph_expansion",
                ["aff::confirmation-bias.adversarial-check"],
            )
        )
        lane_candidates.append(
            {
                "model_id": "confirmation-bias",
                "source": "companion_graph_expansion",
            }
        )
        private_sources.append({"source_kind": "graph_expansion"})

    pipeline = {
        "delta_card": {"findings": []},
        "companion_card": {
            "expansions": [
                {
                    "source_model_id": "margin-of-safety",
                    "relation_type": "antagonist",
                    "model_id": "confirmation-bias",
                    "substrate_chunk": "challenge the safety estimate",
                }
            ]
        },
        "v60_enrichment": {
            "selection_policy": {"max_cards": 2},
            "candidate_pool": {
                "lane_candidates": lane_candidates,
                "embedding_model_hits": [
                    {"rank": 1, "model_id": "prospect-theory", "score": 0.8},
                    {"rank": 2, "model_id": "endowment-effect", "score": 0.7},
                ],
            },
            "selected_cards": cards,
        },
    }
    artifacts: dict[str, tuple[Path, str]] = {}

    def add(role: str, relative: str, value: object, *, raw: bool = False) -> None:
        path = tmp_path / relative
        digest = _write(path, str(value)) if raw else _write_json(path, value)
        artifacts[role] = (path, digest)

    add("source_conversation", "source.txt", "conversation", raw=True)
    add("stage_a_pipeline_result", "pipeline.json", pipeline)
    add(
        "stage_a_private_table_snapshot",
        "private.json",
        {"source_items": private_sources},
    )
    add("stage_a_v60_snapshot", "v60.json", {"selected_cards": cards})
    add("stage_a_preliminary_pressure_review", "review.json", {"status": "passed"})
    add("stage_a_pressure_packet", "packet.json", {"pressure_items": packet_items})
    add(
        "stage_b_revealed_comparison",
        "revealed.json",
        {
            "blind_read_survived_reveal": {
                "immediate_action_difference": "not_material"
            },
            "claim_classification": {
                "unique_answer_improvement": "not_demonstrated"
            },
        },
    )
    add(
        "stage_b_decision",
        "decision.json",
        {"gate_5": {"decision": "consideration_only"}},
    )
    contract = {
        "schema_version": preflight.CONTRACT_SCHEMA,
        "status": "frozen_before_replay",
        "case_id": "case-test",
        "provider_call_budget": 0,
        "runtime_change_authorized": False,
        "inputs": [
            {
                "role": role,
                "path": str(path.relative_to(tmp_path)),
                "sha256": digest,
            }
            for role, (path, digest) in sorted(artifacts.items())
        ],
        "output": {"path": "result.json"},
    }
    return contract


def test_provider_free_preflight_proves_unconsumed_graph_is_noop(tmp_path: Path) -> None:
    contract = _fixture(tmp_path)
    paths = preflight.validate_contract(contract, root=tmp_path)
    result = preflight.build_result(contract, root=tmp_path, paths=paths)
    evidence = result["decision_evidence"]
    assert evidence["graph_expansion_count"] == 1
    assert evidence["graph_specific_admitted_pressure_count"] == 0
    assert evidence["graph_expansions_entered_v60_candidate_pool"] is False
    assert evidence["graph_expansions_entered_v60_selected_cards"] is False
    assert evidence["paid_graph_ablation_candidate"] is False
    assert (
        result["provider_free_baselines"]["graph_disabled_artifact_replay"]["status"]
        == "exact_noop_at_recorded_handoff"
    )


def test_graph_selected_pressure_is_detected_without_claiming_answer_value(
    tmp_path: Path,
) -> None:
    contract = _fixture(tmp_path, graph_selected=True)
    paths = preflight.validate_contract(contract, root=tmp_path)
    result = preflight.build_result(contract, root=tmp_path, paths=paths)
    evidence = result["decision_evidence"]
    assert evidence["graph_specific_admitted_pressure_ids"] == ["graph-pressure"]
    assert evidence["case10_can_identify_graph_contribution"] is True
    assert (
        result["provider_free_baselines"]["graph_disabled_artifact_replay"]["status"]
        == "not_exact"
    )


def test_hash_drift_is_rejected(tmp_path: Path) -> None:
    contract = _fixture(tmp_path)
    source_row = next(
        row for row in contract["inputs"] if row["role"] == "source_conversation"
    )
    (tmp_path / source_row["path"]).write_text("drift", encoding="utf-8")
    with pytest.raises(preflight.ContractError, match="hash drift"):
        preflight.validate_contract(contract, root=tmp_path)


def test_contract_refuses_provider_budget_or_runtime_change(tmp_path: Path) -> None:
    contract = _fixture(tmp_path)
    contract["provider_call_budget"] = 1
    with pytest.raises(preflight.ContractError, match="provider_call_budget"):
        preflight.validate_contract(contract, root=tmp_path)
    contract["provider_call_budget"] = 0
    contract["runtime_change_authorized"] = True
    with pytest.raises(preflight.ContractError, match="runtime_change_authorized"):
        preflight.validate_contract(contract, root=tmp_path)
