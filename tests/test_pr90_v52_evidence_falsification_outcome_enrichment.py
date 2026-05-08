from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V51_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v51.json"
)
AFFORDANCES_V52_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v52.json"
)

TARGET_RECORD_PATHS = {
    "counterfactual-reasoning": MODEL_AFFORDANCE_DIR
    / "batch_10"
    / "counterfactual-reasoning.json",
    "falsifiability": MODEL_AFFORDANCE_DIR / "batch_3a" / "falsifiability.json",
    "logical-fallacies": MODEL_AFFORDANCE_DIR
    / "batch_17"
    / "logical-fallacies.json",
    "premortem": MODEL_AFFORDANCE_DIR / "pilot" / "premortem.json",
    "scientific-method-evidence-testing": MODEL_AFFORDANCE_DIR
    / "batch_4"
    / "scientific-method-evidence-testing.json",
    "step-back": MODEL_AFFORDANCE_DIR / "batch_4" / "step-back.json",
    "true-uncertainty-navigation": MODEL_AFFORDANCE_DIR
    / "batch_3a"
    / "true-uncertainty-navigation.json",
}

NEW_AFFORDANCE_IDS = {
    "counterfactual-reasoning.outcome-quality-retrospective",
    "true-uncertainty-navigation.outcome-decoupled-decision-quality",
}

NEW_ABSENCE_FIELDS = {
    "bad-outcome-excuse-only-counterfactuals",
    "logical-validity-as-implementation-plan",
    "outcome-quality-as-decision-quality-proof",
    "premature-data-analysis-as-evidence-testing",
    "pro-con-list-as-premortem-substitute",
    "runtime-simulation-or-ai-persona-behavior",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr90_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr90_compiled_v52_adds_bounded_outcome_quality_delta() -> None:
    affordances_v51 = _load_compiled(AFFORDANCES_V51_PATH)
    affordances_v52 = _load_compiled(AFFORDANCES_V52_PATH)

    assert affordances_v52["artifact"] == "model_affordances_v52"
    assert affordances_v52["status"] == "draft_review_only"
    assert _model_ids(affordances_v52) == _model_ids(affordances_v51)
    assert len(_model_ids(affordances_v52)) == 222

    assert NEW_AFFORDANCE_IDS.isdisjoint(_affordance_ids(affordances_v51))
    assert _affordance_ids(affordances_v52) - _affordance_ids(affordances_v51) == (
        NEW_AFFORDANCE_IDS
    )
    assert NEW_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v51))
    assert _absence_fields(affordances_v52) - _absence_fields(affordances_v51) == (
        NEW_ABSENCE_FIELDS
    )

    v51_metadata = affordances_v51["compile_metadata"]
    v52_metadata = affordances_v52["compile_metadata"]
    assert v52_metadata["contributing_record_count"] == 222
    assert v52_metadata["affordance_count"] == v51_metadata["affordance_count"] + 2
    assert v52_metadata["affordance_count"] == 298
    assert (
        v52_metadata["absence_record_count"]
        == v51_metadata["absence_record_count"] + 6
    )
    assert v52_metadata["absence_record_count"] == 578
    assert v52_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v52_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr90_counterfactual_split_separates_precommitment_and_retrospective() -> None:
    counterfactual = _load_record("counterfactual-reasoning")
    branch_card = _affordance_by_id(
        counterfactual,
        "counterfactual-reasoning.plausible-alternative-branch-test",
    )
    retrospective_card = _affordance_by_id(
        counterfactual,
        "counterfactual-reasoning.outcome-quality-retrospective",
    )
    excuse_guard = _absence_by_field(
        counterfactual,
        "bad-outcome-excuse-only-counterfactuals",
    )

    assert len(counterfactual["affordances"]) == 2
    assert "recover-plausible-branches" in str(branch_card["treatment_requirements"])
    assert "Best when leaders need to expose omitted scenarios before locking in a plan" in str(
        branch_card["source_evidence"]
    )
    assert "reconstruct-ex-ante-decision-tree" not in str(
        branch_card["treatment_requirements"]
    )

    assert "reconstruct-ex-ante-decision-tree" in str(
        retrospective_card["treatment_requirements"]
    )
    assert "placing the actual outcome in the proper context" in str(
        retrospective_card["source_evidence"]
    )
    assert "separate \"what happened\" from \"what could reasonably have happened\"" in str(
        retrospective_card["source_evidence"]
    )
    assert "Do not use counterfactuals only to excuse failures." in str(
        retrospective_card["misuse_guards"]
    )

    assert excuse_guard["runtime_policy"] == "do_not_promote"
    assert "more eager to put bad outcomes in context than good ones" in str(
        excuse_guard["source_evidence"]
    )


