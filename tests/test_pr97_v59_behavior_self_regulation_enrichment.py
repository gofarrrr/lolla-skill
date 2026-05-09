from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V58_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v58.json"
)
AFFORDANCES_V59_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v59.json"
)

TARGET_RECORD_PATHS = {
    "flow": MODEL_AFFORDANCE_DIR / "batch_1" / "flow.json",
    "goal-setting": MODEL_AFFORDANCE_DIR / "batch_8" / "goal-setting.json",
    "habit-formation": MODEL_AFFORDANCE_DIR / "batch_8" / "habit-formation.json",
    "input-vs-output-goals": MODEL_AFFORDANCE_DIR
    / "batch_8"
    / "input-vs-output-goals.json",
    "persistence-grit": MODEL_AFFORDANCE_DIR
    / "batch_14"
    / "persistence-grit.json",
    "self-control": MODEL_AFFORDANCE_DIR / "batch_14" / "self-control.json",
}

NEW_AFFORDANCE_IDS = {
    "self-control.deliberate-pause-before-impulse-action",
}

NEW_ABSENCE_FIELDS = {
    "abstract-accurate-goal-without-decision-guidance",
    "accurate-output-without-actionable-input",
    "ai-persona-consistency-as-habit-affordance",
    "ai-tendency-encoding-as-self-control-affordance",
    "cue-craving-diagnosis-as-standalone-card",
    "eisenhower-matrix-as-self-control-split",
    "exhaustive-effort-without-leverage",
    "felt-focus-as-problem-fit",
    "flow-without-feedback-or-coordination",
    "grind-without-recovery-or-load-management",
    "job-redesign-for-flow-as-standalone-affordance",
    "premature-solutioning-during-goal-selection",
    "professional-consistency-as-habit-split",
    "self-control-as-infinite-resource",
    "self-control-as-more-deliberation",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr97_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr97_compiled_v59_preserves_coverage_with_bounded_delta() -> None:
    affordances_v58 = _load_compiled(AFFORDANCES_V58_PATH)
    affordances_v59 = _load_compiled(AFFORDANCES_V59_PATH)

    assert affordances_v59["artifact"] == "model_affordances_v59"
    assert affordances_v59["status"] == "draft_review_only"
    assert _model_ids(affordances_v59) == _model_ids(affordances_v58)
    assert len(_model_ids(affordances_v59)) == 222

    assert NEW_AFFORDANCE_IDS.isdisjoint(_affordance_ids(affordances_v58))
    assert _affordance_ids(affordances_v59) - _affordance_ids(affordances_v58) == (
        NEW_AFFORDANCE_IDS
    )
    assert NEW_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v58))
    assert _absence_fields(affordances_v59) - _absence_fields(affordances_v58) == (
        NEW_ABSENCE_FIELDS
    )

    v58_metadata = affordances_v58["compile_metadata"]
    v59_metadata = affordances_v59["compile_metadata"]
    assert v59_metadata["contributing_record_count"] == 222
    assert (
        v59_metadata["affordance_count"]
        == v58_metadata["affordance_count"] + len(NEW_AFFORDANCE_IDS)
    )
    assert v59_metadata["affordance_count"] == 306
    assert (
        v59_metadata["absence_record_count"]
        == v58_metadata["absence_record_count"] + len(NEW_ABSENCE_FIELDS)
    )
    assert v59_metadata["absence_record_count"] == 679
    assert v59_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v59_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr97_self_control_split_has_distinct_pause_transaction() -> None:
    record = _load_record("self-control")
    parent = _affordance_by_id(record, "self-control.system-design-for-follow-through")
    pause_split = _affordance_by_id(
        record,
        "self-control.deliberate-pause-before-impulse-action",
    )

    assert len(record["affordances"]) == 2
    assert "pause-name-pressure-then-act-or-delay" in _requirement_ids(pause_split)
    assert "pause-name-pressure-then-act-or-delay" not in _requirement_ids(parent)
    assert "What’s happening?" in str(pause_split["source_evidence"])
    assert "Do I need more time?" in str(pause_split["source_evidence"])
    assert "steps were skipped" in str(pause_split["source_evidence"])
    assert "good-enough action threshold" in str(pause_split["activation_shape"])
    assert "minimum viable standard" not in str(parent["activation_shape"])

    assert _absence_by_field(
        record,
        "self-control-as-infinite-resource",
    )["status"] == "not_supported_by_source"
    assert "Prioritize adequate sleep, rest, and nutrition" in str(
        _absence_by_field(record, "self-control-as-infinite-resource")[
            "source_evidence"
        ]
    )
    assert "prioritization" in _absence_by_field(
        record,
        "eisenhower-matrix-as-self-control-split",
    )["reason"]


