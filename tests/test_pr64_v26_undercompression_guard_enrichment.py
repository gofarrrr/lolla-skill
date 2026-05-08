from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V25_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v25.json"
)
AFFORDANCES_V26_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v26.json"
)

TARGET_RECORD_PATHS = {
    "category-decisions": MODEL_AFFORDANCE_DIR
    / "batch_15"
    / "category-decisions.json",
    "conjunction-fallacy": MODEL_AFFORDANCE_DIR
    / "batch_13"
    / "conjunction-fallacy.json",
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

TARGET_ABSENCE_FIELDS = {
    "adversarial-countermove-simulation",
    "disjunctive-failure-risk-as-conjunctive-sequence",
    "expert-confidence-as-cumulative-risk-proof",
    "high-status-category-without-independent-rationale",
    "single-familiar-frame-without-context-fit",
    "threat-filter-communication-packaging",
}

DUPLICATE_ROUTING_FIELDS = {
    "adversarial-countermove-simulation",
    "threat-filter-communication-packaging",
}

REJECTED_DUPLICATE_AFFORDANCE_IDS = {
    "conjunction-fallacy.disjunctive-failure-risk-check",
    "evolutionary-pressure.threat-filter-communication-packaging",
    "international-negotiation-and-diplomacy-models.adversarial-countermove-simulation",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr64_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr64_compiled_v26_is_v25_plus_six_absence_records() -> None:
    affordances_v25 = _load_compiled(AFFORDANCES_V25_PATH)
    affordances_v26 = _load_compiled(AFFORDANCES_V26_PATH)

    assert affordances_v26["artifact"] == "model_affordances_v26"
    assert affordances_v26["status"] == "draft_review_only"
    assert _model_ids(affordances_v26) == _model_ids(affordances_v25)
    assert len(_model_ids(affordances_v26)) == 222
    assert _affordance_ids(affordances_v26) == _affordance_ids(affordances_v25)
    assert REJECTED_DUPLICATE_AFFORDANCE_IDS.isdisjoint(
        _affordance_ids(affordances_v26)
    )
    assert TARGET_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v25))
    assert TARGET_ABSENCE_FIELDS.issubset(_absence_fields(affordances_v26))
    assert _absence_fields(affordances_v26) - _absence_fields(affordances_v25) == (
        TARGET_ABSENCE_FIELDS
    )

    v25_metadata = affordances_v25["compile_metadata"]
    v26_metadata = affordances_v26["compile_metadata"]
    assert v26_metadata["contributing_record_count"] == 222
    assert v26_metadata["affordance_count"] == v25_metadata["affordance_count"]
    assert v26_metadata["affordance_count"] == 268
    assert v26_metadata["absence_record_count"] == v25_metadata["absence_record_count"] + 6
    assert v26_metadata["absence_record_count"] == 460
    assert v26_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v26_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr64_guard_records_block_undercompressed_or_duplicate_pickup() -> None:
    conjunction = _load_record("conjunction-fallacy")
    assert _absence_reason_contains(conjunction, "disjunctive failure structures")
    assert _absence_reason_contains(conjunction, "expert confidence alone")

    category = _load_record("category-decisions")
    assert _absence_reason_contains(category, "socially contagious")

    mental_models = _load_record("mental-models-of-reality")
    assert _absence_reason_contains(mental_models, "checking structural fit")

    evolutionary = _load_record("evolutionary-pressure")
    threat_filter = _absence_by_field(
        evolutionary,
        "threat-filter-communication-packaging",
    )
    assert threat_filter["status"] == "duplicate_of_existing_field"
    assert "audience-facing message adoption" in str(threat_filter["reason"])

    diplomacy = _load_record("international-negotiation-and-diplomacy-models")
    countermove = _absence_by_field(diplomacy, "adversarial-countermove-simulation")
    assert countermove["status"] == "duplicate_of_existing_field"
    assert "standalone countermove simulation" in str(countermove["reason"])

    assert {
        _absence_by_field(_record_for_field(field), field)["status"]
        for field in DUPLICATE_ROUTING_FIELDS
    } == {"duplicate_of_existing_field"}


def test_pr64_v26_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v26", "model_affordances_v26")

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


def _absence_by_field(
    record: dict[str, object],
    attempted_field: str,
) -> dict[str, object]:
    for absence in record.get("absence_records", []):
        if isinstance(absence, dict) and absence.get("attempted_field") == attempted_field:
            return absence
    raise AssertionError(f"missing absence record: {attempted_field}")


def _absence_reason_contains(record: dict[str, object], needle: str) -> bool:
    return any(
        needle in str(absence.get("reason", ""))
        for absence in record.get("absence_records", [])
        if isinstance(absence, dict)
    )


def _record_for_field(attempted_field: str) -> dict[str, object]:
    for model_id in TARGET_RECORD_PATHS:
        record = _load_record(model_id)
        if attempted_field in _absence_fields_from_record(record):
            return record
    raise AssertionError(f"missing record for absence field: {attempted_field}")


def _absence_fields_from_record(record: dict[str, object]) -> set[str]:
    return {
        str(absence["attempted_field"])
        for absence in record.get("absence_records", [])
        if isinstance(absence, dict)
    }
