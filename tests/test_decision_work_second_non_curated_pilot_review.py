from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-second-non-curated-pilot-review-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-second-non-curated-pilot-review-v0/review.json"
)
PR229_REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-non-curated-completed-run-pilot-v0/review.json"
)
PR230_REVIEW_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-non-curated-pilot-review-v0.md"
)
PR231_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-second-non-curated-completed-run-pilot-v0.md"
)
PR231_REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-second-non-curated-completed-run-pilot-v0/review.json"
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
EXPECTED_STEPS = [
    "generated_read_intake",
    "brief_supply",
    "rendered_brief",
    "triage_supply",
    "resolver_supply",
    "sidecar_update_packet",
    "sidecar_write_dry_run",
]


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_review_json_schema_gate_and_next_pr() -> None:
    review = _json(REVIEW_PATH)

    assert review["schema_version"] == (
        "lolla.decision_work_second_non_curated_pilot_review.v0"
    )
    assert review["review_metadata"]["mode"] == "docs_review_tests_only"
    assert review["review_metadata"]["model_calls"] == 0
    assert review["review_metadata"]["lolla_invoked"] is False
    assert review["review_metadata"]["runtime_wired"] is False
    assert review["review_metadata"]["queue_worker_added"] is False
    assert review["review_metadata"]["resolver_refs_approved"] is False
    assert review["decision_gate"] == "proceed_to_automation_readiness_package_gate"
    assert review["recommended_next_pr"] == "PR233 Automation Readiness Package Gate v0"


def test_review_compares_pr229_and_pr231_outcomes() -> None:
    review = _json(REVIEW_PATH)
    pr229 = _json(PR229_REVIEW)
    pr231 = _json(PR231_REVIEW)

    assert review["reviewed_pilots"]["pr229"]["case_id"] == pr229["pilot_case"][
        "case_id"
    ]
    assert (
        review["reviewed_pilots"]["pr229"]["final_status"]
        == pr229["runner_outcome"]["final_status"]
    )
    assert (
        review["reviewed_pilots"]["pr229"]["final_status"]
        == "deferred_missing_semantic_read"
    )
    assert review["reviewed_pilots"]["pr229"]["stopped_at"] == "generated_read"
    assert (
        review["reviewed_pilots"]["pr231"]["case_id"]
        == pr231["pilot_case"]["case_id"]
    )
    assert (
        review["reviewed_pilots"]["pr231"]["final_status"]
        == pr231["runner_outcome"]["final_status"]
    )
    assert (
        review["reviewed_pilots"]["pr231"]["final_status"]
        == "sidecar_ready_for_explicit_write"
    )
    assert review["reviewed_pilots"]["pr231"]["stopped_at"] == "dry_run_complete"
    assert review["reviewed_pilots"]["pr231"]["completed_steps"] == EXPECTED_STEPS


def test_review_distinguishes_mechanics_signal_from_semantic_proof() -> None:
    review = _json(REVIEW_PATH)
    text = DOC_PATH.read_text(encoding="utf-8")

    assert review["comparison_findings"]["runner_can_stop_early"] is True
    assert (
        review["comparison_findings"][
            "runner_can_go_deep_with_existing_safe_inputs"
        ]
        is True
    )
    assert (
        review["comparison_findings"]["no_arbitrary_run_semantic_automation_proven"]
        is True
    )
    assert (
        review["comparison_findings"][
            "no_new_non_curated_semantic_understanding_proven"
        ]
        is True
    )
    assert "does not show that a new non-curated conversation" in text
    assert "Together, they still do not show arbitrary-run semantic automation" in text
    assert "not evidence that arbitrary non-curated conversations" in text


def test_status_language_is_accepted_only_with_caveats() -> None:
    findings = _json(REVIEW_PATH)["comparison_findings"]
    text = DOC_PATH.read_text(encoding="utf-8")

    assert findings["sidecar_ready_for_explicit_write_acceptable_with_caveats"]
    assert findings["sidecar_ready_for_explicit_write_too_strong_without_caveats"]
    assert "means dry-run readiness, not actual sidecar write" in text
    assert "not runtime automation" in text
    assert "user-surface availability separate" in text


def test_missingness_lens_does_not_create_unknowns_schema() -> None:
    review = _json(REVIEW_PATH)
    text = DOC_PATH.read_text(encoding="utf-8")

    assert review["missingness_lens"]["missing_required_inputs_preserved"] is True
    assert review["missingness_lens"]["deferred_reasons_preserved"] is True
    assert review["missingness_lens"]["operator_attention_items_preserved"] is True
    assert review["missingness_lens"]["new_unknowns_schema_created"] is False
    assert (
        review["missingness_lens"]["known_known_known_unknown_taxonomy_created"]
        is False
    )
    assert review["missingness_lens"]["semantic_conclusions_added"] is False
    assert "does not add a new Unknowns Register schema" in text
    assert "does not add a known-known / known-unknown taxonomy" in text


def test_review_boundary_flags_remain_false() -> None:
    boundary = _json(REVIEW_PATH)["boundary_checks"]

    for key in (
        "write_attempted",
        "actual_sidecar_write_performed",
        "archive_mutated",
        "historical_archive_mutated",
        "runtime_wiring_changed",
        "runtime_attachment_default_on",
        "resolver_refs_approved",
        "queue_worker_added",
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
        "sidecar_ready_for_explicit_write",
        "dry_run_complete",
        "generated_read_intake",
        "brief_supply",
        "rendered_brief",
        "triage_supply",
        "resolver_supply",
        "sidecar_update_packet",
        "sidecar_write_dry_run",
        "deferred_missing_semantic_read",
        "missing semantic input",
        "Automation Readiness package gate",
        "proceed_to_automation_readiness_package_gate",
        "PR233 Automation Readiness Package Gate v0",
    ):
        assert phrase in text


def test_review_discoverability_references() -> None:
    expected = "Decision Work Second Non-Curated Pilot Review"
    for path in (
        DOC_PATH,
        PR230_REVIEW_DOC,
        PR231_DOC,
        READINESS_PRD,
        AUTOMATIC_SUPPLY_PRD,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr232_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            PR230_REVIEW_DOC,
            PR231_DOC,
            PR231_REVIEW,
            PR229_REVIEW,
            READINESS_PRD,
            AUTOMATIC_SUPPLY_PRD,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0
    assert result["summary"]["info_count"] == 0


def test_pr232_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        REVIEW_PATH,
        PR230_REVIEW_DOC,
        PR231_DOC,
        PR231_REVIEW,
        PR229_REVIEW,
        READINESS_PRD,
        AUTOMATIC_SUPPLY_PRD,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_STRINGS:
            assert forbidden not in text, (path, forbidden)
