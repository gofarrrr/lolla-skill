from __future__ import annotations

import copy
import json
from pathlib import Path

from engine.system_b.conversation_state_candidates import build_source_catalog
from engine.system_b.reasoning_process_contracts import schema_metrics
from engine.system_b.reasoning_process_view_specific_v3 import (
    SUPPORTED_VIEWS,
    compile_response_v3_recordwise,
    remove_legacy_mechanical_parking,
    response_schema_v3,
)
from scripts.evals.replay_reasoning_process_view_specific_v3 import replay


ROOT = Path(__file__).resolve().parents[1]
CASE = "amb1-case02-nonprofit-scale"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_v3_schemas_remove_mechanical_parking_and_remain_bounded() -> None:
    for view_kind in SUPPORTED_VIEWS:
        schema = response_schema_v3(view_kind)
        assert "park_unselected_auxiliary_observations" not in schema["properties"]
        assert "park_unselected_auxiliary_observations" not in schema["required"]
        metrics = schema_metrics(schema)
        assert metrics["bytes"] <= 12000
        assert metrics["depth"] <= 8


def test_case02_v3_replay_admits_all_reviewed_records_without_calls(
    tmp_path: Path,
) -> None:
    report = replay(root=ROOT, output=tmp_path / "v3")
    assert report["status"] == "four_reader_transfer_envelope_provider_free_pass"
    assert report["summary"] == {
        "view_count": 4,
        "record_count": 12,
        "admitted_record_count": 12,
        "quarantined_record_count": 0,
        "mechanical_parking_fields_removed": 4,
        "model_semantic_records_changed": 0,
        "replay_provider_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "runtime_calls": 0,
    }
    assert report["decision"]["provider_calls_authorized"] is False


def test_v3_projection_changes_only_legacy_mechanical_field() -> None:
    for view_kind in SUPPORTED_VIEWS:
        call = _load(
            ROOT
            / "research/reasoning-process-view-specific-v2-probe-2026-07-11/calls"
            / f"{view_kind}.json"
        )
        original = call["candidate_payload"]
        projected = remove_legacy_mechanical_parking(original)
        assert projected["records"] == original["records"]
        assert projected["status"] == original["status"]
        assert projected["global_limitations"] == original["global_limitations"]
        assert "park_unselected_auxiliary_observations" not in projected


def test_v3_record_level_custody_quarantines_bad_sibling_only() -> None:
    view_kind = "challenge_and_revision_response"
    call = _load(
        ROOT
        / "research/reasoning-process-view-specific-v2-probe-2026-07-11/calls"
        / f"{view_kind}.json"
    )
    response = remove_legacy_mechanical_parking(call["candidate_payload"])
    response = copy.deepcopy(response)
    response["records"][1]["prior_claim_or_frame_evidence_ids"] = ["e999"]
    wrapper = _load(
        ROOT
        / "research/reasoning-process-view-specific-interface-2026-07-11/cases"
        / CASE
        / view_kind
        / "reader-packet.json"
    )
    source_path = wrapper["reader_packet"]["source"]["source_path"]
    source_text = (ROOT / source_path).read_text(encoding="utf-8")
    catalog = build_source_catalog(source_text=source_text, source_path=source_path)
    ledger = _load(
        ROOT
        / "research/reasoning-process-phase1-ledger-2026-07-11/cases"
        / CASE
        / "ledger.json"
    )
    compiled = compile_response_v3_recordwise(
        response=response,
        wrapper=wrapper,
        base_ledger=ledger,
        catalog=catalog,
        record_identity="v3-partial-test",
        producer_kind="model",
        producer_id=call["requested_model"],
    )
    assert compiled["window_terminal_disposition"] == "partially_compiled"
    assert sum(item["terminal_state"] == "admitted" for item in compiled["records"]) == 2
    assert sum(item["terminal_state"] == "quarantined" for item in compiled["records"]) == 1
    assert compiled["boundary"]["record_level_validation_weakened"] is False
