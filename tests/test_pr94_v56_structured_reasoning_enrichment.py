from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V55_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v55.json"
)
AFFORDANCES_V56_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v56.json"
)

TARGET_RECORD_PATHS = {
    "category-decisions": MODEL_AFFORDANCE_DIR
    / "batch_15"
    / "category-decisions.json",
    "conjunction-fallacy": MODEL_AFFORDANCE_DIR
    / "batch_13"
    / "conjunction-fallacy.json",
    "critical-thinking": MODEL_AFFORDANCE_DIR
    / "batch_10"
    / "critical-thinking.json",
    "evolutionary-pressure": MODEL_AFFORDANCE_DIR
    / "batch_16"
    / "evolutionary-pressure.json",
    "international-negotiation-and-diplomacy-models": MODEL_AFFORDANCE_DIR
    / "batch_7"
    / "international-negotiation-and-diplomacy-models.json",
    "mental-models-of-reality": MODEL_AFFORDANCE_DIR
    / "batch_17"
    / "mental-models-of-reality.json",
}

NEW_AFFORDANCE_IDS = {
    "category-decisions.category-of-one-positioning-frame",
    "critical-thinking.framework-fit-stress-fracture-check",
    "critical-thinking.personal-data-action-threshold-check",
}

NEW_ABSENCE_FIELDS = {
    "academic-selfie-as-standalone-affordance",
    "accessibility-over-accuracy-as-evolutionary-pressure",
    "adaptation-loop-without-selection-evidence",
    "category-lock-in-after-causal-shift",
    "evolutionary-logic-as-fatalism",
    "fud-tactic-as-diplomacy",
    "group-smoothed-step-probabilities-as-rigor",
    "model-name-collection-without-decision-pressure",
    "standalone-cwd-agent-orchestration",
    "universal-playbook-before-taxonomy-validation",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr94_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr94_compiled_v56_preserves_coverage_with_bounded_delta() -> None:
    affordances_v55 = _load_compiled(AFFORDANCES_V55_PATH)
    affordances_v56 = _load_compiled(AFFORDANCES_V56_PATH)

    assert affordances_v56["artifact"] == "model_affordances_v56"
    assert affordances_v56["status"] == "draft_review_only"
    assert _model_ids(affordances_v56) == _model_ids(affordances_v55)
    assert len(_model_ids(affordances_v56)) == 222

    assert NEW_AFFORDANCE_IDS.isdisjoint(_affordance_ids(affordances_v55))
    assert _affordance_ids(affordances_v56) - _affordance_ids(affordances_v55) == (
        NEW_AFFORDANCE_IDS
    )
    assert NEW_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v55))
    assert _absence_fields(affordances_v56) - _absence_fields(affordances_v55) == (
        NEW_ABSENCE_FIELDS
    )

    v55_metadata = affordances_v55["compile_metadata"]
    v56_metadata = affordances_v56["compile_metadata"]
    assert v56_metadata["contributing_record_count"] == 222
    assert (
        v56_metadata["affordance_count"]
        == v55_metadata["affordance_count"] + len(NEW_AFFORDANCE_IDS)
    )
    assert v56_metadata["affordance_count"] == 303
    assert (
        v56_metadata["absence_record_count"]
        == v55_metadata["absence_record_count"] + len(NEW_ABSENCE_FIELDS)
    )
    assert v56_metadata["absence_record_count"] == 624
    assert v56_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v56_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr94_positive_splits_have_distinct_receiver_transactions() -> None:
    category = _load_record("category-decisions")
    category_split = _affordance_by_id(
        category,
        "category-decisions.category-of-one-positioning-frame",
    )
    assert len(category["affordances"]) == 2
    assert "1 Specific Problem, 1 Specific Person, 1 Specific Way" in str(
        category_split["source_evidence"]
    )
    assert "jobs-to-be-done" in str(category_split["activation_shape"])
    assert "deterministic routing" in str(category_split["misuse_guards"])

    critical = _load_record("critical-thinking")
    framework_split = _affordance_by_id(
        critical,
        "critical-thinking.framework-fit-stress-fracture-check",
    )
    personal_data_split = _affordance_by_id(
        critical,
        "critical-thinking.personal-data-action-threshold-check",
    )
    assert len(critical["affordances"]) == 3
    assert "tiny stress fractures" in str(framework_split["source_evidence"])
    assert "decomposition" in str(framework_split["misuse_guards"])
    assert "missing crucial **personal data**" in str(
        personal_data_split["source_evidence"]
    )
    assert "one-day answers" in str(personal_data_split["source_evidence"])
    assert "empathy" in str(personal_data_split["activation_shape"])


def test_pr94_rejected_splits_are_preserved_as_absence_rails() -> None:
    conjunction = _load_record("conjunction-fallacy")
    assert len(conjunction["affordances"]) == 1
    group_smoothing_guard = _absence_by_field(
        conjunction,
        "group-smoothed-step-probabilities-as-rigor",
    )
    assert group_smoothing_guard["runtime_policy"] == "do_not_promote"
    assert "separate, independent judgments" in str(
        group_smoothing_guard["source_evidence"]
    )

    mental_models = _load_record("mental-models-of-reality")
    assert len(mental_models["affordances"]) == 1
    model_name_guard = _absence_by_field(
        mental_models,
        "model-name-collection-without-decision-pressure",
    )
    assert "collecting elegant models" in str(model_name_guard["source_evidence"])
    assert "mechanism, threshold, or protocol" in str(
        model_name_guard["source_evidence"]
    )

    evolutionary = _load_record("evolutionary-pressure")
    assert len(evolutionary["affordances"]) == 1
    assert _absence_by_field(
        evolutionary,
        "accessibility-over-accuracy-as-evolutionary-pressure",
    )["status"] == "duplicate_of_existing_field"
    assert "fatalism" in str(
        _absence_by_field(evolutionary, "evolutionary-logic-as-fatalism")[
            "source_evidence"
        ]
    )
    assert "what the system is rewarding" in str(
        _absence_by_field(evolutionary, "adaptation-loop-without-selection-evidence")[
            "source_evidence"
        ]
    )

    international = _load_record("international-negotiation-and-diplomacy-models")
    assert len(international["affordances"]) == 1
    assert "Coordinator, Worker, Delegator" in str(
        _absence_by_field(international, "standalone-cwd-agent-orchestration")[
            "source_evidence"
        ]
    )
    assert "FUD" in str(
        _absence_by_field(international, "fud-tactic-as-diplomacy")[
            "source_evidence"
        ]
    )


def test_pr94_v56_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v56", "model_affordances_v56")

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
