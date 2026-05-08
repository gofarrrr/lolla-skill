from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V28_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v28.json"
)
AFFORDANCES_V29_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v29.json"
)

TARGET_RECORD_PATHS = {
    "inversion": MODEL_AFFORDANCE_DIR / "pilot" / "inversion.json",
    "optionality": MODEL_AFFORDANCE_DIR / "pilot" / "optionality.json",
    "second-order-thinking": MODEL_AFFORDANCE_DIR
    / "pilot"
    / "second-order-thinking.json",
}

TARGET_ABSENCE_FIELDS = {
    "disjunctive-failsafe-as-optionality",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr67_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr67_compiled_v29_is_v28_plus_one_absence_record() -> None:
    affordances_v28 = _load_compiled(AFFORDANCES_V28_PATH)
    affordances_v29 = _load_compiled(AFFORDANCES_V29_PATH)

    assert affordances_v29["artifact"] == "model_affordances_v29"
    assert affordances_v29["status"] == "draft_review_only"
    assert _model_ids(affordances_v29) == _model_ids(affordances_v28)
    assert len(_model_ids(affordances_v29)) == 222
    assert _affordance_ids(affordances_v29) == _affordance_ids(affordances_v28)
    assert TARGET_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v28))
    assert TARGET_ABSENCE_FIELDS.issubset(_absence_fields(affordances_v29))
    assert _absence_fields(affordances_v29) - _absence_fields(affordances_v28) == (
        TARGET_ABSENCE_FIELDS
    )

    v28_metadata = affordances_v28["compile_metadata"]
    v29_metadata = affordances_v29["compile_metadata"]
    assert v29_metadata["contributing_record_count"] == 222
    assert v29_metadata["affordance_count"] == v28_metadata["affordance_count"]
    assert v29_metadata["affordance_count"] == 268
    assert v29_metadata["absence_record_count"] == v28_metadata["absence_record_count"] + 1
    assert v29_metadata["absence_record_count"] == 469
    assert v29_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v29_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr67_optionality_guard_blocks_generic_failsafe_pickup() -> None:
    optionality = _load_record("optionality")
    guard = _absence_by_field(optionality, "disjunctive-failsafe-as-optionality")

    assert guard["status"] == "duplicate_of_existing_field"
    assert "reversible paths" in str(guard["reason"])
    assert "Pure component-failure mitigation" in str(guard["reason"])


def test_pr67_second_order_recovery_path_check_is_folded_into_existing_affordance() -> None:
    second_order = _load_record("second-order-thinking")
    affordance = _affordance_by_id(
        second_order,
        "second-order-thinking.downstream-reversal-stress-test",
    )

    requirements = affordance["treatment_requirements"]
    assert any(
        isinstance(requirement, dict)
        and requirement.get("requirement_id") == "recovery-path-check"
        for requirement in requirements
    )
    assert any(
        "cheap recovery path has already disappeared" in str(question)
        for question in affordance["diagnostic_questions"]
    )
    assert any(
        isinstance(evidence, dict)
        and "cheap recovery path has already disappeared"
        in str(evidence.get("source_quote"))
        for evidence in affordance["source_evidence"]
    )


def test_pr67_v29_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v29", "model_affordances_v29")

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


def _affordance_by_id(
    record: dict[str, object],
    affordance_id: str,
) -> dict[str, object]:
    for affordance in record.get("affordances", []):
        if isinstance(affordance, dict) and affordance.get("affordance_id") == affordance_id:
            return affordance
    raise AssertionError(f"missing affordance: {affordance_id}")


def _absence_by_field(
    record: dict[str, object],
    attempted_field: str,
) -> dict[str, object]:
    for absence in record.get("absence_records", []):
        if isinstance(absence, dict) and absence.get("attempted_field") == attempted_field:
            return absence
    raise AssertionError(f"missing absence record: {attempted_field}")
