from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V37_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v37.json"
)
AFFORDANCES_V38_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v38.json"
)

TARGET_RECORD_PATHS = {
    "bayesian": MODEL_AFFORDANCE_DIR / "batch_13" / "bayesian.json",
    "expected-value": MODEL_AFFORDANCE_DIR / "batch_1" / "expected-value.json",
    "false-precision-avoidance": MODEL_AFFORDANCE_DIR
    / "batch_10"
    / "false-precision-avoidance.json",
    "risk-assessment": MODEL_AFFORDANCE_DIR / "batch_1" / "risk-assessment.json",
}

NEW_ABSENCE_FIELDS = {
    "human-system-risk-without-personal-data-routing",
    "precision-avoidance-that-blocks-needed-probability-update",
    "short-run-structural-shift-claim-without-explicit-update",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr76_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr76_compiled_v38_hardens_without_new_affordance_ids() -> None:
    affordances_v37 = _load_compiled(AFFORDANCES_V37_PATH)
    affordances_v38 = _load_compiled(AFFORDANCES_V38_PATH)

    assert affordances_v38["artifact"] == "model_affordances_v38"
    assert affordances_v38["status"] == "draft_review_only"
    assert _model_ids(affordances_v38) == _model_ids(affordances_v37)
    assert len(_model_ids(affordances_v38)) == 222
    assert _affordance_ids(affordances_v38) == _affordance_ids(affordances_v37)
    assert len(_affordance_ids(affordances_v38)) == 271

    assert NEW_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v37))
    assert _absence_fields(affordances_v38) - _absence_fields(affordances_v37) == (
        NEW_ABSENCE_FIELDS
    )

    v37_metadata = affordances_v37["compile_metadata"]
    v38_metadata = affordances_v38["compile_metadata"]
    assert v38_metadata["contributing_record_count"] == 222
    assert v38_metadata["affordance_count"] == v37_metadata["affordance_count"]
    assert v38_metadata["affordance_count"] == 271
    assert (
        v38_metadata["absence_record_count"]
        == v37_metadata["absence_record_count"] + 3
    )
    assert v38_metadata["absence_record_count"] == 512
    assert v38_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v38_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr76_expected_value_requires_boundary_condition_communication() -> None:
    record = _load_record("expected-value")
    affordance = _affordance_by_id(
        record,
        "expected-value.probability-weighted-payoff-boundary",
    )
    requirement = _requirement_by_id(
        affordance,
        "communicate-assumptions-and-boundary-conditions",
    )

    assert "boundary conditions" in str(requirement["description"])
    assert "The calculated EV must be shared" in str(affordance["source_evidence"])
    assert "stop being credible" in str(affordance["diagnostic_questions"])


def test_pr76_risk_assessment_routes_human_system_risk() -> None:
    record = _load_record("risk-assessment")
    guard = _absence_by_field(
        record,
        "human-system-risk-without-personal-data-routing",
    )

    assert guard["status"] == "duplicate_of_existing_field"
    assert guard["runtime_policy"] == "do_not_promote"
    assert "human-context models" in str(guard["reason"])
    assert "personal data" in str(guard["source_evidence"])


def test_pr76_false_precision_does_not_block_needed_probability_updates() -> None:
    record = _load_record("false-precision-avoidance")
    guard = _absence_by_field(
        record,
        "precision-avoidance-that-blocks-needed-probability-update",
    )

    assert guard["status"] == "duplicate_of_existing_field"
    assert "base-rates" in str(guard["reason"])
    assert "bayesian" in str(guard["reason"])
    assert "rounding away precision" in str(guard["source_evidence"])
    assert "quantitative prior-updating" in str(guard["source_evidence"])


def test_pr76_bayesian_routes_short_run_claims_to_noise_models() -> None:
    record = _load_record("bayesian")
    guard = _absence_by_field(
        record,
        "short-run-structural-shift-claim-without-explicit-update",
    )

    assert guard["status"] == "duplicate_of_existing_field"
    assert "regression-to-the-mean" in str(guard["reason"])
    assert "law-of-large-numbers" in str(guard["reason"])
    assert "short run of wins, losses, or experiment results" in str(
        guard["source_evidence"]
    )
    assert "sample size" in str(guard["source_evidence"])


def test_pr76_v38_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v38", "model_affordances_v38")

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
