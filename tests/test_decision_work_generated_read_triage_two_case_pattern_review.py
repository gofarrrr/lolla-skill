from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-generated-read-triage-two-case-pattern-review-v0.md"
)
REVIEW_PATH = (
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
PR195_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-generated-read-second-triage-pilot-v0.md"
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
STABLE_ROUTES = {
    "source_depth_insufficient",
    "private_context_required",
    "high_overtrust_risk",
    "runtime_attachment_blocked",
}
FORBIDDEN_SELECTED_ROUTES = {
    "good_answer",
    "bad_answer",
    "approved",
    "certified",
    "safe_to_act",
    "safe_to_deploy",
    "clinically_validated",
    "legally_adequate",
    "compliance_cleared",
    "correct_advice",
    "lolla_improved_decision",
    "human_validated",
    "product_proof",
    "agent_action_authorized",
    "automatic_action_authorized",
}


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_two_case_triage_review_schema_cases_and_gate() -> None:
    review = _json(REVIEW_PATH)

    assert (
        review["schema_version"]
        == "lolla.decision_work_generated_read_triage_two_case_pattern_review.v0"
    )
    assert {case["case_id"] for case in review["compared_cases"]} == {
        "launch-public-enterprise-beta",
        "deploy-assisted-intake-routing",
    }
    assert set(review["stable_route_categories"]) == STABLE_ROUTES
    assert review["decision_gate"] == "proceed_to_generated_read_resolver_supply_plan"
    assert (
        review["recommended_next_pr"]
        == "PR197 Decision Work Generated Read Resolver Supply Plan v0"
    )


def test_two_case_review_matches_checked_in_triage_reads() -> None:
    review = _json(REVIEW_PATH)
    launch = _json(LAUNCH_TRIAGE)
    deploy = _json(DEPLOY_TRIAGE)
    by_case = {case["case_id"]: case for case in review["compared_cases"]}

    assert set(by_case["launch-public-enterprise-beta"]["route_categories"]) == set(
        launch["route_categories"]
    )
    assert set(by_case["deploy-assisted-intake-routing"]["route_categories"]) == set(
        deploy["route_categories"]
    )
    assert set(launch["route_categories"]).isdisjoint(FORBIDDEN_SELECTED_ROUTES)
    assert set(deploy["route_categories"]).isdisjoint(FORBIDDEN_SELECTED_ROUTES)
    assert launch["forbidden_route_concepts_absent"] is True
    assert deploy["forbidden_route_concepts_absent"] is True


def test_two_case_review_preserves_case_specific_domain_pattern() -> None:
    review = _json(REVIEW_PATH)
    case_specific = review["case_specific_route_categories"]

    assert case_specific["launch-public-enterprise-beta"] == [
        "ordinary_caveated_offline_brief_candidate"
    ]
    assert set(case_specific["deploy-assisted-intake-routing"]) == {
        "domain_review_recommended",
        "legal_or_compliance_review_recommended",
        "not_ready_for_user_surface",
        "agent_inspection_only",
    }
    assert review["domain_risk_pattern"][
        "deploy_assisted_intake_routing"
    ] == "domain_and_compliance_sensitive_case_with_user_surface_blocked"
    assert review["forbidden_categories_absent"] is True


def test_two_case_review_preserves_runtime_resolver_and_action_boundaries() -> None:
    review = _json(REVIEW_PATH)
    downstream = review["downstream_boundary"]
    custody = review["custody_flags"]

    assert review["resolver_boundary_pattern"]["can_plan_resolver_supply"] is True
    assert review["resolver_boundary_pattern"]["resolver_refs_marked_usable"] is False
    assert downstream["can_plan_generated_read_resolver_supply"] is True
    assert downstream["can_mark_resolver_refs_usable"] is False
    assert downstream["can_update_runtime_sidecar"] is False
    assert downstream["can_wire_runtime"] is False
    assert downstream["can_call_models"] is False
    assert downstream["can_score_answer_quality"] is False
    assert downstream["can_claim_product_proof"] is False
    assert downstream["can_claim_human_validation"] is False
    assert downstream["can_authorize_agent_action"] is False
    assert downstream["can_authorize_automatic_action"] is False
    assert custody["model_calls"] == 0
    assert custody["provider_api_calls"] == 0
    assert custody["runtime_invoked"] is False
    assert custody["skill_invoked"] is False
    assert custody["new_triage_read_generated"] is False
    assert custody["third_case_triage_generated"] is False
    assert custody["resolver_refs_marked_usable"] is False
    assert custody["runtime_sidecar_updated"] is False
    assert custody["answer_quality_scored"] is False
    assert custody["agent_action_authorized"] is False


def test_review_doc_records_pattern_findings_and_next_pr() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "# Decision Work Generated Read Triage Two-Case Pattern Review v0" in text
    assert "launch-public-enterprise-beta" in text
    assert "deploy-assisted-intake-routing" in text
    assert "proceed_to_generated_read_resolver_supply_plan" in text
    assert "PR197 Decision Work Generated Read Resolver Supply Plan v0" in text
    assert "does not generate another triage read" in text
    assert "not resolver approval or runtime sidecar update" in text


def test_discoverability_docs_reference_pr196() -> None:
    expected = "Decision Work Generated Read Triage Two-Case Pattern Review"
    for path in (
        DOC_PATH,
        PR195_DOC,
        PRD_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr196_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            LAUNCH_TRIAGE,
            DEPLOY_TRIAGE,
            PR195_DOC,
            PRD_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_pr196_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        REVIEW_PATH,
        LAUNCH_TRIAGE,
        DEPLOY_TRIAGE,
        PR195_DOC,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_STRINGS:
            assert marker not in text, f"{path}:{marker}"
