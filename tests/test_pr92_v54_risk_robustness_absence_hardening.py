from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V53_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v53.json"
)
AFFORDANCES_V54_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v54.json"
)

TARGET_RECORD_PATHS = {
    "antifragility": MODEL_AFFORDANCE_DIR / "batch_2" / "antifragility.json",
    "calculated-risk-taking": MODEL_AFFORDANCE_DIR
    / "batch_1"
    / "calculated-risk-taking.json",
    "margin-of-safety": MODEL_AFFORDANCE_DIR / "batch_2" / "margin-of-safety.json",
    "resilience": MODEL_AFFORDANCE_DIR / "batch_2" / "resilience.json",
    "risk-assessment": MODEL_AFFORDANCE_DIR / "batch_1" / "risk-assessment.json",
    "risk-vs-uncertainty": MODEL_AFFORDANCE_DIR
    / "batch_9"
    / "risk-vs-uncertainty.json",
}

NEW_ABSENCE_FIELDS = {
    "cold-rationality-as-complete-calculation",
    "familiar-framework-as-calculated-risk",
    "fat-tail-false-precision-as-calculated-risk",
    "fear-uncertainty-doubt-without-risk-evidence",
    "mean-or-base-case-as-risk-envelope",
    "optimistic-base-case-as-margin-of-safety",
    "optimistic-explanation-style-as-risk-blindness",
    "resilience-as-overload-normalization",
    "static-buffer-as-durable-margin",
    "stress-exposure-without-feedback-update",
    "unknown-unknowns-as-exhaustively-mapped",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr92_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr92_compiled_v54_is_absence_only_delta() -> None:
    affordances_v53 = _load_compiled(AFFORDANCES_V53_PATH)
    affordances_v54 = _load_compiled(AFFORDANCES_V54_PATH)

    assert affordances_v54["artifact"] == "model_affordances_v54"
    assert affordances_v54["status"] == "draft_review_only"
    assert _model_ids(affordances_v54) == _model_ids(affordances_v53)
    assert len(_model_ids(affordances_v54)) == 222

    assert _affordance_ids(affordances_v54) == _affordance_ids(affordances_v53)
    assert NEW_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v53))
    assert _absence_fields(affordances_v54) - _absence_fields(affordances_v53) == (
        NEW_ABSENCE_FIELDS
    )

    v53_metadata = affordances_v53["compile_metadata"]
    v54_metadata = affordances_v54["compile_metadata"]
    assert v54_metadata["contributing_record_count"] == 222
    assert v54_metadata["affordance_count"] == v53_metadata["affordance_count"]
    assert v54_metadata["affordance_count"] == 298
    assert (
        v54_metadata["absence_record_count"]
        == v53_metadata["absence_record_count"] + 11
    )
    assert v54_metadata["absence_record_count"] == 594
    assert v54_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v54_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr92_risk_robustness_ring_remains_compressed_after_full_reread() -> None:
    affordances_v53 = _load_compiled(AFFORDANCES_V53_PATH)
    affordances_v54 = _load_compiled(AFFORDANCES_V54_PATH)

    v53_counts = _affordance_counts_by_model(affordances_v53)
    v54_counts = _affordance_counts_by_model(affordances_v54)

    for model_id in TARGET_RECORD_PATHS:
        assert v54_counts[model_id] == v53_counts[model_id]
        assert v54_counts[model_id] == 1


def test_pr92_absence_rails_block_broad_risk_theater() -> None:
    margin = _load_record("margin-of-safety")
    base_case_guard = _absence_by_field(
        margin,
        "optimistic-base-case-as-margin-of-safety",
    )
    static_buffer_guard = _absence_by_field(
        margin,
        "static-buffer-as-durable-margin",
    )
    assert "recent track record of estimation errors" in str(
        base_case_guard["source_evidence"]
    )
    assert "burn rate, exposure, or environmental volatility" in str(
        static_buffer_guard["source_evidence"]
    )

    risk_uncertainty = _load_record("risk-vs-uncertainty")
    unknown_unknowns_guard = _absence_by_field(
        risk_uncertainty,
        "unknown-unknowns-as-exhaustively-mapped",
    )
    risk_envelope_guard = _absence_by_field(
        risk_uncertainty,
        "mean-or-base-case-as-risk-envelope",
    )
    assert "no system can prepare for all risks" in str(
        unknown_unknowns_guard["source_evidence"]
    )
    assert "low-probability, high-impact risks" in str(
        risk_envelope_guard["source_evidence"]
    )

    calculated = _load_record("calculated-risk-taking")
    cold_rationality_guard = _absence_by_field(
        calculated,
        "cold-rationality-as-complete-calculation",
    )
    familiar_frame_guard = _absence_by_field(
        calculated,
        "familiar-framework-as-calculated-risk",
    )
    fat_tail_guard = _absence_by_field(
        calculated,
        "fat-tail-false-precision-as-calculated-risk",
    )
    assert "cold rationality" in str(cold_rationality_guard["source_evidence"])
    assert "I have seen this one before" in str(familiar_frame_guard["source_evidence"])
    assert "fat tails" in str(fat_tail_guard["source_evidence"])

    risk_assessment = _load_record("risk-assessment")
    fud_guard = _absence_by_field(
        risk_assessment,
        "fear-uncertainty-doubt-without-risk-evidence",
    )
    assert "FUD (Fear, Uncertainty, and Doubt)" in str(fud_guard["source_evidence"])
    assert fud_guard["runtime_policy"] == "do_not_promote"

    resilience = _load_record("resilience")
    overload_guard = _absence_by_field(
        resilience,
        "resilience-as-overload-normalization",
    )
    optimism_guard = _absence_by_field(
        resilience,
        "optimistic-explanation-style-as-risk-blindness",
    )
    assert "normalize overload" in str(overload_guard["source_evidence"])
    assert "bold forecasts and timid decisions" in str(optimism_guard["source_evidence"])

    antifragility = _load_record("antifragility")
    feedback_guard = _absence_by_field(
        antifragility,
        "stress-exposure-without-feedback-update",
    )
    assert "systematically compare outcomes" in str(feedback_guard["source_evidence"])
    assert "continually assessing and tweaking the plan" in str(
        feedback_guard["source_evidence"]
    )


def test_pr92_v54_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v54", "model_affordances_v54")

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
