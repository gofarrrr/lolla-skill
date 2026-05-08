from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V43_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v43.json"
)
AFFORDANCES_V44_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v44.json"
)

TARGET_RECORD_PATHS = {
    "blooms-taxonomy": MODEL_AFFORDANCE_DIR / "batch_12" / "blooms-taxonomy.json",
    "cognitive-load-theory": MODEL_AFFORDANCE_DIR
    / "batch_12"
    / "cognitive-load-theory.json",
    "curse-of-knowledge": MODEL_AFFORDANCE_DIR
    / "batch_14"
    / "curse-of-knowledge.json",
    "deliberate-practice": MODEL_AFFORDANCE_DIR
    / "batch_12"
    / "deliberate-practice.json",
    "desirable-difficulties": MODEL_AFFORDANCE_DIR
    / "batch_12"
    / "desirable-difficulties.json",
    "dunning-kruger-effect": MODEL_AFFORDANCE_DIR
    / "batch_14"
    / "dunning-kruger-effect.json",
    "expertise-reversal-effect": MODEL_AFFORDANCE_DIR
    / "batch_12"
    / "expertise-reversal-effect.json",
    "feynman-technique": MODEL_AFFORDANCE_DIR
    / "batch_12"
    / "feynman-technique.json",
    "generation-effect": MODEL_AFFORDANCE_DIR
    / "batch_12"
    / "generation-effect.json",
    "learning-curve": MODEL_AFFORDANCE_DIR / "batch_12" / "learning-curve.json",
    "perceptual-learning": MODEL_AFFORDANCE_DIR
    / "batch_17"
    / "perceptual-learning.json",
    "scaffolding-educational": MODEL_AFFORDANCE_DIR
    / "batch_17"
    / "scaffolding-educational.json",
    "schema-acquisition": MODEL_AFFORDANCE_DIR
    / "batch_12"
    / "schema-acquisition.json",
    "zone-of-development": MODEL_AFFORDANCE_DIR
    / "batch_12"
    / "zone-of-development.json",
}

NEW_AFFORDANCE_IDS = {
    "curse-of-knowledge.observed-novice-validation-before-clarity-trust",
    "expertise-reversal-effect.extract-tacit-expert-cognition-with-stories",
    "learning-curve.progressive-scaffold-and-handoff",
    "perceptual-learning.tacit-cue-extraction-before-training",
}

NEW_ABSENCE_FIELDS = {
    "audience-deciphering-as-rigor",
    "dke-as-intuition-suppression",
    "early-progress-as-scalable-mastery",
    "expert-schema-as-correct-by-default",
    "low-load-fluency-as-mastery",
    "lower-level-overwork-as-progress",
    "one-shot-stretch-calibration-without-feedback",
    "practice-entrenches-flawed-model",
    "scaffolded-fluency-as-independent-mastery",
    "schema-as-execution-mastery",
    "self-generated-model-defense",
    "simplified-explanation-without-uncomfortable-evidence",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr82_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr82_compiled_v44_adds_bounded_learning_mastery_enrichment() -> None:
    affordances_v43 = _load_compiled(AFFORDANCES_V43_PATH)
    affordances_v44 = _load_compiled(AFFORDANCES_V44_PATH)

    assert affordances_v44["artifact"] == "model_affordances_v44"
    assert affordances_v44["status"] == "draft_review_only"
    assert _model_ids(affordances_v44) == _model_ids(affordances_v43)
    assert len(_model_ids(affordances_v44)) == 222

    assert NEW_AFFORDANCE_IDS.isdisjoint(_affordance_ids(affordances_v43))
    assert _affordance_ids(affordances_v44) - _affordance_ids(affordances_v43) == (
        NEW_AFFORDANCE_IDS
    )
    assert NEW_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v43))
    assert _absence_fields(affordances_v44) - _absence_fields(affordances_v43) == (
        NEW_ABSENCE_FIELDS
    )

    v43_metadata = affordances_v43["compile_metadata"]
    v44_metadata = affordances_v44["compile_metadata"]
    assert v44_metadata["contributing_record_count"] == 222
    assert v44_metadata["affordance_count"] == v43_metadata["affordance_count"] + 4
    assert v44_metadata["affordance_count"] == 282
    assert (
        v44_metadata["absence_record_count"]
        == v43_metadata["absence_record_count"] + 12
    )
    assert v44_metadata["absence_record_count"] == 548
    assert v44_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v44_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr82_split_affordances_preserve_transaction_identity() -> None:
    curse = _load_record("curse-of-knowledge")
    expertise = _load_record("expertise-reversal-effect")
    learning_curve = _load_record("learning-curve")
    perceptual = _load_record("perceptual-learning")

    curse_old = _affordance_by_id(
        curse,
        "curse-of-knowledge.audience-starting-state-reconstruction",
    )
    curse_split = _affordance_by_id(
        curse,
        "curse-of-knowledge.observed-novice-validation-before-clarity-trust",
    )
    perceptual_old = _affordance_by_id(
        perceptual,
        "perceptual-learning.train-cue-discrimination",
    )
    perceptual_split = _affordance_by_id(
        perceptual,
        "perceptual-learning.tacit-cue-extraction-before-training",
    )

    assert "verify-with-novice-demonstration" not in str(curse_old)
    assert "verify-clarity-with-recipient-demonstration" in str(curse_split)
    assert "Observe, don't ask" in str(curse_split["source_evidence"])
    assert "extract-tacit-cues-with-stories-and-pari" not in str(perceptual_old)
    assert "elicit-stories-and-pari-before-cue-training" in str(perceptual_split)
    assert "Experts often struggle to articulate their tacit knowledge" in str(
        perceptual_split["source_evidence"]
    )

    assert "stage-demonstration-practice-correction-and-handoff" in str(
        _affordance_by_id(
            learning_curve,
            "learning-curve.progressive-scaffold-and-handoff",
        )
    )
    assert "convert-expert-stories-into-cue-patterns" in str(
        _affordance_by_id(
            expertise,
            "expertise-reversal-effect.extract-tacit-expert-cognition-with-stories",
        )
    )