def test_pr90_true_uncertainty_split_stays_distinct_from_counterfactual() -> None:
    true_uncertainty = _load_record("true-uncertainty-navigation")
    scenario_card = _affordance_by_id(
        true_uncertainty,
        "true-uncertainty-navigation.scenario-bound-robust-action",
    )
    decision_quality_card = _affordance_by_id(
        true_uncertainty,
        "true-uncertainty-navigation.outcome-decoupled-decision-quality",
    )
    outcome_guard = _absence_by_field(
        true_uncertainty,
        "outcome-quality-as-decision-quality-proof",
    )

    assert len(true_uncertainty["affordances"]) == 2
    assert "tie-ambiguity-to-commitment-shape" in str(
        scenario_card["treatment_requirements"]
    )
    assert "judge-decision-against-information-not-result" not in str(
        scenario_card["treatment_requirements"]
    )

    assert "judge-decision-against-information-not-result" in str(
        decision_quality_card["treatment_requirements"]
    )
    assert "separating the quality of the *decision* from the quality of the *outcome*" in str(
        decision_quality_card["source_evidence"]
    )
    assert "preferences and complete information of a decision maker" in str(
        decision_quality_card["source_evidence"]
    )
    assert "Did not duplicate counterfactual retrospective branch reconstruction" in str(
        decision_quality_card["review_notes"]
    )

    assert outcome_guard["status"] == "not_supported_by_source"
    assert "a good decision is one that is consistent" in str(
        outcome_guard["source_evidence"]
    )


def test_pr90_absence_rails_block_fake_rigor_without_positive_bloat() -> None:
    scientific_method = _load_record("scientific-method-evidence-testing")
    premature_data_guard = _absence_by_field(
        scientific_method,
        "premature-data-analysis-as-evidence-testing",
    )
    assert len(scientific_method["affordances"]) == 1
    assert "jump prematurely into data without defining" in str(
        premature_data_guard["source_evidence"]
    )
    assert "Focus first on **rigorously framing the question or hypothesis**" in str(
        premature_data_guard["source_evidence"]
    )

    premortem = _load_record("premortem")
    pro_con_guard = _absence_by_field(
        premortem,
        "pro-con-list-as-premortem-substitute",
    )
    runtime_sim_guard = _absence_by_field(
        premortem,
        "runtime-simulation-or-ai-persona-behavior",
    )
    assert len(premortem["affordances"]) == 1
    assert "accentuate the positives and overlook negatives" in str(
        pro_con_guard["source_evidence"]
    )
    assert "Digital Twins" in str(runtime_sim_guard["source_evidence"])
    assert "multi-agent simulations" in str(runtime_sim_guard["source_evidence"])

    logical_fallacies = _load_record("logical-fallacies")
    implementation_guard = _absence_by_field(
        logical_fallacies,
        "logical-validity-as-implementation-plan",
    )
    assert len(logical_fallacies["affordances"]) == 1
    assert "understanding *what* to do and executing *how* to do it" in str(
        implementation_guard["source_evidence"]
    )
    assert "complexity of human action" in str(implementation_guard["source_evidence"])


def test_pr90_audited_records_remain_compressed_when_no_transaction_split() -> None:
    affordances_v51 = _load_compiled(AFFORDANCES_V51_PATH)
    affordances_v52 = _load_compiled(AFFORDANCES_V52_PATH)

    v51_counts = _affordance_counts_by_model(affordances_v51)
    v52_counts = _affordance_counts_by_model(affordances_v52)

    for model_id in (
        "falsifiability",
        "logical-fallacies",
        "premortem",
        "scientific-method-evidence-testing",
        "step-back",
    ):
        assert v52_counts[model_id] == v51_counts[model_id]


def test_pr90_v52_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v52", "model_affordances_v52")

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
