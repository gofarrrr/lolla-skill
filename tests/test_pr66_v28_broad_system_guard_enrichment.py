from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V27_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v27.json"
)
AFFORDANCES_V28_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v28.json"
)

TARGET_RECORD_PATHS = {
    "incentives": MODEL_AFFORDANCE_DIR / "batch_1" / "incentives.json",
    "systems-thinking": MODEL_AFFORDANCE_DIR / "pilot" / "systems-thinking.json",
}

TARGET_ABSENCE_FIELDS = {
    "emotional-desire-communication-as-standalone-incentives-affordance",
    "environment-reshaping-decision-without-loop-evidence",
    "generic-complexity-or-latticework-without-system-behavior",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr66_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr66_compiled_v28_is_v27_plus_three_absence_records() -> None:
    affordances_v27 = _load_compiled(AFFORDANCES_V27_PATH)
    affordances_v28 = _load_compiled(AFFORDANCES_V28_PATH)

    assert affordances_v28["artifact"] == "model_affordances_v28"
    assert affordances_v28["status"] == "draft_review_only"
    assert _model_ids(affordances_v28) == _model_ids(affordances_v27)
    assert len(_model_ids(affordances_v28)) == 222
    assert _affordance_ids(affordances_v28) == _affordance_ids(affordances_v27)
    assert TARGET_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v27))
    assert TARGET_ABSENCE_FIELDS.issubset(_absence_fields(affordances_v28))
    assert _absence_fields(affordances_v28) - _absence_fields(affordances_v27) == (
        TARGET_ABSENCE_FIELDS
    )

    v27_metadata = affordances_v27["compile_metadata"]
    v28_metadata = affordances_v28["compile_metadata"]
    assert v28_metadata["contributing_record_count"] == 222
    assert v28_metadata["affordance_count"] == v27_metadata["affordance_count"]
    assert v28_metadata["affordance_count"] == 268
    assert v28_metadata["absence_record_count"] == v27_metadata["absence_record_count"] + 3
    assert v28_metadata["absence_record_count"] == 468
    assert v28_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v28_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr66_guard_records_block_broad_system_overactivation() -> None:
    incentives = _load_record("incentives")
    emotion_guard = _absence_by_field(
        incentives,
        "emotional-desire-communication-as-standalone-incentives-affordance",
    )
    assert emotion_guard["status"] == "duplicate_of_existing_field"
    assert "Pure emotional copy or persuasion pickup" in str(emotion_guard["reason"])

    systems_thinking = _load_record("systems-thinking")
    generic_complexity_guard = _absence_by_field(
        systems_thinking,
        "generic-complexity-or-latticework-without-system-behavior",
    )
    environment_guard = _absence_by_field(
        systems_thinking,
        "environment-reshaping-decision-without-loop-evidence",
    )
    assert generic_complexity_guard["status"] == "not_supported_by_source"
    assert "actual system behavior evidence" in str(generic_complexity_guard["reason"])
    assert environment_guard["status"] == "duplicate_of_existing_field"
    assert "feedback-loop mapping" in str(environment_guard["reason"])


def test_pr66_v28_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v28", "model_affordances_v28")

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


def _absence_by_field(
    record: dict[str, object],
    attempted_field: str,
) -> dict[str, object]:
    for absence in record.get("absence_records", []):
        if isinstance(absence, dict) and absence.get("attempted_field") == attempted_field:
            return absence
    raise AssertionError(f"missing absence record: {attempted_field}")
