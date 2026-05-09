from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V57_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v57.json"
)
AFFORDANCES_V58_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v58.json"
)

TARGET_RECORD_PATHS = {
    "active-listening": MODEL_AFFORDANCE_DIR / "batch_6" / "active-listening.json",
    "non-violent-communication": MODEL_AFFORDANCE_DIR
    / "batch_7"
    / "non-violent-communication.json",
    "persuasion-principles": MODEL_AFFORDANCE_DIR
    / "batch_7"
    / "persuasion-principles.json",
    "understanding-motivations": MODEL_AFFORDANCE_DIR
    / "batch_7"
    / "understanding-motivations.json",
    "pre-suasion": MODEL_AFFORDANCE_DIR / "batch_15" / "pre-suasion.json",
    "storytelling-frameworks": MODEL_AFFORDANCE_DIR
    / "batch_15"
    / "storytelling-frameworks.json",
}

NEW_AFFORDANCE_IDS = {
    "active-listening.tacit-process-capture-before-abstraction",
    "understanding-motivations.motive-to-implementation-path-check",
}

NEW_ABSENCE_FIELDS = {
    "ai-backstory-as-behavior-guarantee",
    "ai-persona-psychological-fingerprint-as-motive-evidence",
    "authority-evidence-as-merits-substitute",
    "buyer-avatar-language-as-motivation-proof",
    "clarity-as-weapon-without-relational-fit",
    "context-setting-as-confirmation-bias",
    "dialectic-assumption-testing-as-nvc-split",
    "education-based-persuasion-as-obligation-pressure",
    "emotional-sale-without-rational-proof",
    "empathetic-validation-as-active-listening-split",
    "feedback-add-structure-as-nvc-split",
    "high-concept-analogy-as-persuasion-proof",
    "hot-cognition-packaging-as-motivation-split",
    "irrelevant-prime-used-as-leverage",
    "leader-story-as-credibility-proof",
    "long-listening-without-decision-change",
    "motivation-diagnosis-without-falsifier",
    "named-influence-principles-as-single-persuasion-split",
    "named-story-framework-as-standalone-card",
    "radical-transparency-as-nvc-split",
    "story-coherence-as-causal-proof",
    "story-data-story-without-evidence-boundary",
    "tacit-process-capture-without-concrete-episode",
    "trust-theater-before-ask",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr96_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr96_compiled_v58_preserves_coverage_with_bounded_delta() -> None:
    affordances_v57 = _load_compiled(AFFORDANCES_V57_PATH)
    affordances_v58 = _load_compiled(AFFORDANCES_V58_PATH)

    assert affordances_v58["artifact"] == "model_affordances_v58"
    assert affordances_v58["status"] == "draft_review_only"
    assert _model_ids(affordances_v58) == _model_ids(affordances_v57)
    assert len(_model_ids(affordances_v58)) == 222

    assert NEW_AFFORDANCE_IDS.isdisjoint(_affordance_ids(affordances_v57))
    assert _affordance_ids(affordances_v58) - _affordance_ids(affordances_v57) == (
        NEW_AFFORDANCE_IDS
    )
    assert NEW_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v57))
    assert _absence_fields(affordances_v58) - _absence_fields(affordances_v57) == (
        NEW_ABSENCE_FIELDS
    )

    v57_metadata = affordances_v57["compile_metadata"]
    v58_metadata = affordances_v58["compile_metadata"]
    assert v58_metadata["contributing_record_count"] == 222
    assert (
        v58_metadata["affordance_count"]
        == v57_metadata["affordance_count"] + len(NEW_AFFORDANCE_IDS)
    )
    assert v58_metadata["affordance_count"] == 305
    assert (
        v58_metadata["absence_record_count"]
        == v57_metadata["absence_record_count"] + len(NEW_ABSENCE_FIELDS)
    )
    assert v58_metadata["absence_record_count"] == 664
    assert v58_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v58_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr96_positive_splits_preserve_transaction_identity() -> None:
    active = _load_record("active-listening")
    active_parent = _affordance_by_id(
        active,
        "active-listening.hidden-disagreement-diagnostic-loop",
    )
    process_split = _affordance_by_id(
        active,
        "active-listening.tacit-process-capture-before-abstraction",
    )
    assert len(active["affordances"]) == 2
    assert "thought chain" in str(process_split["source_evidence"])
    assert "expert" in str(process_split["activation_shape"])
    assert "generic best-practice advice" in str(process_split["misuse_guards"])
    assert "capture-process-before-abstracting-advice" in _requirement_ids(
        process_split
    )
    assert "capture-process-before-abstracting-advice" not in _requirement_ids(
        active_parent
    )

    motivations = _load_record("understanding-motivations")
    motivations_parent = _affordance_by_id(
        motivations,
        "understanding-motivations.hidden-driver-hypothesis-test",
    )
    implementation_split = _affordance_by_id(
        motivations,
        "understanding-motivations.motive-to-implementation-path-check",
    )
    assert len(motivations["affordances"]) == 2
    assert "implementation falters despite a clear strategy" in str(
        implementation_split["source_evidence"]
    )
    assert "living social system" in str(implementation_split["source_evidence"])
    assert "rational switch" in str(implementation_split["misuse_guards"])
    assert "test-implementation-path-after-driver" in _requirement_ids(
        implementation_split
    )
    assert "test-implementation-path-after-driver" not in _requirement_ids(
        motivations_parent
    )


