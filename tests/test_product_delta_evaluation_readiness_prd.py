from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
PRD_PATH = REPO_ROOT / "docs/evals/product-delta-evaluation-readiness-prd-v0.md"
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/product-delta-evaluation-readiness-prd-v0/review.json"
)
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
EVALS_README_PATH = REPO_ROOT / "docs/evals/README.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"

EXPECTED_SCHEMA = "lolla.product_delta_evaluation_readiness_prd_review.v0"
EXPECTED_GATE = "proceed_to_balanced_offline_product_delta_batch_plan"
EXPECTED_NEXT_PR = "Balanced Offline Product Delta Evidence Batch Plan v0"
REQUIRED_PRODUCT_DELTA_REFS = {
    "docs/evals/product-delta-evidence-thesis-v0.md",
    "docs/evals/vanilla-vs-lolla-provisional-review-protocol-v0.md",
    "docs/evals/vanilla-vs-lolla-provisional-review-v0.json",
    "engine/system_b/product_delta_readiness.py",
    "scripts/evals/build_product_delta_provisional_review.py",
    "engine/system_b/product_delta_boundary_lint.py",
    "scripts/evals/lint_product_delta_evidence.py",
    "engine/system_b/product_delta_specialist_packets.py",
    "scripts/evals/build_product_delta_specialist_packets.py",
}
REQUIRED_HUMAN_REVIEW_REFS = {
    "docs/evals/human-review-workflow.md",
    "docs/evals/lolla-failure-taxonomy.md",
    "docs/evals/lolla-human-review-v0.json",
    "docs/evals/actionable-delta-rubric-v0.md",
    "engine/system_b/human_review.py",
}
REQUIRED_REVIEW_CORPUS_REFS = {
    "engine/system_b/review_corpus.py",
    "scripts/export_review_corpus.py",
}
REQUIRED_BATCH_INCLUSIONS = {
    "likely_no_change_cases",
    "noisy_or_worse_candidates",
    "inconclusive_cases",
    "lost_user_intent_cases",
    "lolla_added_friction_without_leverage_cases",
    "vanilla_answer_already_good_enough_cases",
    "verification_deferral_boundary_improvement_cases",
    "partial_or_ambiguous_improvement_cases",
}
BOUNDARY_FALSE_FIELDS = {
    "lolla_invoked",
    "lolla_skill_invoked",
    "new_lolla_runs_created",
    "live_evaluator_created",
    "llm_as_judge_created",
    "answer_quality_scored",
    "product_proof",
    "human_validated",
    "advice_correctness_claimed",
    "runtime_changed",
    "resolver_refs_approved",
    "agent_action_authorized",
    "automatic_action_authorized",
}
PRIVATE_MARKERS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)


def _review() -> dict[str, Any]:
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_review_json_schema_gate_and_next_pr() -> None:
    payload = _review()

    assert payload["schema_version"] == EXPECTED_SCHEMA
    assert payload["decision_gate"] == EXPECTED_GATE
    assert payload["recommended_next_pr"] == EXPECTED_NEXT_PR


def test_review_records_existing_eval_lanes() -> None:
    artifacts = _review()["source_artifacts_reviewed"]

    assert REQUIRED_PRODUCT_DELTA_REFS <= set(artifacts["product_delta_evidence_lane"])
    assert REQUIRED_HUMAN_REVIEW_REFS <= set(
        artifacts["human_review_answer_level_eval_lane"]
    )
    assert REQUIRED_REVIEW_CORPUS_REFS <= set(
        artifacts["review_corpus_queue_builder_lane"]
    )


