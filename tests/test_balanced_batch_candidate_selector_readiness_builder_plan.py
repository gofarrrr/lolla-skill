from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = (
    REPO_ROOT
    / "docs/evals/balanced-batch-candidate-selector-readiness-builder-plan-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/balanced-batch-candidate-selector-readiness-builder-plan-v0/review.json"
)
SOURCE_PLAN_PATH = (
    REPO_ROOT / "docs/evals/balanced-offline-product-delta-evidence-batch-plan-v0.md"
)
READINESS_PRD_PATH = REPO_ROOT / "docs/evals/product-delta-evaluation-readiness-prd-v0.md"
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
EVALS_README_PATH = REPO_ROOT / "docs/evals/README.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"

EXPECTED_SCHEMA = (
    "lolla.balanced_batch_candidate_selector_readiness_builder_plan_review.v0"
)
EXPECTED_GATE = "proceed_to_balanced_batch_candidate_selector_builder"
EXPECTED_NEXT_PR = "Balanced Batch Candidate Selector / Readiness Builder v0"
PLAN_TITLE = "Balanced Batch Candidate Selector / Readiness Builder Plan"
REQUIRED_BUCKETS = {
    "likely_material_improvement_candidate",
    "partial_improvement_candidate",
    "likely_no_change_candidate",
    "noisy_or_worse_candidate",
    "inconclusive_candidate",
    "lost_user_intent_candidate",
    "friction_without_leverage_candidate",
    "vanilla_already_good_enough_candidate",
    "useful_verification_deferral_boundary_candidate",
    "overcorrection_or_user_need_drift_candidate",
}
REQUIRED_SELECTION_SIGNALS = {
    "existing_product_delta_readiness_metadata",
    "existing_provisional_labels",
    "specialist_disagreement_or_fan_in_signals",
    "human_review_taxonomy_labels_where_available",
    "failure_taxonomy_hints_where_available",
    "archived_case_metadata_without_copying_raw_conversation_text",
    "run_health_and_capture_adequacy_metadata",
    "review_corpus_readiness_metadata",
}
REQUIRED_OUTPUT_FIELDS = {
    "schema",
    "generated_at",
    "source_scope",
    "candidate_count",
    "candidates[]",
    "candidate_id_or_case_ref",
    "proposed_bucket",
    "bucket_reason_summary",
    "readiness_status",
    "missing_required_artifacts",
    "custody_flags",
    "private_artifact_refs",
    "checked_in_safe_refs",
    "non_claims",
    "review_next_step",
}
REQUIRED_STATUSES = {
    "ready_for_balanced_product_delta_review",
    "deferred_missing_artifacts",
    "deferred_private_context_required",
    "blocked_privacy_risk",
    "blocked_capture_or_run_health",
    "blocked_schema_or_custody_failure",
    "excluded_not_relevant",
    "excluded_duplicate_or_near_duplicate",
}
REQUIRED_FORBIDDEN_BEHAVIORS = {
    "do_not_read_or_export_raw_private_conversation_text_into_checked_in_batch_files",
    "do_not_copy_raw_revised_answers",
    "do_not_copy_raw_memos",
    "do_not_copy_provider_model_text",
    "do_not_copy_private_ledgers",
    "do_not_copy_local_absolute_private_paths",
    "do_not_infer_answer_quality",
    "do_not_assign_final_labels",
    "do_not_score_cases",
    "do_not_claim_product_proof",
    "do_not_call_models_or_providers",
    "do_not_invoke_lolla_or_lolla_skill",
    "do_not_create_new_lolla_runs",
    "do_not_mutate_archives",
    "do_not_touch_skill_md",
    "do_not_touch_scripts_skill",
    "do_not_touch_scripts_archive_run",
}
BOUNDARY_FALSE_FIELDS = {
    "lolla_invoked",
    "lolla_skill_invoked",
    "new_lolla_runs_created",
    "live_evaluator_created",
    "llm_as_judge_created",
    "product_delta_review_run",
    "candidate_selector_implemented",
    "answer_quality_scored",
    "product_proof",
    "human_validated",
    "advice_correctness_claimed",
    "runtime_changed",
    "archive_mutated",
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


def test_candidate_buckets_match_balanced_batch_plan() -> None:
    payload = _review()

    assert REQUIRED_BUCKETS == set(payload["candidate_buckets"])


def test_allowed_selection_signals_are_safe_metadata_only() -> None:
    payload = _review()

    assert REQUIRED_SELECTION_SIGNALS <= set(payload["allowed_selection_signals"])
    assert payload["candidate_source_rules"]["explicit_source_scope_required"] is True
    assert payload["candidate_source_rules"]["broad_archive_scan_allowed"] is False
    assert payload["candidate_source_rules"]["raw_private_artifacts_remain_local"] is True
    assert payload["candidate_source_rules"]["future_review_required_before_product_delta_conclusion"] is True


def test_readiness_criteria_refuse_final_quality_or_proof_claims() -> None:
    criteria = _review()["readiness_criteria"]

    assert criteria["stable_candidate_ref_required"] is True
    assert criteria["safe_source_ref_required"] is True
    assert criteria["custody_metadata_required"] is True
    assert criteria["proposed_bucket_required"] is True
    assert criteria["bucket_reason_summary_required"] is True
    assert criteria["final_product_delta_label_allowed"] is False
    assert criteria["answer_quality_score_allowed"] is False
    assert criteria["product_proof_allowed"] is False
    assert criteria["advice_correctness_claim_allowed"] is False
    assert criteria["agent_approval_allowed"] is False


def test_future_output_shape_and_statuses_are_defined() -> None:
    payload = _review()

    assert REQUIRED_OUTPUT_FIELDS <= set(payload["future_output_schema_expectations"])
    assert REQUIRED_STATUSES <= set(payload["readiness_statuses"])


def test_forbidden_selection_behavior_blocks_overclaim_and_private_export() -> None:
    forbidden = set(_review()["forbidden_selection_behavior"])

    assert REQUIRED_FORBIDDEN_BEHAVIORS <= forbidden


def test_anti_flattery_principle_and_outcome_space_are_preserved() -> None:
    payload = _review()

    assert "not trying to find wins" in payload["anti_flattery_principle"]
    assert "useful, partial, no-change, noisy, worse, or inconclusive" in payload[
        "anti_flattery_principle"
    ]
    assert set(payload["outcome_space_preserved"]) == {
        "useful",
        "partial",
        "no_change",
        "noisy",
        "worse",
        "inconclusive",
    }
    assert payload["prior_downgrade_signal_preserved"]["case_id"] == (
        "accept-operations-role-startup"
    )


def test_boundary_flags_stay_closed() -> None:
    payload = _review()
    boundary = payload["boundary_checks"]

    assert boundary["model_calls"] == 0
    for field in BOUNDARY_FALSE_FIELDS:
        assert boundary[field] is False, field


def test_plan_doc_records_plan_only_selector_boundary() -> None:
    text = _text(PLAN_PATH)
    normalized = " ".join(text.split())

    assert "This PR is plan-only" in text
    assert "does not implement the selector" in text
    assert "scan archives broadly" in normalized
    assert "The selector/readiness builder is not trying to find wins" in text
    assert "not final labels" in normalized
    assert EXPECTED_GATE in text
    assert EXPECTED_NEXT_PR in text


def test_discoverability_docs_reference_candidate_selector_plan() -> None:
    for path in (
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        EVALS_README_PATH,
        BOARD_README_PATH,
        READINESS_PRD_PATH,
        SOURCE_PLAN_PATH,
    ):
        assert PLAN_TITLE in _text(path), path


def test_product_delta_boundary_lint_passes_new_artifacts() -> None:
    report = lint_product_delta_paths(
        [
            PLAN_PATH,
            REVIEW_PATH,
            SOURCE_PLAN_PATH,
            READINESS_PRD_PATH,
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
    combined = "\n".join(_text(path) for path in (PLAN_PATH, REVIEW_PATH))

    for marker in PRIVATE_MARKERS:
        assert marker not in combined
