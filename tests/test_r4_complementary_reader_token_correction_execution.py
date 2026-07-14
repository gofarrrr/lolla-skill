from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.system_b.r4_complementary_readers import value_sha256
from scripts.evals import (
    finalize_r4_complementary_reader_token_correction_execution as closeout,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = (
    ROOT
    / "research/lolla-r4-complementary-reader-token-correction-execution-2026-07-14-a2"
)


def _load(name: str) -> dict:
    return json.loads((OUTPUT / name).read_text(encoding="utf-8"))


def _without(value: dict, field: str) -> dict:
    return {key: item for key, item in value.items() if key != field}


def test_corrected_execution_is_sealed_and_terminal() -> None:
    result = closeout.validate()

    assert result["status"] == (
        "attempt_closed_operational_correction_passed_semantic_restraint_failed"
    )
    assert result["provider_calls"] == 4
    assert result["relationship_calls"] == 2
    assert result["provider_reported_cost_usd"] == 0.010835
    assert result["cost_ceiling_met"] is True
    assert result["mechanical_conclusion"]["token_allocation_correction_succeeded"] is True
    assert result["semantic_conclusion"]["semantic_hypothesis_supported"] is False
    assert result["decision"]["additional_provider_call_authorized"] is False
    assert result["decision"]["runtime_or_graph_integration_authorized"] is False


def test_source_first_dimensions_preserve_mixed_result_without_scalar() -> None:
    review = _load("source-first-review.json")
    dimensions = {row["dimension"]: row["verdict"] for row in review["dimensions"]}

    assert review["semantic_review_performed"] is True
    assert review["relationship_review_performed"] is True
    assert review["source_first_target_visible_to_provider"] is False
    assert review["scalar_quality_score"] is None
    assert dimensions == {
        "material_pressure_recovered": "pass_narrowly",
        "false_positive_restraint": "fail",
        "evidence_precision": "fail",
        "role_placement": "pass_structurally",
        "relationship_fidelity": "fail_semantic_restraint",
        "operational_load_and_cost": "pass_observed_exactly",
    }


def test_control_false_positives_and_later_source_conflict_are_explicit() -> None:
    review = _load("source-first-review.json")
    control = next(
        row
        for row in review["case_reviews"]
        if row["case_id"] == "v1-case03-executive-hire"
    )
    verdicts = [row["verdict"] for row in control["record_reviews"]]

    assert control["verdict"] == "restraint_failed"
    assert len(control["record_reviews"]) == 5
    assert "false_positive_later_source_not_integrated" in verdicts
    first = control["record_reviews"][0]
    assert first["decisive_aliases"] == ["e061", "e105"]


def test_target_recovers_one_pressure_but_preserves_misses() -> None:
    review = _load("source-first-review.json")
    target = next(
        row
        for row in review["case_reviews"]
        if row["case_id"] == "v1-case02-discharge-transport"
    )

    assert target["verdict"] == "narrow_material_recovery_with_overgeneration"
    assert any(
        row["verdict"] == "material_target_pressure_recovered"
        for row in target["record_reviews"]
    )
    assert target["missed_target_material"] == [
        "cross-setting generalization from two wards in one participating city",
        "accessible-vehicle supply outside the bounded pilot setting",
    ]


def test_exact_call_costs_and_broad_reasoning_flag_are_not_hidden() -> None:
    result = _load("execution-closeout.json")
    costs = [row["provider_reported_cost_usd"] for row in result["call_observations"]]

    assert costs == [0.0036835, 0.001651, 0.003977, 0.0015235]
    assert sum(costs) == pytest.approx(0.010835)
    assert all(row["finish_reason"] == "stop" for row in result["call_observations"])
    assert all(row["reasoning_tokens"] == 0 for row in result["call_observations"])
    assert all(
        row["runner_broad_reasoning_field_presence_flag"] is True
        for row in result["call_observations"]
    )
    assert all(
        row["reasoning_field_contents_preserved"] is False
        for row in result["call_observations"]
    )


def test_manifest_and_closeout_chain_self_hashes_are_exact() -> None:
    manifest = _load("evidence-manifest.json")
    review = _load("source-first-review.json")
    result = _load("execution-closeout.json")

    assert manifest["manifest_sha256"] == value_sha256(
        _without(manifest, "manifest_sha256")
    )
    assert review["result_sha256"] == value_sha256(_without(review, "result_sha256"))
    assert result["result_sha256"] == value_sha256(_without(result, "result_sha256"))
    assert review["evidence_manifest_sha256"] == manifest["manifest_sha256"]
    assert result["evidence_manifest_sha256"] == manifest["manifest_sha256"]
    assert result["source_first_review_sha256"] == review["result_sha256"]
    assert manifest["file_count"] == len(manifest["files"])


def test_call_expectation_tampering_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rows = list(closeout.EXPECTED_CALLS)
    rows[0] = {**rows[0], "completion_tokens": 415}
    monkeypatch.setattr(closeout, "EXPECTED_CALLS", tuple(rows))

    with pytest.raises(
        closeout.R4TokenCorrectionCloseoutError,
        match="frozen call evidence drifted",
    ):
        closeout.validate()


def test_finalizer_has_no_provider_transport_or_api_key_path() -> None:
    source = Path(closeout.__file__).read_text(encoding="utf-8")

    assert "urlopen" not in source
    assert "OPENROUTER_API_KEY" not in source
    assert "OPENAI_API_KEY" not in source
    assert "_provider_call(" not in source
