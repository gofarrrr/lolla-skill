from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V56_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v56.json"
)
AFFORDANCES_V57_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v57.json"
)

TARGET_RECORD_PATHS = {
    "chain-of-thought": MODEL_AFFORDANCE_DIR / "batch_17" / "chain-of-thought.json",
    "cognitive-biases": MODEL_AFFORDANCE_DIR / "batch_14" / "cognitive-biases.json",
    "cognitive-gaps-assessment": MODEL_AFFORDANCE_DIR
    / "batch_10"
    / "cognitive-gaps-assessment.json",
    "false-precision-avoidance": MODEL_AFFORDANCE_DIR
    / "batch_10"
    / "false-precision-avoidance.json",
    "reasoning-mode-router": MODEL_AFFORDANCE_DIR
    / "batch_10"
    / "reasoning-mode-router.json",
    "representativeness-heuristic": MODEL_AFFORDANCE_DIR
    / "batch_13"
    / "representativeness-heuristic.json",
}

NEW_ABSENCE_FIELDS = {
    "analysis-stop-rule-without-false-precision",
    "audience-processing-mode-as-reasoning-router-split",
    "bias-awareness-overcorrects-calibrated-intuition",
    "communication-analogy-as-probability-evidence",
    "communication-brevity-without-decision-threshold",
    "communication-transfer-as-standalone-gap-affordance",
    "exact-narrower-bias-available-as-general-bias-card",
    "expert-pattern-match-as-proof",
    "generic-unknown-unknowns-without-exposure",
    "logic-tree-decomposition-as-chain-of-thought-split",
    "perspective-taking-as-general-debiasing-affordance",
    "prompt-chaining-as-runtime-prompt-affordance",
    "prompt-concision-as-runtime-prompt-affordance",
    "recent-vividness-without-prototype-match",
    "role-prompt-or-agent-persona-routing-affordance",
    "slight-knowledge-advantage-as-gap-closure",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr95_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr95_compiled_v57_preserves_coverage_without_positive_splits() -> None:
    affordances_v56 = _load_compiled(AFFORDANCES_V56_PATH)
    affordances_v57 = _load_compiled(AFFORDANCES_V57_PATH)

    assert affordances_v57["artifact"] == "model_affordances_v57"
    assert affordances_v57["status"] == "draft_review_only"
    assert _model_ids(affordances_v57) == _model_ids(affordances_v56)
    assert len(_model_ids(affordances_v57)) == 222

    assert _affordance_ids(affordances_v57) == _affordance_ids(affordances_v56)
    assert NEW_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v56))
    assert _absence_fields(affordances_v57) - _absence_fields(affordances_v56) == (
        NEW_ABSENCE_FIELDS
    )

    v56_metadata = affordances_v56["compile_metadata"]
    v57_metadata = affordances_v57["compile_metadata"]
    assert v57_metadata["contributing_record_count"] == 222
    assert v57_metadata["affordance_count"] == v56_metadata["affordance_count"]
    assert v57_metadata["affordance_count"] == 303
    assert (
        v57_metadata["absence_record_count"]
        == v56_metadata["absence_record_count"] + len(NEW_ABSENCE_FIELDS)
    )
    assert v57_metadata["absence_record_count"] == 640
    assert v57_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v57_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr95_scope_records_remain_single_affordance_cards() -> None:
    expected_absence_counts = {
        "chain-of-thought": 6,
        "cognitive-biases": 5,
        "cognitive-gaps-assessment": 5,
        "false-precision-avoidance": 7,
        "reasoning-mode-router": 5,
        "representativeness-heuristic": 6,
    }

    for model_id, expected_absence_count in expected_absence_counts.items():
        record = _load_record(model_id)
        assert len(record["affordances"]) == 1
        assert len(record["absence_records"]) == expected_absence_count


def test_pr95_reasoning_friction_boundaries_are_first_class_absences() -> None:
    chain = _load_record("chain-of-thought")
    prompt_guard = _absence_by_field(
        chain,
        "prompt-chaining-as-runtime-prompt-affordance",
    )
    assert prompt_guard["status"] == "source_too_thin"
    assert "Prompt Chaining" in str(prompt_guard["source_evidence"])
    assert "runtime prompt mechanics" in prompt_guard["reason"]
    assert _absence_by_field(
        chain,
        "logic-tree-decomposition-as-chain-of-thought-split",
    )["status"] == "duplicate_of_existing_field"

    router = _load_record("reasoning-mode-router")
    role_prompt_guard = _absence_by_field(
        router,
        "role-prompt-or-agent-persona-routing-affordance",
    )
    assert role_prompt_guard["status"] == "source_too_thin"
    assert "persona" in str(role_prompt_guard["source_evidence"])
    assert "dormant skill prompts" in role_prompt_guard["reason"]
    assert _absence_by_field(
        router,
        "audience-processing-mode-as-reasoning-router-split",
    )["status"] == "duplicate_of_existing_field"

    gaps = _load_record("cognitive-gaps-assessment")
    guru_guard = _absence_by_field(gaps, "slight-knowledge-advantage-as-gap-closure")
    assert "guru" in str(guru_guard["source_evidence"])
    assert "authority-bias" in guru_guard["reason"]
    unknown_guard = _absence_by_field(gaps, "generic-unknown-unknowns-without-exposure")
    assert unknown_guard["status"] == "not_supported_by_source"
    assert "evidence bar" in unknown_guard["reason"]


def test_pr95_bias_probability_and_precision_boundaries_are_routed() -> None:
    representativeness = _load_record("representativeness-heuristic")
    analogy_guard = _absence_by_field(
        representativeness,
        "communication-analogy-as-probability-evidence",
    )
    assert analogy_guard["status"] == "duplicate_of_existing_field"
    assert "Uber of X" in str(analogy_guard["source_evidence"])
    assert "probability evidence" in analogy_guard["reason"]
    assert "I have seen this one before" in str(
        _absence_by_field(representativeness, "expert-pattern-match-as-proof")[
            "source_evidence"
        ]
    )

    biases = _load_record("cognitive-biases")
    narrower_bias_guard = _absence_by_field(
        biases,
        "exact-narrower-bias-available-as-general-bias-card",
    )
    assert narrower_bias_guard["status"] == "duplicate_of_existing_field"
    assert "Confirmation Bias" in str(narrower_bias_guard["source_evidence"])
    intuition_guard = _absence_by_field(
        biases,
        "bias-awareness-overcorrects-calibrated-intuition",
    )
    assert intuition_guard["runtime_policy"] == "do_not_promote"
    assert "calibrated intuition" in intuition_guard["reason"]

    false_precision = _load_record("false-precision-avoidance")
    assert _absence_by_field(
        false_precision,
        "analysis-stop-rule-without-false-precision",
    )["status"] == "duplicate_of_existing_field"
    prompt_guard = _absence_by_field(
        false_precision,
        "prompt-concision-as-runtime-prompt-affordance",
    )
    assert prompt_guard["status"] == "source_too_thin"
    assert "runtime prompt assembly" in prompt_guard["reason"]


def test_pr95_v57_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v57", "model_affordances_v57")

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


def _absence_by_field(record: dict[str, object], attempted_field: str) -> dict[str, object]:
    return next(
        absence
        for absence in record["absence_records"]
        if absence["attempted_field"] == attempted_field
    )