def test_pr82_absence_rails_block_false_learning_mastery_promotions() -> None:
    assert "rigorous practice merely entrenches the error" in str(
        _absence_by_field(
            _load_record("deliberate-practice"),
            "practice-entrenches-flawed-model",
        )
    )
    assert "not by the audience in deciphering it" in str(
        _absence_by_field(
            _load_record("desirable-difficulties"),
            "audience-deciphering-as-rigor",
        )
    )
    assert "defend the hypothesis aggressively" in str(
        _absence_by_field(
            _load_record("generation-effect"),
            "self-generated-model-defense",
        )
    )
    assert "mastery of the underlying content" in str(
        _absence_by_field(
            _load_record("cognitive-load-theory"),
            "low-load-fluency-as-mastery",
        )
    )
    assert "knowing *what* to do" in str(
        _absence_by_field(
            _load_record("schema-acquisition"),
            "schema-as-execution-mastery",
        )
    )
    assert "modify the structure or difficulty of the next developmental step" in str(
        _absence_by_field(
            _load_record("zone-of-development"),
            "one-shot-stretch-calibration-without-feedback",
        )
    )


def test_pr82_absence_rails_block_false_authority_and_fluency() -> None:
    assert "scales responsibility faster than capability has actually consolidated" in str(
        _absence_by_field(
            _load_record("learning-curve"),
            "early-progress-as-scalable-mastery",
        )
    )
    assert "erroneous embedded beliefs" in str(
        _absence_by_field(
            _load_record("expertise-reversal-effect"),
            "expert-schema-as-correct-by-default",
        )
    )
    assert "decisive judgment" in str(
        _absence_by_field(
            _load_record("blooms-taxonomy"),
            "lower-level-overwork-as-progress",
        )
    )
    assert "most uncomfortable" in str(
        _absence_by_field(
            _load_record("feynman-technique"),
            "simplified-explanation-without-uncomfortable-evidence",
        )
    )
    assert "dismiss all intuitive thinking" in str(
        _absence_by_field(
            _load_record("dunning-kruger-effect"),
            "dke-as-intuition-suppression",
        )
    )
    assert "due to the scaffold" in str(
        _absence_by_field(
            _load_record("scaffolding-educational"),
            "scaffolded-fluency-as-independent-mastery",
        )
    )


def test_pr82_v44_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v44", "model_affordances_v44")

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
    for affordance in record["affordances"]:
        if affordance["affordance_id"] == affordance_id:
            return affordance
    raise AssertionError(f"Missing affordance_id: {affordance_id}")


def _absence_by_field(
    record: dict[str, object],
    attempted_field: str,
) -> dict[str, object]:
    for absence in record["absence_records"]:
        if absence["attempted_field"] == attempted_field:
            return absence
    raise AssertionError(f"Missing absence attempted_field: {attempted_field}")