def test_pr97_behavior_records_are_hardened_without_extra_positive_splits() -> None:
    goal = _load_record("goal-setting")
    assert len(goal["affordances"]) == 1
    assert "only* set goals" in str(
        _absence_by_field(goal, "premature-solutioning-during-goal-selection")[
            "source_evidence"
        ]
    )
    assert "frontline employees make daily decisions" in str(
        _absence_by_field(goal, "abstract-accurate-goal-without-decision-guidance")[
            "source_evidence"
        ]
    )

    input_output = _load_record("input-vs-output-goals")
    assert len(input_output["affordances"]) == 1
    accurate_output_guard = _absence_by_field(
        input_output,
        "accurate-output-without-actionable-input",
    )
    assert accurate_output_guard["runtime_policy"] == "do_not_promote"
    assert "serve chicken salad" in str(accurate_output_guard["source_evidence"])

    grit = _load_record("persistence-grit")
    assert len(grit["affordances"]) == 1
    assert "Blind persistence" in str(
        _absence_by_field(grit, "grind-without-recovery-or-load-management")[
            "source_evidence"
        ]
    )
    assert "boil the ocean" in str(
        _absence_by_field(grit, "exhaustive-effort-without-leverage")[
            "source_evidence"
        ]
    )


def test_pr97_habit_and_flow_owner_boundaries_prevent_bloat() -> None:
    habit = _load_record("habit-formation")
    habit_card = _affordance_by_id(
        habit,
        "habit-formation.automatic-action-design-check",
    )
    assert len(habit["affordances"]) == 1
    assert "pristine document" not in str(habit_card["activation_shape"]["do_not_use_when"])
    assert "pristine document" in _absence_by_field(
        habit,
        "strategy-document-as-execution",
    )["reason"]
    assert _absence_by_field(
        habit,
        "cue-craving-diagnosis-as-standalone-card",
    )["status"] == "duplicate_of_existing_field"
    assert "**consistent** \"psychological fingerprint\"" in str(
        _absence_by_field(habit, "ai-persona-consistency-as-habit-affordance")[
            "source_evidence"
        ]
    )

    flow = _load_record("flow")
    assert len(flow["affordances"]) == 1
    assert "Are we solving the right problem?" in str(
        _absence_by_field(flow, "felt-focus-as-problem-fit")["source_evidence"]
    )
    assert "feedback loops, stakeholder coordination" in str(
        _absence_by_field(flow, "flow-without-feedback-or-coordination")[
            "source_evidence"
        ]
    )
    assert _absence_by_field(
        flow,
        "job-redesign-for-flow-as-standalone-affordance",
    )["status"] == "source_too_thin"


def test_pr97_v59_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v59", "model_affordances_v59")

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


def _absence_by_field(record: dict[str, object], attempted_field: str) -> dict[str, object]:
    return next(
        absence
        for absence in record["absence_records"]
        if absence["attempted_field"] == attempted_field
    )


def _requirement_ids(affordance: dict[str, object]) -> set[str]:
    return {
        requirement["requirement_id"]
        for requirement in affordance["treatment_requirements"]
    }
