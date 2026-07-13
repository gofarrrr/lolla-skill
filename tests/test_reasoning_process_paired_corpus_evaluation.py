from __future__ import annotations

import copy
import json
from pathlib import Path

from scripts.evals.validate_reasoning_process_paired_corpus_evaluation import DIMENSIONS, validate

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/evals/reasoning-process-paired-corpus-evaluation-v1.json"
REVIEW = ROOT / "research/reasoning-process-paired-corpus-evaluation-2026-07-12/corpus-review.json"
REPORT = ROOT / "research/reasoning-process-paired-corpus-evaluation-2026-07-12/validation-report.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_checked_in_corpus_validation_passes_without_calls_or_scores() -> None:
    report = _load(REPORT)
    assert report["status"] == "provider_free_paired_corpus_validation_pass"
    assert report["reviewed_case_count"] == 4
    assert report["dimension_count"] == 7
    assert report["errors"] == []
    assert report["boundary"]["provider_calls"] == 0
    assert report["boundary"]["graph_calls"] == 0
    assert report["boundary"]["scalar_score_computed"] is False


def test_every_case_has_all_seven_non_scalar_dimensions() -> None:
    review = _load(REVIEW)
    assert len(review["reviewed_cases"]) == 4
    for case in review["reviewed_cases"]:
        assert tuple(case["dimensions"]) == DIMENSIONS
        for item in case["dimensions"].values():
            assert isinstance(item["disposition"], str)
            assert item["finding"]
            assert "score" not in item


def test_corpus_preserves_mixed_evidence_instead_of_declaring_one_winner() -> None:
    review = _load(REVIEW)
    by_architecture = {case["architecture"]: case for case in review["reviewed_cases"]}
    assert by_architecture["independent_role_first_v22"]["dimensions"]["central_role_allocation"]["disposition"] == "fail"
    assert by_architecture["independent_role_first_v23"]["dimensions"]["central_role_allocation"]["disposition"] == "fail"
    assert by_architecture["paired_role_first_v24"]["dimensions"]["central_role_allocation"]["disposition"] == "pass"
    assert by_architecture["status_free_paired_role_first_v241"]["dimensions"]["central_role_allocation"]["disposition"] == "pass"
    assert by_architecture["paired_role_first_v24"]["dimensions"]["relationship_preservation"]["disposition"] == "operationally_blocked"
    assert all(case["dimensions"]["evidence_precision"]["disposition"] == "partial" for case in review["reviewed_cases"])


def test_next_experiment_is_shadow_impact_not_more_calls_or_integration() -> None:
    decision = _load(REVIEW)["decision"]
    assert decision["selected_next_experiment"] == "read_only_shadow_graph_impact"
    assert decision["another_transfer_call_selected"] is False
    assert decision["new_provider_calls_authorized"] is False
    assert decision["production_integration_authorized"] is False
    assert decision["live_graph_routing_authorized"] is False


def test_validator_rejects_scalar_score_and_unsafe_authorization(tmp_path: Path) -> None:
    review = copy.deepcopy(_load(REVIEW))
    review["reviewed_cases"][0]["dimensions"]["central_role_allocation"]["score"] = 1
    review["decision"]["production_integration_authorized"] = True
    bad = tmp_path / "bad-review.json"
    bad.write_text(json.dumps(review), encoding="utf-8")
    report = validate(CONTRACT, bad)
    assert report["status"] == "provider_free_paired_corpus_validation_fail"
    assert any("forbidden aggregate field" in error for error in report["errors"])
    assert any("unsafe authorization" in error for error in report["errors"])