def test_current_evidence_boundary_is_conservative() -> None:
    boundary = _review()["current_evidence_boundary"]

    assert boundary["serious_but_conservative"] is True
    assert boundary["cautious_evidence_not_product_proof"] is True
    assert (
        boundary[
            "product_delta_asks_what_changed_and_where_result_is_partial_noisy_or_inconclusive"
        ]
        is True
    )
    assert (
        boundary[
            "human_review_can_label_answer_level_improvement_but_remains_human_review_evidence"
        ]
        is True
    )
    assert boundary["does_not_justify_reliable_improvement_claim"] is True
    assert boundary["ground_truth"] is False
    assert boundary["judge_calibrated"] is False
    assert boundary["agent_use_approved_without_human_review"] is False


def test_downgrade_signal_is_preserved_as_anti_flattery_evidence() -> None:
    signal = _review()["key_downgrade_signal"]

    assert signal["case_id"] == "accept-operations-role-startup"
    assert signal["from_candidate"] == "material_improvement_candidate"
    assert signal["to_candidate"] == "partial_improvement_candidate"
    assert signal["treated_as_positive_eval_signal"] is True
    assert "resist" in _review()["strongest_useful_signal"].lower()


def test_balanced_batch_includes_negative_no_change_and_ambiguous_cases() -> None:
    inclusions = set(_review()["balanced_batch_inclusions"])

    assert REQUIRED_BATCH_INCLUSIONS <= inclusions


def test_roadmap_keeps_live_eval_harness_optional_and_plan_only() -> None:
    prs = _review()["follow_on_prs"]

    assert len(prs) == 10
    assert prs[0] == "Product Delta Evaluation Readiness PRD v0"
    assert prs[1] == "Balanced Offline Evidence Batch Plan v0"
    assert prs[-1] == "Optional Live Eval Harness Plan v0, plan-only"


def test_live_evaluator_is_rejected_as_the_immediate_move() -> None:
    rejected = _review()["rejected_immediate_moves"][
        "live_evaluator_that_reads_current_conversation_and_judges_lolla_answer"
    ]

    assert rejected["rejected_as_next_move"] is True
    assert {
        "raw_private_text_handling",
        "provider_model_calls",
        "answer_scoring_risk",
        "product_proof_creep",
    } <= set(rejected["reasons"])


def test_non_goals_and_boundary_flags_stay_closed() -> None:
    payload = _review()
    non_goals = set(payload["non_goals"])
    boundary = payload["boundary_checks"]

    assert "no_live_evaluator" in non_goals
    assert "no_provider_or_model_calls" in non_goals
    assert "no_lolla_skill_invocation" in non_goals
    assert "no_llm_as_judge_system" in non_goals
    assert "no_answer_quality_scoring" in non_goals
    assert boundary["model_calls"] == 0
    for field in BOUNDARY_FALSE_FIELDS:
        assert boundary[field] is False, field


def test_prd_contains_required_lane_and_roadmap_language() -> None:
    text = _text(PRD_PATH)

    assert "Product Delta Evidence Lane" in text
    assert "Human Review / Answer-Level Eval Lane" in text
    assert "Review Corpus / Queue Builder" in text
    assert "Balanced Offline Product Delta Evidence Batch v0" in text
    assert "likely no-change cases" in text
    assert "noisy or worse candidates" in text
    assert "lost-user-intent cases" in text
    assert "a live evaluator that reads the current conversation" in text
    assert EXPECTED_GATE in text


def test_discoverability_docs_reference_new_eval_prd() -> None:
    expected = "Product Delta Evaluation Readiness PRD"

    for path in (
        PROGRESS_PATH,
        EVALS_README_PATH,
        BOARD_README_PATH,
    ):
        assert expected in _text(path), path


def test_product_delta_boundary_lint_passes_new_artifacts() -> None:
    report = lint_product_delta_paths(
        [
            PRD_PATH,
            REVIEW_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            EVALS_README_PATH,
            BOARD_README_PATH,
        ]
    )

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def test_no_private_markers_in_new_artifacts() -> None:
    combined = "\n".join(_text(path) for path in (PRD_PATH, REVIEW_PATH))

    for marker in PRIVATE_MARKERS:
        assert marker not in combined
