from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V22_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v22.json"
)
AFFORDANCES_V23_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v23.json"
)

TARGET_RECORD_PATHS = {
    "active-listening": MODEL_AFFORDANCE_DIR / "batch_6" / "active-listening.json",
    "chaos-theory": MODEL_AFFORDANCE_DIR / "batch_9" / "chaos-theory.json",
    "constructive-feedback-models": MODEL_AFFORDANCE_DIR
    / "batch_6"
    / "constructive-feedback-models.json",
    "elasticity": MODEL_AFFORDANCE_DIR / "batch_16" / "elasticity.json",
    "internal-locus-of-control": MODEL_AFFORDANCE_DIR
    / "batch_14"
    / "internal-locus-of-control.json",
    "meta-cognitive-reflection": MODEL_AFFORDANCE_DIR
    / "batch_17"
    / "meta-cognitive-reflection.json",
    "problem-framing-and-reframing": MODEL_AFFORDANCE_DIR
    / "pilot"
    / "problem-framing-and-reframing.json",
}

TARGET_ABSENCE_FIELDS = {
    "agency-as-dismissal-of-opposing-feedback",
    "case-at-hand-correction-without-process-diagnosis",
    "elastic-snippet-without-relevance-quality-check",
    "imposed-will-without-system-listening",
    "rationalization-as-reflection",
    "technical-frame-without-organizational-context",
    "vulnerability-probing-without-containment",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr61_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr61_compiled_v23_is_v22_plus_seven_absence_records() -> None:
    affordances_v22 = _load_compiled(AFFORDANCES_V22_PATH)
    affordances_v23 = _load_compiled(AFFORDANCES_V23_PATH)

    assert affordances_v23["artifact"] == "model_affordances_v23"
    assert affordances_v23["status"] == "draft_review_only"
    assert _model_ids(affordances_v23) == _model_ids(affordances_v22)
    assert len(_model_ids(affordances_v23)) == 222
    assert _affordance_ids(affordances_v23) == _affordance_ids(affordances_v22)
    assert TARGET_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v22))
    assert TARGET_ABSENCE_FIELDS.issubset(_absence_fields(affordances_v23))
    assert _absence_fields(affordances_v23) - _absence_fields(affordances_v22) == (
        TARGET_ABSENCE_FIELDS
    )

    v22_metadata = affordances_v22["compile_metadata"]
    v23_metadata = affordances_v23["compile_metadata"]
    assert v23_metadata["contributing_record_count"] == 222
    assert v23_metadata["affordance_count"] == v22_metadata["affordance_count"]
    assert v23_metadata["affordance_count"] == 268
    assert v23_metadata["absence_record_count"] == v22_metadata["absence_record_count"] + 7
    assert v23_metadata["absence_record_count"] == 441
    assert v23_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v23_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr61_guard_records_block_specific_overclaims() -> None:
    problem_framing = _load_record("problem-framing-and-reframing")
    assert (
        "technical-frame-without-organizational-context"
        in _absence_fields_from_record(problem_framing)
    )
    assert _absence_reason_contains(problem_framing, "organizational context")

    elasticity = _load_record("elasticity")
    assert (
        "elastic-snippet-without-relevance-quality-check"
        in _absence_fields_from_record(elasticity)
    )
    assert _absence_reason_contains(elasticity, "irrelevant, low quality")

    constructive_feedback = _load_record("constructive-feedback-models")
    assert (
        "case-at-hand-correction-without-process-diagnosis"
        in _absence_fields_from_record(constructive_feedback)
    )
    assert _absence_reason_contains(constructive_feedback, "process")

    internal_locus = _load_record("internal-locus-of-control")
    assert (
        "agency-as-dismissal-of-opposing-feedback"
        in _absence_fields_from_record(internal_locus)
    )
    assert _absence_reason_contains(internal_locus, "opposing feedback")

    meta_cognitive = _load_record("meta-cognitive-reflection")
    assert "rationalization-as-reflection" in _absence_fields_from_record(
        meta_cognitive
    )
    assert _absence_reason_contains(meta_cognitive, "post-hoc rationalization")

    active_listening = _load_record("active-listening")
    assert (
        "vulnerability-probing-without-containment"
        in _absence_fields_from_record(active_listening)
    )
    assert _absence_reason_contains(active_listening, "containment")

    chaos_theory = _load_record("chaos-theory")
    assert (
        "imposed-will-without-system-listening"
        in _absence_fields_from_record(chaos_theory)
    )
    assert _absence_reason_contains(chaos_theory, "observed system behavior")


def test_pr61_v23_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v23", "model_affordances_v23")

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
