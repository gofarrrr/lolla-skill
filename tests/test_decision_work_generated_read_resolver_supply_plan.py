from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-generated-read-resolver-supply-plan-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-generated-read-resolver-supply-plan-v0/review.json"
)
PR196_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-generated-read-triage-two-case-pattern-review-v0.md"
)
PR196_REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-generated-read-triage-two-case-pattern-review-v0/review.json"
)
LAUNCH_TRIAGE = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-generated-read-triage-generation-pilot-v0/triage.json"
)
DEPLOY_TRIAGE = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-generated-read-second-triage-pilot-v0/triage.json"
)
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-automatic-semantic-supply-prd-v0.md"
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
REQUIRED_INPUTS = {
    "generated_interpretation_read_json",
    "pr182_intake_result_json",
    "pr186_brief_supply_json",
    "pr187_rendered_brief_markdown",
    "pr192_triage_supply_json",
    "generated_triage_json",
}
REQUIRED_STATUSES = {
    "ready_for_resolver_candidate_packet",
    "candidate_packet_with_runtime_block",
    "deferred_missing_triage",
    "deferred_missing_rendered_brief",
    "deferred_missing_brief_supply",
    "blocked_intake_not_accepted",
    "blocked_triage_missing",
    "blocked_privacy_risk",
    "blocked_authority_claim",
    "requires_operator_repair",
}
REQUIRED_BLOCKED_FIELDS = {
    "answer_quality_judgment",
    "advice_correctness_judgment",
    "lolla_improvement_claim",
    "human_validation_claim",
    "product_proof_claim",
    "resolver_ref_approval",
    "runtime_sidecar_permission",
    "agent_action_permission",
    "automatic_action_permission",
}


def _review() -> dict:
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


def test_review_json_schema_inputs_and_gate() -> None:
    review = _review()

    assert (
        review["schema_version"]
        == "lolla.decision_work_generated_read_resolver_supply_plan.v0"
    )
    assert REQUIRED_INPUTS.issubset(set(review["allowed_resolver_supply_inputs"]))
    assert review["decision_gate"] == (
        "proceed_to_generated_read_resolver_supply_adapter"
    )
    assert (
        review["recommended_next_pr"]
        == "PR198 Decision Work Generated Read Resolver Supply Adapter v0"
    )


def test_candidate_statuses_and_blocked_fields_are_conservative() -> None:
    review = _review()

    assert REQUIRED_STATUSES.issubset(set(review["resolver_supply_statuses"]))
    assert REQUIRED_BLOCKED_FIELDS.issubset(set(review["blocked_fields"]))
    assert "source_triage_route_categories" in review["allowed_safe_ref_candidates"]
    assert "route_summary" in review["allowed_safe_ref_candidates"]
    assert "source_depth_limits" in review["evidence_only_fields"]
    assert "overtrust_risk" in review["evidence_only_fields"]


def test_required_refs_uncertainty_and_route_effects_are_explicit() -> None:
    review = _review()
    source_refs = review["required_source_refs"]
    route_effects = review["required_triage_routes"]

    assert source_refs["generated_read"] is True
    assert source_refs["intake_result"] is True
    assert source_refs["brief_supply"] is True
    assert source_refs["rendered_brief"] is True
    assert source_refs["triage_supply"] is True
    assert source_refs["triage_read"] is True
    assert source_refs["content_included"] is False
    assert review["required_uncertainty"]["missing_uncertainty_blocks"] is True
    assert (
        route_effects["runtime_attachment_blocked"]
        == "runtime_use_blocked"
    )
    assert route_effects["agent_inspection_only"] == (
        "runtime_and_user_surface_blocked"
    )
    assert route_effects["not_ready_for_user_surface"] == "user_surface_blocked"


def test_resolver_approval_runtime_sidecar_and_action_boundaries_are_closed() -> None:
    review = _review()
    custody = review["custody_requirements"]

    assert review["resolver_approval_forbidden"]["resolver_refs_approved"] is False
    assert (
        review["resolver_approval_forbidden"]["resolver_refs_marked_usable"]
        is False
    )
    assert (
        review["resolver_approval_forbidden"]["candidate_packet_is_approval"]
        is False
    )
    assert review["runtime_sidecar_update_forbidden"]["can_update_sidecar"] is False
    assert (
        review["runtime_sidecar_update_forbidden"]["can_write_runtime_sidecar"]
        is False
    )
    assert review["runtime_sidecar_update_forbidden"]["can_wire_runtime"] is False
    assert custody["model_calls"] == 0
    assert custody["runtime_invoked"] is False
    assert custody["skill_invoked"] is False
    assert custody["archive_mutated"] is False
    assert custody["resolver_supply_code_implemented"] is False
    assert custody["resolver_refs_approved"] is False
    assert custody["resolver_refs_marked_usable"] is False
    assert custody["runtime_sidecar_updated"] is False
    assert custody["runtime_wired"] is False
    assert custody["product_proof"] is False
    assert custody["human_validated"] is False
    assert custody["answer_quality_scored"] is False
    assert custody["advice_correctness_claimed"] is False
    assert custody["agent_action_authorized"] is False
    assert custody["automatic_action_authorized"] is False


def test_doc_answers_resolver_supply_questions_and_gate() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "# Decision Work Generated Read Resolver Supply Plan v0" in text
    assert "resolver supply is not resolver approval" in text
    assert "Resolver Supply Candidate" in text
    assert "Allowed Resolver Supply Inputs" in text
    assert "Safe Ref Candidates" in text
    assert "Evidence-Only And Blocked Fields" in text
    assert "Required Triage Routes" in text
    assert "candidate_packet_with_runtime_block" in text
    assert "proceed_to_generated_read_resolver_supply_adapter" in text
    assert "PR198 Decision Work Generated Read Resolver Supply Adapter v0" in text
    assert "Do not implement resolver approval" in text


def test_discoverability_docs_reference_pr197() -> None:
    expected = "Decision Work Generated Read Resolver Supply Plan"
    for path in (
        DOC_PATH,
        PR196_DOC,
        PRD_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr197_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            PR196_DOC,
            PR196_REVIEW,
            LAUNCH_TRIAGE,
            DEPLOY_TRIAGE,
            PRD_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_pr197_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        REVIEW_PATH,
        PR196_DOC,
        PR196_REVIEW,
        LAUNCH_TRIAGE,
        DEPLOY_TRIAGE,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_STRINGS:
            assert marker not in text, f"{path}:{marker}"
