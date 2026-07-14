from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.system_b.r4_complementary_readers import value_sha256
from scripts.evals import finalize_r4_complementary_reader_execution as closeout


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research/lolla-r4-complementary-reader-execution-2026-07-14-a1"


def _load(name: str) -> dict:
    return json.loads((OUTPUT / name).read_text(encoding="utf-8"))


def _without(value: dict, field: str) -> dict:
    return {key: item for key, item in value.items() if key != field}


def test_checked_in_closeout_validates_and_is_terminal() -> None:
    result = closeout.validate()

    assert result["status"] == (
        "attempt_closed_token_allocation_failure_semantic_question_unresolved"
    )
    assert result["provider_calls"] == 2
    assert result["relationship_calls"] == 0
    assert result["provider_reported_cost_usd"] == 0.009036
    assert result["cost_ceiling_met"] is True
    assert result["decision"]["semantic_hypothesis_resolved"] is False
    assert result["decision"]["additional_provider_call_authorized"] is False
    assert result["decision"]["this_attempt_may_be_retried"] is False


@pytest.mark.parametrize(
    ("case_id", "completion", "reasoning", "remainder", "cost"),
    [
        ("v1-case02-discharge-transport", 885, 865, 20, 0.004387),
        ("v1-case03-executive-hire", 886, 861, 25, 0.004649),
    ],
)
def test_exact_truncation_and_cost_evidence_is_preserved(
    case_id: str,
    completion: int,
    reasoning: int,
    remainder: int,
    cost: float,
) -> None:
    result = _load("execution-closeout.json")
    row = next(item for item in result["call_observations"] if item["case_id"] == case_id)

    assert row["operator_attribution_ok"] is True
    assert row["finish_reason"] == "length"
    assert row["operational_status"] == "candidate_parse_failed"
    assert row["completion_tokens"] == completion
    assert row["reasoning_tokens"] == reasoning
    assert row["non_reasoning_completion_token_remainder"] == remainder
    assert row["provider_reported_cost_usd"] == cost
    assert row["candidate_admitted"] is False
    assert row["raw_partial_content_used_as_semantic_evidence"] is False


def test_source_first_semantic_dimensions_remain_unresolved() -> None:
    review = _load("source-first-review.json")
    dimensions = {row["dimension"]: row["verdict"] for row in review["dimensions"]}

    assert review["semantic_review_performed"] is False
    assert review["partial_raw_content_reviewed_for_semantic_pass"] is False
    assert review["relationship_review_performed"] is False
    assert review["scalar_quality_score"] is None
    assert dimensions["material_pressure_recovered"].startswith("not_evaluable")
    assert dimensions["false_positive_restraint"].startswith("not_evaluable")
    assert dimensions["evidence_precision"].startswith("not_evaluable")
    assert dimensions["role_placement"].startswith("not_evaluable")
    assert dimensions["relationship_fidelity"].startswith("not_evaluable")
    assert dimensions["operational_load_and_cost"] == "observed_exactly"


def test_closeout_chain_and_manifest_self_hashes_are_exact() -> None:
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
    assert manifest["provider_calls"] == 2


def test_relationship_calls_are_absent_and_stop_rule_is_explicit() -> None:
    result = _load("execution-closeout.json")

    assert not list(OUTPUT.glob("*/call-*-relationship-*.json"))
    assert result["mechanical_conclusion"]["relationship_dependency_opened"] is False
    assert result["mechanical_conclusion"]["stop_rule_worked"] is True
    assert result["preserved_boundaries"]["automatic_retry_performed"] is False
    assert result["preserved_boundaries"]["partial_json_rescued"] is False


def test_call_expectation_tampering_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = dict(closeout.EXPECTED["v1-case02-discharge-transport"])
    expected["reasoning_tokens"] = 864
    monkeypatch.setitem(closeout.EXPECTED, "v1-case02-discharge-transport", expected)

    with pytest.raises(
        closeout.R4ExecutionCloseoutError, match="frozen call evidence drifted"
    ):
        closeout.validate()


def test_finalizer_has_no_provider_transport_or_api_key_path() -> None:
    source = Path(closeout.__file__).read_text(encoding="utf-8")

    assert "urlopen" not in source
    assert "OPENROUTER_API_KEY" not in source
    assert "OPENAI_API_KEY" not in source
    assert "_provider_call(" not in source
