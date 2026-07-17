from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
PLAN_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-non-curated-completed-run-pilot-plan-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-non-curated-completed-run-pilot-plan-v0/review.json"
)
RUNNER_REVIEW = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-offline-operator-runner-fixture-review-v0.md"
)
RUNNER_ADAPTER = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-offline-operator-runner-adapter-v0.md"
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
EXPECTED_STATUS_GROUPS = {
    "success": (
        "sidecar_ready_for_explicit_write",
        "sidecar_ready_blocked_state",
    ),
    "deferred": (
        "deferred_missing_semantic_read",
        "deferred_missing_triage",
    ),
    "blocked": (
        "blocked_privacy_risk",
        "blocked_source_depth_insufficient",
        "blocked_schema_or_custody_failure",
        "blocked_runtime_or_user_surface_risk",
    ),
    "failure": ("runner_failed_closed",),
}
MISSINGNESS_FIELDS = (
    "missing_required_inputs",
    "blocker_reasons",
    "deferred_reasons",
    "operator_attention_items",
    "source_depth_status",
    "runtime_use_status",
    "user_surface_status",
)
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


def test_non_curated_pilot_plan_review_schema_gate_and_metadata() -> None:
    review = _json(REVIEW_PATH)

    assert (
        review["schema_version"]
        == "lolla.decision_work_non_curated_completed_run_pilot_plan_review.v0"
    )
    assert review["review_metadata"]["mode"] == "docs_tests_only"
    assert review["review_metadata"]["pilot_run_created"] is False
    assert review["review_metadata"]["model_calls"] == 0
    assert review["review_metadata"]["lolla_invoked"] is False
    assert review["review_metadata"]["runtime_wired"] is False
    assert review["review_metadata"]["queue_worker_added"] is False
    assert review["review_metadata"]["resolver_refs_approved"] is False
    assert review["review_metadata"]["actual_sidecar_write_performed"] is False
    assert review["decision_gate"] == "proceed_to_non_curated_completed_run_pilot"
    assert review["recommended_next_pr"] == "PR229 Non-Curated Completed-Run Pilot v0"


def test_non_curated_pilot_plan_defines_candidate_fixture_and_inputs() -> None:
    text = PLAN_DOC.read_text(encoding="utf-8")
    review = _json(REVIEW_PATH)

    assert review["pilot_candidate_policy"]["operator_selected_explicitly"] is True
    assert (
        review["pilot_candidate_policy"][
            "synthetic_or_sanitized_archive_like_fixture_default"
        ]
        is True
    )
    assert review["pilot_candidate_policy"]["auto_discovery_forbidden"] is True
    assert "not `launch-public-enterprise-beta`" in text
    assert "not `deploy-assisted-intake-routing`" in text
    assert "synthetic or sanitized archive-like fixture" in text
    assert "explicit local completed-run archive may be referenced only as read-only" in text
    for required_input in review["required_existing_inputs"]:
        assert required_input in text
    for arg in review["expected_pr229_runner_command_args"]:
        assert arg in text


def test_non_curated_pilot_plan_statuses_and_missingness_lens() -> None:
    text = PLAN_DOC.read_text(encoding="utf-8")
    review = _json(REVIEW_PATH)

    assert review["expected_statuses"] == {
        key: list(values) for key, values in EXPECTED_STATUS_GROUPS.items()
    }
    for values in EXPECTED_STATUS_GROUPS.values():
        for status in values:
            assert status in text
    assert review["missingness_fields_to_preserve"] == list(MISSINGNESS_FIELDS)
    for field in MISSINGNESS_FIELDS:
        assert field in text
    assert "must not introduce a new Unknowns Register schema" in text
    assert "known-known / known-unknown taxonomy" in text
    assert "must not infer missing source context" in text
    assert review["semantic_boundaries"]["infer_new_semantic_meaning"] is False
    assert review["semantic_boundaries"]["generate_interpretation_read"] is False


def test_non_curated_pilot_plan_output_policy_refusals_and_summary_contract() -> None:
    text = PLAN_DOC.read_text(encoding="utf-8")
    review = _json(REVIEW_PATH)

    assert review["output_policy"]["runner_summary_temp_only"] is True
    assert review["output_policy"]["checked_in_sidecar_outputs_allowed"] is False
    assert review["output_policy"]["real_archive_write_allowed"] is False
    assert "Outputs that must not be checked in" in text
    assert "Outputs that must remain temp/operator-local" in text
    assert "Do not pass `--write-sidecar` in PR229" in text
    for field in (
        "write_attempted_false",
        "actual_sidecar_write_performed_false",
        "archive_mutated_false",
        "historical_archive_mutated_false",
        "resolver_refs_approved_false",
        "runtime_wiring_changed_false",
    ):
        assert field in review["runner_summary_must_preserve"]
    for refusal in (
        "missing_generated_read",
        "missing_generated_triage",
        "source_depth_insufficient",
        "privacy_or_private_marker",
        "real_archive_write_attempt",
        "resolver_refs_approved_true",
    ):
        assert refusal in review["refusal_rules"]


def test_non_curated_pilot_plan_non_claims() -> None:
    text = PLAN_DOC.read_text(encoding="utf-8")
    review = _json(REVIEW_PATH)

    for flag in (
        "call_models_or_providers",
        "run_lolla",
        "invoke_lolla_skill",
    ):
        assert review["semantic_boundaries"][flag] is False
    for phrase in (
        "model/provider calls",
        "$lolla",
        "Lolla skill",
        "semantic interpretation generation",
        "queue workers",
        "runtime wiring",
        "resolver approval",
        "write sidecars",
        "mutate archives",
        "product proof",
        "human validation",
        "answer-quality scoring",
        "advice-correctness",
        "action authorization",
    ):
        assert phrase in text
    assert any(
        claim == "plan_does_not_create_queue_worker"
        for claim in review["non_claims"]
    )


def test_non_curated_pilot_plan_discoverability_references() -> None:
    expected = "Decision Work Non-Curated Completed-Run Pilot Plan"
    for path in (
        PLAN_DOC,
        RUNNER_REVIEW,
        RUNNER_ADAPTER,
        READINESS_PRD,
        AUTOMATIC_SUPPLY_PRD,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr228_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            PLAN_DOC,
            REVIEW_PATH,
            RUNNER_REVIEW,
            RUNNER_ADAPTER,
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


def test_pr228_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        PLAN_DOC,
        REVIEW_PATH,
        RUNNER_REVIEW,
        RUNNER_ADAPTER,
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
