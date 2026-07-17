from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = REPO_ROOT / "docs/evals/balanced-offline-product-delta-evidence-batch-plan-v0.md"
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/balanced-offline-product-delta-evidence-batch-plan-v0/review.json"
)
READINESS_PRD_PATH = REPO_ROOT / "docs/evals/product-delta-evaluation-readiness-prd-v0.md"
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
EVALS_README_PATH = REPO_ROOT / "docs/evals/README.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"

EXPECTED_SCHEMA = "lolla.balanced_offline_product_delta_evidence_batch_plan_review.v0"
EXPECTED_GATE = "proceed_to_balanced_batch_candidate_selector_plan"
EXPECTED_NEXT_PR = "Balanced Batch Candidate Selector / Readiness Builder Plan v0"
REQUIRED_BUCKETS = {
    "likely_material_improvement_candidates",
    "partial_improvement_candidates",
    "likely_no_change_cases",
    "noisy_or_worse_candidates",
    "inconclusive_cases",
    "lost_user_intent_candidates",
    "friction_without_leverage_cases",
    "vanilla_already_good_enough_cases",
    "verification_deferral_boundary_or_decision_leverage_improvement_cases",
    "overcorrection_or_user_need_drift_cases",
}
REQUIRED_PROTOCOL_REFS = {
    "docs/evals/product-delta-evidence-thesis-v0.md",
    "docs/evals/vanilla-vs-lolla-provisional-review-protocol-v0.md",
    "docs/evals/vanilla-vs-lolla-provisional-review-v0.json",
    "docs/evals/product-delta-eval-readiness-and-provisional-run-v0.md",
    "docs/evals/codex-assisted-product-delta-batch-v0.md",
    "docs/evals/product-delta-provisional-report-v0.md",
    "docs/evals/context-engineered-provisional-review-architecture-v0.md",
    "docs/evals/product-delta-specialist-review-contracts-v0.md",
    "docs/evals/codex-assisted-specialist-review-batch-v0.md",
    "docs/evals/product-delta-fan-in-disagreement-report-v0.md",
    "docs/evals/product-delta-pr71-pr84-packaging-gate-v0.md",
}
REQUIRED_HUMAN_REVIEW_REFS = {
    "docs/evals/human-review-workflow.md",
    "docs/evals/lolla-failure-taxonomy.md",
    "docs/evals/lolla-human-review-v0.json",
    "docs/evals/actionable-delta-rubric-v0.md",
}
REQUIRED_IMPLEMENTATION_REFS = {
    "engine/system_b/product_delta_readiness.py",
    "scripts/evals/build_product_delta_provisional_review.py",
    "engine/system_b/product_delta_boundary_lint.py",
    "scripts/evals/lint_product_delta_evidence.py",
    "engine/system_b/product_delta_specialist_packets.py",
    "scripts/evals/build_product_delta_specialist_packets.py",
    "engine/system_b/human_review.py",
    "engine/system_b/review_corpus.py",
    "scripts/export_review_corpus.py",
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


def test_plan_records_all_balanced_batch_buckets() -> None:
    buckets = {bucket["bucket_id"] for bucket in _review()["batch_buckets"]}

    assert REQUIRED_BUCKETS <= buckets


def test_bucket_rationales_include_the_anti_flattery_purpose() -> None:
    bucket_map = {bucket["bucket_id"]: bucket for bucket in _review()["batch_buckets"]}

    assert "avoid flattering" in bucket_map["likely_no_change_cases"]["why_it_matters"]
    assert "find harm" in bucket_map["noisy_or_worse_candidates"]["why_it_matters"]
    assert "tolerate uncertainty" in bucket_map["inconclusive_cases"]["why_it_matters"]
    assert "preserves user goals" in bucket_map["lost_user_intent_candidates"][
        "why_it_matters"
    ]
    assert "unnecessary friction" in bucket_map["vanilla_already_good_enough_cases"][
        "why_it_matters"
    ]
    assert "avoid overclaiming" in bucket_map["partial_improvement_candidates"][
        "why_it_matters"
    ]


def test_source_artifacts_and_implementation_refs_are_recorded() -> None:
    artifacts = _review()["source_artifacts_reviewed"]

    assert REQUIRED_PROTOCOL_REFS <= set(artifacts["protocol_and_reports"])
    assert REQUIRED_HUMAN_REVIEW_REFS <= set(artifacts["human_review_references"])
    assert REQUIRED_IMPLEMENTATION_REFS <= set(artifacts["implementation_references"])


def test_candidate_source_rules_do_not_select_or_run_batch_yet() -> None:
    rules = _review()["candidate_source_rules"]

    assert rules["existing_safe_artifacts_only"] is True
    assert rules["raw_conversation_export_for_checked_in_batch_forbidden"] is True
    assert rules["actual_batch_cases_chosen_in_this_pr"] is False
    assert rules["missing_bucket_allowed_as_finding"] is True


def test_privacy_custody_and_checkin_policy_stays_safe() -> None:
    rules = _review()["privacy_and_custody_rules"]

    assert rules["raw_conversation_text_checked_in"] is False
    assert rules["raw_memo_text_checked_in"] is False
    assert rules["raw_revised_answer_text_checked_in"] is False
    assert rules["provider_model_text_checked_in"] is False
    assert rules["private_ledgers_checked_in"] is False
    assert rules["local_absolute_private_paths_checked_in"] is False
    assert rules["secrets_checked_in"] is False
    assert "relative_source_refs" in rules["allowed_checked_in_material"]
    assert "explicit_non_claims" in rules["allowed_checked_in_material"]


def test_anti_overclaim_and_boundary_flags_stay_closed() -> None:
    payload = _review()
    anti_overclaim = payload["anti_overclaim_rules"]
    boundary = payload["boundary_checks"]

    for value in anti_overclaim.values():
        assert value is False
    assert boundary["model_calls"] == 0
    for field in BOUNDARY_FALSE_FIELDS:
        assert boundary[field] is False, field


def test_prior_downgrade_is_preserved_as_positive_signal() -> None:
    signal = _review()["anti_flattery_signal"]

    assert signal["case_id"] == "accept-operations-role-startup"
    assert signal["from_candidate"] == "material_improvement_candidate"
    assert signal["to_candidate"] == "partial_improvement_candidate"
    assert "downgrade pressure" in signal["why_it_matters"]


def test_follow_on_prs_are_plan_then_selector_then_review() -> None:
    prs = _review()["follow_on_prs"]

    assert prs[0] == "Balanced Batch Candidate Selector / Readiness Builder Plan v0"
    assert prs[1] == "Balanced Batch Candidate Review v0"
    assert "Optional Live Eval Harness Plan v0, plan-only and later" == prs[-1]
    assert len(prs) == 8


def test_plan_doc_contains_core_principle_and_non_goals() -> None:
    text = _text(PLAN_PATH)
    normalized = " ".join(text.split())

    assert "The goal is not to prove Lolla is better" in text
    assert "useful, partial, no-change, noisy, worse, or inconclusive" in normalized
    assert "Do not check in:" in text
    assert "raw conversation text" in text
    assert "Do not expand this lane just to create more artifacts" not in text
    assert EXPECTED_GATE in text


def test_discoverability_docs_reference_balanced_batch_plan() -> None:
    expected = "Balanced Offline Product Delta Evidence Batch Plan"

    for path in (
        PROGRESS_PATH,
        EVALS_README_PATH,
        BOARD_README_PATH,
        READINESS_PRD_PATH,
    ):
        assert expected in _text(path), path


def test_product_delta_boundary_lint_passes_new_artifacts() -> None:
    report = lint_product_delta_paths(
        [
            PLAN_PATH,
            REVIEW_PATH,
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
