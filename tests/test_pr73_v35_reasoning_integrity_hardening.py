from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V34_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v34.json"
)
AFFORDANCES_V35_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v35.json"
)

TARGET_RECORD_PATHS = {
    "chain-of-thought": MODEL_AFFORDANCE_DIR
    / "batch_17"
    / "chain-of-thought.json",
    "chain-of-verification": MODEL_AFFORDANCE_DIR
    / "batch_4"
    / "chain-of-verification.json",
    "critical-thinking": MODEL_AFFORDANCE_DIR
    / "batch_10"
    / "critical-thinking.json",
}

NEW_ABSENCE_FIELDS = {
    "emotion-filtered-rationality-as-critical-thinking",
    "sequence-probability-stress-test-as-chain-of-verification",
    "standalone-problem-disaggregation-as-critical-thinking",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr73_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr73_compiled_v35_hardens_without_new_affordance_ids() -> None:
    affordances_v34 = _load_compiled(AFFORDANCES_V34_PATH)
    affordances_v35 = _load_compiled(AFFORDANCES_V35_PATH)

    assert affordances_v35["artifact"] == "model_affordances_v35"
    assert affordances_v35["status"] == "draft_review_only"
    assert _model_ids(affordances_v35) == _model_ids(affordances_v34)
    assert len(_model_ids(affordances_v35)) == 222
    assert _affordance_ids(affordances_v35) == _affordance_ids(affordances_v34)

    assert NEW_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v34))
    assert NEW_ABSENCE_FIELDS.issubset(_absence_fields(affordances_v35))
    assert _absence_fields(affordances_v35) - _absence_fields(affordances_v34) == (
        NEW_ABSENCE_FIELDS
    )

    v34_metadata = affordances_v34["compile_metadata"]
    v35_metadata = affordances_v35["compile_metadata"]
    assert v35_metadata["contributing_record_count"] == 222
    assert v35_metadata["affordance_count"] == v34_metadata["affordance_count"]
    assert v35_metadata["affordance_count"] == 271
    assert (
        v35_metadata["absence_record_count"]
        == v34_metadata["absence_record_count"] + 3
    )
    assert v35_metadata["absence_record_count"] == 501
    assert v35_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v35_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr73_chain_of_thought_prunes_reasoning_theater() -> None:
    record = _load_record("chain-of-thought")
    affordance = _affordance_by_id(
        record,
        "chain-of-thought.audit-stepwise-reasoning",
    )
    prune_requirement = _requirement_by_id(
        affordance,
        "prune-chain-to-governing-answer",
    )

    assert "governing answer" in str(prune_requirement["description"])
    assert "low-value branches" in str(prune_requirement["good_output_shape"])
    assert "one-day answer" in str(affordance["diagnostic_questions"])
    assert "ruthlessly prune branches" in str(affordance["source_evidence"])


def test_pr73_chain_of_verification_routes_sequence_probability_elsewhere() -> None:
    record = _load_record("chain-of-verification")
    guard = _absence_by_field(
        record,
        "sequence-probability-stress-test-as-chain-of-verification",
    )

    assert guard["status"] == "duplicate_of_existing_field"
    assert guard["runtime_policy"] == "do_not_promote"
    assert "conjunction-fallacy" in str(guard["reason"])
    assert "auditable evidence trail" in str(guard["reason"])


def test_pr73_critical_thinking_preserves_relevant_human_data() -> None:
    record = _load_record("critical-thinking")
    affordance = _affordance_by_id(
        record,
        "critical-thinking.claim-evidence-assumption-check",
    )
    personal_data_requirement = _requirement_by_id(
        affordance,
        "preserve-personal-data-and-action-threshold",
    )
    framework_requirement = _requirement_by_id(
        affordance,
        "test-active-framework-fit",
    )

    assert "personal data" in str(personal_data_requirement["description"])
    assert "one-day answer" in str(personal_data_requirement["evidence_required"])
    assert "framework" in str(framework_requirement["description"])
    assert "stress fracture" in str(framework_requirement["evidence_required"])
    assert "framework shopping" in str(affordance["misuse_guards"])

    emotion_guard = _absence_by_field(
        record,
        "emotion-filtered-rationality-as-critical-thinking",
    )
    assert emotion_guard["runtime_policy"] == "do_not_promote"
    assert "personal data" in str(emotion_guard["reason"])

    decomposition_guard = _absence_by_field(
        record,
        "standalone-problem-disaggregation-as-critical-thinking",
    )
    assert decomposition_guard["status"] == "duplicate_of_existing_field"
    assert "decomposition" in str(decomposition_guard["reason"])


def test_pr73_v35_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v35", "model_affordances_v35")

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
