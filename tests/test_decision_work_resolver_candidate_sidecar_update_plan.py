from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-resolver-candidate-sidecar-update-plan-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-resolver-candidate-sidecar-update-plan-v0/review.json"
)
PR200_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-automatic-semantic-supply-pre-runtime-v1-package-gate-v0.md"
)
PR199_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-generated-read-resolver-supply-review-v0.md"
)
PR199_REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-generated-read-resolver-supply-review-v0/review.json"
)
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
)
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"
FORBIDDEN_STRINGS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)
REQUIRED_STATUSES = {
    "ready_for_sidecar_update_packet",
    "packet_with_runtime_block",
    "deferred_missing_resolver_supply",
    "blocked_resolver_supply_not_candidate",
    "blocked_privacy_risk",
    "blocked_authority_claim",
    "blocked_runtime_write_attempt",
    "requires_operator_repair",
}
FORBIDDEN_FIELDS = {
    "resolver_ref_approval",
    "resolver_refs_marked_usable",
    "actual_sidecar_write",
    "archive_mutation",
    "runtime_wiring",
    "product_proof",
    "human_validation",
    "answer_quality_score",
    "advice_correctness_claim",
    "agent_action_authorization",
    "automatic_action_authorization",
}


def _review() -> dict:
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


def test_review_json_schema_statuses_and_gate() -> None:
    review = _review()

    assert (
        review["schema_version"]
        == "lolla.decision_work_resolver_candidate_sidecar_update_plan.v0"
    )
    assert REQUIRED_STATUSES.issubset(set(review["sidecar_update_packet_statuses"]))
    assert review["decision_gate"] == (
        "proceed_to_resolver_candidate_sidecar_update_packet_adapter"
    )
    assert (
        review["recommended_next_pr"]
        == "PR202 Resolver Candidate Sidecar Update Packet Adapter v0"
    )


def test_allowed_fields_and_forbidden_fields_are_conservative() -> None:
    review = _review()

    assert "pr198_resolver_supply_candidate_packet_json" in review["allowed_inputs"]
    assert "proposed_sidecar_state" in review["allowed_sidecar_update_packet_fields"]
    assert "actual_sidecar_write_performed_false" in (
        review["allowed_sidecar_update_packet_fields"]
    )
    assert FORBIDDEN_FIELDS.issubset(set(review["forbidden_fields"]))
    assert review["required_source_refs"]["resolver_supply_packet"] is True
    assert review["required_source_refs"]["raw_content_included"] is False
    assert review["required_candidate_statuses"]["non_candidate_statuses_block"] is True


def test_runtime_user_surface_agent_and_resolver_boundaries_are_closed() -> None:
    review = _review()
    runtime = review["runtime_block_handling"]
    user_surface = review["user_surface_block_handling"]
    agent = review["agent_inspection_handling"]
    resolver = review["resolver_approval_forbidden"]
    sidecar = review["actual_sidecar_write_forbidden"]
    archive = review["archive_mutation_forbidden"]
    wiring = review["runtime_wiring_forbidden"]
    metadata = review["review_metadata"]

    assert runtime["runtime_block_must_travel_forward"] is True
    assert runtime["packet_can_override_runtime_block"] is False
    assert runtime["launch_expected_packet_status"] == "ready_for_sidecar_update_packet"
    assert runtime["deploy_expected_packet_status"] == "packet_with_runtime_block"
    assert user_surface["customer_ready"] is False
    assert user_surface["deploy_user_surface_status"] == "blocked"
    assert agent["agent_action_authorized"] is False
    assert agent["automatic_action_authorized"] is False
    assert resolver["resolver_refs_approved"] is False
    assert resolver["resolver_refs_marked_usable"] is False
    assert resolver["sidecar_update_packet_is_approval"] is False
    assert sidecar["can_update_sidecar"] is False
    assert sidecar["can_write_decision_work_directory"] is False
    assert sidecar["actual_sidecar_write_performed"] is False
    assert archive["archive_mutated"] is False
    assert archive["archive_sidecar_written"] is False
    assert wiring["runtime_wiring_changed"] is False
    assert wiring["runtime_hook_changed"] is False
    assert metadata["sidecar_update_packet_code_implemented"] is False
    assert metadata["actual_sidecar_write_performed"] is False
    assert metadata["archive_mutated"] is False
    assert metadata["runtime_wiring_changed"] is False
    assert metadata["resolver_refs_approved"] is False


def test_deterministic_allowances_do_not_allow_semantic_or_runtime_work() -> None:
    review = _review()

    assert "validate_resolver_supply_schema" in review["deterministic_allowances"]
    assert "copy_safe_refs_and_summaries" in review["deterministic_allowances"]
    assert (
        "derive_packet_status_from_explicit_candidate_status_only"
        in review["deterministic_allowances"]
    )
    assert "no_new_messy_conversation_interpretation" in (
        review["semantic_interpretation_not_allowed"]
    )
    assert "no_answer_quality_judgment" in review["semantic_interpretation_not_allowed"]
    assert "no_advice_correctness_judgment" in (
        review["semantic_interpretation_not_allowed"]
    )
    assert "plan_does_not_write_sidecars" in review["non_claims"]
    assert "plan_does_not_approve_resolver_refs" in review["non_claims"]
    assert "plan_does_not_wire_runtime" in review["non_claims"]


def test_plan_doc_answers_sidecar_packet_questions() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "# Decision Work Resolver Candidate Sidecar Update Plan v0" in text
    assert "Sidecar Update Packet" in text
    assert "proposed offline packet" in text
    assert "not an actual runtime sidecar update" in text
    assert "Launch-Beta Behavior" in text
    assert "Deploy-Intake Behavior" in text
    assert "ready_for_sidecar_update_packet" in text
    assert "packet_with_runtime_block" in text
    assert "proceed_to_resolver_candidate_sidecar_update_packet_adapter" in text
    assert "Do not write sidecars" in text


def test_discoverability_docs_reference_pr201() -> None:
    expected = "Decision Work Resolver Candidate Sidecar Update Plan"
    for path in (
        DOC_PATH,
        PR200_DOC,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr201_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            PR200_DOC,
            PR199_DOC,
            PR199_REVIEW,
            PRD_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_pr201_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        REVIEW_PATH,
        PR200_DOC,
        PR199_DOC,
        PR199_REVIEW,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_STRINGS:
            assert forbidden not in text, (path, forbidden)
