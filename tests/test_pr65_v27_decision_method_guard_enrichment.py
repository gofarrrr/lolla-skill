from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V26_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v26.json"
)
AFFORDANCES_V27_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v27.json"
)

TARGET_RECORD_PATHS = {
    "base-rates": MODEL_AFFORDANCE_DIR / "pilot" / "base-rates.json",
    "expected-value": MODEL_AFFORDANCE_DIR / "batch_1" / "expected-value.json",
    "trade-offs": MODEL_AFFORDANCE_DIR / "batch_1" / "trade-offs.json",
}

TARGET_ABSENCE_FIELDS = {
    "standalone-compression-comprehensiveness-affordance",
    "standalone-decision-tree-scenario-or-game-theory-affordance",
    "standalone-minmax-game-theory-affordance",
    "standalone-reference-class-forecasting-affordance",
    "standalone-system-2-humility-or-debiasing-affordance",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr65_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr65_compiled_v27_is_v26_plus_five_absence_records() -> None:
    affordances_v26 = _load_compiled(AFFORDANCES_V26_PATH)
    affordances_v27 = _load_compiled(AFFORDANCES_V27_PATH)

    assert affordances_v27["artifact"] == "model_affordances_v27"
    assert affordances_v27["status"] == "draft_review_only"
    assert _model_ids(affordances_v27) == _model_ids(affordances_v26)
    assert len(_model_ids(affordances_v27)) == 222
    assert _affordance_ids(affordances_v27) == _affordance_ids(affordances_v26)
    assert TARGET_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v26))
    assert TARGET_ABSENCE_FIELDS.issubset(_absence_fields(affordances_v27))
    assert _absence_fields(affordances_v27) - _absence_fields(affordances_v26) == (
        TARGET_ABSENCE_FIELDS
    )

    v26_metadata = affordances_v26["compile_metadata"]
    v27_metadata = affordances_v27["compile_metadata"]
    assert v27_metadata["contributing_record_count"] == 222
    assert v27_metadata["affordance_count"] == v26_metadata["affordance_count"]
    assert v27_metadata["affordance_count"] == 268
    assert v27_metadata["absence_record_count"] == v26_metadata["absence_record_count"] + 5
    assert v27_metadata["absence_record_count"] == 465
    assert v27_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v27_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr65_guard_records_block_adjacent_method_pickup() -> None:
    base_rates = _load_record("base-rates")
    base_rate_guard = _absence_by_field(
        base_rates,
        "standalone-system-2-humility-or-debiasing-affordance",
    )
    assert base_rate_guard["status"] == "duplicate_of_existing_field"
    assert "outside-view reference-class anchoring" in str(base_rate_guard["reason"])

    expected_value = _load_record("expected-value")
    reference_guard = _absence_by_field(
        expected_value,
        "standalone-reference-class-forecasting-affordance",
    )
    method_guard = _absence_by_field(
        expected_value,
        "standalone-decision-tree-scenario-or-game-theory-affordance",
    )
    assert reference_guard["status"] == "duplicate_of_existing_field"
    assert method_guard["status"] == "duplicate_of_existing_field"
    assert "base-rates record" in str(reference_guard["reason"])
    assert "probability-weighted payoff comparison" in str(method_guard["reason"])

    trade_offs = _load_record("trade-offs")
    compression_guard = _absence_by_field(
        trade_offs,
        "standalone-compression-comprehensiveness-affordance",
    )
    game_theory_guard = _absence_by_field(
        trade_offs,
        "standalone-minmax-game-theory-affordance",
    )
    assert compression_guard["status"] == "duplicate_of_existing_field"
    assert game_theory_guard["status"] == "duplicate_of_existing_field"
    assert "Compression-specific behavior" in str(compression_guard["reason"])
    assert "game-theory-payoffs" in str(game_theory_guard["reason"])


def test_pr65_v27_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v27", "model_affordances_v27")

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
