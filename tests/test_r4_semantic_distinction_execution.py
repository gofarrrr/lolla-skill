from __future__ import annotations

import ast
import json
from pathlib import Path

from engine.system_b.r4_complementary_readers import value_sha256
from scripts.evals import finalize_r4_semantic_distinction_execution as finalizer


ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _without(value: dict, field: str) -> dict:
    return {key: item for key, item in value.items() if key != field}


def test_checked_in_execution_closeout_validates_provider_free() -> None:
    closeout = finalizer.validate()

    assert closeout["status"] == (
        "attempt_closed_mechanically_complete_semantic_restraint_failed"
    )
    assert closeout["run_id"] == "lolla-r4-semantic-distinction-holdout-a3"
    assert closeout["provider_calls"] == 4
    assert closeout["relationship_calls"] == 2
    assert closeout["provider_reported_cost_usd"] == 0.01107025
    assert closeout["maximum_provider_reported_cost_total_usd"] == 0.03
    assert closeout["cost_ceiling_met"] is True
    assert closeout["semantic_conclusion"]["semantic_hypothesis_supported"] is False
    assert closeout["decision"]["additional_provider_call_authorized"] is False


def test_all_four_calls_are_exact_and_reasoning_values_are_not_preserved() -> None:
    closeout = _load(finalizer.CLOSEOUT)
    calls = closeout["call_observations"]

    assert [row["call_ordinal"] for row in calls] == [1, 2, 3, 4]
    assert [row["task"] for row in calls] == [
        "uncertainty",
        "relationship",
        "uncertainty",
        "relationship",
    ]
    assert [row["case_id"] for row in calls] == [
        "v1-case01-flood-infrastructure",
        "v1-case01-flood-infrastructure",
        "v1-case04-component-sourcing",
        "v1-case04-component-sourcing",
    ]
    assert sum(row["provider_reported_cost_usd"] for row in calls) == 0.01107025
    assert all(row["operator_attribution_ok"] is True for row in calls)
    assert all(row["candidate_admitted"] is True for row in calls)
    assert all(row["finish_reason"] == "stop" for row in calls)
    assert all(row["reasoning_tokens"] == 0 for row in calls)
    assert all(
        row["reasoning_envelope_status"] == "reasoning_metadata_only"
        for row in calls
    )
    assert all(row["reasoning_values_preserved"] is False for row in calls)


def test_source_first_review_is_a_vector_and_records_the_restraint_failure() -> None:
    review = _load(finalizer.SOURCE_REVIEW)
    dimensions = {row["dimension"]: row for row in review["dimensions"]}
    cases = {row["case_id"]: row for row in review["case_reviews"]}

    assert review["status"] == "semantic_hypothesis_not_supported_restraint_failed"
    assert review["source_first_target_visible_to_provider"] is False
    assert review["target_opened_only_after_provider_execution_completed"] is True
    assert review["scalar_quality_score"] is None
    assert set(dimensions) == {
        "material_pressure_recovered",
        "false_positive_restraint",
        "evidence_precision",
        "role_placement",
        "relationship_fidelity",
        "operational_load_and_cost",
    }
    assert dimensions["material_pressure_recovered"]["verdict"] == "pass_narrowly"
    assert dimensions["false_positive_restraint"]["verdict"] == "fail"
    assert dimensions["evidence_precision"]["verdict"] == "fail"
    assert dimensions["relationship_fidelity"]["verdict"] == (
        "fail_semantic_restraint"
    )
    assert cases["v1-case01-flood-infrastructure"]["verdict"] == (
        "narrow_material_recovery_with_precision_and_overgeneration_failures"
    )
    assert cases["v1-case04-component-sourcing"]["verdict"] == "restraint_failed"


def test_every_compiled_record_has_an_explicit_source_first_verdict() -> None:
    review = _load(finalizer.SOURCE_REVIEW)
    reviewed_ids = {
        row["record_id"]
        for case in review["case_reviews"]
        for row in case["record_reviews"]
    }
    expected_ids = {
        record_id
        for tasks in finalizer.EXPECTED_RECORD_IDS.values()
        for record_ids in tasks.values()
        for record_id in record_ids
    }

    assert reviewed_ids == expected_ids
    assert len(reviewed_ids) == 8
    assert all(
        row["decisive_aliases"]
        for case in review["case_reviews"]
        for row in case["record_reviews"]
    )


def test_manifest_and_closeout_hashes_lock_the_complete_evidence_package() -> None:
    manifest = _load(finalizer.MANIFEST)
    review = _load(finalizer.SOURCE_REVIEW)
    closeout = _load(finalizer.CLOSEOUT)

    assert manifest["file_count"] == len(manifest["files"]) == 36
    assert manifest["provider_calls"] == 4
    assert manifest["provider_reported_cost_usd"] == 0.01107025
    assert manifest["manifest_sha256"] == value_sha256(
        _without(manifest, "manifest_sha256")
    )
    assert review["result_sha256"] == value_sha256(
        _without(review, "result_sha256")
    )
    assert closeout["result_sha256"] == value_sha256(
        _without(closeout, "result_sha256")
    )
    assert review["evidence_manifest_sha256"] == manifest["manifest_sha256"]
    assert closeout["evidence_manifest_sha256"] == manifest["manifest_sha256"]
    assert closeout["source_first_review_sha256"] == review["result_sha256"]
    assert all((ROOT / row["path"]).is_file() for row in manifest["files"])
    assert all(
        finalizer._file_sha(ROOT / row["path"]) == row["sha256"]
        and len((ROOT / row["path"]).read_bytes()) == row["utf8_bytes"]
        for row in manifest["files"]
    )
    assert not any(row["path"].endswith(".env") for row in manifest["files"])


def test_closeout_preserves_every_unauthorized_boundary() -> None:
    closeout = _load(finalizer.CLOSEOUT)
    preserved = closeout["preserved_boundaries"]
    decision = closeout["decision"]

    assert all(value is False for value in preserved.values())
    assert decision["this_attempt_may_be_retried"] is False
    assert decision["additional_provider_call_authorized"] is False
    assert decision["runtime_or_graph_integration_authorized"] is False
    assert decision["wider_corpus_execution_authorized"] is False
    assert decision["r5_product_evidence_authorized"] is False
    assert decision["production_model_selected"] is False
    assert decision["case01_and_case04_now_exposed_development_evidence"] is True
    assert decision["future_provider_validation_requires_new_holdout_and_authorization"] is True


def test_finalizer_itself_has_no_network_transport_dependency() -> None:
    tree = ast.parse(Path(finalizer.__file__).read_text(encoding="utf-8"))
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
