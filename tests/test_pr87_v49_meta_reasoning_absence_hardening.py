from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V48_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v48.json"
)
AFFORDANCES_V49_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v49.json"
)

TARGET_RECORD_PATHS = {
    "latticework-of-mental-models": MODEL_AFFORDANCE_DIR
    / "batch_17"
    / "latticework-of-mental-models.json",
    "mental-models-of-reality": MODEL_AFFORDANCE_DIR
    / "batch_17"
    / "mental-models-of-reality.json",
    "system-2": MODEL_AFFORDANCE_DIR / "batch_17" / "system-2.json",
}

NEW_ABSENCE_FIELDS = {
    "depleted-deliberation-window-as-reliable-audit",
    "high-level-abstraction-without-mechanism-threshold-or-protocol",
    "over-deliberation-overrides-validated-expert-intuition",
    "pseudo-deliberation-as-system-2",
    "surface-model-familiarity-as-expertise",
}

COMPRESSION_OK_MODEL_IDS = {
    "chain-of-thought",
    "chain-of-verification",
    "cognitive-gaps-assessment",
    "dialectical-reasoning",
    "formal-reasoning",
    "latticework-of-mental-models",
    "logical-fallacies",
    "mental-models-of-reality",
    "meta-cognitive-reflection",
    "reasoning-mode-router",
    "system-1",
    "system-2",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr87_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr87_compiled_v49_adds_absence_rails_without_positive_bloat() -> None:
    affordances_v48 = _load_compiled(AFFORDANCES_V48_PATH)
    affordances_v49 = _load_compiled(AFFORDANCES_V49_PATH)

    assert affordances_v49["artifact"] == "model_affordances_v49"
    assert affordances_v49["status"] == "draft_review_only"
    assert _model_ids(affordances_v49) == _model_ids(affordances_v48)
    assert len(_model_ids(affordances_v49)) == 222

    assert _affordance_ids(affordances_v49) == _affordance_ids(affordances_v48)
    assert NEW_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v48))
    assert _absence_fields(affordances_v49) - _absence_fields(affordances_v48) == (
        NEW_ABSENCE_FIELDS
    )

    v48_metadata = affordances_v48["compile_metadata"]
    v49_metadata = affordances_v49["compile_metadata"]
    assert v49_metadata["contributing_record_count"] == 222
    assert v49_metadata["affordance_count"] == v48_metadata["affordance_count"]
    assert v49_metadata["affordance_count"] == 293
    assert (
        v49_metadata["absence_record_count"]
        == v48_metadata["absence_record_count"] + 5
    )
    assert v49_metadata["absence_record_count"] == 567
    assert v49_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v49_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr87_meta_reasoning_absence_rails_are_source_backed() -> None:
    latticework = _load_record("latticework-of-mental-models")
    surface_expertise_guard = _absence_by_field(
        latticework,
        "surface-model-familiarity-as-expertise",
    )
    assert surface_expertise_guard["runtime_policy"] == "do_not_promote"
    assert "cargo-cult thinking" in str(surface_expertise_guard["source_evidence"])
    assert len(latticework["affordances"]) == 1

    mental_models = _load_record("mental-models-of-reality")
    abstraction_guard = _absence_by_field(
        mental_models,
        "high-level-abstraction-without-mechanism-threshold-or-protocol",
    )
    assert abstraction_guard["status"] == "not_supported_by_source"
    assert "mechanism, threshold, or protocol" in str(
        abstraction_guard["source_evidence"]
    )
    assert len(mental_models["affordances"]) == 1

    system_2 = _load_record("system-2")
    pseudo_deliberation_guard = _absence_by_field(
        system_2,
        "pseudo-deliberation-as-system-2",
    )
    depleted_window_guard = _absence_by_field(
        system_2,
        "depleted-deliberation-window-as-reliable-audit",
    )
    expert_intuition_guard = _absence_by_field(
        system_2,
        "over-deliberation-overrides-validated-expert-intuition",
    )
    assert pseudo_deliberation_guard["runtime_policy"] == "do_not_promote"
    assert "process is theater" in str(pseudo_deliberation_guard["source_evidence"])
    assert "System 2 fatigue is real" in str(depleted_window_guard["source_evidence"])
    assert "Not every decision benefits from deliberation" in str(
        expert_intuition_guard["source_evidence"]
    )
    assert len(system_2["affordances"]) == 1


def test_pr87_audited_broad_reasoning_records_remain_compressed() -> None:
    affordances_v48 = _load_compiled(AFFORDANCES_V48_PATH)
    affordances_v49 = _load_compiled(AFFORDANCES_V49_PATH)

    v48_counts = _affordance_counts_by_model(affordances_v48)
    v49_counts = _affordance_counts_by_model(affordances_v49)

    for model_id in COMPRESSION_OK_MODEL_IDS:
        assert v49_counts[model_id] == v48_counts[model_id]


def test_pr87_v49_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v49", "model_affordances_v49")

    for path in LIVE_RUNTIME_PATHS:
        text = path.read_text(encoding="utf-8")
        assert all(fragment not in text for fragment in forbidden)


def _load_record(model_id: str) -> dict[str, object]:
    return json.loads(TARGET_RECORD_PATHS[model_id].read_text(encoding="utf-8"))


def _load_compiled(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _model_ids(compiled: dict[str, object]) -> set[str]:
    return {record["model_id"] for record in compiled["model_records"]}


def _affordance_ids(compiled: dict[str, object]) -> set[str]:
    return {
        affordance["affordance_id"]
        for record in compiled["model_records"]
        for affordance in record["affordances"]
    }


def _absence_fields(compiled: dict[str, object]) -> set[str]:
    return {
        absence["attempted_field"]
        for record in compiled["model_records"]
        for absence in record["absence_records"]
    }


def _affordance_counts_by_model(compiled: dict[str, object]) -> dict[str, int]:
    return {
        record["model_id"]: len(record["affordances"])
        for record in compiled["model_records"]
    }


def _absence_by_field(record: dict[str, object], attempted_field: str) -> dict[str, object]:
    return next(
        absence
        for absence in record["absence_records"]
        if absence["attempted_field"] == attempted_field
    )
