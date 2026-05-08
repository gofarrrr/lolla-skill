from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V47_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v47.json"
)
AFFORDANCES_V48_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v48.json"
)

TARGET_RECORD_PATHS = {
    "cognitive-dissonance": MODEL_AFFORDANCE_DIR
    / "batch_14"
    / "cognitive-dissonance.json",
    "confirmation-bias": MODEL_AFFORDANCE_DIR
    / "batch_4"
    / "confirmation-bias.json",
    "dunning-kruger-effect": MODEL_AFFORDANCE_DIR
    / "batch_14"
    / "dunning-kruger-effect.json",
    "intellectual-humility": MODEL_AFFORDANCE_DIR
    / "batch_4"
    / "intellectual-humility.json",
    "peer-review-your-perspectives": MODEL_AFFORDANCE_DIR
    / "batch_5"
    / "peer-review-your-perspectives.json",
    "theory-induced-blindness": MODEL_AFFORDANCE_DIR
    / "batch_10"
    / "theory-induced-blindness.json",
}

NEW_AFFORDANCE_IDS = {
    "cognitive-dissonance.private-doubt-before-group-consensus",
    "confirmation-bias.first-falsifier-before-approval",
}

NEW_ABSENCE_FIELDS = {
    "abstract-framework-without-concrete-action",
    "excessive-humility-underweights-supported-evidence",
    "same-paradigm-review-as-peer-review",
    "skilled-low-confidence-as-incompetence",
}

COMPRESSION_OK_MODEL_IDS = {
    "anchoring",
    "bias-blind-spot",
    "cognitive-biases",
    "critical-thinking",
    "einstellung-effect",
    "false-precision-avoidance",
    "hindsight-bias",
    "intellectual-humility",
    "metacognitive-questioning",
    "peer-review-your-perspectives",
    "rationalization",
    "representativeness-heuristic",
    "theory-induced-blindness",
    "wysiati",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr86_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr86_compiled_v48_adds_bounded_reasoning_debiasing_enrichment() -> None:
    affordances_v47 = _load_compiled(AFFORDANCES_V47_PATH)
    affordances_v48 = _load_compiled(AFFORDANCES_V48_PATH)

    assert affordances_v48["artifact"] == "model_affordances_v48"
    assert affordances_v48["status"] == "draft_review_only"
    assert _model_ids(affordances_v48) == _model_ids(affordances_v47)
    assert len(_model_ids(affordances_v48)) == 222

    assert NEW_AFFORDANCE_IDS.isdisjoint(_affordance_ids(affordances_v47))
    assert _affordance_ids(affordances_v48) - _affordance_ids(affordances_v47) == (
        NEW_AFFORDANCE_IDS
    )
    assert NEW_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v47))
    assert _absence_fields(affordances_v48) - _absence_fields(affordances_v47) == (
        NEW_ABSENCE_FIELDS
    )

    v47_metadata = affordances_v47["compile_metadata"]
    v48_metadata = affordances_v48["compile_metadata"]
    assert v48_metadata["contributing_record_count"] == 222
    assert v48_metadata["affordance_count"] == v47_metadata["affordance_count"] + 2
    assert v48_metadata["affordance_count"] == 293
    assert (
        v48_metadata["absence_record_count"]
        == v47_metadata["absence_record_count"] + 4
    )
    assert v48_metadata["absence_record_count"] == 562
    assert v48_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v48_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr86_confirmation_bias_split_preserves_transaction_identity() -> None:
    confirmation_bias = _load_record("confirmation-bias")
    equal_weight = _affordance_by_id(
        confirmation_bias,
        "confirmation-bias.disconfirming-evidence-equality-check",
    )
    first_falsifier = _affordance_by_id(
        confirmation_bias,
        "confirmation-bias.first-falsifier-before-approval",
    )

    assert len(confirmation_bias["affordances"]) == 2
    assert "surface-disconfirming-case-with-equal-weight" in str(
        equal_weight["treatment_requirements"]
    )
    assert "name-first-falsifier-before-approval" not in str(
        equal_weight["treatment_requirements"]
    )
    assert "protect-first-falsifier-before-approval" in str(
        first_falsifier["treatment_requirements"]
    )
    assert "Once a senior sponsor signals the preferred answer" in str(
        first_falsifier["source_evidence"]
    )
    assert "missing-denominator card" in str(
        first_falsifier["misuse_guards"]
    )


def test_pr86_cognitive_dissonance_split_separates_group_pressure() -> None:
    cognitive_dissonance = _load_record("cognitive-dissonance")
    commitment_review = _affordance_by_id(
        cognitive_dissonance,
        "cognitive-dissonance.commitment-evidence-revision-check",
    )
    group_dissonance = _affordance_by_id(
        cognitive_dissonance,
        "cognitive-dissonance.private-doubt-before-group-consensus",
    )

    assert len(cognitive_dissonance["affordances"]) == 2
    assert "private dissent" in str(commitment_review["activation_shape"])
    assert "collect-anonymous-assessments-before-group-discussion" in str(
        group_dissonance["treatment_requirements"]
    )
    assert "private doubts and the public team consensus" in str(
        group_dissonance["source_evidence"]
    )
    assert "sunk-cost exit criteria" in str(group_dissonance["misuse_guards"])


def test_pr86_new_absence_rails_harden_without_positive_bloat() -> None:
    theory_blindness = _load_record("theory-induced-blindness")
    abstract_guard = _absence_by_field(
        theory_blindness,
        "abstract-framework-without-concrete-action",
    )
    assert abstract_guard["runtime_policy"] == "do_not_promote"
    assert "concrete images and human actions" in str(abstract_guard["source_evidence"])
    assert len(theory_blindness["affordances"]) == 1

    dunning_kruger = _load_record("dunning-kruger-effect")
    impostor_guard = _absence_by_field(
        dunning_kruger,
        "skilled-low-confidence-as-incompetence",
    )
    assert impostor_guard["status"] == "not_supported_by_source"
    assert "Impostor Syndrome" in str(impostor_guard["source_evidence"])
    assert len(dunning_kruger["affordances"]) == 1

    peer_review = _load_record("peer-review-your-perspectives")
    paradigm_guard = _absence_by_field(
        peer_review,
        "same-paradigm-review-as-peer-review",
    )
    assert paradigm_guard["runtime_policy"] == "do_not_promote"
    assert "same paradigm reinforce shared blind spots" in str(
        paradigm_guard["source_evidence"]
    )
    assert len(peer_review["affordances"]) == 1

    intellectual_humility = _load_record("intellectual-humility")
    humility_guard = _absence_by_field(
        intellectual_humility,
        "excessive-humility-underweights-supported-evidence",
    )
    assert humility_guard["status"] == "not_supported_by_source"
    assert "well-supported positions" in str(humility_guard["source_evidence"])
    assert len(intellectual_humility["affordances"]) == 1


def test_pr86_adjacent_reasoning_debiasing_records_remain_compressed() -> None:
    affordances_v47 = _load_compiled(AFFORDANCES_V47_PATH)
    affordances_v48 = _load_compiled(AFFORDANCES_V48_PATH)

    v47_counts = _affordance_counts_by_model(affordances_v47)
    v48_counts = _affordance_counts_by_model(affordances_v48)

    for model_id in COMPRESSION_OK_MODEL_IDS:
        assert v48_counts[model_id] == v47_counts[model_id]


def test_pr86_v48_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v48", "model_affordances_v48")

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
