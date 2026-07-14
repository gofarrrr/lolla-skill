from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research/lolla-r4-separated-surface-experiment-v1-execution-2026-07-14-a1"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_raw_execution_a1_is_terminal_first_failure_custody() -> None:
    result = _load(OUTPUT / "result.json")
    manifest = _load(OUTPUT / "raw-evidence-manifest.json")
    consumption = _load(OUTPUT / "authorization-consumption.json")

    assert result["status"] == "stopped_on_first_failure"
    assert result["provider_calls"] == 7
    assert result["call_ordinals"] == list(range(1, 8))
    assert [row["operational_status"] for row in result["call_results"][:6]] == ["completed"] * 6
    assert result["call_results"][6]["operational_status"] == "terminal_validation_failure"
    assert result["call_results"][6]["finish_reason"] == "error"
    assert result["first_failure_stopped_further_transport"] is True
    assert not any(OUTPUT.glob("call-08-*"))
    assert result["automatic_retries"] == 0
    assert result["semantic_retries"] == 0
    assert result["fallback_models"] == 0
    assert result["model_substitutions"] == 0
    assert result["response_healing"] is False

    assert consumption["status"] == "consumed_terminal_first_failure"
    assert consumption["authorization_sha256"] == "e41321fec40af572ae643af73cb6a04a7624756d84c723b0c09bcb2829450edf"
    assert consumption["provider_calls"] == 7
    assert consumption["second_execution_authorized"] is False

    for row in manifest["files"]:
        artifact = OUTPUT / row["path"]
        assert artifact.is_file()
        assert hashlib.sha256(artifact.read_bytes()).hexdigest() == row["sha256"]
        assert len(artifact.read_bytes()) == row["bytes"]
    assert manifest["provider_calls"] == 7
    assert manifest["completed_calls"] == 6
    assert manifest["failed_ordinal"] == 7


def test_source_first_review_preserves_partial_evidence_without_overclaim() -> None:
    review = _load(OUTPUT / "source-first-review.json")

    assert review["decision"] == "semantic_result_not_evaluable"
    assert review["scalar_score"] is None
    assert review["provider_evaluator_calls"] == 0
    assert review["record_count"] == 9
    assert len(review["record_verdicts"]) == 9
    assert {row["verdict"] for row in review["record_verdicts"]} == {"false_positive"}
    assert review["quiet_control_summary"] == {
        "case01_paired": "failed_both_quiet_surfaces",
        "case01_separated_decision_gap": "correct_zero",
        "case01_separated_reconsideration_dependency": "false_positives_present",
        "case02_paired": "failed_both_quiet_surfaces",
        "case02_separated_decision_gap": "correct_zero",
        "case02_separated_reconsideration_dependency": "false_positives_present",
    }
    assert review["positive_case_status"] == {
        "case03": "not_evaluable_call_07_failed_and_calls_08_09_unattempted",
        "case04": "not_evaluable_calls_10_11_12_unattempted",
    }
    assert review["companion_pressure_conclusion"] == "not_evaluable_without_positive_case_matched_comparisons"


def test_execution_closeout_and_evidence_manifest_are_restart_safe() -> None:
    closeout = _load(OUTPUT / "execution-closeout.json")
    manifest = _load(OUTPUT / "evidence-manifest.json")

    assert closeout["decision"] == "semantic_result_not_evaluable"
    assert closeout["calls_attempted"] == 7
    assert closeout["calls_completed"] == 6
    assert closeout["failed_ordinal"] == 7
    assert closeout["authorization_consumed"] is True
    assert closeout["current_provider_authorization"] == {"maximum_calls": 0, "maximum_cost_usd": 0.0}
    assert closeout["evidence_published"] is False
    assert closeout["second_execution_authorized"] is False
    assert manifest["decision"] == "semantic_result_not_evaluable"
    for row in manifest["files"]:
        artifact = ROOT / row["path"]
        assert artifact.is_file()
        assert hashlib.sha256(artifact.read_bytes()).hexdigest() == row["sha256"]
        assert len(artifact.read_bytes()) == row["bytes"]
