from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.reasoning_process_chronological_shards import (
    build_chronological_shard_packets,
    validate_chronological_shard_packet,
)
from scripts.evals.review_reasoning_process_chronological_shards import review

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "research/reasoning-process-chronological-shards-2026-07-11/report.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_chronological_shards_rebuild_and_partition_each_family() -> None:
    case_id = "amb1-case05-family-archive"
    source_path = f"research/designed-ambiguous-pool-v1-2026-07-10/capture-ready-cases/{case_id}.txt"
    source_text = (ROOT / source_path).read_text(encoding="utf-8")
    full = _load(
        ROOT
        / "research/reasoning-process-view-specific-interface-2026-07-11/cases"
        / case_id
        / "position_and_decision_trajectory/reader-packet.json"
    )
    packets = build_chronological_shard_packets(
        case_id=case_id,
        source_path=source_path,
        source_text=source_text,
        global_alias_map=full["evidence_alias_map"],
    )
    assert len(packets) == 12
    expected = {item["alias"] for item in full["evidence_alias_map"]}
    for view in {item["packet"]["view_kind"] for item in packets}:
        aliases = [
            alias
            for item in packets
            if item["packet"]["view_kind"] == view
            for alias in item["packet"]["focal_region"]["evidence_aliases"]
        ]
        assert len(aliases) == len(set(aliases))
        assert set(aliases) == expected
    for packet in packets:
        assert validate_chronological_shard_packet(packet, source_text=source_text)["status"] == "chronological_shard_packet_valid"


def test_position_endpoint_preserves_first_and_final_pairs_without_global_source() -> None:
    report = _load(REPORT_PATH)
    for case in report["cases"]:
        endpoints = [
            item
            for item in case["artifacts"]
            if item["view_kind"] == "position_and_decision_trajectory"
            and item["shard_kind"] == "position_endpoint_comparison"
        ]
        assert len(endpoints) == 1
        assert endpoints[0]["focal_turn_indices"] == [1, 7]
        wrapper = _load(ROOT / endpoints[0]["path"])
        assert wrapper["packet"]["boundary"]["auxiliary_ledger_included"] is False
        assert wrapper["packet"]["boundary"]["semantic_prefilter_performed"] is False


def test_shard_design_is_bounded_but_more_expensive_than_failed_global_design() -> None:
    report = _load(REPORT_PATH)
    assert report["summary"]["future_total_calls_per_case"] == 19
    assert report["summary"]["future_total_max_records_per_case"] == 38
    assert max(case["maximum_packet_utf8_bytes"] for case in report["cases"]) <= 12000
    assert all(case["shard_count"] == 12 for case in report["cases"])
    assert report["boundary"]["global_synthesis_authorized"] is False
    assert report["boundary"]["provider_probe_authorized"] is False


def test_all_twenty_protected_targets_are_colocated_provider_free() -> None:
    result = review(_load(REPORT_PATH))
    assert result["status"] == "provider_free_target_representation_pass"
    assert result["summary"]["protected_targets_colocated"] == 20
    assert result["decision"]["prompt_schema_and_record_custody_design_authorized"] is True
    assert result["decision"]["provider_probe_authorized"] is False
