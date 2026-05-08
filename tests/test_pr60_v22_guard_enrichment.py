from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V21_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v21.json"
)
AFFORDANCES_V22_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v22.json"
)

TARGET_RECORD_PATHS = {
    "baseline-establishment": MODEL_AFFORDANCE_DIR
    / "batch_8"
    / "baseline-establishment.json",
    "chain-of-thought": MODEL_AFFORDANCE_DIR
    / "batch_17"
    / "chain-of-thought.json",
    "game-theory-payoffs": MODEL_AFFORDANCE_DIR
    / "batch_5"
    / "game-theory-payoffs.json",
    "theory-of-constraints": MODEL_AFFORDANCE_DIR
    / "pilot"
    / "theory-of-constraints.json",
}

TARGET_ABSENCE_FIELDS = {
    "bottleneck-claim-without-measurement-loop",
    "commitment-threat-or-promise-without-credibility-device",
    "goal-baseline-with-solution-imported",
    "structured-reasoning-without-implementation-path",
    "technical-bottleneck-without-ownership-route",
}

UNCHANGED_CHAIN_OF_THOUGHT_ABSENCE_FIELDS = {
    "chain-of-thought-as-truth",
    "reasoning-transcript-without-verification",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr60_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr60_compiled_v22_is_v21_plus_five_absence_records() -> None:
    affordances_v21 = _load_compiled(AFFORDANCES_V21_PATH)
    affordances_v22 = _load_compiled(AFFORDANCES_V22_PATH)

    assert affordances_v22["artifact"] == "model_affordances_v22"
    assert affordances_v22["status"] == "draft_review_only"
    assert _model_ids(affordances_v22) == _model_ids(affordances_v21)
    assert len(_model_ids(affordances_v22)) == 222
    assert _affordance_ids(affordances_v22) == _affordance_ids(affordances_v21)
    assert TARGET_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v21))
    assert TARGET_ABSENCE_FIELDS.issubset(_absence_fields(affordances_v22))
    assert _absence_fields(affordances_v22) - _absence_fields(affordances_v21) == (
        TARGET_ABSENCE_FIELDS
    )

    v21_metadata = affordances_v21["compile_metadata"]
    v22_metadata = affordances_v22["compile_metadata"]
    assert v22_metadata["contributing_record_count"] == 222
    assert v22_metadata["affordance_count"] == v21_metadata["affordance_count"]
    assert v22_metadata["affordance_count"] == 268
    assert v22_metadata["absence_record_count"] == v21_metadata["absence_record_count"] + 5
    assert v22_metadata["absence_record_count"] == 434
    assert v22_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v22_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr60_guard_records_block_specific_overclaims() -> None:
    baseline = _load_record("baseline-establishment")
    assert "goal-baseline-with-solution-imported" in _absence_fields_from_record(baseline)
    assert _absence_reason_contains(baseline, "desired outcome")

    game_theory = _load_record("game-theory-payoffs")
    assert (
        "commitment-threat-or-promise-without-credibility-device"
        in _absence_fields_from_record(game_theory)
    )
    assert _absence_reason_contains(game_theory, "credible")

    chain_of_thought = _load_record("chain-of-thought")
    assert "structured-reasoning-without-implementation-path" in _absence_fields_from_record(
        chain_of_thought
    )
    assert _absence_reason_contains(chain_of_thought, "living system")

    theory_of_constraints = _load_record("theory-of-constraints")
    assert "bottleneck-claim-without-measurement-loop" in _absence_fields_from_record(
        theory_of_constraints
    )
    assert "technical-bottleneck-without-ownership-route" in _absence_fields_from_record(
        theory_of_constraints
    )
    assert _absence_reason_contains(theory_of_constraints, "governing metric")
    assert _absence_reason_contains(theory_of_constraints, "decision-right constraints")


def test_pr60_chain_of_thought_adds_only_the_implementation_path_absence() -> None:
    affordances_v21 = _load_compiled(AFFORDANCES_V21_PATH)
    affordances_v22 = _load_compiled(AFFORDANCES_V22_PATH)
    old_chain_record = _compiled_record(affordances_v21, "chain-of-thought")
    chain_record = _compiled_record(affordances_v22, "chain-of-thought")

    assert _absence_fields_from_record(old_chain_record) == (
        UNCHANGED_CHAIN_OF_THOUGHT_ABSENCE_FIELDS
    )
    assert _absence_fields_from_record(chain_record) == (
        UNCHANGED_CHAIN_OF_THOUGHT_ABSENCE_FIELDS
        | {"structured-reasoning-without-implementation-path"}
    )


def test_pr60_v22_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v22", "model_affordances_v22")

    for path in LIVE_RUNTIME_PATHS:
        text = path.read_text(encoding="utf-8")
        assert all(fragment not in text for fragment in forbidden)


def _load_record(model_id: str) -> dict[str, object]:
    return json.loads(TARGET_RECORD_PATHS[model_id].read_text(encoding="utf-8"))


def _load_compiled(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _model_ids(compiled: dict[str, object]) -> set[str]:
    return {
        str(record["model_id"])
        for record in compiled.get("model_records", [])
        if isinstance(record, dict)
    }


def _affordance_ids(compiled: dict[str, object]) -> set[str]:
    return {
        str(affordance["affordance_id"])
        for record in compiled.get("model_records", [])
        if isinstance(record, dict)
        for affordance in record.get("affordances", [])
        if isinstance(affordance, dict)
    }


def _absence_fields(compiled: dict[str, object]) -> set[str]:
    return {
        str(absence["attempted_field"])
        for record in compiled.get("model_records", [])
        if isinstance(record, dict)
        for absence in record.get("absence_records", [])
        if isinstance(absence, dict)
    }


def _absence_fields_from_record(record: dict[str, object]) -> set[str]:
    return {
        str(absence["attempted_field"])
        for absence in record.get("absence_records", [])
        if isinstance(absence, dict)
    }


def _absence_reason_contains(record: dict[str, object], needle: str) -> bool:
    return any(
        needle in str(absence.get("reason", ""))
        for absence in record.get("absence_records", [])
        if isinstance(absence, dict)
    )


def _compiled_record(
    compiled: dict[str, object],
    model_id: str,
) -> dict[str, object]:
    for record in compiled.get("model_records", []):
        if isinstance(record, dict) and record["model_id"] == model_id:
            return record
    raise AssertionError(f"missing compiled record: {model_id}")
