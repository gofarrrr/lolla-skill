from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V40_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v40.json"
)
AFFORDANCES_V41_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v41.json"
)

TARGET_RECORD_PATHS = {
    "butterfly-effect": MODEL_AFFORDANCE_DIR / "batch_9" / "butterfly-effect.json",
    "chaos-theory": MODEL_AFFORDANCE_DIR / "batch_9" / "chaos-theory.json",
    "emergence": MODEL_AFFORDANCE_DIR / "batch_1" / "emergence.json",
    "self-organization-and-emergent-order": MODEL_AFFORDANCE_DIR
    / "batch_16"
    / "self-organization-and-emergent-order.json",
}

NEW_ABSENCE_FIELDS = {
    "let-it-emerge-without-minimal-structure",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr79_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr79_compiled_v41_adds_only_complexity_guard_absence() -> None:
    affordances_v40 = _load_compiled(AFFORDANCES_V40_PATH)
    affordances_v41 = _load_compiled(AFFORDANCES_V41_PATH)

    assert affordances_v41["artifact"] == "model_affordances_v41"
    assert affordances_v41["status"] == "draft_review_only"
    assert _model_ids(affordances_v41) == _model_ids(affordances_v40)
    assert len(_model_ids(affordances_v41)) == 222

    assert _affordance_ids(affordances_v41) == _affordance_ids(affordances_v40)
    assert NEW_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v40))
    assert _absence_fields(affordances_v41) - _absence_fields(affordances_v40) == (
        NEW_ABSENCE_FIELDS
    )

    v40_metadata = affordances_v40["compile_metadata"]
    v41_metadata = affordances_v41["compile_metadata"]
    assert v41_metadata["contributing_record_count"] == 222
    assert v41_metadata["affordance_count"] == v40_metadata["affordance_count"]
    assert v41_metadata["affordance_count"] == 276
    assert (
        v41_metadata["absence_record_count"]
        == v40_metadata["absence_record_count"] + 1
    )
    assert v41_metadata["absence_record_count"] == 515
    assert v41_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v41_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr79_emergence_blocks_let_it_emerge_without_minimal_structure() -> None:
    record = _load_record("emergence")
    guard = _absence_by_field(record, "let-it-emerge-without-minimal-structure")

    assert guard["runtime_policy"] == "do_not_promote"
    assert "minimal structure, constraints, and feedback" in str(guard["reason"])
    assert "spontaneity or openness" in str(guard["source_evidence"])
    assert "setting the minimal structure, constraints, and feedback" in str(
        guard["source_evidence"]
    )
    assert "let-it-emerge/no-design" in str(record["review_notes"])


def test_pr79_butterfly_effect_hardens_cascade_mysticism_guard() -> None:
    record = _load_record("butterfly-effect")
    guard = _absence_by_field(record, "cascade-mysticism")

    assert guard["runtime_policy"] == "do_not_promote"
    assert "plausible transmission path" in str(guard["reason"])
    assert "plausible transmission path" in str(guard["source_evidence"])
    assert "anti-mysticism rail" in str(record["review_notes"])


def test_pr79_chaos_theory_hardens_accountability_escape_guard() -> None:
    record = _load_record("chaos-theory")
    guard = _absence_by_field(record, "chaos-as-accountability-escape")

    assert guard["runtime_policy"] == "do_not_promote"
    assert "avoid prioritization, bounded bets, or accountability" in str(
        guard["reason"]
    )
    assert "prioritization, bounded bets, or accountability" in str(
        guard["source_evidence"]
    )
    assert "adaptation and monitoring" in str(guard["source_evidence"])
    assert "accountability rail" in str(record["review_notes"])


def test_pr79_self_organization_hardens_no_design_guard() -> None:
    record = _load_record("self-organization-and-emergent-order")
    guard = _absence_by_field(record, "emergent-order-as-no-design-needed")

    assert guard["runtime_policy"] == "do_not_promote"
    assert "design is unnecessary" in str(guard["reason"])
    assert "goals, feedback, or guardrails" in str(guard["source_evidence"])
    assert "drift rather than adapt intelligently" in str(guard["source_evidence"])
    assert "no-design-needed absence" in str(record["review_notes"])


def test_pr79_v41_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v41", "model_affordances_v41")

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


def _absence_by_field(
    record: dict[str, object],
    attempted_field: str,
) -> dict[str, object]:
    return next(
        absence
        for absence in record["absence_records"]
        if absence["attempted_field"] == attempted_field
    )
