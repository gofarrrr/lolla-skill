from __future__ import annotations

import ast
import json
from pathlib import Path

from engine.system_b.r3_fresh_consumer import value_sha256
from scripts.evals import build_r4_conversation_state_fan_in_replay as builder


ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_checked_in_replay_validates_provider_free() -> None:
    summary, cases = builder.validate()

    assert summary["status"] == "provider_free_fan_in_replay_complete"
    assert summary["provider_calls"] == 0
    assert summary["provider_cost_usd"] == 0.0
    assert summary["runtime_graph_prompt_or_model_changes"] == 0
    assert set(cases) == set(builder.CASE_IDS)
    assert summary["aggregate"] == {
        "case_count": 4,
        "reader_result_count": 24,
        "reader_state_counts": {
            "complete": 5,
            "completed_zero": 1,
            "partial": 2,
            "failed": 2,
            "missing": 14,
        },
        "admitted_record_count": 7,
        "source_locator_count": 21,
        "all_handoffs_within_bounds": True,
    }


def test_complete_zero_partial_failed_and_missing_paths_are_exact() -> None:
    _summary, cases = builder.validate()

    assert cases["v1-case01-flood-infrastructure"]["fan_in"]["reader_state_counts"] == {
        "complete": 3,
        "completed_zero": 0,
        "partial": 0,
        "failed": 0,
        "missing": 3,
    }
    case02 = cases["v1-case02-discharge-transport"]
    qualification = next(
        result
        for result in case02["reader_results"]
        if result["surface"] == "qualification"
    )
    assert qualification["state"] == "completed_zero"
    assert qualification["records"] == []
    assert qualification["artifact"] is not None
    assert all(
        result["state"] == "missing"
        for result in case02["reader_results"]
        if result["surface"]
        in {"unresolved_matter", "reopen_condition", "cross_thread_relationship"}
    )

    case06 = cases[builder.ROLE_JOIN_FAILURE]
    by_surface = {result["surface"]: result for result in case06["reader_results"]}
    assert by_surface["starting_position"]["state"] == "failed"
    assert by_surface["starting_position"]["issue"]["code"] == "schema_or_custody_failed"
    assert by_surface["current_position"]["state"] == "partial"
    assert by_surface["qualification"]["state"] == "partial"
    assert len(by_surface["current_position"]["records"]) == 1
    assert len(by_surface["qualification"]["records"]) == 1

    case09 = cases[builder.TRANSPORT_FAILURE]
    by_surface = {result["surface"]: result for result in case09["reader_results"]}
    assert by_surface["starting_position"]["state"] == "failed"
    assert by_surface["starting_position"]["issue"]["code"] == "transport_failed"
    assert by_surface["current_position"]["state"] == "missing"
    assert by_surface["current_position"]["issue"]["code"] == "upstream_dependency_unavailable"
    assert case09["status"] == "conversation_state_fan_in_unavailable"


def test_provider_authored_payloads_and_exact_locators_are_preserved() -> None:
    _summary, cases = builder.validate()

    for case_id, value in cases.items():
        aliases = {
            item["alias"]: item for item in value["source_registry"]["aliases"]
        }
        for result in value["reader_results"]:
            for record in result["records"]:
                assert record["semantic_payload"]["case_id"] == case_id
                assert record["semantic_payload"]["role_record_id"] == record["record_id"]
                assert record["surface"] == result["surface"]
                for locator in record["source_locators"]:
                    assert locator == aliases[locator["alias"]]
                    assert locator["speaker"] in {"user", "assistant"}
                    assert 1 <= locator["turn_index"] <= 24
        assert value["boundary"]["semantic_role_inferred_by_code"] is False
        assert value["boundary"]["prose_keywords_or_chronology_used_for_meaning"] is False
        assert value["boundary"]["missing_reader_output_filled"] is False


def test_private_transport_error_is_not_copied_into_fan_in() -> None:
    _summary, cases = builder.validate()
    historical = _load(
        builder.TRANSFER_ROOT
        / f"{builder.TRANSPORT_FAILURE}-primary"
        / "call-01-starting-result.json"
    )
    private_user_id = historical["provider_error"]["user_id"]
    serialized = json.dumps(cases[builder.TRANSPORT_FAILURE], sort_keys=True)

    assert private_user_id
    assert private_user_id not in serialized
    assert "provider_error" not in serialized
    assert "requires more credits" not in serialized
    assert "raw provider error details are not copied" in serialized


def test_replay_outputs_and_summary_have_exact_hash_custody() -> None:
    summary, cases = builder.validate()

    assert summary["result_sha256"] == value_sha256(
        {key: item for key, item in summary.items() if key != "result_sha256"}
    )
    for row in summary["cases"]:
        value = cases[row["case_id"]]
        path = ROOT / row["fan_in_path"]
        assert builder._sha(path) == row["fan_in_file_sha256"]
        assert value["result_sha256"] == row["fan_in_result_sha256"]
        assert value["fan_in"]["within_bounds"] is True
        assert value["fan_in"]["interpretation"] == (
            "mechanical load vector only; no direction of quality is inferred"
        )


def test_replay_selects_preparation_without_authorizing_a_call() -> None:
    summary, _cases = builder.validate()
    decision = summary["next_experiment_decision"]

    assert decision["provider_free_preparation_earned"] is True
    assert decision["provider_call_authorized"] is False
    assert decision["runtime_integration_authorized"] is False
    assert summary["expected_changed_measurement"]["status"] == "passed_provider_free"
    assert summary["expected_changed_measurement"]["semantic_improvement_claimed"] is False


def test_builder_imports_no_network_or_provider_sdk() -> None:
    source = Path(builder.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }

    assert imported.isdisjoint(
        {"anthropic", "google", "httpx", "openai", "requests", "urllib"}
    )
    assert "os.environ" not in source


def test_rebuild_is_deterministic() -> None:
    paths = [builder.SUMMARY_PATH] + [
        builder.OUTPUT_ROOT / case_id / "fan-in.json" for case_id in builder.CASE_IDS
    ]
    before = tuple(builder._sha(path) for path in paths)
    builder.build()
    after = tuple(builder._sha(path) for path in paths)

    assert after == before
