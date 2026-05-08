from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V46_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v46.json"
)
AFFORDANCES_V47_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v47.json"
)

TARGET_RECORD_PATHS = {
    "abstraction": MODEL_AFFORDANCE_DIR / "batch_11" / "abstraction.json",
    "analogies-and-metaphors": MODEL_AFFORDANCE_DIR
    / "batch_6"
    / "analogies-and-metaphors.json",
    "association": MODEL_AFFORDANCE_DIR / "batch_11" / "association.json",
    "divergent-vs-convergent-thinking": MODEL_AFFORDANCE_DIR
    / "batch_11"
    / "divergent-vs-convergent-thinking.json",
    "mental-simulation": MODEL_AFFORDANCE_DIR
    / "batch_11"
    / "mental-simulation.json",
}

NEW_AFFORDANCE_IDS = {
    "abstraction.abductive-hypothesis-framing-check",
    "analogies-and-metaphors.generative-analogy-search",
    "association.schema-bridge-for-usable-context",
    "mental-simulation.persona-fidelity-role-play",
}

NEW_ABSENCE_FIELDS = {
    "demographic-only-persona-simulation",
    "schema-bridge-without-audience-action",
    "superficial-divergence-volume-without-variety",
}

COMPRESSION_OK_MODEL_IDS = {
    "adaptation",
    "brainstorming",
    "branch-solve-merge",
    "creative-destruction",
    "curiosity",
    "lateral-thinking",
    "narratives",
    "simplification",
    "synthesis-and-integration",
    "variation-and-selection",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr85_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr85_compiled_v47_adds_bounded_creative_synthesis_enrichment() -> None:
    affordances_v46 = _load_compiled(AFFORDANCES_V46_PATH)
    affordances_v47 = _load_compiled(AFFORDANCES_V47_PATH)

    assert affordances_v47["artifact"] == "model_affordances_v47"
    assert affordances_v47["status"] == "draft_review_only"
    assert _model_ids(affordances_v47) == _model_ids(affordances_v46)
    assert len(_model_ids(affordances_v47)) == 222

    assert NEW_AFFORDANCE_IDS.isdisjoint(_affordance_ids(affordances_v46))
    assert _affordance_ids(affordances_v47) - _affordance_ids(affordances_v46) == (
        NEW_AFFORDANCE_IDS
    )
    assert NEW_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v46))
    assert _absence_fields(affordances_v47) - _absence_fields(affordances_v46) == (
        NEW_ABSENCE_FIELDS
    )

    v46_metadata = affordances_v46["compile_metadata"]
    v47_metadata = affordances_v47["compile_metadata"]
    assert v47_metadata["contributing_record_count"] == 222
    assert v47_metadata["affordance_count"] == v46_metadata["affordance_count"] + 4
    assert v47_metadata["affordance_count"] == 291
    assert (
        v47_metadata["absence_record_count"]
        == v46_metadata["absence_record_count"] + 3
    )
    assert v47_metadata["absence_record_count"] == 558
    assert v47_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v47_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr85_positive_splits_preserve_receiver_transaction_identity() -> None:
    association = _load_record("association")
    schema_bridge = _affordance_by_id(
        association,
        "association.schema-bridge-for-usable-context",
    )
    structural_test = _affordance_by_id(
        association,
        "association.structural-association-test",
    )
    assert "map-schema-to-actionable-context" in str(
        schema_bridge["treatment_requirements"]
    )
    assert "instant context and understanding" in str(schema_bridge["source_evidence"])
    assert "proof" in str(schema_bridge["misuse_guards"])
    assert "schema-bridge" not in structural_test["affordance_id"]

    abstraction = _load_record("abstraction")
    hypothesis = _affordance_by_id(
        abstraction,
        "abstraction.abductive-hypothesis-framing-check",
    )
    assert "frame-hypothesis-then-test" in str(hypothesis["treatment_requirements"])
    assert "limited set of observations" in str(hypothesis["source_evidence"])
    assert "confirmed model" in str(hypothesis["misuse_guards"])

    mental_simulation = _load_record("mental-simulation")
    persona = _affordance_by_id(
        mental_simulation,
        "mental-simulation.persona-fidelity-role-play",
    )
    assert "define-persona-fidelity-and-validation" in str(
        persona["treatment_requirements"]
    )
    assert "digital twin creator" in str(persona["source_evidence"])
    assert "demographics alone" in str(persona["misuse_guards"])

    analogies = _load_record("analogies-and-metaphors")
    generative = _affordance_by_id(
        analogies,
        "analogies-and-metaphors.generative-analogy-search",
    )
    assert "generate-then-bound-analogy" in str(
        generative["treatment_requirements"]
    )
    assert "remote source domain" in str(generative["activation_shape"])
    assert "counterexamples" in str(generative["source_evidence"])
    assert "proof" in str(generative["misuse_guards"])


def test_pr85_new_absences_guard_quality_without_positive_bloat() -> None:
    association = _load_record("association")
    assert _absence_by_field(
        association,
        "schema-bridge-without-audience-action",
    )["runtime_policy"] == "do_not_promote"
    assert "action or clear predictions" in str(
        _absence_by_field(
            association,
            "schema-bridge-without-audience-action",
        )["source_evidence"]
    )

    mental_simulation = _load_record("mental-simulation")
    persona_guard = _absence_by_field(
        mental_simulation,
        "demographic-only-persona-simulation",
    )
    assert persona_guard["status"] == "not_supported_by_source"
    assert "stereotyping" in str(persona_guard["source_evidence"])

    divergent = _load_record("divergent-vs-convergent-thinking")
    superficial_guard = _absence_by_field(
        divergent,
        "superficial-divergence-volume-without-variety",
    )
    assert superficial_guard["runtime_policy"] == "do_not_promote"
    assert "volume and **variety**" in str(superficial_guard["source_evidence"])
    assert len(divergent["affordances"]) == 1


def test_pr85_adjacent_creative_synthesis_records_remain_compressed() -> None:
    affordances_v46 = _load_compiled(AFFORDANCES_V46_PATH)
    affordances_v47 = _load_compiled(AFFORDANCES_V47_PATH)

    v46_counts = _affordance_counts_by_model(affordances_v46)
    v47_counts = _affordance_counts_by_model(affordances_v47)

    for model_id in COMPRESSION_OK_MODEL_IDS:
        assert v47_counts[model_id] == v46_counts[model_id]


def test_pr85_v47_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v47", "model_affordances_v47")

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


def _affordance_by_id(
    record: dict[str, object],
    affordance_id: str,
) -> dict[str, object]:
    return next(
        affordance
        for affordance in record["affordances"]
        if affordance["affordance_id"] == affordance_id
    )


def _absence_by_field(record: dict[str, object], attempted_field: str) -> dict[str, object]:
    return next(
        absence
        for absence in record["absence_records"]
        if absence["attempted_field"] == attempted_field
    )
