from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-generated-read-to-brief-supply-plan-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-generated-read-to-brief-supply-plan-v0/review.json"
)
PR184_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-operator-codex-generated-read-pilot-v0.md"
)
PR184_READ = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/read.json"
)
PR184_INTAKE = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/intake.json"
)
PR182_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-generated-interpretation-read-intake-v0.md"
)
PR139_RULES = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-enrichment-rules-contract-v0.json"
)
PR140_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-offline-enriched-builder-v0.md"
)
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
)
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"

EXPECTED_ALLOWED_FIELDS = {
    "decision_question",
    "likely_starting_direction",
    "revised_direction_or_action_consequence",
    "decision_thresholds",
    "evidence_gates",
    "useful_friction",
    "what_the_final_answer_does_not_prove",
}
EXPECTED_EVIDENCE_ONLY_FIELDS = {
    "live_options",
    "abandoned_or_rejected_options",
    "noisy_friction",
    "lost_value",
    "assistant_influence_on_user_framing",
    "safe_for_agent_inspection_only",
}
EXPECTED_BLOCKED_FIELDS = {
    "answer_quality_score",
    "improvement_score",
    "approval",
    "certification",
    "product_proof",
    "human_validation",
    "advice_correctness",
    "lolla_improved_decision_proof",
    "agent_action_authorization",
    "automatic_action_authorization",
    "runtime_sidecar_update_authorization",
    "raw_conversation_text",
    "raw_revised_answer_text",
    "raw_memo_text",
    "provider_text",
    "private_ledgers",
    "local_absolute_paths",
    "secrets",
    "hidden_chain_of_thought_style_material",
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


def _pilot_read() -> dict[str, Any]:
    return json.loads(PR184_READ.read_text())


def _pilot_intake() -> dict[str, Any]:
    return json.loads(PR184_INTAKE.read_text())


def test_review_json_schema_and_custody_flags() -> None:
    review = _review()

    assert (
        review["schema_version"]
        == "lolla.decision_work_generated_read_to_brief_supply_plan.v0"
    )
    custody = review["custody_flags"]
    assert custody["runtime_invoked"] is False
    assert custody["skill_invoked"] is False
    assert custody["archive_mutated"] is False
    assert custody["model_calls"] == 0
    assert custody["generated_read_created"] is False
    assert custody["brief_generated"] is False
    assert custody["enriched_brief_generated"] is False
    assert custody["triage_generated"] is False
    assert custody["resolver_refs_approved"] is False
    assert custody["runtime_sidecar_updated"] is False
    assert custody["human_validated"] is False
    assert custody["product_proof"] is False
    assert custody["answer_quality_scored"] is False
    assert custody["agent_action_authorized"] is False
    assert custody["automatic_action_authorized"] is False


def test_review_source_artifacts_exist() -> None:
    for item in _review()["source_artifacts_reviewed"]:
        artifact = REPO_ROOT / item["artifact_ref"]
        assert artifact.exists(), item["artifact_ref"]


def test_allowed_brief_feed_fields_match_existing_rules_contract() -> None:
    review = _review()
    rules = json.loads(PR139_RULES.read_text())

    allowed = {item["field_name"] for item in review["allowed_brief_feed_fields"]}
    rules_allowed = {
        item["field_name"] for item in rules["allowed_user_facing_fields"]
    }

    assert allowed == EXPECTED_ALLOWED_FIELDS
    assert allowed == rules_allowed

    for item in review["allowed_brief_feed_fields"]:
        assert item["requires_source_refs"] is True
        assert item["requires_uncertainty"] is True
        assert item["requires_privacy_limit"] is True
        assert item["requires_human_review_flag"] is True
        assert item["must_not_be_quality_label"] is True


def test_minimal_supply_fields_are_present_in_pr184_read() -> None:
    review = _review()
    read_fields = {
        item["field_name"]: item for item in _pilot_read()["interpreted_fields"]
    }
    required = {
        item["field_name"]
        for item in review["allowed_brief_feed_fields"]
        if item["required_for_minimal_supply"]
    }

    assert required == {
        "decision_question",
        "revised_direction_or_action_consequence",
        "what_the_final_answer_does_not_prove",
    }
    assert required <= set(read_fields)

    for field_name in required:
        field = read_fields[field_name]
        assert field["source_refs"]
        assert field["uncertainty"]
        assert field["privacy_limit"]
        assert field["must_not_be_used_as_quality_label"] is True


def test_evidence_only_and_blocked_fields_are_explicit() -> None:
    review = _review()

    assert {
        item["field_name"] for item in review["evidence_only_fields"]
    } == EXPECTED_EVIDENCE_ONLY_FIELDS
    assert set(review["blocked_fields"]) >= EXPECTED_BLOCKED_FIELDS


def test_source_uncertainty_privacy_and_non_claim_requirements_are_strict() -> None:
    review = _review()

    assert review["required_source_refs"] == {
        "source_refs_required_for_every_allowed_field": True,
        "source_ref_artifacts_must_be_relative_repo_refs": True,
        "source_status_required": True,
        "locator_required": True,
        "missing_source_refs_status": "blocked_missing_source_refs",
    }
    assert review["required_uncertainty"][
        "uncertainty_required_for_every_allowed_field"
    ] is True
    assert review["required_uncertainty"]["missing_uncertainty_status"] == (
        "blocked_missing_uncertainty"
    )
    privacy = review["privacy_requirements"]
    assert privacy["raw_conversation_text_allowed"] is False
    assert privacy["raw_revised_answer_text_allowed"] is False
    assert privacy["raw_memo_text_allowed"] is False
    assert privacy["provider_text_allowed"] is False
    assert privacy["private_ledgers_allowed"] is False
    assert privacy["local_absolute_paths_allowed"] is False
    assert privacy["privacy_block_status"] == "blocked_privacy_risk"

    non_claims = set(review["non_claim_requirements"])
    assert "not_human_validated" in non_claims
    assert "not_product_proof" in non_claims
    assert "not_answer_quality_score" in non_claims
    assert "not_agent_action_authorization" in non_claims
    assert "not_correctness_proof" in non_claims
    assert "must_not_be_used_as_quality_label" in non_claims


def test_deterministic_allowances_do_not_include_semantic_interpretation() -> None:
    review = _review()

    assert "copy_allowed_field_values_without_expanding_meaning" in review[
        "deterministic_allowances"
    ]
    forbidden = set(review["semantic_interpretation_not_allowed"])
    assert "fill_missing_fields" in forbidden
    assert "judge_whether_advice_was_good" in forbidden
    assert "judge_whether_lolla_improved_the_decision" in forbidden
    assert "write_new_user_facing_brief_prose" in forbidden


def test_accepted_intake_boundary_stays_offline_only() -> None:
    review = _review()
    intake = _pilot_intake()

    assert review["accepted_intake_requirements"]["required_intake_status"] == (
        intake["intake_status"]
    )
    assert intake["accepted_for_downstream"] is True
    assert intake["downstream_allowed"]["can_feed_brief"] is True
    assert intake["downstream_allowed"]["can_update_sidecar"] is False
    assert intake["downstream_allowed"]["can_authorize_agent_action"] is False
    assert intake["downstream_allowed"]["can_be_used_as_quality_label"] is False


def test_decision_gate_selects_adapter_without_runtime_sidecar_work() -> None:
    review = _review()

    assert review["decision_gate"] == (
        "proceed_to_generated_read_brief_supply_adapter"
    )
    assert review["recommended_next_pr"] == (
        "PR186 Decision Work Generated Read Brief Supply Adapter v0"
    )
    non_claims = set(review["non_claims"])
    assert "plan_does_not_generate_briefs" in non_claims
    assert "plan_does_not_enrich_briefs" in non_claims
    assert "plan_does_not_generate_triage" in non_claims
    assert "plan_does_not_approve_resolver_refs" in non_claims
    assert "plan_does_not_update_sidecars" in non_claims
    assert "plan_does_not_call_models" in non_claims


def test_doc_records_findings_and_next_gate() -> None:
    text = DOC_PATH.read_text()

    assert "# Decision Work Generated Read To Brief Supply Plan v0" in text
    assert "proceed_to_generated_read_brief_supply_adapter" in text
    assert "PR186 Decision Work Generated Read Brief Supply Adapter v0" in text
    assert "This is plan, review, and tests only" in text
    assert "does not generate" in text
    assert "Decision Work Brief" in text
    assert "must not" in text
    assert "write new user-facing brief prose" in text


def test_discoverability_docs_reference_pr185() -> None:
    for path in (
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
        PRD_PATH,
        PR184_DOC,
        PR182_DOC,
    ):
        text = path.read_text().lower().replace("generated-read", "generated read")
        assert "generated read" in text, str(path)
        assert "brief supply" in text, str(path)


def test_pr185_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            PR184_DOC,
            PR184_READ,
            PR184_INTAKE,
            PR182_DOC,
            PR139_RULES,
            PR140_DOC,
            PRD_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_pr185_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        REVIEW_PATH,
        PR184_DOC,
        PR184_READ,
        PR184_INTAKE,
        PR182_DOC,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text()
        for marker in FORBIDDEN_STRINGS:
            assert marker not in text, f"{path}:{marker}"
