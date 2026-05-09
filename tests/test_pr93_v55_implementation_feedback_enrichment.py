from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V54_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v54.json"
)
AFFORDANCES_V55_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v55.json"
)

TARGET_RECORD_PATHS = {
    "agile-methodologies": MODEL_AFFORDANCE_DIR
    / "batch_17"
    / "agile-methodologies.json",
    "debugging-strategies": MODEL_AFFORDANCE_DIR
    / "batch_8"
    / "debugging-strategies.json",
    "devops-and-continuous-integration": MODEL_AFFORDANCE_DIR
    / "batch_8"
    / "devops-and-continuous-integration.json",
    "feedback-loops": MODEL_AFFORDANCE_DIR / "batch_8" / "feedback-loops.json",
    "iteration": MODEL_AFFORDANCE_DIR / "batch_8" / "iteration.json",
    "lean-startup-methodology": MODEL_AFFORDANCE_DIR
    / "batch_8"
    / "lean-startup-methodology.json",
}

NEW_AFFORDANCE_IDS = {
    "feedback-loops.absolute-standard-drift-guard",
    "lean-startup-methodology.subhypothesis-experiment-coverage-map",
}

NEW_ABSENCE_FIELDS = {
    "analysis-paralysis-as-debugging-rigor",
    "ceremonial-review-loop-as-iteration",
    "deductive-debugging-for-novel-creation",
    "feedback-volume-as-feedback-quality",
    "fixed-dependency-denial-as-agility",
    "framework-reuse-as-lean-validation",
    "implementation-practice-checklist-as-source-supported-devops-ci",
    "internal-capacity-blind-lean-recommendation",
    "iteration-without-current-synthesis",
    "local-signal-as-whole-system-truth",
    "mandated-conclusion-as-hypothesis-driven-sprint",
    "one-way-communication-as-feedback-loop",
    "premature-data-dive-as-iteration",
    "qualitative-empathy-as-demand-proof",
    "rigid-blueprint-as-iteration",
    "single-frame-debugging-as-complete-diagnosis",
    "solution-before-diagnosis",
    "sprint-local-velocity-as-system-performance",
    "sunk-cost-path-continuation-as-iteration",
    "symptom-pivot-as-product-learning",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr93_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr93_compiled_v55_preserves_runtime_model_coverage() -> None:
    affordances_v54 = _load_compiled(AFFORDANCES_V54_PATH)
    affordances_v55 = _load_compiled(AFFORDANCES_V55_PATH)

    assert affordances_v55["artifact"] == "model_affordances_v55"
    assert affordances_v55["status"] == "draft_review_only"
    assert _model_ids(affordances_v55) == _model_ids(affordances_v54)
    assert len(_model_ids(affordances_v55)) == 222

    assert NEW_AFFORDANCE_IDS.isdisjoint(_affordance_ids(affordances_v54))
    assert _affordance_ids(affordances_v55) - _affordance_ids(affordances_v54) == (
        NEW_AFFORDANCE_IDS
    )
    assert NEW_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v54))
    assert _absence_fields(affordances_v55) - _absence_fields(affordances_v54) == (
        NEW_ABSENCE_FIELDS
    )

    v54_metadata = affordances_v54["compile_metadata"]
    v55_metadata = affordances_v55["compile_metadata"]
    assert v55_metadata["contributing_record_count"] == 222
    assert (
        v55_metadata["affordance_count"]
        == v54_metadata["affordance_count"] + len(NEW_AFFORDANCE_IDS)
    )
    assert v55_metadata["affordance_count"] == 300
    assert (
        v55_metadata["absence_record_count"]
        == v54_metadata["absence_record_count"] + len(NEW_ABSENCE_FIELDS)
    )
    assert v55_metadata["absence_record_count"] == 614
    assert v55_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v55_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr93_positive_splits_are_limited_to_distinct_transactions() -> None:
    feedback = _load_record("feedback-loops")
    feedback_split = _affordance_by_id(
        feedback,
        "feedback-loops.absolute-standard-drift-guard",
    )
    assert "slow acceptance of diminishing quality" in str(
        feedback_split["source_evidence"]
    )
    assert "lowering the bar" in str(feedback_split["diagnostic_questions"])
    assert len(feedback["affordances"]) == 3

    lean = _load_record("lean-startup-methodology")
    lean_split = _affordance_by_id(
        lean,
        "lean-startup-methodology.subhypothesis-experiment-coverage-map",
    )
    assert "sub-hypotheses" in str(lean_split["source_evidence"])
    assert "one positive metric" in str(lean_split["misuse_guards"])
    assert len(lean["affordances"]) == 2


def test_pr93_rejected_split_candidates_remain_compressed_as_absence_rails() -> None:
    iteration = _load_record("iteration")
    assert len(iteration["affordances"]) == 1
    assert "one-day-answer" in iteration["review_notes"]["normalization_note"]
    assert _absence_by_field(
        iteration,
        "iteration-without-current-synthesis",
    )["runtime_policy"] == "do_not_promote"
    assert "wading prematurely into data" in str(
        _absence_by_field(iteration, "premature-data-dive-as-iteration")[
            "source_evidence"
        ]
    )

    agile = _load_record("agile-methodologies")
    assert len(agile["affordances"]) == 1
    assert "adjacent-owner candidates" in agile["review_notes"]["normalization_note"]
    assert "end-to-end system performance" in str(
        _absence_by_field(agile, "sprint-local-velocity-as-system-performance")[
            "source_evidence"
        ]
    )
    assert _absence_by_field(
        agile,
        "mandated-conclusion-as-hypothesis-driven-sprint",
    )["runtime_policy"] == "do_not_promote"

    devops = _load_record("devops-and-continuous-integration")
    assert devops["status"] == "weak_support"
    assert len(devops["affordances"]) == 1
    assert devops["affordances"][0]["status"] == "weak_support"
    assert devops["affordances"][0]["confidence"] == "medium"
    assert "not explicitly defined" in str(
        _absence_by_field(
            devops,
            "implementation-practice-checklist-as-source-supported-devops-ci",
        )["source_evidence"]
    )

    debugging = _load_record("debugging-strategies")
    assert len(debugging["affordances"]) == 1
    assert "better owned by adjacent records" in debugging["review_notes"][
        "normalization_note"
    ]
    assert "abductive reasoning" in str(
        _absence_by_field(debugging, "deductive-debugging-for-novel-creation")[
            "source_evidence"
        ]
    )
    assert "analysis paralysis" in str(
        _absence_by_field(debugging, "analysis-paralysis-as-debugging-rigor")[
            "source_evidence"
        ]
    )


def test_pr93_v55_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v55", "model_affordances_v55")

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
