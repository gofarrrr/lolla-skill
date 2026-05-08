from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V33_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v33.json"
)
AFFORDANCES_V34_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v34.json"
)

TARGET_RECORD_PATHS = {
    "inversion": MODEL_AFFORDANCE_DIR / "pilot" / "inversion.json",
    "leverage-points": MODEL_AFFORDANCE_DIR / "batch_1" / "leverage-points.json",
    "second-order-thinking": MODEL_AFFORDANCE_DIR
    / "pilot"
    / "second-order-thinking.json",
}

NEW_AFFORDANCE_IDS = {
    "inversion.survivor-absence-signal",
    "inversion.zero-base-continuation-test",
    "leverage-points.value-driver-sensitivity-tree",
}

REJECTED_POSITIVE_SPLIT_IDS = {
    "leverage-points.core-message-leverage",
    "second-order-thinking.audience-mental-state-consequence",
    "second-order-thinking.machine-level-cause-diagnosis",
}

NEW_ABSENCE_FIELDS = {
    "generic-hidden-denominator-without-reversed-target",
    "audience-modeling-without-downstream-message-effect",
    "machine-level-diagnosis-without-downstream-consequence",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr72_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr72_compiled_v34_is_v33_plus_three_split_affordances() -> None:
    affordances_v33 = _load_compiled(AFFORDANCES_V33_PATH)
    affordances_v34 = _load_compiled(AFFORDANCES_V34_PATH)

    assert affordances_v34["artifact"] == "model_affordances_v34"
    assert affordances_v34["status"] == "draft_review_only"
    assert _model_ids(affordances_v34) == _model_ids(affordances_v33)
    assert len(_model_ids(affordances_v34)) == 222

    assert NEW_AFFORDANCE_IDS.isdisjoint(_affordance_ids(affordances_v33))
    assert NEW_AFFORDANCE_IDS.issubset(_affordance_ids(affordances_v34))
    assert REJECTED_POSITIVE_SPLIT_IDS.isdisjoint(_affordance_ids(affordances_v34))
    assert _affordance_ids(affordances_v34) - _affordance_ids(affordances_v33) == (
        NEW_AFFORDANCE_IDS
    )

    assert NEW_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v33))
    assert NEW_ABSENCE_FIELDS.issubset(_absence_fields(affordances_v34))
    assert _absence_fields(affordances_v34) - _absence_fields(affordances_v33) == (
        NEW_ABSENCE_FIELDS
    )

    v33_metadata = affordances_v33["compile_metadata"]
    v34_metadata = affordances_v34["compile_metadata"]
    assert v34_metadata["contributing_record_count"] == 222
    assert v34_metadata["affordance_count"] == v33_metadata["affordance_count"] + 3
    assert v34_metadata["affordance_count"] == 271
    assert (
        v34_metadata["absence_record_count"]
        == v33_metadata["absence_record_count"] + 3
    )
    assert v34_metadata["absence_record_count"] == 498
    assert v34_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v34_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr72_positive_splits_have_transaction_specific_evidence() -> None:
    inversion = _load_record("inversion")
    zero_base = _affordance_by_id(
        inversion,
        "inversion.zero-base-continuation-test",
    )
    assert "inherited path" in str(zero_base["activation_shape"]["do_not_use_when"])
    assert "continue, modify, or exit" in str(
        zero_base["treatment_requirements"][0]["good_output_shape"]
    )
    assert "clean sheet" in str(zero_base["source_evidence"])

    survivor_signal = _affordance_by_id(
        inversion,
        "inversion.survivor-absence-signal",
    )
    assert "reverses the apparent intervention target" in _absence_by_field(
        inversion,
        "generic-hidden-denominator-without-reversed-target",
    )["reason"]
    assert "survivorship-bias" in str(survivor_signal["misuse_guards"])
    assert "intervention target" in str(
        survivor_signal["treatment_requirements"][0]["good_output_shape"]
    )

    leverage = _load_record("leverage-points")
    value_driver = _affordance_by_id(
        leverage,
        "leverage-points.value-driver-sensitivity-tree",
    )
    assert "measurable" in str(value_driver["activation_shape"]["use_when"])
    assert "what if" in str(value_driver["source_evidence"])
    assert "practical influence" in str(
        value_driver["treatment_requirements"][0]["evidence_required"]
    )


def test_pr72_rejected_splits_are_absence_guards_not_positive_cards() -> None:
    leverage = _load_record("leverage-points")
    assert _absence_by_field(
        leverage,
        "standalone-communication-core-affordance",
    )["runtime_policy"] == "do_not_promote"
    assert "curse-of-knowledge" in str(
        _absence_by_field(
            leverage,
            "standalone-communication-core-affordance",
        )["reason"]
    )

    second_order = _load_record("second-order-thinking")
    machine_guard = _absence_by_field(
        second_order,
        "machine-level-diagnosis-without-downstream-consequence",
    )
    assert machine_guard["status"] == "duplicate_of_existing_field"
    assert "root-cause-analysis" in str(machine_guard["reason"])
    assert "downstream reversal" in str(machine_guard["reason"])

    audience_guard = _absence_by_field(
        second_order,
        "audience-modeling-without-downstream-message-effect",
    )
    assert audience_guard["status"] == "duplicate_of_existing_field"
    assert "curse-of-knowledge" in str(audience_guard["reason"])
    assert "second-order effect" in str(audience_guard["source_evidence"])


def test_pr72_v34_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v34", "model_affordances_v34")

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
