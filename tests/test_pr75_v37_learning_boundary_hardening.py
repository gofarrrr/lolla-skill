from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V36_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v36.json"
)
AFFORDANCES_V37_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v37.json"
)

TARGET_RECORD_PATHS = {
    "metacognitive-questioning": MODEL_AFFORDANCE_DIR
    / "batch_10"
    / "metacognitive-questioning.json",
    "scaffolding": MODEL_AFFORDANCE_DIR / "batch_12" / "scaffolding.json",
    "growth-mindset": MODEL_AFFORDANCE_DIR / "batch_14" / "growth-mindset.json",
    "perceptual-learning": MODEL_AFFORDANCE_DIR
    / "batch_17"
    / "perceptual-learning.json",
    "scaffolding-educational": MODEL_AFFORDANCE_DIR
    / "batch_17"
    / "scaffolding-educational.json",
}

NEW_ABSENCE_FIELDS = {
    "generic-workflow-staging-as-educational-scaffolding",
    "growth-language-overrides-base-rates-or-stop-criteria",
    "instructional-novice-scaffold-as-generic-scaffolding",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr75_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr75_compiled_v37_hardens_without_new_affordance_ids() -> None:
    affordances_v36 = _load_compiled(AFFORDANCES_V36_PATH)
    affordances_v37 = _load_compiled(AFFORDANCES_V37_PATH)

    assert affordances_v37["artifact"] == "model_affordances_v37"
    assert affordances_v37["status"] == "draft_review_only"
    assert _model_ids(affordances_v37) == _model_ids(affordances_v36)
    assert len(_model_ids(affordances_v37)) == 222
    assert _affordance_ids(affordances_v37) == _affordance_ids(affordances_v36)
    assert len(_affordance_ids(affordances_v37)) == 271

    assert NEW_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v36))
    assert _absence_fields(affordances_v37) - _absence_fields(affordances_v36) == (
        NEW_ABSENCE_FIELDS
    )

    v36_metadata = affordances_v36["compile_metadata"]
    v37_metadata = affordances_v37["compile_metadata"]
    assert v37_metadata["contributing_record_count"] == 222
    assert v37_metadata["affordance_count"] == v36_metadata["affordance_count"]
    assert v37_metadata["affordance_count"] == 271
    assert (
        v37_metadata["absence_record_count"]
        == v36_metadata["absence_record_count"] + 3
    )
    assert v37_metadata["absence_record_count"] == 509
    assert v37_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v37_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr75_scaffolding_records_route_without_collapsing_ownership() -> None:
    scaffolding = _load_record("scaffolding")
    generic_guard = _absence_by_field(
        scaffolding,
        "instructional-novice-scaffold-as-generic-scaffolding",
    )
    assert generic_guard["status"] == "duplicate_of_existing_field"
    assert "scaffolding-educational" in str(generic_guard["reason"])

    educational = _load_record("scaffolding-educational")
    educational_guard = _absence_by_field(
        educational,
        "generic-workflow-staging-as-educational-scaffolding",
    )
    assert educational_guard["status"] == "duplicate_of_existing_field"
    assert "scaffolding" in str(educational_guard["reason"])


def test_pr75_growth_mindset_rejects_constraint_denial() -> None:
    record = _load_record("growth-mindset")
    guard = _absence_by_field(
        record,
        "growth-language-overrides-base-rates-or-stop-criteria",
    )

    assert guard["runtime_policy"] == "do_not_promote"
    assert "base-rates" in str(guard["reason"])
    assert "sunk-cost" in str(guard["reason"])
    assert "Danger When Growth Language Denies Real Constraints" in str(
        guard["source_evidence"]
    )


def test_pr75_perceptual_learning_hardens_tacit_cue_extraction() -> None:
    record = _load_record("perceptual-learning")
    affordance = _affordance_by_id(
        record,
        "perceptual-learning.train-cue-discrimination",
    )
    requirement = _requirement_by_id(
        affordance,
        "extract-tacit-cues-with-stories-and-pari",
    )

    assert "cue library" in str(requirement["description"])
    assert "Precursor, Action, Result, and Interpretation" in str(
        affordance["source_evidence"]
    )
    assert "generic expert interviewing" in str(affordance["misuse_guards"])


def test_pr75_metacognitive_questioning_hardens_next_question_cycle() -> None:
    record = _load_record("metacognitive-questioning")
    affordance = _affordance_by_id(
        record,
        "metacognitive-questioning.process-inspection-next-question-gate",
    )
    requirement = _requirement_by_id(
        affordance,
        "cycle-variables-question-and-consolidation",
    )

    assert "relevant variables" in str(requirement["description"])
    assert "Consolidating gains" in str(affordance["source_evidence"])
    assert "better question" in str(affordance["misuse_guards"])


def test_pr75_v37_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v37", "model_affordances_v37")

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


def _affordance_by_id(
    record: dict[str, object],
    affordance_id: str,
) -> dict[str, object]:
    return next(
        affordance
        for affordance in record["affordances"]
        if affordance["affordance_id"] == affordance_id
    )


def _requirement_by_id(
    affordance: dict[str, object],
    requirement_id: str,
) -> dict[str, object]:
    return next(
        requirement
        for requirement in affordance["treatment_requirements"]
        if requirement["requirement_id"] == requirement_id
    )


def _absence_by_field(record: dict[str, object], attempted_field: str) -> dict[str, object]:
    return next(
        absence
        for absence in record["absence_records"]
        if absence["attempted_field"] == attempted_field
    )
