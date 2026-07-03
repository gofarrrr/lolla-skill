from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from engine.system_b.decision_work_generated_interpretation_read_intake import (
    validate_generated_interpretation_read,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-generated-interpretation-read-intake-review-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-generated-interpretation-read-intake-review-v0/review.json"
)
INTAKE_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-generated-interpretation-read-intake-v0.md"
)
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
)
QUEUE_CONTRACT_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-offline-interpretation-queue-contract-v0.md"
)
PROMPT_PACKET_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-operator-codex-interpretation-prompt-packet-v0.md"
)
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"

EXISTING_READS = {
    "launch-public-enterprise-beta": REPO_ROOT
    / "reviews/codex-assisted/decision-work-conversation-interpretation-tiny-offline-read-v0/read.json",
    "deploy-assisted-intake-routing": REPO_ROOT
    / "reviews/codex-assisted/decision-work-conversation-interpretation-second-tiny-offline-read-v0/read.json",
    "ceo-remove-founding-cofounder": REPO_ROOT
    / "reviews/codex-assisted/decision-work-conversation-interpretation-third-tiny-offline-read-v0/read.json",
}
EXPECTED_REJECTIONS = {
    "unsupported_schema": "unsupported_schema",
    "missing_source_refs": "rejected_missing_source_refs",
    "missing_uncertainty": "rejected_missing_uncertainty",
    "product_proof_true": "rejected_product_proof_claim",
    "human_validated_true": "rejected_human_validation_claim",
    "answer_quality_scored_true": "rejected_quality_label",
    "agent_action_authorized_true": "rejected_action_authorization",
    "automatic_action_authorized_true": "rejected_action_authorization",
    "quality_label_guard_false": "rejected_quality_label",
    "local_absolute_path": "rejected_local_absolute_path",
    "raw_private_marker": "rejected_privacy_risk",
    "missing_required_non_claim": "requires_operator_repair",
}
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


def _review() -> dict[str, Any]:
    return json.loads(REVIEW_PATH.read_text())


def _base_read() -> dict[str, Any]:
    return json.loads(EXISTING_READS["launch-public-enterprise-beta"].read_text())


def _write_candidate(tmp_path: Path, payload: dict[str, Any]) -> Path:
    path = tmp_path / "candidate.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _synthetic_payload(name: str) -> dict[str, Any]:
    payload = copy.deepcopy(_base_read())
    if name == "unsupported_schema":
        payload["schema_version"] = "lolla.unsupported_read.v0"
    elif name == "missing_source_refs":
        payload["interpreted_fields"][0]["source_refs"] = []
    elif name == "missing_uncertainty":
        del payload["interpreted_fields"][0]["uncertainty"]
    elif name == "product_proof_true":
        payload["custody_flags"]["product_proof"] = True
    elif name == "human_validated_true":
        payload["custody_flags"]["human_validated"] = True
    elif name == "answer_quality_scored_true":
        payload["custody_flags"]["answer_quality_scored"] = True
    elif name == "agent_action_authorized_true":
        payload["custody_flags"]["agent_action_authorized"] = True
    elif name == "automatic_action_authorized_true":
        payload["custody_flags"]["automatic_action_authorized"] = True
    elif name == "quality_label_guard_false":
        payload["interpreted_fields"][0]["must_not_be_used_as_quality_label"] = False
    elif name == "local_absolute_path":
        payload["interpreted_fields"][0]["source_refs"][0]["artifact"] = (
            "/" + "Users" + "/example/private/archive/result.json"
        )
    elif name == "raw_private_marker":
        payload["read_metadata"]["notes"].append("SEC" + "RET")
    elif name == "missing_required_non_claim":
        payload["non_claims"] = [
            claim for claim in payload["non_claims"] if claim != "not_product_proof"
        ]
    else:
        raise AssertionError(name)
    return payload


def test_review_json_shape_and_boundary_flags() -> None:
    review = _review()

    assert (
        review["schema_version"]
        == "lolla.decision_work_generated_interpretation_read_intake_review.v0"
    )
    assert review["reviewed_stage"] == (
        "PR182 Decision Work Generated Interpretation Read Intake And Validator v0"
    )
    assert review["human_validated"] is False
    assert review["product_proof"] is False
    assert review["model_calls"] == 0
    assert review["runtime_invoked"] is False
    assert review["skill_invoked"] is False
    assert review["archive_mutated"] is False
    assert review["prompt_changed"] is False
    assert review["skill_files_changed"] is False
    assert review["answer_quality_scored"] is False
    assert review["agent_action_authorized"] is False
    assert review["automatic_action_authorized"] is False
    assert review["generated_reads_created"] is False
    assert review["briefs_rendered"] is False
    assert review["briefs_enriched"] is False
    assert review["triage_generated"] is False
    assert review["resolver_refs_updated"] is False
    assert review["runtime_sidecars_updated"] is False


