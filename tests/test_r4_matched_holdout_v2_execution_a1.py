from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research/lolla-r4-matched-holdout-v2-execution-2026-07-14-a1"


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_raw_execution_a1_is_sealed_provider_free() -> None:
    from scripts.evals import seal_r4_matched_holdout_v2_execution_a1 as seal

    summary = seal.validate_raw()

    assert summary == {
        "status": "raw_execution_sealed_before_semantic_review",
        "provider_calls": 8,
        "provider_reported_cost_usd": 0.01408165,
        "authorization_consumed": True,
    }


def test_authorization_is_consumed_and_cannot_authorize_a_second_run() -> None:
    value = _load(OUTPUT / "authorization-consumption.json")

    assert value["authorization_sha256"] == (
        "3cfe4f0fa5d4be3b8941ca54e9f0fcc4f25c17f354788ff9db8c995366ddd49d"
    )
    assert value["status"] == "consumed_terminal_run_complete"
    assert value["provider_transport_constructed"] is True
    assert value["provider_calls_attempted"] == 8
    assert value["provider_calls_completed"] == 8
    assert value["second_execution_authorized"] is False
    assert value["retry_or_replacement_call_authorized"] is False


def test_raw_manifest_locks_every_runner_file_and_terminal_call() -> None:
    manifest = _load(OUTPUT / "raw-evidence-manifest.json")

    assert manifest["status"] == "raw_execution_sealed_before_semantic_review"
    assert manifest["file_count"] == len(manifest["files"]) == 25
    assert manifest["provider_calls"] == 8
    assert manifest["provider_reported_cost_usd"] == 0.01408165
    assert [row["ordinal"] for row in manifest["calls"]] == list(range(1, 9))
    assert all(row["operator_attribution_ok"] for row in manifest["calls"])
    assert all(row["local_admission_status"] == "passed" for row in manifest["calls"])
    assert all(row["reasoning_tokens"] == 0 for row in manifest["calls"])
    assert all(row["raw_response_preserved_exactly"] for row in manifest["calls"])
    assert all((ROOT / row["path"]).is_file() for row in manifest["files"])


def test_sealer_has_no_network_or_semantic_review_dependency() -> None:
    from scripts.evals import seal_r4_matched_holdout_v2_execution_a1 as seal

    source = Path(seal.__file__).read_text(encoding="utf-8")
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
    assert "target" not in source.lower()
    assert "source-first" not in source.lower()


def test_sealer_rejects_raw_response_tampering(tmp_path: Path) -> None:
    from scripts.evals import seal_r4_matched_holdout_v2_execution_a1 as seal

    copied = tmp_path / "execution"
    copied.mkdir()
    for path in OUTPUT.glob("call-*"):
        (copied / path.name).write_bytes(path.read_bytes())
    (copied / "result.json").write_bytes((OUTPUT / "result.json").read_bytes())
    raw = copied / "call-01-raw-response.bin"
    raw.write_bytes(raw.read_bytes() + b"tamper")

    with pytest.raises(seal.R4MatchedExecutionA1SealError, match="raw response"):
        seal._build_raw_values(output=copied)


def test_checked_in_source_first_closeout_validates_provider_free() -> None:
    from scripts.evals import finalize_r4_matched_holdout_v2_execution_a1 as final

    closeout = final.validate()

    assert closeout["status"] == (
        "execution_complete_residual_task_repair_insufficient"
    )
    assert closeout["decision"] == "residual_task_repair_insufficient"
    assert closeout["provider_calls"] == 8
    assert closeout["provider_reported_cost_usd"] == 0.01408165
    assert closeout["authorization_consumed"] is True
    assert closeout["additional_provider_call_authorized"] is False
    assert closeout["scalar_quality_score"] is None
    assert closeout["verification"]["focused_tests"] == {
        "passed": 111,
        "failed": 0,
    }
    assert closeout["verification"]["full_repository_suite"] == {
        "passed": 4939,
        "failed": 0,
        "subtests_passed": 93,
        "warnings": 1,
        "warning_scope": "pre_existing_datetime_utcnow_deprecation",
    }
    assert closeout["verification"]["frozen_replay"] == {
        "case_count": 12,
        "case_artifact_links": 543,
        "unique_frozen_json_artifacts": 400,
    }


