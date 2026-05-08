from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V44_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v44.json"
)
AFFORDANCES_V45_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v45.json"
)

TARGET_RECORD_PATHS = {
    "calculated-risk-taking": MODEL_AFFORDANCE_DIR
    / "batch_1"
    / "calculated-risk-taking.json",
    "expected-value": MODEL_AFFORDANCE_DIR / "batch_1" / "expected-value.json",
    "multi-criteria-decision-analysis": MODEL_AFFORDANCE_DIR
    / "batch_1"
    / "multi-criteria-decision-analysis.json",
    "opportunity-cost": MODEL_AFFORDANCE_DIR / "batch_3a" / "opportunity-cost.json",
    "prioritization": MODEL_AFFORDANCE_DIR / "batch_2" / "prioritization.json",
    "risk-assessment": MODEL_AFFORDANCE_DIR / "batch_1" / "risk-assessment.json",
    "status-quo-bias": MODEL_AFFORDANCE_DIR / "batch_5" / "status-quo-bias.json",
    "sunk-cost-fallacy": MODEL_AFFORDANCE_DIR
    / "batch_1"
    / "sunk-cost-fallacy.json",
    "trade-offs": MODEL_AFFORDANCE_DIR / "batch_1" / "trade-offs.json",
}

NEW_AFFORDANCE_IDS = {
    "status-quo-bias.default-choice-architecture",
    "sunk-cost-fallacy.precommitment-exit-criteria",
}

NEW_ABSENCE_FIELDS = {
    "calculated-label-with-unbounded-downside",
    "criteria-chosen-after-option-review",
    "default-continuation-as-costless",
    "ev-without-verifiable-causal-links",
    "rhetorical-tradeoff-without-reallocation",
    "risk-work-as-governance-optics",
    "symptom-ranking-before-root-cause",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr83_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr83_compiled_v45_adds_decision_action_enrichment() -> None:
    affordances_v44 = _load_compiled(AFFORDANCES_V44_PATH)
    affordances_v45 = _load_compiled(AFFORDANCES_V45_PATH)

    assert affordances_v45["artifact"] == "model_affordances_v45"
    assert affordances_v45["status"] == "draft_review_only"
    assert _model_ids(affordances_v45) == _model_ids(affordances_v44)
    assert len(_model_ids(affordances_v45)) == 222

    assert NEW_AFFORDANCE_IDS.isdisjoint(_affordance_ids(affordances_v44))
    assert _affordance_ids(affordances_v45) - _affordance_ids(affordances_v44) == (
        NEW_AFFORDANCE_IDS
    )
    assert NEW_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v44))
    assert _absence_fields(affordances_v45) - _absence_fields(affordances_v44) == (
        NEW_ABSENCE_FIELDS
    )

    v44_metadata = affordances_v44["compile_metadata"]
    v45_metadata = affordances_v45["compile_metadata"]
    assert v45_metadata["contributing_record_count"] == 222
    assert v45_metadata["affordance_count"] == v44_metadata["affordance_count"] + 2
    assert v45_metadata["affordance_count"] == 284
    assert (
        v45_metadata["absence_record_count"]
        == v44_metadata["absence_record_count"] + 7
    )
    assert v45_metadata["absence_record_count"] == 555
    assert v45_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v45_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr83_split_affordances_preserve_transaction_identity() -> None:
    sunk_cost = _load_record("sunk-cost-fallacy")
    status_quo = _load_record("status-quo-bias")

    recommitment = _affordance_by_id(
        sunk_cost,
        "sunk-cost-fallacy.future-value-recommitment",
    )
    precommitment = _affordance_by_id(
        sunk_cost,
        "sunk-cost-fallacy.precommitment-exit-criteria",
    )
    incumbent_test = _affordance_by_id(
        status_quo,
        "status-quo-bias.incumbent-option-inertia-test",
    )
    default_design = _affordance_by_id(
        status_quo,
        "status-quo-bias.default-choice-architecture",
    )

    assert "Proactively define specific conditions" not in str(recommitment)
    assert "predefine-stop-change-criteria" in str(precommitment)
    assert "before sunk-cost pressure forms" in str(precommitment["review_notes"])
    assert "knee-deep in the Big Muddy" in str(precommitment["source_evidence"])

    assert "automatically enrolls employees in a 401(k) plan" in str(
        default_design["source_evidence"]
    )
    assert "reduce-choice-overload-with-welfare-check" in str(default_design)
    assert "default-choice-architecture" not in incumbent_test["affordance_id"]
    assert "exploitative inertia" in str(default_design)


def test_pr83_absence_rails_block_false_decision_authority() -> None:
    assert "causal links between events that can be verified" in str(
        _absence_by_field(
            _load_record("expected-value"),
            "ev-without-verifiable-causal-links",
        )
    )
    assert "criteria must be established *before* reviewing the options" in str(
        _absence_by_field(
            _load_record("multi-criteria-decision-analysis"),
            "criteria-chosen-after-option-review",
        )
    )
    assert "presenting problem (symptom)" in str(
        _absence_by_field(
            _load_record("prioritization"),
            "symptom-ranking-before-root-cause",
        )
    )
    assert "refuse to actually reallocate resources" in str(
        _absence_by_field(
            _load_record("trade-offs"),
            "rhetorical-tradeoff-without-reallocation",
        )
    )


def test_pr83_absence_rails_block_false_action_and_safety() -> None:
    assert "staying the course has no cost" in str(
        _absence_by_field(
            _load_record("opportunity-cost"),
            "default-continuation-as-costless",
        )
    )
    assert "downside was not bounded" in str(
        _absence_by_field(
            _load_record("calculated-risk-taking"),
            "calculated-label-with-unbounded-downside",
        )
    )
    assert "governance optics" in str(
        _absence_by_field(
            _load_record("risk-assessment"),
            "risk-work-as-governance-optics",
        )
    )


def test_pr83_v45_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v45", "model_affordances_v45")

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
    for affordance in record["affordances"]:
        if affordance["affordance_id"] == affordance_id:
            return affordance
    raise AssertionError(f"Missing affordance_id: {affordance_id}")


def _absence_by_field(
    record: dict[str, object],
    attempted_field: str,
) -> dict[str, object]:
    for absence in record["absence_records"]:
        if absence["attempted_field"] == attempted_field:
            return absence
    raise AssertionError(f"Missing absence attempted_field: {attempted_field}")
