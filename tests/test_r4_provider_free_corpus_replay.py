from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from engine.system_b.r3_fresh_consumer import value_sha256
from scripts.evals import build_r4_provider_free_corpus_replay as builder


ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _by_id(items: list[dict]) -> dict[str, dict]:
    return {item["case_id"]: item for item in items}


def test_checked_in_replay_validates_without_provider() -> None:
    inventory, gaps, result = builder.validate()

    assert inventory["status"] == "provider_free_inventory_complete"
    assert inventory["provider_calls"] == 0
    assert inventory["provider_cost_usd"] == 0.0
    assert inventory["case_count"] == 12
    assert inventory["case_artifact_record_count"] == sum(
        case["relevant_artifact_count"] for case in inventory["cases"]
    )
    assert inventory["case_artifact_link_count"] == 543
    assert inventory["unique_case_linked_json_artifact_count"] == 400
    assert gaps["summary"]["reviewed_false_stand_down"] == 2
    assert result["provider_calls"] == 0
    assert result["provider_cost_usd"] == 0.0
    assert result["selected_next_repair"]["implementation_authorized_by_this_result"] is False
    assert result["selected_next_repair"]["provider_call_authorized_by_this_result"] is False


def test_all_sources_are_24_messages_and_hash_locked_across_three_inputs() -> None:
    inventory, _gaps, _result = builder.validate()
    manifest = _load(builder.SOURCE_MANIFEST)
    review = _by_id(_load(builder.NATURALIZED_REVIEW)["cases"])
    preflight = _by_id(
        [
            item
            for item in _load(builder.PREFLIGHT_REPORT)["artifacts"]
            if item["split"] == "transfer"
        ]
    )

    assert len(inventory["cases"]) == 12
    assert {item["case_id"] for item in manifest["transfer_cases"]} == {
        item["case_id"] for item in inventory["cases"]
    }
    for source in manifest["transfer_cases"]:
        case_id = source["case_id"]
        record = _by_id(inventory["cases"])[case_id]
        assert source["message_count"] == 24
        assert record["authoritative_source"]["message_count"] == 24
        assert builder._sha(ROOT / source["path"]) == source["sha256"]
        assert review[case_id]["naturalized_sha256"] == source["sha256"]
        assert preflight[case_id]["source_sha256"] == source["sha256"]
        assert preflight[case_id]["message_count"] == 24


def test_completion_failure_and_missingness_states_are_not_conflated() -> None:
    inventory, gaps, _result = builder.validate()
    cases = _by_id(inventory["cases"])
    gap_cases = _by_id(gaps["cases"])

    assert len(builder.COMPLETE_CASES) == 7
    for case_id in builder.COMPLETE_CASES:
        surfaces = cases[case_id]["surfaces"]
        assert surfaces["starting_position"]["state"] == "complete"
        assert surfaces["current_position"]["state"] == "complete"
        assert surfaces["qualification"]["state"] == "complete"
        assert surfaces["failure_artifact"]["state"] == "not_applicable"
        assert surfaces["direct_pressure"]["state"] == "complete"
        assert surfaces["graph_pressure"]["state"] == "complete"

    join = cases[builder.ROLE_JOIN_FAILURE]["surfaces"]
    assert join["starting_position"] == {
        "explicit_record_count": 0,
        "note": "Provider output was quarantined; zero admitted records is not a semantic empty result.",
        "state": "failed",
    }
    assert join["current_position"]["state"] == "partial"
    assert join["qualification"]["state"] == "partial"
    assert join["failure_artifact"]["state"] == "complete"

    for case_id in builder.TRANSPORT_FAILURES:
        surfaces = cases[case_id]["surfaces"]
        assert surfaces["starting_position"]["state"] == "failed"
        assert surfaces["current_position"]["state"] == "missing"
        assert surfaces["qualification"]["state"] == "missing"
        assert surfaces["failure_artifact"]["state"] == "complete"
        assert gap_cases[case_id]["first_observable_gap"]["stage"] == "starting_role_transport"


