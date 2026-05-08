from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V41_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v41.json"
)
AFFORDANCES_V42_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v42.json"
)

TARGET_RECORD_PATHS = {
    "constructive-feedback-models": MODEL_AFFORDANCE_DIR
    / "batch_6"
    / "constructive-feedback-models.json",
    "cross-cultural-communication-frameworks": MODEL_AFFORDANCE_DIR
    / "batch_5"
    / "cross-cultural-communication-frameworks.json",
    "cultural-dimensions-theory": MODEL_AFFORDANCE_DIR
    / "batch_15"
    / "cultural-dimensions-theory.json",
    "cultural-intelligence": MODEL_AFFORDANCE_DIR
    / "batch_15"
    / "cultural-intelligence.json",
    "feedback-models-sbi": MODEL_AFFORDANCE_DIR
    / "batch_6"
    / "feedback-models-sbi.json",
    "liking-principle": MODEL_AFFORDANCE_DIR
    / "batch_15"
    / "liking-principle.json",
    "narratives": MODEL_AFFORDANCE_DIR / "batch_15" / "narratives.json",
    "pre-suasion": MODEL_AFFORDANCE_DIR / "batch_15" / "pre-suasion.json",
    "reciprocity-principle": MODEL_AFFORDANCE_DIR
    / "batch_7"
    / "reciprocity-principle.json",
    "social-proof": MODEL_AFFORDANCE_DIR / "batch_2" / "social-proof.json",
    "understanding-motivations": MODEL_AFFORDANCE_DIR
    / "batch_7"
    / "understanding-motivations.json",
}

NEW_AFFORDANCE_IDS = {
    "cross-cultural-communication-frameworks.align-conversation-layer-before-message",
}

NEW_ABSENCE_FIELDS = {
    "amp-or-reward-architecture-as-hidden-driver-split",
    "charisma-or-familiarity-without-broad-competence",
    "named-cultural-dimension-taxonomy-without-source-or-case-evidence",
    "outcome-only-sbi-feedback",
    "widespread-or-expired-norm-as-proof",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr80_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr80_compiled_v42_adds_bounded_communication_enrichment() -> None:
    affordances_v41 = _load_compiled(AFFORDANCES_V41_PATH)
    affordances_v42 = _load_compiled(AFFORDANCES_V42_PATH)

    assert affordances_v42["artifact"] == "model_affordances_v42"
    assert affordances_v42["status"] == "draft_review_only"
    assert _model_ids(affordances_v42) == _model_ids(affordances_v41)
    assert len(_model_ids(affordances_v42)) == 222

    assert NEW_AFFORDANCE_IDS.isdisjoint(_affordance_ids(affordances_v41))
    assert _affordance_ids(affordances_v42) - _affordance_ids(affordances_v41) == (
        NEW_AFFORDANCE_IDS
    )
    assert NEW_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v41))
    assert _absence_fields(affordances_v42) - _absence_fields(affordances_v41) == (
        NEW_ABSENCE_FIELDS
    )

    v41_metadata = affordances_v41["compile_metadata"]
    v42_metadata = affordances_v42["compile_metadata"]
    assert v42_metadata["contributing_record_count"] == 222
    assert v42_metadata["affordance_count"] == v41_metadata["affordance_count"] + 1
    assert v42_metadata["affordance_count"] == 277
    assert (
        v42_metadata["absence_record_count"]
        == v41_metadata["absence_record_count"] + 5
    )
    assert v42_metadata["absence_record_count"] == 520
    assert v42_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v42_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr80_cross_cultural_split_preserves_layer_identity() -> None:
    record = _load_record("cross-cultural-communication-frameworks")
    affordance = _affordance_by_id(
        record,
        "cross-cultural-communication-frameworks.align-conversation-layer-before-message",
    )

    assert "practical, emotional, or social" in str(affordance["mechanism"])
    assert "name-layer-and-preserve-goal" in str(affordance["treatment_requirements"])
    assert "frame-translation action check instead" in str(
        affordance["activation_shape"]
    )
    assert "three different conversations" in str(affordance["source_evidence"])
    assert "same kind of conversation" in str(affordance["source_evidence"])