def test_pr96_rejected_communication_and_adoption_splits_are_absence_rails() -> None:
    nvc = _load_record("non-violent-communication")
    feedback_guard = _absence_by_field(nvc, "feedback-add-structure-as-nvc-split")
    assert len(nvc["affordances"]) == 1
    assert feedback_guard["status"] == "duplicate_of_existing_field"
    assert "feedback-models-sbi" in feedback_guard["reason"]
    assert _absence_by_field(
        nvc,
        "clarity-as-weapon-without-relational-fit",
    )["status"] == "not_supported_by_source"
    assert "dialectic" in _absence_by_field(
        nvc,
        "dialectic-assumption-testing-as-nvc-split",
    )["reason"]

    persuasion = _load_record("persuasion-principles")
    named_guard = _absence_by_field(
        persuasion,
        "named-influence-principles-as-single-persuasion-split",
    )
    assert len(persuasion["affordances"]) == 1
    assert named_guard["runtime_policy"] == "do_not_promote"
    assert "reciprocity, liking, authority, social proof" in str(
        named_guard["source_evidence"]
    )
    assert "merit evaluation" in _absence_by_field(
        persuasion,
        "authority-evidence-as-merits-substitute",
    )["reason"]
    assert "catchy analogy" in _absence_by_field(
        persuasion,
        "high-concept-analogy-as-persuasion-proof",
    )["reason"]

    pre_suasion = _load_record("pre-suasion")
    assert len(pre_suasion["affordances"]) == 1
    assert "rational and technical proof" in str(
        _absence_by_field(pre_suasion, "emotional-sale-without-rational-proof")[
            "source_evidence"
        ]
    )
    assert "irrelevant" in str(
        _absence_by_field(pre_suasion, "irrelevant-prime-used-as-leverage")[
            "source_evidence"
        ]
    )
    assert "motivated reasoning" in str(
        _absence_by_field(pre_suasion, "context-setting-as-confirmation-bias")[
            "source_evidence"
        ]
    )

    storytelling = _load_record("storytelling-frameworks")
    assert len(storytelling["affordances"]) == 1
    assert "Normal \u2192 Explosion \u2192 New Normal" in str(
        _absence_by_field(storytelling, "named-story-framework-as-standalone-card")[
            "source_evidence"
        ]
    )
    assert "**backstory** is a carefully crafted narrative" in str(
        _absence_by_field(storytelling, "ai-backstory-as-behavior-guarantee")[
            "source_evidence"
        ]
    )
    assert "causal proof" in _absence_by_field(
        storytelling,
        "story-coherence-as-causal-proof",
    )["reason"]


def test_pr96_v58_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v58", "model_affordances_v58")

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


def _absence_by_field(record: dict[str, object], attempted_field: str) -> dict[str, object]:
    return next(
        absence
        for absence in record["absence_records"]
        if absence["attempted_field"] == attempted_field
    )


def _requirement_ids(affordance: dict[str, object]) -> set[str]:
    return {
        requirement["requirement_id"]
        for requirement in affordance["treatment_requirements"]
    }
