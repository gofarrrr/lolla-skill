from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "docs/evals/lolla-r4-separated-surface-experiment-v1-target.json"
TARGET_REVIEW = (
    ROOT / "docs/evals/lolla-r4-separated-surface-experiment-v1-target-review.json"
)
HUMAN_CHECKPOINT = "69d3026b9022394481f4463765c53fea09da5d0a"
EXPECTED = {
    "r4s1-case01-cave-rescue-readiness": ("quiet", "quiet"),
    "r4s1-case02-neighborhood-observatory-winter-access": ("quiet", "quiet"),
    "r4s1-case03-relaxed-performance-tour": ("supported", "quiet"),
    "r4s1-case04-native-seed-cryopreservation": ("quiet", "supported"),
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_protected_target_is_complete_source_first_and_non_scalar() -> None:
    target = _load(TARGET)

    assert target["status"] == "protected_target_frozen_before_provider_visible_design"
    assert target["human_review_checkpoint_commit"] == HUMAN_CHECKPOINT
    assert target["provider_calls"] == 0
    assert target["provider_cost_usd"] == 0.0
    assert target["provider_outputs_existed_when_authored"] is False
    assert target["request_previews_existed_when_authored"] is False
    assert target["target_visible_to_provider"] is False
    assert target["runner_may_load_target"] is False
    assert target["scalar_quality_score"] is None
    assert len(target["cases"]) == 4

    for case in target["cases"]:
        decision_gap, dependency = EXPECTED[case["case_id"]]
        surfaces = case["canonical_surface_targets"]
        assert surfaces["unresolved_matter"]["disposition"] == decision_gap
        assert surfaces["reopen_condition"]["disposition"] == dependency
        assert case["intended_role_contradicted"] is False
        assert case["explicit_limitations"]
        assert case["ontology_assumptions"]
        assert case["likely_false_positives"]
        for canonical_surface, surface in surfaces.items():
            assert canonical_surface in {"unresolved_matter", "reopen_condition"}
            assert surface["strongest_source_aliases"]
            assert surface["speaker_ownership"]
            assert surface["modal_force"]
            assert surface["temporal_placement"]
            assert surface["machinery_treatment"]
            assert surface["expected_canonical_surface"] == canonical_surface
            assert surface["expected_result"]["outcome"] in {
                "records_present",
                "no_supported_record_observed",
                "ambiguous",
            }


def test_target_review_binds_exact_target_and_precedes_requests() -> None:
    target_bytes = TARGET.read_bytes()
    review = _load(TARGET_REVIEW)

    assert review["status"] == "protected_target_frozen_before_requests"
    assert review["human_review_checkpoint_commit"] == HUMAN_CHECKPOINT
    assert review["target"]["sha256"] == hashlib.sha256(target_bytes).hexdigest()
    assert review["target"]["utf8_bytes"] == len(target_bytes)
    assert review["request_previews_existed_when_target_frozen"] is False
    assert review["provider_visible"] is False
    assert review["runner_may_load_target"] is False
    assert review["runner_may_load_review_metadata"] is False
    assert review["provider_calls"] == 0
    assert review["provider_cost_usd"] == 0.0

    for path in (TARGET, TARGET_REVIEW):
        relative = path.relative_to(ROOT)
        result = subprocess.run(
            ["git", "cat-file", "-e", f"{HUMAN_CHECKPOINT}:{relative}"],
            cwd=ROOT,
            check=False,
            capture_output=True,
        )
        assert result.returncode != 0
