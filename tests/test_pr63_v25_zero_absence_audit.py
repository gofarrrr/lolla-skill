from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V24_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v24.json"
)
AFFORDANCES_V25_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v25.json"
)

TARGET_RECORD_PATHS = {
    "decision-trees": MODEL_AFFORDANCE_DIR / "batch_1" / "decision-trees.json",
    "power-dynamics": MODEL_AFFORDANCE_DIR / "pilot" / "power-dynamics.json",
}

TARGET_ABSENCE_FIELDS = {
    "behavior-free-human-decision-tree",
    "exhaustive-option-tree-affordance",
    "generic-disagreement-as-power-contest",
    "standalone-decision-tree-runtime-automation-affordance",
    "winning-negotiation-without-opportunity-cost-check",
}

INTENTIONAL_ZERO_ABSENCE_MODELS = {
    "lindy-effect",
    "premortem",
    "sunk-cost-fallacy",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr63_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr63_compiled_v25_is_v24_plus_five_absence_records() -> None:
    affordances_v24 = _load_compiled(AFFORDANCES_V24_PATH)
    affordances_v25 = _load_compiled(AFFORDANCES_V25_PATH)

    assert affordances_v25["artifact"] == "model_affordances_v25"
    assert affordances_v25["status"] == "draft_review_only"
    assert _model_ids(affordances_v25) == _model_ids(affordances_v24)
    assert len(_model_ids(affordances_v25)) == 222
    assert _affordance_ids(affordances_v25) == _affordance_ids(affordances_v24)
    assert TARGET_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v24))
    assert TARGET_ABSENCE_FIELDS.issubset(_absence_fields(affordances_v25))
    assert _absence_fields(affordances_v25) - _absence_fields(affordances_v24) == (
        TARGET_ABSENCE_FIELDS
    )

    v24_metadata = affordances_v24["compile_metadata"]
    v25_metadata = affordances_v25["compile_metadata"]
    assert v25_metadata["contributing_record_count"] == 222
    assert v25_metadata["affordance_count"] == v24_metadata["affordance_count"]
    assert v25_metadata["affordance_count"] == 268
    assert v25_metadata["absence_record_count"] == v24_metadata["absence_record_count"] + 5
    assert v25_metadata["absence_record_count"] == 454
    assert v25_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v25_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr63_guard_records_block_specific_zero_absence_overclaims() -> None:
    decision_trees = _load_record("decision-trees")
    assert "standalone-decision-tree-runtime-automation-affordance" in (
        _absence_fields_from_record(decision_trees)
    )
    assert "behavior-free-human-decision-tree" in _absence_fields_from_record(
        decision_trees
    )
    assert "exhaustive-option-tree-affordance" in _absence_fields_from_record(
        decision_trees
    )
    assert _absence_reason_contains(decision_trees, "separate runtime automation")
    assert _absence_reason_contains(decision_trees, "emotions, beliefs")
    assert _absence_reason_contains(decision_trees, "exhaustive tree")

    power_dynamics = _load_record("power-dynamics")
    assert "generic-disagreement-as-power-contest" in _absence_fields_from_record(
        power_dynamics
    )
    assert "winning-negotiation-without-opportunity-cost-check" in (
        _absence_fields_from_record(power_dynamics)
    )
    assert _absence_reason_contains(power_dynamics, "every disagreement")
    assert _absence_reason_contains(power_dynamics, "opportunity-cost check")


def test_pr63_remaining_zero_absence_models_are_intentional_no_change() -> None:
    affordances_v25 = _load_compiled(AFFORDANCES_V25_PATH)

    assert {
        str(record["model_id"])
        for record in affordances_v25.get("model_records", [])
        if isinstance(record, dict) and not record.get("absence_records")
    } == INTENTIONAL_ZERO_ABSENCE_MODELS


def test_pr63_v25_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v25", "model_affordances_v25")

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
