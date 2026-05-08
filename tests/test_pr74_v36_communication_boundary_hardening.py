from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V35_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v35.json"
)
AFFORDANCES_V36_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v36.json"
)

TARGET_RECORD_PATHS = {
    "active-listening": MODEL_AFFORDANCE_DIR / "batch_6" / "active-listening.json",
    "constructive-feedback-models": MODEL_AFFORDANCE_DIR
    / "batch_6"
    / "constructive-feedback-models.json",
    "feedback-models-sbi": MODEL_AFFORDANCE_DIR
    / "batch_6"
    / "feedback-models-sbi.json",
    "persuasion-principles": MODEL_AFFORDANCE_DIR
    / "batch_7"
    / "persuasion-principles.json",
    "information-theory": MODEL_AFFORDANCE_DIR
    / "batch_13"
    / "information-theory.json",
    "curse-of-knowledge": MODEL_AFFORDANCE_DIR
    / "batch_14"
    / "curse-of-knowledge.json",
    "narratives": MODEL_AFFORDANCE_DIR / "batch_15" / "narratives.json",
    "storytelling-frameworks": MODEL_AFFORDANCE_DIR
    / "batch_15"
    / "storytelling-frameworks.json",
}

NEW_ABSENCE_FIELDS = {
    "compression-that-strips-system-or-human-signal",
    "listening-through-adversarial-incentives",
    "mindless-compliance-as-persuasion-goal",
    "narrative-when-protocol-or-threshold-needed",
    "sbi-with-incomplete-or-motivated-information",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr74_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr74_compiled_v36_hardens_without_new_affordance_ids() -> None:
    affordances_v35 = _load_compiled(AFFORDANCES_V35_PATH)
    affordances_v36 = _load_compiled(AFFORDANCES_V36_PATH)

    assert affordances_v36["artifact"] == "model_affordances_v36"
    assert affordances_v36["status"] == "draft_review_only"
    assert _model_ids(affordances_v36) == _model_ids(affordances_v35)
    assert len(_model_ids(affordances_v36)) == 222
    assert _affordance_ids(affordances_v36) == _affordance_ids(affordances_v35)
    assert len(_affordance_ids(affordances_v36)) == 271

    assert NEW_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v35))
    assert _absence_fields(affordances_v36) - _absence_fields(affordances_v35) == (
        NEW_ABSENCE_FIELDS
    )

    v35_metadata = affordances_v35["compile_metadata"]
    v36_metadata = affordances_v36["compile_metadata"]
    assert v36_metadata["contributing_record_count"] == 222
    assert v36_metadata["affordance_count"] == v35_metadata["affordance_count"]
    assert v36_metadata["affordance_count"] == 271
    assert (
        v36_metadata["absence_record_count"]
        == v35_metadata["absence_record_count"] + 5
    )
    assert v36_metadata["absence_record_count"] == 506
    assert v36_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v36_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr74_active_listening_hardens_without_split() -> None:
    record = _load_record("active-listening")
    affordance_ids = {affordance["affordance_id"] for affordance in record["affordances"]}
    assert affordance_ids == {"active-listening.hidden-disagreement-diagnostic-loop"}

    affordance = _affordance_by_id(
        record,
        "active-listening.hidden-disagreement-diagnostic-loop",
    )
    requirement = _requirement_by_id(
        affordance,
        "capture-process-before-abstracting-advice",
    )
    assert "how the person thinks" in str(requirement["description"])
    assert "generic best-practice advice" in str(affordance["misuse_guards"])
    assert "ask them how they think" in str(affordance["source_evidence"])

    guard = _absence_by_field(record, "listening-through-adversarial-incentives")
    assert guard["status"] == "duplicate_of_existing_field"
    assert "Prisoner's Dilemma" in str(guard["reason"])


def test_pr74_communication_hardeners_preserve_adjacent_boundaries() -> None:
    curse = _affordance_by_id(
        _load_record("curse-of-knowledge"),
        "curse-of-knowledge.audience-starting-state-reconstruction",
    )
    assert _requirement_by_id(curse, "verify-with-novice-demonstration")
    assert "direct novice observation" in str(curse["misuse_guards"])

    storytelling = _affordance_by_id(
        _load_record("storytelling-frameworks"),
        "storytelling-frameworks.structure-behavior-change-message",
    )
    assert _requirement_by_id(storytelling, "cut-search-story-and-excess-baggage")
    assert "story of the solution" in str(storytelling["diagnostic_questions"])

    feedback = _affordance_by_id(
        _load_record("constructive-feedback-models"),
        "constructive-feedback-models.specific-standard-correction",
    )
    assert _requirement_by_id(feedback, "check-machine-level-when-pattern-repeats")
    assert "machine level" in str(feedback["diagnostic_questions"])


def test_pr74_communication_guards_are_first_class_absences() -> None:
    assert _absence_by_field(
        _load_record("information-theory"),
        "compression-that-strips-system-or-human-signal",
    )["runtime_policy"] == "do_not_promote"
    assert _absence_by_field(
        _load_record("persuasion-principles"),
        "mindless-compliance-as-persuasion-goal",
    )["runtime_policy"] == "do_not_promote"
    assert _absence_by_field(
        _load_record("narratives"),
        "narrative-when-protocol-or-threshold-needed",
    )["status"] == "duplicate_of_existing_field"
    assert _absence_by_field(
        _load_record("feedback-models-sbi"),
        "sbi-with-incomplete-or-motivated-information",
    )["runtime_policy"] == "do_not_promote"


def test_pr74_v36_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v36", "model_affordances_v36")

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
