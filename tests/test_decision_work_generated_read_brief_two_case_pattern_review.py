from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-generated-read-brief-two-case-pattern-review-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-generated-read-brief-two-case-pattern-review-v0/review.json"
)
LAUNCH_BRIEF = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-generated-read-rendered-launch-public-enterprise-beta-v0.md"
)
DEPLOY_BRIEF = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-generated-read-rendered-deploy-assisted-intake-routing-v0.md"
)
PR189_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-generated-read-second-brief-rendering-pilot-v0.md"
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


def _review() -> dict:
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


def test_two_case_review_schema_cases_and_gate() -> None:
    review = _review()

    assert (
        review["schema_version"]
        == "lolla.decision_work_generated_read_brief_two_case_pattern_review.v0"
    )
    assert {case["case_id"] for case in review["compared_cases"]} == {
        "launch-public-enterprise-beta",
        "deploy-assisted-intake-routing",
    }
    assert review["decision_gate"] == "proceed_to_generated_read_triage_supply_plan"
    assert (
        review["recommended_next_pr"]
        == "PR191 Decision Work Generated Read Triage Supply Plan v0"
    )


def test_two_case_review_preserves_boundaries() -> None:
    review = _review()
    custody = review["custody_flags"]
    downstream = review["downstream_boundary"]

    assert custody["model_calls"] == 0
    assert custody["runtime_invoked"] is False
    assert custody["skill_invoked"] is False
    assert custody["archive_mutated"] is False
    assert custody["new_read_generated"] is False
    assert custody["third_case_rendered"] is False
    assert custody["brief_enriched"] is False
    assert custody["triage_generated"] is False
    assert custody["resolver_refs_marked_usable"] is False
    assert custody["runtime_sidecar_updated"] is False
    assert custody["product_proof"] is False
    assert custody["human_validated"] is False
    assert custody["answer_quality_scored"] is False
    assert custody["agent_action_authorized"] is False
    assert custody["automatic_action_authorized"] is False
    assert downstream["can_plan_generated_read_triage_supply"] is True
    assert downstream["can_generate_triage"] is False
    assert downstream["can_update_runtime_sidecar"] is False
    assert downstream["can_call_models"] is False
    assert downstream["can_authorize_agent_action"] is False


def test_two_rendered_briefs_share_required_generated_read_boundary_language() -> None:
    for path in (LAUNCH_BRIEF, DEPLOY_BRIEF):
        text = path.read_text(encoding="utf-8")
        assert "# Decision Work Generated Read Brief" in text
        assert "not proof that the interpretation is true" in text
        assert "Supply status: `ready_for_offline_brief_rendering`" in text
        assert "Uncertainty: medium." in text
        assert "Source references" in text
        assert "Evidence-only fields excluded" in text
        assert "Product proof: no" in text
        assert "Human validation: no" in text
        assert "Answer-quality scoring: no" in text
        assert "Runtime sidecar update allowed: no" in text
        assert "Agent action authorization: no" in text

    assert "public enterprise beta" in LAUNCH_BRIEF.read_text(encoding="utf-8")
    assert "outpatient clinics" in DEPLOY_BRIEF.read_text(encoding="utf-8")
    assert "clinical compliance" in DEPLOY_BRIEF.read_text(encoding="utf-8")


def test_review_doc_records_pattern_findings_and_next_pr() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "# Decision Work Generated Read Brief Two-Case Pattern Review v0" in text
    assert "launch-public-enterprise-beta" in text
    assert "deploy-assisted-intake-routing" in text
    assert "proceed_to_generated_read_triage_supply_plan" in text
    assert "PR191 Decision Work Generated Read Triage Supply Plan v0" in text
    assert "does not generate triage" in text
    assert "not to generate triage yet" in text


def test_discoverability_docs_reference_pr190() -> None:
    expected = "Decision Work Generated Read Brief Two-Case Pattern Review"
    for path in (
        DOC_PATH,
        PR189_DOC,
        PRD_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr190_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            LAUNCH_BRIEF,
            DEPLOY_BRIEF,
            PR189_DOC,
            PRD_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_pr190_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        REVIEW_PATH,
        LAUNCH_BRIEF,
        DEPLOY_BRIEF,
        PR189_DOC,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_STRINGS:
            assert marker not in text, f"{path}:{marker}"
