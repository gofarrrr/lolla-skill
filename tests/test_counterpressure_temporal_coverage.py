from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.evals.score_counterpressure_temporal_coverage import (
    build_temporal_coverage_result,
)


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _artifact(path: Path, *, turn_index: int | None, quote: str = "") -> Path:
    events = []
    if turn_index is not None:
        events.append(
            {
                "kind": "material_qualification",
                "source": {
                    "turn_index": turn_index,
                    "speaker": "user",
                    "quote": quote,
                },
            }
        )
    _write_json(path, {"semantic_events": {"user_pressure_events": events}})
    return path


def test_temporal_scorer_keeps_first_introduction_distinct_from_concept(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source = tmp_path / "conversation.txt"
    source.write_text(
        "[Turn 1] USER:\nThe initial qualification matters.\n\n"
        "[Turn 1] ASSISTANT:\nI will reason about it.\n\n"
        "[Turn 2] USER:\nThe later qualification is stronger.\n",
        encoding="utf-8",
    )
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    contract = tmp_path / "contract.json"
    _write_json(
        contract,
        {
            "schema_version": "lolla.counterpressure_temporal_coverage_contract.v0",
            "contract_id": "test-contract",
            "current_artifact_use": "diagnostic_only_not_promotion_evidence",
            "observations": [
                {
                    "case_id": "case-test",
                    "observation_id": "pressure.test",
                    "source_path": "conversation.txt",
                    "source_file_sha256": source_hash,
                    "first_introduction_evidence": [
                        {
                            "turn_index": 1,
                            "speaker": "user",
                            "quote": "The initial qualification matters.",
                        }
                    ],
                    "later_strengthening_evidence": [
                        {
                            "turn_index": 2,
                            "speaker": "user",
                            "quote": "The later qualification is stronger.",
                        }
                    ],
                }
            ],
        },
    )
    monkeypatch.setattr(
        "scripts.evals.score_counterpressure_temporal_coverage.REPO_ROOT",
        tmp_path,
    )
    artifacts = [
        _artifact(
            tmp_path / "run-1.json",
            turn_index=1,
            quote="The initial qualification matters.",
        ),
        _artifact(
            tmp_path / "run-2.json",
            turn_index=2,
            quote="The later qualification is stronger.",
        ),
        _artifact(tmp_path / "run-3.json", turn_index=None),
    ]

    result = build_temporal_coverage_result(
        contract_path=contract,
        case_id="case-test",
        arm_name="test-arm",
        artifact_paths=artifacts,
    )

    metrics = result["metrics"]
    assert metrics["first_introduction_coverage"]["weighted_recall"] == 1 / 3
    assert metrics["concept_coverage"]["weighted_recall"] == 2 / 3
    assert metrics["later_strengthening_coverage"]["weighted_recall"] == 1 / 3
    assert metrics["first_introduction_coverage"]["stable_observation_ids"] == []
    assert metrics["concept_coverage"]["stable_observation_ids"] == []
    assert metrics["exact_source_validity"] == 1.0
    assert result["evaluation_status"] == (
        "diagnostic_only_not_promotion_evidence"
    )


def test_system_scope_credits_predeclared_span_in_another_reader_family(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source = tmp_path / "conversation.txt"
    source.write_text(
        "[Turn 1] USER:\nThe material qualification.\n",
        encoding="utf-8",
    )
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    contract = tmp_path / "contract.json"
    _write_json(
        contract,
        {
            "contract_id": "cross-family-test",
            "current_artifact_use": "diagnostic_only_not_promotion_evidence",
            "observations": [
                {
                    "case_id": "case-test",
                    "observation_id": "pressure.test",
                    "source_path": "conversation.txt",
                    "source_file_sha256": source_hash,
                    "first_introduction_evidence": [
                        {
                            "turn_index": 1,
                            "speaker": "user",
                            "quote": "The material qualification.",
                        }
                    ],
                    "later_strengthening_evidence": [],
                }
            ],
        },
    )
    artifact = tmp_path / "artifact.json"
    _write_json(
        artifact,
        {
            "semantic_events": {
                "user_pressure_events": [],
                "evidence_boundary_events": [
                    {
                        "kind": "stated_unknown",
                        "source": {
                            "turn_index": 1,
                            "speaker": "user",
                            "quote": "The material qualification.",
                        },
                    }
                ],
            }
        },
    )
    monkeypatch.setattr(
        "scripts.evals.score_counterpressure_temporal_coverage.REPO_ROOT",
        tmp_path,
    )

    pressure_only = build_temporal_coverage_result(
        contract_path=contract,
        case_id="case-test",
        arm_name="pressure-only",
        artifact_paths=[artifact],
    )
    system_level = build_temporal_coverage_result(
        contract_path=contract,
        case_id="case-test",
        arm_name="system-level",
        artifact_paths=[artifact],
        family_scope="all_source_grounded_families",
    )

    assert pressure_only["metrics"]["concept_coverage"]["weighted_recall"] == 0
    assert system_level["metrics"]["concept_coverage"]["weighted_recall"] == 1
    assert system_level["per_run"][0]["matching_families_by_observation"][
        "pressure.test"
    ]["concept"] == ["evidence_boundary_events"]
