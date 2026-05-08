from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V23_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v23.json"
)
AFFORDANCES_V24_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v24.json"
)

TARGET_RECORD_PATHS = {
    "anchoring": MODEL_AFFORDANCE_DIR / "batch_1" / "anchoring.json",
    "confidence-calibration": MODEL_AFFORDANCE_DIR
    / "pilot"
    / "confidence-calibration.json",
    "inversion": MODEL_AFFORDANCE_DIR / "pilot" / "inversion.json",
    "multi-criteria-decision-analysis": MODEL_AFFORDANCE_DIR
    / "batch_1"
    / "multi-criteria-decision-analysis.json",
    "optionality": MODEL_AFFORDANCE_DIR / "pilot" / "optionality.json",
    "second-order-thinking": MODEL_AFFORDANCE_DIR
    / "pilot"
    / "second-order-thinking.json",
    "systems-thinking": MODEL_AFFORDANCE_DIR / "pilot" / "systems-thinking.json",
}

TARGET_ABSENCE_FIELDS = {
    "audience-anchor-without-shared-schema",
    "calibration-as-bias-immunity",
    "domain-calibration-transfer-without-domain-evidence",
    "externalized-failure-without-internal-cause",
    "linear-blueprint-without-human-system-data",
    "matrix-output-without-frontline-decision-rule",
    "system-redesign-without-observed-behavior",
    "team-option-set-after-shared-anchor",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr62_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr62_compiled_v24_is_v23_plus_eight_absence_records() -> None:
    affordances_v23 = _load_compiled(AFFORDANCES_V23_PATH)
    affordances_v24 = _load_compiled(AFFORDANCES_V24_PATH)

    assert affordances_v24["artifact"] == "model_affordances_v24"
    assert affordances_v24["status"] == "draft_review_only"
    assert _model_ids(affordances_v24) == _model_ids(affordances_v23)
    assert len(_model_ids(affordances_v24)) == 222
    assert _affordance_ids(affordances_v24) == _affordance_ids(affordances_v23)
    assert TARGET_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v23))
    assert TARGET_ABSENCE_FIELDS.issubset(_absence_fields(affordances_v24))
    assert _absence_fields(affordances_v24) - _absence_fields(affordances_v23) == (
        TARGET_ABSENCE_FIELDS
    )

    v23_metadata = affordances_v23["compile_metadata"]
    v24_metadata = affordances_v24["compile_metadata"]
    assert v24_metadata["contributing_record_count"] == 222
    assert v24_metadata["affordance_count"] == v23_metadata["affordance_count"]
    assert v24_metadata["affordance_count"] == 268
    assert v24_metadata["absence_record_count"] == v23_metadata["absence_record_count"] + 8
    assert v24_metadata["absence_record_count"] == 449
    assert v24_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v24_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr62_guard_records_block_specific_overclaims() -> None:
    anchoring = _load_record("anchoring")
    assert "audience-anchor-without-shared-schema" in _absence_fields_from_record(
        anchoring
    )
    assert _absence_reason_contains(anchoring, "audience")

    mcda = _load_record("multi-criteria-decision-analysis")
    assert (
        "matrix-output-without-frontline-decision-rule"
        in _absence_fields_from_record(mcda)
    )
    assert _absence_reason_contains(mcda, "frontline")

    second_order = _load_record("second-order-thinking")
    assert "linear-blueprint-without-human-system-data" in _absence_fields_from_record(
        second_order
    )
    assert _absence_reason_contains(second_order, "living social system")

    optionality = _load_record("optionality")
    assert "team-option-set-after-shared-anchor" in _absence_fields_from_record(
        optionality
    )
    assert _absence_reason_contains(optionality, "first salient proposal")

    systems = _load_record("systems-thinking")
    assert "system-redesign-without-observed-behavior" in _absence_fields_from_record(
        systems
    )
    assert _absence_reason_contains(systems, "current-system behavior evidence")

    confidence = _load_record("confidence-calibration")
    assert "calibration-as-bias-immunity" in _absence_fields_from_record(confidence)
    assert "domain-calibration-transfer-without-domain-evidence" in (
        _absence_fields_from_record(confidence)
    )
    assert _absence_reason_contains(confidence, "bias-free")
    assert _absence_reason_contains(confidence, "domain-matched")

    inversion = _load_record("inversion")
    assert "externalized-failure-without-internal-cause" in _absence_fields_from_record(
        inversion
    )
    assert _absence_reason_contains(inversion, "internal decisions")


def test_pr62_v24_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v24", "model_affordances_v24")

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


def _absence_fields_from_record(record: dict[str, object]) -> set[str]:
    return {
        str(absence["attempted_field"])
        for absence in record.get("absence_records", [])
        if isinstance(absence, dict)
    }


def _absence_reason_contains(record: dict[str, object], needle: str) -> bool:
    return any(
        needle in str(absence.get("reason", ""))
        for absence in record.get("absence_records", [])
        if isinstance(absence, dict)
    )
