from __future__ import annotations

import json
import sys
from pathlib import Path

from scripts.evals import run_user_counterpressure_temporal_preflight as runner


FIRST = (
    "we haven't had the real conversation about what 3 nights a week away "
    "actually looks like for four-plus years"
)
LATER = (
    'But he said it in the way that means "I will not stop you from taking '
    'it." Which is different from "yes this is a good idea for us."'
)


def _write_passing_artifact(path: Path) -> Path:
    events = [
        {
            "kind": "material_qualification",
            "source": {
                "turn_index": 2,
                "speaker": "user",
                "quote": FIRST,
            },
        },
        {
            "kind": "material_qualification",
            "source": {
                "turn_index": 4,
                "speaker": "user",
                "quote": LATER,
            },
        },
    ]
    path.write_text(
        json.dumps(
            {
                "schema_version": "lolla.user_counterpressure_temporal_shadow.v0",
                "semantic_events": {"user_pressure_events": events},
                "semantic_candidate_ledger": {
                    "reader_calls": [
                        {
                            "reader_role": "user_pressure",
                            "raw_candidate_counts": {"user_pressure_events": 2},
                        }
                    ],
                    "candidates": [
                        {
                            "raw_proposal": {
                                "kind": "material_qualification",
                            }
                        },
                        {
                            "raw_proposal": {
                                "kind": "material_qualification",
                            }
                        },
                    ],
                },
                "validation": {
                    "user_counterpressure": {
                        "user_pressure_events": {
                            "raw_count": 2,
                            "validated_count": 2,
                        }
                    }
                },
                "model_usage": {
                    "calls": [
                        {
                            "status": "ok",
                            "prompt_tokens": 10,
                            "completion_tokens": 5,
                            "total_tokens": 15,
                        }
                    ]
                },
                "evaluation_execution": {
                    "failed_attempts_before_success": 0,
                },
            }
        ),
        encoding="utf-8",
    )
    return path


def test_temporal_runner_validates_frozen_contract() -> None:
    contract = runner.validate_contract()

    assert contract["contract_status"] == "prepared_no_calls_executed"
    assert contract["successful_call_budget"] == 3
    assert contract["prompt_contract"]["change_type"] == (
        "temporal_addendum_only"
    )


def test_temporal_result_requires_both_reasoning_and_audit_coverage(
    tmp_path: Path,
) -> None:
    artifacts = [
        _write_passing_artifact(tmp_path / f"run-{index}.json")
        for index in range(1, 4)
    ]
    result = runner.build_result(
        contract=runner.validate_contract(),
        artifact_paths=artifacts,
    )

    assert result["reasoning_substrate_passed"] is True
    assert result["audit_trail_passed"] is True
    assert result["mechanical_passed"] is True
    assert result["passed"] is True
    assert result["decision"] == "eligible_for_three_case_discussion"
    assert result["operational"]["successful_call_count"] == 3
    assert result["operational"]["total_tokens"] == 45


def test_temporal_default_command_makes_no_model_call(monkeypatch) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["run_user_counterpressure_temporal_preflight.py"],
    )

    assert runner.main() == 0