def test_reviewed_reads_match_actual_validator_acceptance() -> None:
    review = _review()
    reviewed_by_case = {item["case_id"]: item for item in review["reviewed_reads"]}

    assert set(reviewed_by_case) == set(EXISTING_READS)
    assert set(review["accepted_reads"]) == set(EXISTING_READS)

    for case_id, path in EXISTING_READS.items():
        result = validate_generated_interpretation_read(
            read_path=path,
            created_at="2026-07-03T00:00:00Z",
        )
        reviewed = reviewed_by_case[case_id]
        assert result["intake_status"] == "accepted"
        assert reviewed["intake_status"] == result["intake_status"]
        assert reviewed["schema_detected"] == result["read_schema_detected"]
        assert reviewed["can_update_sidecar_in_pr182"] is False
        assert reviewed["can_authorize_agent_action"] is False


def test_rejected_synthetic_cases_match_actual_validator_statuses(tmp_path: Path) -> None:
    review = _review()
    reviewed = {
        item["fixture_name"]: item["expected_intake_status"]
        for item in review["rejected_synthetic_cases"]
    }

    assert reviewed == EXPECTED_REJECTIONS

    for fixture_name, expected_status in EXPECTED_REJECTIONS.items():
        path = _write_candidate(tmp_path, _synthetic_payload(fixture_name))
        result = validate_generated_interpretation_read(
            read_path=path,
            created_at="2026-07-03T00:00:00Z",
        )
        assert result["intake_status"] == expected_status
        assert result["accepted_for_downstream"] is False
        assert result["downstream_allowed"]["can_update_sidecar"] is False
        assert result["downstream_allowed"]["can_authorize_agent_action"] is False


def test_downstream_boundary_assessment_stays_narrow() -> None:
    boundary = _review()["downstream_boundary_assessment"]

    assert boundary["accepted_reads_can_feed_later_offline_brief_steps"] is True
    assert boundary["accepted_reads_can_update_runtime_sidecars_in_pr182"] is False
    assert boundary["accepted_reads_can_authorize_agent_action"] is False
    assert boundary["accepted_reads_can_be_used_as_quality_labels"] is False
    assert "later offline" in boundary["finding"].lower()
    assert "not runtime attachment or action" in boundary["finding"].lower()


def test_review_names_risks_without_overclaiming() -> None:
    review = _review()

    assert "semantically wrong" in review["false_positive_risk"]["risk"]
    assert "Repair-required" in review["false_negative_risk"]["mitigation"]
    assert "cannot prove full conversation truth" in review["source_depth_risk"]["risk"]
    assert "raw/private text" in review["privacy_risk"]["risk"]
    assert "proof" in review["overclaim_risk"]["risk"]
    assert review["decision_gate"] == "proceed_to_operator_codex_generated_read_pilot"
    assert review["recommended_next_pr"] == (
        "PR184 Operator/Codex Generated Read Pilot v0"
    )


def test_review_non_claims_exclude_forbidden_claims() -> None:
    non_claims = set(_review()["non_claims"])

    assert "review_is_not_human_validation" in non_claims
    assert "review_is_not_product_proof" in non_claims
    assert "review_does_not_score_answer_quality" in non_claims
    assert "review_does_not_claim_advice_correctness" in non_claims
    assert "review_does_not_authorize_agent_action" in non_claims
    assert "review_does_not_authorize_automatic_action" in non_claims
    assert "review_does_not_generate_interpretation_reads" in non_claims
    assert "review_does_not_update_sidecars" in non_claims


def test_doc_explains_review_only_boundary_and_next_gate() -> None:
    text = DOC_PATH.read_text()

    assert "# Decision Work Generated Interpretation Read Intake Review v0" in text
    assert "This is review, docs, and tests only" in text
    assert "Unsafe synthetic examples are not checked in" in text
    assert "Acceptance means the read has passed structural and custody intake" in text
    assert "proceed_to_operator_codex_generated_read_pilot" in text
    assert "PR184 Operator/Codex Generated Read Pilot v0" in text


def test_docs_and_review_pass_product_delta_lint() -> None:
    report = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            INTAKE_DOC_PATH,
            PRD_PATH,
            QUEUE_CONTRACT_DOC,
            PROMPT_PACKET_DOC,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert report["summary"]["blocking_error_count"] == 0
    assert report["summary"]["warning_count"] == 0


def test_pr183_files_do_not_contain_private_markers() -> None:
    for path in [DOC_PATH, REVIEW_PATH, Path(__file__)]:
        text = path.read_text()
        for marker in FORBIDDEN_STRINGS:
            assert marker not in text
