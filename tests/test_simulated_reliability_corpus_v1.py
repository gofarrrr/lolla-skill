from pathlib import Path

from scripts.evals.validate_simulated_reliability_corpus_v1 import validate


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_simulated_reliability_corpus_v1_is_frozen_and_valid() -> None:
    result = validate(root=REPO_ROOT)

    assert result == {
        "status": "pass",
        "calibration_cases": 8,
        "transfer_cases": 12,
        "transfer_messages": 288,
        "transfer_words": 21938,
        "behavior_mix": {
            "pressure_expected": 6,
            "stand_down_expected": 4,
            "park_expected": 2,
        },
        "lolla_pipeline_provider_calls": 0,
        "rejected_source_editor_provider_calls": 12,
    }
