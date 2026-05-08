from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V29_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v29.json"
)
AFFORDANCES_V30_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v30.json"
)

TARGET_RECORD_PATHS = {
    "chain-of-thought": MODEL_AFFORDANCE_DIR / "batch_17" / "chain-of-thought.json",
    "chain-of-verification": MODEL_AFFORDANCE_DIR
    / "batch_4"
    / "chain-of-verification.json",
    "latticework-of-mental-models": MODEL_AFFORDANCE_DIR
    / "batch_17"
    / "latticework-of-mental-models.json",
    "mental-models-of-reality": MODEL_AFFORDANCE_DIR
    / "batch_17"
    / "mental-models-of-reality.json",
    "meta-cognitive-reflection": MODEL_AFFORDANCE_DIR
    / "batch_17"
    / "meta-cognitive-reflection.json",
    "reasoning-mode-router": MODEL_AFFORDANCE_DIR
    / "batch_10"
    / "reasoning-mode-router.json",
}

TARGET_ABSENCE_FIELDS = {
    "anchored-or-template-captured-mode-selection",
    "actor-mental-model-inference",
    "confirmation-only-verification-chain",
    "elaborate-stepwise-chain-when-core-variable-or-nonlinear-leap-is-needed",
    "reflection-without-cognitive-quiet-or-action-budget",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr68_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr68_compiled_v30_is_v29_plus_five_absence_records() -> None:
    affordances_v29 = _load_compiled(AFFORDANCES_V29_PATH)
    affordances_v30 = _load_compiled(AFFORDANCES_V30_PATH)

    assert affordances_v30["artifact"] == "model_affordances_v30"
    assert affordances_v30["status"] == "draft_review_only"
    assert _model_ids(affordances_v30) == _model_ids(affordances_v29)
    assert len(_model_ids(affordances_v30)) == 222
    assert _affordance_ids(affordances_v30) == _affordance_ids(affordances_v29)
    assert TARGET_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v29))
    assert TARGET_ABSENCE_FIELDS.issubset(_absence_fields(affordances_v30))
    assert _absence_fields(affordances_v30) - _absence_fields(affordances_v29) == (
        TARGET_ABSENCE_FIELDS
    )

    v29_metadata = affordances_v29["compile_metadata"]
    v30_metadata = affordances_v30["compile_metadata"]
    assert v30_metadata["contributing_record_count"] == 222
    assert v30_metadata["affordance_count"] == v29_metadata["affordance_count"]
    assert v30_metadata["affordance_count"] == 268
    assert v30_metadata["absence_record_count"] == v29_metadata["absence_record_count"] + 5
    assert v30_metadata["absence_record_count"] == 474
    assert v30_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v30_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr68_guard_records_block_reasoning_theater_overactivation() -> None:
    chain_of_thought = _load_record("chain-of-thought")
    stepwise_guard = _absence_by_field(
        chain_of_thought,
        "elaborate-stepwise-chain-when-core-variable-or-nonlinear-leap-is-needed",
    )
    assert stepwise_guard["status"] == "not_supported_by_source"
    assert "nonlinear leap" in str(stepwise_guard["reason"])
    assert "one or two variables" in str(stepwise_guard["reason"])

    chain_of_verification = _load_record("chain-of-verification")
    verification_guard = _absence_by_field(
        chain_of_verification,
        "confirmation-only-verification-chain",
    )
    assert verification_guard["status"] == "not_supported_by_source"
    assert "disconfirmation path" in str(verification_guard["reason"])

    reasoning_mode_router = _load_record("reasoning-mode-router")
    routing_guard = _absence_by_field(
        reasoning_mode_router,
        "anchored-or-template-captured-mode-selection",
    )
    assert routing_guard["status"] == "not_supported_by_source"
    assert "first framing" in str(routing_guard["reason"])
    assert "contradictory evidence" in str(routing_guard["reason"])

    mental_models = _load_record("mental-models-of-reality")
    actor_guard = _absence_by_field(
        mental_models,
        "actor-mental-model-inference",
    )
    assert actor_guard["status"] == "duplicate_of_existing_field"
    assert "narrower empathy" in str(actor_guard["reason"])

    meta_reflection = _load_record("meta-cognitive-reflection")
    quiet_guard = _absence_by_field(
        meta_reflection,
        "reflection-without-cognitive-quiet-or-action-budget",
    )
    assert quiet_guard["status"] == "not_supported_by_source"
    assert "cognitive quiet" in str(quiet_guard["reason"])
    assert "timely relational response" in str(quiet_guard["reason"])


def test_pr68_broad_meta_treatments_surface_pruning_and_route_capture() -> None:
    latticework = _load_record("latticework-of-mental-models")
    latticework_affordance = _affordance_by_id(
        latticework,
        "latticework-of-mental-models.cross-check-causal-layers",
    )
    assert any(
        isinstance(requirement, dict)
        and requirement.get("requirement_id") == "cap-and-prune-model-set"
        for requirement in latticework_affordance["treatment_requirements"]
    )
    assert any(
        "model cuts should be pruned" in str(question)
        for question in latticework_affordance["diagnostic_questions"]
    )

    reasoning_mode_router = _load_record("reasoning-mode-router")
    router_affordance = _affordance_by_id(
        reasoning_mode_router,
        "reasoning-mode-router.context-driven-mode-selection-check",
    )
    first_requirement = router_affordance["treatment_requirements"][0]
    assert first_requirement["requirement_id"] == "name-stage-and-mode-fit"
    assert "familiar label" in str(first_requirement["evidence_required"])
    assert "template-captured" in str(first_requirement["good_output_shape"])


def test_pr68_v30_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v30", "model_affordances_v30")

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


def _affordance_by_id(
    record: dict[str, object],
    affordance_id: str,
) -> dict[str, object]:
    for affordance in record.get("affordances", []):
        if isinstance(affordance, dict) and affordance.get("affordance_id") == affordance_id:
            return affordance
    raise AssertionError(f"missing affordance: {affordance_id}")