def test_pr80_persuasion_influence_records_harden_without_splits() -> None:
    pre_suasion = _load_record("pre-suasion")
    reciprocity = _load_record("reciprocity-principle")
    social_proof = _load_record("social-proof")
    liking = _load_record("liking-principle")

    pre_suasion_affordance = _affordance_by_id(
        pre_suasion,
        "pre-suasion.set-context-with-merit-and-consent-check",
    )
    assert "correct-irrelevant-incidental-prime" in str(
        pre_suasion_affordance["treatment_requirements"]
    )
    assert "rational link correction" in str(pre_suasion_affordance["source_evidence"])

    reciprocity_affordance = _affordance_by_id(
        reciprocity,
        "reciprocity-principle.costly-value-trust-test",
    )
    assert "verify-promises-before-goodwill" in str(
        reciprocity_affordance["treatment_requirements"]
    )
    assert "past goodwill" in str(reciprocity_affordance["misuse_guards"])

    social_guard = _absence_by_field(
        social_proof,
        "widespread-or-expired-norm-as-proof",
    )
    assert social_guard["runtime_policy"] == "do_not_promote"
    assert "long passed their expiration date" in str(social_guard["source_evidence"])
    assert "routinely upgraded" in str(social_guard["source_evidence"])

    liking_affordance = _affordance_by_id(
        liking,
        "liking-principle.build-receptivity-with-substance-check",
    )
    liking_guard = _absence_by_field(
        liking,
        "charisma-or-familiarity-without-broad-competence",
    )
    assert "ground-warmth-in-audience-language-and-problem" in str(
        liking_affordance["treatment_requirements"]
    )
    assert "exact phrases, terminology, and vernacular" in str(
        liking_affordance["source_evidence"]
    )
    assert liking_guard["runtime_policy"] == "do_not_promote"
    assert "lack of broad competence" in str(liking_guard["source_evidence"])


def test_pr80_feedback_and_motivation_records_harden_without_splits() -> None:
    constructive = _load_record("constructive-feedback-models")
    sbi = _load_record("feedback-models-sbi")
    motivations = _load_record("understanding-motivations")

    constructive_affordance = _affordance_by_id(
        constructive,
        "constructive-feedback-models.specific-standard-correction",
    )
    assert "funnel-feedback-to-actionable-signal" in str(
        constructive_affordance["treatment_requirements"]
    )
    assert "Providing excessive charts" in str(
        constructive_affordance["source_evidence"]
    )

    sbi_affordance = _affordance_by_id(
        sbi,
        "feedback-models-sbi.situation-impact-invitation-structure",
    )
    sbi_guard = _absence_by_field(sbi, "outcome-only-sbi-feedback")
    assert "avoid-deficiency-only-demoralization" in str(
        sbi_affordance["treatment_requirements"]
    )
    assert "deficiencies" in str(sbi_affordance["source_evidence"])
    assert sbi_guard["runtime_policy"] == "do_not_promote"
    assert "decision process *ex ante*" in str(sbi_guard["source_evidence"])

    motivation_affordance = _affordance_by_id(
        motivations,
        "understanding-motivations.hidden-driver-hypothesis-test",
    )
    motivation_guard = _absence_by_field(
        motivations,
        "amp-or-reward-architecture-as-hidden-driver-split",
    )
    assert "test-implementation-path-after-driver" in str(
        motivation_affordance["treatment_requirements"]
    )
    assert "Implementation in a living social system" in str(
        motivation_affordance["source_evidence"]
    )
    assert motivation_guard["runtime_policy"] == "do_not_promote"
    assert "Motivation 2.0" in str(motivation_guard["source_evidence"])


def test_pr80_narrative_and_cultural_records_harden_without_bloat() -> None:
    narratives = _load_record("narratives")
    dimensions = _load_record("cultural-dimensions-theory")
    intelligence = _load_record("cultural-intelligence")

    narrative_affordance = _affordance_by_id(
        narratives,
        "narratives.make-causal-meaning-actionable",
    )
    assert "test-competing-story-frames" in str(
        narrative_affordance["treatment_requirements"]
    )
    assert "different frames yield different insights" in str(
        narrative_affordance["source_evidence"]
    )

    dimension_guard = _absence_by_field(
        dimensions,
        "named-cultural-dimension-taxonomy-without-source-or-case-evidence",
    )
    assert dimension_guard["runtime_policy"] == "do_not_promote"
    assert "Hofstede's or Trompenaars'" in str(dimension_guard["source_evidence"])
    assert "map is not the territory" in str(dimension_guard["source_evidence"])

    intelligence_affordance = _affordance_by_id(
        intelligence,
        "cultural-intelligence.translate-human-worlds-before-adoption",
    )
    assert "treat-personal-data-as-behavioral-evidence" in str(
        intelligence_affordance["treatment_requirements"]
    )
    assert "objective facts *and* **personal data**" in str(
        intelligence_affordance["source_evidence"]
    )
    assert "Ignoring these feelings throws away crucial data" in str(
        intelligence_affordance["source_evidence"]
    )


def test_pr80_v42_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v42", "model_affordances_v42")

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


def _absence_by_field(
    record: dict[str, object],
    attempted_field: str,
) -> dict[str, object]:
    return next(
        absence
        for absence in record["absence_records"]
        if absence["attempted_field"] == attempted_field
    )
