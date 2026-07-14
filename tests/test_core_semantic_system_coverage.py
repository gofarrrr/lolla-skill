from __future__ import annotations

import json
from pathlib import Path

from scripts.evals.score_core_semantic_system_coverage import (
    DEFAULT_MANIFEST,
    build_system_coverage,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_system_coverage_preserves_old_family_score_and_exposes_cross_family() -> None:
    result = build_system_coverage(
        manifest_path=DEFAULT_MANIFEST,
        artifact_root=REPO_ROOT / "research/core-semantic-sk3-2026-07-10",
    )
    existing = json.loads(
        (
            REPO_ROOT
            / "research/core-semantic-sk3-2026-07-10/corpus-comparison.json"
        ).read_text(encoding="utf-8")
    )

    assert result["case_count"] == 12
    assert result["gold_observation_count"] == 102
    assert result["family_aligned"]["weighted_recall"] == existing[
        "shadow_path"
    ]["weighted_mean_recall"]
    assert result["family_aligned"]["stable_observation_count"] == existing[
        "shadow_path"
    ]["stable_observation_count"]
    assert result["system_level"]["weighted_recall"] > result[
        "family_aligned"
    ]["weighted_recall"]
    assert result["system_level"]["stable_observation_count"] > result[
        "family_aligned"
    ]["stable_observation_count"]
    assert result["cross_family"]["rescued_observation_run_count"] == 50

    case08 = next(
        item
        for item in result["per_case"]
        if item["case_id"] == "case-08-oncologist-career-family"
    )
    rescued = [
        rescue
        for run in case08["per_run"]
        for rescue in run["cross_family_rescues"]
        if rescue["observation_id"] == "pressure.husband_conversation_not_real"
    ]
    assert len(rescued) == 3
    assert all(
        "live_constraint_events" in item["matching_families"]
        for item in rescued
    )
    assert any(
        "evidence_boundary_events" in item["matching_families"]
        for item in rescued
    )
