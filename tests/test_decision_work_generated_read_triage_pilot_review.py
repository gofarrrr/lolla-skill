from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-generated-read-triage-pilot-review-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-generated-read-triage-pilot-review-v0/review.json"
)
TRIAGE_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-generated-read-triage-generation-pilot-v0/triage.json"
)
PR193_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-generated-read-triage-generation-pilot-v0.md"
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


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_review_json_schema_gate_and_source_case() -> None:
    review = _json(REVIEW_PATH)

    assert (
        review["schema_version"]
        == "lolla.decision_work_generated_read_triage_pilot_review.v0"
    )
    assert review["source_case"]["case_id"] == "launch-public-enterprise-beta"
    assert review["triage_read_ref"] == (
        "reviews/codex-assisted/"
        "decision-work-generated-read-triage-generation-pilot-v0/triage.json"
    )
    assert review["decision_gate"] == "proceed_to_second_generated_read_triage_pilot"
    assert (
        review["recommended_next_pr"]
        == "PR195 Second Generated Read Triage Pilot v0"
    )


def test_reviewed_routes_match_pr193_triage_read() -> None:
    review = _json(REVIEW_PATH)
    triage = _json(TRIAGE_PATH)

    assert set(review["reviewed_route_categories"]) == set(triage["route_categories"])
    assert review["route_quality_without_scoring"][
        "routes_attention_instead_of_grading"
    ] is True
    assert review["route_quality_without_scoring"][
        "ordinary_caveated_route_requires_pairing_with_caveats"
    ] is True
    assert review["route_quality_without_scoring"][
        "forbidden_answer_grade_routes_absent"
    ] is True


def test_review_preserves_uncertainty_source_depth_and_forbidden_claim_boundary() -> None:
    review = _json(REVIEW_PATH)
    forbidden = review["forbidden_claim_scan"]
    downstream = review["downstream_boundary"]
    custody = review["custody_flags"]

    assert review["uncertainty_preservation"]["preserved"] is True
    assert review["source_depth_preservation"]["preserved"] is True
    assert forbidden["selected_forbidden_routes_present"] is False
    assert forbidden["product_proof_claimed"] is False
    assert forbidden["human_validation_claimed"] is False
    assert forbidden["answer_quality_scoring_claimed"] is False
    assert forbidden["advice_correctness_claimed"] is False
    assert forbidden["agent_action_authorized"] is False
    assert forbidden["automatic_action_authorized"] is False
    assert downstream["can_attempt_second_generated_read_triage_pilot"] is True
    assert downstream["can_mark_resolver_refs_usable"] is False
    assert downstream["can_update_runtime_sidecar"] is False
    assert downstream["can_wire_runtime"] is False
    assert downstream["can_call_models"] is False
    assert downstream["can_score_answer_quality"] is False
    assert downstream["can_authorize_agent_action"] is False
    assert custody["model_calls"] == 0
    assert custody["provider_api_calls"] == 0
    assert custody["second_case_generated"] is False
    assert custody["runtime_sidecar_updated"] is False
    assert custody["answer_quality_scored"] is False


def test_doc_answers_review_questions_and_records_boundary() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "# Decision Work Generated Read Triage Pilot Review v0" in text
    assert "Does the triage read route attention rather than grade answer quality?" in text
    assert "Does it preserve uncertainty and source-depth limitations?" in text
    assert "Does it avoid approval or safe-to-act language?" in text
    assert "Does it keep runtime/user-surface boundaries clear?" in text
    assert "Does it avoid resolver approval and sidecar updates?" in text
    assert "proceed_to_second_generated_read_triage_pilot" in text
    assert "PR195 Second Generated Read Triage Pilot v0" in text
    assert "does not create a second triage read" in text
    assert "does not" in text
    assert "update runtime sidecars" in text


def test_discoverability_docs_reference_pr194() -> None:
    expected = "Decision Work Generated Read Triage Pilot Review"
    for path in (
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
        PRD_PATH,
        PR193_DOC,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr194_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            TRIAGE_PATH,
            PR193_DOC,
            PRD_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_pr194_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        REVIEW_PATH,
        TRIAGE_PATH,
        PR193_DOC,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_STRINGS:
            assert marker not in text, f"{path}:{marker}"