def test_zero_record_is_empty_output_not_missing_contract() -> None:
    inventory, _gaps, _result = builder.validate()
    case02 = _by_id(inventory["cases"])["v1-case02-discharge-transport"]

    assert case02["surfaces"]["qualification"] == {
        "explicit_record_count": 0,
        "state": "complete",
    }
    for case in inventory["cases"]:
        assert case["surfaces"]["unresolved_matter"]["state"] == "missing"
        assert case["surfaces"]["reopen_condition"]["state"] == "missing"
        assert case["surfaces"]["cross_thread_relationship"]["state"] == "missing"


def test_source_locators_resolve_without_claiming_semantic_grounding() -> None:
    inventory, _gaps, _result = builder.validate()

    for case in inventory["cases"]:
        metrics = case["source_locator_metrics"]
        assert metrics["alias_count"] > 0
        assert metrics["alias_turn_range"] == [1, 12]
        assert set(metrics["alias_speaker_counts"]) == {"assistant", "user"}
        assert metrics["orphan_role_source_reference_count"] == 0
        assert metrics["semantic_grounding_inferred"] is False
        assert (
            sum(metrics["admitted_role_source_reference_speaker_counts"].values())
            == metrics["admitted_role_source_reference_count"]
        )


def test_fan_in_is_a_vector_and_primary_graph_never_activated() -> None:
    inventory, gaps, _result = builder.validate()

    for case in inventory["cases"]:
        load = case["fan_in_load"]
        assert load["annotated_role_input_utf8_bytes"] > 0
        assert load["source_alias_count"] > 0
        assert load["interpretation"] == "load vector only; no direction of quality is inferred"
        assert load["graph_active_candidate_count"] == 0
        assert load["graph_reserve_candidate_count"] == 0
    assert gaps["summary"]["primary_graph_active_candidates"] == 0
    assert gaps["summary"]["graph_pressure_provider_calls"] == 0


def test_false_stand_down_uses_only_frozen_diagnostic_review() -> None:
    _inventory, gaps, _result = builder.validate()
    cases = _by_id(gaps["cases"])
    false_ids = {
        case_id
        for case_id, case in cases.items()
        if case["source_review_disposition"] == "false_stand_down"
    }

    assert false_ids == {
        "v1-case01-flood-infrastructure",
        "v1-case02-discharge-transport",
    }
    assert all(
        cases[case_id]["first_observable_gap"]["kind"] == "reviewed_false_stand_down"
        for case_id in false_ids
    )
    assert cases["v1-case03-executive-hire"]["source_review_disposition"] == "correct"


def test_inventory_is_metadata_only_and_partitions_exposed_work() -> None:
    inventory, _gaps, _result = builder.validate()
    serialized = json.dumps(inventory, sort_keys=True)
    all_artifacts = [
        artifact
        for case in inventory["cases"]
        for artifact in case["relevant_artifacts"]
    ]

    assert all(artifact["content_copied"] is False for artifact in all_artifacts)
    assert any(
        artifact["evidence_partition"] == "exposed_development_or_review"
        and "exposed" in artifact["classifications"]
        and "transfer" not in artifact["classifications"]
        for artifact in all_artifacts
    )
    for case in inventory["cases"]:
        assert [item["format"] for item in case["receipt_artifacts"]] == [
            "json",
            "markdown",
        ]
        assert all(
            builder._sha(ROOT / item["path"]) == item["sha256"]
            for item in case["receipt_artifacts"]
        )
    historical_failure = _load(
        builder.TRANSFER_ROOT
        / "v1-case09-software-migration-primary"
        / "result.json"
    )
    private_user_id = historical_failure["calls"][0]["provider_error"]["user_id"]
    assert private_user_id
    assert private_user_id not in serialized
    assert '"provider_error"' not in serialized
    assert '"user_id"' not in serialized