def test_every_provider_record_has_a_source_first_verdict() -> None:
    review = _load(OUTPUT / "source-first-review.json")
    run = _load(OUTPUT / "result.json")
    reviewed = {row["record_id"] for row in review["record_reviews"]}
    admitted = {
        record["record_id"]
        for call in run["calls"]
        for reader in call["compiled"]["reader_results"]
        for record in reader["records"]
    }

    assert reviewed == admitted
    assert len(reviewed) == 16
    assert all(row["provider_aliases"] for row in review["record_reviews"])
    assert all(row["strongest_target_aliases"] for row in review["record_reviews"])
    assert all(row["source_first_verdict"] for row in review["record_reviews"])
    assert all(row["speaker_ownership_verdict"] for row in review["record_reviews"])
    assert all(row["modal_fidelity_verdict"] for row in review["record_reviews"])


def test_matched_review_preserves_mixed_findings_without_a_score() -> None:
    review = _load(OUTPUT / "source-first-review.json")
    dimensions = {row["dimension"]: row for row in review["dimensions"]}
    cases = {row["case_id"]: row for row in review["case_reviews"]}

    assert review["decision"] == "residual_task_repair_insufficient"
    assert review["scalar_quality_score"] is None
    assert dimensions["mechanical_execution_and_attribution"]["verdict"] == "pass"
    assert dimensions["false_positive_restraint"]["verdict"] == "fail"
    assert dimensions["genuine_residual_sensitivity"]["verdict"] == (
        "pass_with_evidence_precision_qualifications"
    )
    assert dimensions["prior_anchoring_resistance"]["verdict"] == "mixed"
    assert cases["r4h2-case01-community-audio-archive"]["arm_b"][
        "false_positive_records"
    ] == 2
    assert cases["r4h2-case02-serialized-essay-pilot"]["arm_a"][
        "all_surface_targets_passed"
    ] is True
    assert cases["r4h2-case02-serialized-essay-pilot"]["arm_b"][
        "all_surface_targets_passed"
    ] is False
    assert cases["r4h2-case03-research-workspace-service"]["arm_b"][
        "genuine_target_recovered"
    ] is True
    assert cases["r4h2-case04-shared-language-course"]["arm_b"][
        "genuine_target_recovered"
    ] is True


def test_residual_arm_repeats_contract_defined_false_positive_classes() -> None:
    review = _load(OUTPUT / "source-first-review.json")
    rows = [
        row
        for row in review["record_reviews"]
        if row["arm"] == "B_frozen_residual_task" and row["false_positive"]
    ]

    assert len(rows) == 5
    assert {row["false_positive_class"] for row in rows} >= {
        "governed_capacity_threshold",
        "scheduled_decision_machinery",
        "duplicated_current_gap_as_future_dependency",
        "assistant_proposal_elevated_to_present_gap",
    }
    assert review["decision_matrix_application"]["category"] == (
        "residual_task_repair_insufficient"
    )
    assert review["decision_matrix_application"][
        "residual_passed_all_restraint_gates"
    ] is False
    assert review["decision_matrix_application"][
        "residual_preserved_both_genuine_targets"
    ] is True


def test_final_evidence_manifest_locks_execution_and_review() -> None:
    from engine.system_b.r4_complementary_readers import value_sha256
    from scripts.evals import finalize_r4_matched_holdout_v2_execution_a1 as final

    manifest = _load(OUTPUT / "evidence-manifest.json")
    review = _load(OUTPUT / "source-first-review.json")
    closeout = _load(OUTPUT / "execution-closeout.json")

    assert manifest["manifest_sha256"] == value_sha256(
        {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    )
    assert review["result_sha256"] == value_sha256(
        {key: value for key, value in review.items() if key != "result_sha256"}
    )
    assert closeout["result_sha256"] == value_sha256(
        {key: value for key, value in closeout.items() if key != "result_sha256"}
    )
    assert manifest["provider_calls"] == 8
    assert manifest["provider_reported_cost_usd"] == 0.01408165
    assert manifest["source_first_review_sha256"] == review["result_sha256"]
    assert closeout["evidence_manifest_sha256"] == manifest["manifest_sha256"]
    assert closeout["source_first_review_sha256"] == review["result_sha256"]
    assert all((ROOT / row["path"]).is_file() for row in manifest["files"])
    assert all(final._file_sha(ROOT / row["path"]) == row["sha256"] for row in manifest["files"])


def test_finalizer_has_no_network_transport_dependency() -> None:
    from scripts.evals import finalize_r4_matched_holdout_v2_execution_a1 as final

    tree = ast.parse(Path(final.__file__).read_text(encoding="utf-8"))
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }

    assert imported.isdisjoint(
        {"anthropic", "google", "httpx", "openai", "requests", "urllib"}
    )
