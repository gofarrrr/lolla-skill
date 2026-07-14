from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research/lolla-r4-separated-surface-experiment-v1-execution-2026-07-14-a2"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_raw_execution_a2_is_complete_final_run_custody() -> None:
    result = _load(OUTPUT / "result.json")
    manifest = _load(OUTPUT / "raw-evidence-manifest.json")
    consumption = _load(OUTPUT / "authorization-consumption.json")

    assert result["status"] == "complete"
    assert result["provider_calls"] == 12
    assert result["call_ordinals"] == list(range(1, 13))
    assert [row["operational_status"] for row in result["call_results"]] == ["completed"] * 12
    assert [row["finish_reason"] for row in result["call_results"]] == ["stop"] * 12
    assert result["first_failure_stopped_further_transport"] is False
    assert result["automatic_retries"] == 0
    assert result["semantic_retries"] == 0
    assert result["fallback_models"] == 0
    assert result["model_substitutions"] == 0
    assert result["response_healing"] is False

    assert consumption["status"] == "consumed_complete_final_execution"
    assert consumption["authorization_instance"] == "lolla-r4-separated-surface-experiment-v1-a2"
    assert consumption["founder_authorization_type"] == "new final full-execution authorization"
    assert consumption["authorization_sha256"] == "e41321fec40af572ae643af73cb6a04a7624756d84c723b0c09bcb2829450edf"
    assert consumption["previous_a1_authorization"] == "consumed_and_not_reusable"
    assert consumption["a2_authorization"] == "separately_issued_one_use_final_permitted_execution"
    assert consumption["third_execution_authorized"] is False

    assert manifest["provider_calls"] == 12
    assert manifest["completed_calls"] == 12
    assert manifest["failed_ordinal"] is None
    assert manifest["unattempted_ordinals"] == []
    for row in manifest["files"]:
        artifact = OUTPUT / row["path"]
        assert artifact.is_file()
        assert hashlib.sha256(artifact.read_bytes()).hexdigest() == row["sha256"]
        assert len(artifact.read_bytes()) == row["bytes"]


def test_final_a2_review_preserves_non_scalar_task_shape_decision() -> None:
    review = _load(OUTPUT / "source-first-review.json")
    closeout = _load(OUTPUT / "execution-closeout.json")
    evidence = _load(OUTPUT / "evidence-manifest.json")

    assert review["decision"] == "separated_tasks_ineffective_companions_persist"
    assert review["record_count"] == 18
    assert review["supported_record_count"] == 4
    assert review["false_positive_record_count"] == 14
    assert review["paired_false_positive_records"] == 7
    assert review["separated_false_positive_records"] == 7
    assert review["correct_zero_reviews"] == [2, 4]
    assert review["scalar_score"] is None
    assert review["positive_case_findings_preserved"] is True
    assert review["paired_positive_companions"] == [8, 10]
    assert review["separated_positive_companions"] == [7, 12]
    assert review["provider_evaluator_calls"] == 0
    assert review["protected_evidence_opened_after_raw_checkpoint"] is True
    assert len(review["record_verdicts"]) == 18

    assert closeout["status"] == "closed_complete_final_execution"
    assert closeout["decision"] == "separated_tasks_ineffective_companions_persist"
    assert closeout["calls_attempted"] == 12
    assert closeout["calls_completed"] == 12
    assert closeout["provider_reported_cost_usd"] == 0.02148425
    assert closeout["current_provider_authorization"] == {"maximum_calls": 0, "maximum_cost_usd": 0.0}
    assert closeout["third_execution_authorized"] is False
    assert closeout["evidence_published"] is False

    assert evidence["decision"] == "separated_tasks_ineffective_companions_persist"
    assert evidence["provider_calls"] == 12
    assert evidence["evidence_published"] is False
    for row in evidence["files"]:
        artifact = ROOT / row["path"]
        assert artifact.is_file()
        assert hashlib.sha256(artifact.read_bytes()).hexdigest() == row["sha256"]
        assert len(artifact.read_bytes()) == row["bytes"]