def test_measurement_contract_has_ten_non_scalar_dimensions() -> None:
    contract = _load(builder.MEASUREMENT_CONTRACT)
    ids = {item["id"] for item in contract["dimensions"]}

    assert ids == {
        "system_level_coverage",
        "role_placement",
        "temporal_fidelity",
        "speaker_ownership",
        "cross_thread_integrity",
        "source_precision",
        "fan_in_load",
        "false_stand_down",
        "over_fragmentation",
        "custody_and_replay",
    }
    assert contract["aggregation"] == {
        "automatic_release_gate": None,
        "allowed": "Report a vector of exact mechanical observations beside explicitly labeled human or probabilistic judgments.",
        "composite_score": None,
        "quality_badge": None,
    }
    assert contract["budget"]["provider_calls_authorized"] == 0


def test_builder_imports_no_network_or_provider_sdk() -> None:
    tree = ast.parse(Path(builder.__file__).read_text(encoding="utf-8"))
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }

    assert imported.isdisjoint(
        {
            "anthropic",
            "google",
            "httpx",
            "openai",
            "requests",
            "urllib",
        }
    )
    assert "os.environ" not in Path(builder.__file__).read_text(encoding="utf-8")


def test_frozen_inventory_excludes_explicit_downstream_r4_outputs() -> None:
    inventory, _gaps, _result = builder.validate()
    recorded = {
        artifact["path"]
        for case in inventory["cases"]
        for artifact in case["relevant_artifacts"]
    }

    assert builder.DOWNSTREAM_OUTPUT_ROOTS == (
        ROOT / "research/lolla-r4-conversation-state-fan-in-2026-07-13",
        ROOT / "research/lolla-r4-complementary-reader-preflight-2026-07-13",
    )
    assert builder.DOWNSTREAM_INPUT_PATHS == (
        ROOT / "docs/evals/lolla-r4-complementary-reader-experiment-contract-v1.json",
        ROOT / "docs/evals/lolla-r4-complementary-reader-source-first-target-v1.json",
    )
    assert not any(
        path.startswith(
            (
                "research/lolla-r4-conversation-state-fan-in-2026-07-13/",
                "research/lolla-r4-complementary-reader-preflight-2026-07-13/",
            )
        )
        for path in recorded
    )
    assert not set(recorded).intersection(
        {
            "docs/evals/lolla-r4-complementary-reader-experiment-contract-v1.json",
            "docs/evals/lolla-r4-complementary-reader-source-first-target-v1.json",
        }
    )


def test_self_hashes_and_cross_hashes_are_exact() -> None:
    inventory, gaps, result = builder.validate()

    assert inventory["result_sha256"] == value_sha256(
        {key: value for key, value in inventory.items() if key != "result_sha256"}
    )
    assert gaps["result_sha256"] == value_sha256(
        {key: value for key, value in gaps.items() if key != "result_sha256"}
    )
    assert result["result_sha256"] == value_sha256(
        {key: value for key, value in result.items() if key != "result_sha256"}
    )
    assert gaps["source_inventory_result_sha256"] == inventory["result_sha256"]
    assert result["inventory_result_sha256"] == inventory["result_sha256"]
    assert result["gap_matrix_result_sha256"] == gaps["result_sha256"]


def test_tampered_inventory_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    inventory = _load(builder.INVENTORY_PATH)
    inventory["provider_calls"] = 1
    tampered = tmp_path / "inventory.json"
    tampered.write_text(json.dumps(inventory), encoding="utf-8")
    monkeypatch.setattr(builder, "INVENTORY_PATH", tampered)

    with pytest.raises(builder.R4ReplayError, match="self-hash drifted"):
        builder.validate()


def test_tampered_source_manifest_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    manifest = _load(builder.SOURCE_MANIFEST)
    manifest["transfer_cases"][0]["sha256"] = "0" * 64
    tampered = tmp_path / "manifest.json"
    tampered.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(builder, "SOURCE_MANIFEST", tampered)

    with pytest.raises(builder.R4ReplayError, match="source custody drifted"):
        builder.validate()


def test_rebuild_is_deterministic() -> None:
    before = tuple(builder._sha(path) for path in (builder.INVENTORY_PATH, builder.GAP_MATRIX_PATH, builder.RESULT_PATH))
    builder.build()
    after = tuple(builder._sha(path) for path in (builder.INVENTORY_PATH, builder.GAP_MATRIX_PATH, builder.RESULT_PATH))

    assert after == before
