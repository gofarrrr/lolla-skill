from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-sidecar-internal-v1-completion-prd-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-sidecar-internal-v1-completion-prd-v0/review.json"
)
AUTOMATIC_SUPPLY_PRD = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
)
PR216_PACKAGE_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-controlled-archive-sidecar-write-fixture-package-gate-v0.md"
)
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"
EXPECTED_SCHEMA = (
    "lolla.decision_work_sidecar_internal_v1_completion_prd_review.v0"
)
EXPECTED_CHAIN = [
    "generated read",
    "intake validation",
    "brief supply",
    "rendered Decision Work Brief",
    "triage supply packet",
    "generated triage read",
    "resolver-supply candidate packet",
    "sidecar update packet",
    "dry-run sidecar preview",
    "explicit operator sidecar write",
    "controlled archive-shaped fixture write",
]
EXPECTED_SEQUENCE = [
    "PR218 Real Archive Sidecar Write Plan v0",
    "PR219 Real Archive Sidecar Write Adapter v0",
    "PR220 Real Archive Sidecar Write Review v0",
    "PR221 Real Archive Sidecar Write Package Gate v0",
    "PR222 Internal Demo / Operator Runbook v0",
    "PR223 Current State / Limitations Narrative Refresh v0",
]
EXPECTED_BUNDLES = {
    "Bundle A": ["PR218", "PR219"],
    "Bundle B": ["PR220", "PR221"],
    "Bundle C": ["PR222", "PR223"],
}
FORBIDDEN_MARKERS = (
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


def test_prd_records_current_chain_finish_line_and_next_boundary() -> None:
    text = PRD_PATH.read_text(encoding="utf-8")

    assert "# Decision Work Sidecar Internal v1 Completion PRD v0" in text
    for section in (
        "## 1. Current State",
        "## 2. Recommended Internal v1 Finish Line",
        "## 3. What This Internal v1 Is Not",
        "## 4. Remaining PR Plan To Internal v1",
        "## 5. PR Bundling Recommendation",
        "## 6. Acceptance Criteria For Internal v1",
        "## 7. Risks",
        "## 8. Stop Conditions",
        "## 9. Decision Gate",
        "## 10. Review JSON",
    ):
        assert section in text
    for chain_item in EXPECTED_CHAIN:
        assert chain_item in text
    for sequence_item in EXPECTED_SEQUENCE:
        assert sequence_item in text
    assert "Real historical archive mutation does not exist yet" in text
    assert "Do not implement PR218 from this PRD" in text
    assert "proceed_to_real_archive_sidecar_write_plan" in text


def test_review_json_schema_sequence_bundles_and_gate() -> None:
    review = _review()

    assert review["schema"] == EXPECTED_SCHEMA
    assert review["remaining_pr_count_ballpark"] == 6
    assert review["selected_gate"] == "proceed_to_real_archive_sidecar_write_plan"
    assert review["recommended_next_pr"] == "PR218 Real Archive Sidecar Write Plan v0"
    assert review["current_state_claim"]["controlled_archive_fixture_write_exists"] is True
    assert review["current_state_claim"]["real_historical_archive_mutation_exists"] is False
    assert review["current_state_claim"]["covered_cases"] == [
        "launch-public-enterprise-beta",
        "deploy-assisted-intake-routing",
    ]
    assert [
        f"{item['pr']} {item['title']}" for item in review["recommended_pr_sequence"]
    ] == EXPECTED_SEQUENCE
    assert {
        item["bundle"]: item["prs"] for item in review["recommended_bundles"]
    } == EXPECTED_BUNDLES


def test_review_json_preserves_custody_flags_and_non_claims() -> None:
    review = _review()
    flags = review["custody_flags"]
    non_claims = set(review["explicit_non_claims"])
    finish_line = review["internal_v1_finish_line"]

    assert flags["model_calls"] == 0
    assert flags["lolla_invoked"] is False
    assert flags["runtime_wired"] is False
    assert flags["archive_mutated"] is False
    assert flags["resolver_refs_approved"] is False
    assert flags["product_proof"] is False
    assert flags["human_validated"] is False
    assert flags["answer_quality_scored"] is False
    assert flags["action_authorized"] is False
    assert finish_line["default_runtime_behavior"] is False
    assert finish_line["internal_operator_capability_only"] is True
    for key, value in finish_line["must_preserve_false"].items():
        assert value is False, key
    for non_claim in (
        "not_customer_readiness",
        "not_default_on_runtime_behavior",
        "not_runtime_model_or_provider_calls",
        "not_resolver_approval",
        "not_product_proof",
        "not_human_validation",
        "not_answer_quality_scoring",
        "not_advice_correctness",
        "not_action_authorization",
    ):
        assert non_claim in non_claims


def test_review_json_names_acceptance_risks_and_stop_conditions() -> None:
    review = _review()
    risks = set(review["biggest_risks"])
    stops = set(review["stop_conditions"])

    assert "archive_mutation_risk" in risks
    assert "candidate_packets_mistaken_for_approval" in risks
    assert "sidecar_shaped_files_mistaken_for_runtime_success" in risks
    assert "deploy_healthcare_compliance_case_overread" in risks
    assert "target_archive_path_safety_cannot_be_proven" in stops
    assert "dry_run_and_sidecar_update_packet_do_not_match" in stops
    assert "local_absolute_paths_would_leak" in stops
    assert "proof_scoring_action_or_human_validation_claim_appears" in stops


def test_discoverability_docs_reference_pr217() -> None:
    expected = "Decision Work Sidecar Internal v1 Completion PRD"
    for path in (
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
        AUTOMATIC_SUPPLY_PRD,
        PR216_PACKAGE_DOC,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr217_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            PRD_PATH,
            REVIEW_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
            AUTOMATIC_SUPPLY_PRD,
            PR216_PACKAGE_DOC,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_pr217_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        PRD_PATH,
        REVIEW_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
        AUTOMATIC_SUPPLY_PRD,
        PR216_PACKAGE_DOC,
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_MARKERS:
            assert forbidden not in text, (path, forbidden)
