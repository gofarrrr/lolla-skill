from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-non-curated-pilot-review-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-non-curated-pilot-review-v0/review.json"
)
PR229_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-non-curated-completed-run-pilot-v0.md"
)
PR229_REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-non-curated-completed-run-pilot-v0/review.json"
)
PR228_PLAN = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-non-curated-completed-run-pilot-plan-v0.md"
)
READINESS_PRD = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-sidecar-automation-readiness-prd-v0.md"
)
AUTOMATIC_SUPPLY_PRD = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-automatic-semantic-supply-prd-v0.md"
)
HISTORICAL_DISCOVERY_PATH = REPO_ROOT / "docs/history/decision-work-product-delta-discoverability.md"
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


def test_review_json_schema_gate_and_next_pr() -> None:
    review = _json(REVIEW_PATH)

    assert review["schema_version"] == (
        "lolla.decision_work_non_curated_pilot_review.v0"
    )
    assert review["decision_gate"] == (
        "proceed_to_second_non_curated_completed_run_pilot"
    )
    assert (
        review["recommended_next_pr"]
        == "PR231 Second Non-Curated Completed-Run Pilot v0"
    )
    assert review["review_metadata"]["model_calls"] == 0
    assert review["review_metadata"]["lolla_invoked"] is False
    assert review["review_metadata"]["runtime_wired"] is False
    assert review["review_metadata"]["queue_worker_added"] is False
    assert review["review_metadata"]["resolver_refs_approved"] is False
    assert review["review_metadata"]["checked_in_sidecar_outputs_created"] is False


def test_review_matches_pr229_deferred_outcome() -> None:
    review = _json(REVIEW_PATH)
    source = _json(PR229_REVIEW)

    assert (
        review["source_pilot_review_ref"]
        == "reviews/codex-assisted/decision-work-non-curated-completed-run-pilot-v0/review.json"
    )
    assert review["reviewed_runner_outcome"] == source["runner_outcome"]
    assert review["reviewed_case"]["case_id"] == source["pilot_case"]["case_id"]
    assert review["reviewed_case"]["generated_read_present"] is False
    assert review["reviewed_case"]["generated_triage_present"] is False
    assert (
        review["reviewed_runner_outcome"]["final_status"]
        == "deferred_missing_semantic_read"
    )
    assert review["reviewed_runner_outcome"]["stopped_at"] == "generated_read"
    assert "generated_read_missing" in review["reviewed_runner_outcome"][
        "deferred_reasons"
    ]


def test_review_answers_accept_deferred_but_require_second_pilot() -> None:
    answers = _json(REVIEW_PATH)["review_answers"]

    assert answers["deferred_result_acceptable_first_signal"] is True
    assert answers["missingness_visible_enough"] is True
    assert answers["deferred_reasons_clear_enough"] is True
    assert answers["stopped_at_clear_enough"] is True
    assert answers["skipped_downstream_steps_clear_enough"] is True
    assert answers["avoids_product_readiness_implication"] is True
    assert answers["source_depth_gap_not_hidden"] is True
    assert answers["semantic_input_gap_not_hidden"] is True
    assert answers["enough_for_package_readiness"] is False
    assert answers["second_non_curated_pilot_needed"] is True


def test_review_preserves_missingness_lens_without_new_unknowns_schema() -> None:
    review = _json(REVIEW_PATH)
    text = DOC_PATH.read_text(encoding="utf-8")

    assert review["missingness_lens"]["missing_required_inputs_preserved"] is True
    assert review["missingness_lens"]["deferred_reasons_preserved"] is True
    assert review["missingness_lens"]["new_unknowns_schema_created"] is False
    assert (
        review["missingness_lens"]["known_known_known_unknown_taxonomy_created"]
        is False
    )
    assert review["missingness_lens"]["semantic_conclusions_added"] is False
    assert "does not add a new Unknowns Register schema" in text
    assert "does not add a known-known / known-unknown taxonomy" in text
    assert "does not infer semantic meaning from absence" in text


def test_review_boundary_flags_remain_false() -> None:
    boundary = _json(REVIEW_PATH)["boundary_checks"]

    for key in (
        "write_attempted",
        "actual_sidecar_write_performed",
        "archive_mutated",
        "historical_archive_mutated",
        "runtime_wiring_changed",
        "resolver_refs_approved",
        "product_proof",
        "human_validated",
        "answer_quality_scored",
        "advice_correctness_claimed",
        "approval_or_certification_added",
        "agent_action_authorized",
        "automatic_action_authorized",
    ):
        assert boundary[key] is False


def test_review_doc_answers_requested_questions() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in (
        "deferred_missing_semantic_read",
        "stopped_at: generated_read",
        "generated_read_missing",
        "A deferred result is not failure",
        "missing_required_inputs",
        "deferred_reasons",
        "skipped downstream steps",
        "does not infer semantic meaning from absence",
        "does not show that a non-curated case is ready for sidecar write",
        "not sufficient for automation-readiness packaging",
        "second non-curated completed-run pilot",
        "existing checked-in-safe semantic inputs",
        "proceed_to_second_non_curated_completed_run_pilot",
    ):
        assert phrase in text


def test_review_discoverability_references() -> None:
    expected = "Decision Work Non-Curated Pilot Review"
    for path in (
        DOC_PATH,
        PR229_DOC,
        PR228_PLAN,
        READINESS_PRD,
        AUTOMATIC_SUPPLY_PRD,
        HISTORICAL_DISCOVERY_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr230_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            PR229_DOC,
            PR229_REVIEW,
            PR228_PLAN,
            READINESS_PRD,
            AUTOMATIC_SUPPLY_PRD,
            HISTORICAL_DISCOVERY_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0
    assert result["summary"]["info_count"] == 0


def test_pr230_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        REVIEW_PATH,
        PR229_DOC,
        PR229_REVIEW,
        PR228_PLAN,
        READINESS_PRD,
        AUTOMATIC_SUPPLY_PRD,
        HISTORICAL_DISCOVERY_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_STRINGS:
            assert forbidden not in text, (path, forbidden)
