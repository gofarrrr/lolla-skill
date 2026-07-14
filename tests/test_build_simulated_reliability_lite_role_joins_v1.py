from __future__ import annotations

from pathlib import Path

from scripts.evals.build_simulated_reliability_lite_role_joins_v1 import build


def test_preserved_lite_artifacts_join_without_semantic_repair(tmp_path: Path) -> None:
    report = build(tmp_path / "joins")
    assert report["provider_calls"] == 0
    assert report["case06"]["record_counts"] == {
        "starting": 1,
        "current": 1,
        "qualification": 1,
    }
    assert report["case06"]["qualification_review_outcome"] == (
        "unresolved_qualification_present"
    )
    assert report["case07"]["current_observation_count"] == 1
    assert report["case07"]["qualification_observation_count"] == 0
    assert report["case07"]["qualification_review_outcome"] == (
        "no_unresolved_qualification_observed"
    )
    assert report["quiet_false_positive_used_in_join"] is False
    assert report["semantic_repair_performed"] is False
    assert report["deterministic_semantic_inference"] is False
    assert report["scalar_quality_score"] is None
