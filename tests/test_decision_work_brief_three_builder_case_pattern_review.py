from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-three-builder-case-pattern-review-v0/review.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-three-builder-case-pattern-review-v0.md"
)
BUILDER_OUTPUTS = {
    "launch-public-enterprise-beta": REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-builder-enriched-launch-public-enterprise-beta-v0.md",
    "deploy-assisted-intake-routing": REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-builder-enriched-deploy-assisted-intake-routing-v0.md",
    "ceo-remove-founding-cofounder": REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-builder-enriched-ceo-remove-founding-cofounder-v0.md",
}
SCHEMA_VERSION = "lolla.decision_work_brief_three_builder_case_pattern_review.v0"
EXPECTED_CASES = set(BUILDER_OUTPUTS)
ALLOWED_DECISION_GATES = {
    "proceed_to_human_review_intake_plan",
    "proceed_to_fourth_builder_case",
    "patch_builder_rules_again",
    "run_more_local_private_adequacy_checks",
    "package_pr146_pr149",
    "pause_until_human_review",
    "stop_and_simplify",
}
REQUIRED_FALSE_FIELDS = {
    "human_validated",
    "product_proof",
    "runtime_invoked",
    "skill_invoked",
    "archive_mutated",
    "answer_quality_scored",
    "agent_action_authorized",
}
REQUIRED_CUSTODY_FALSE_FIELDS = REQUIRED_FALSE_FIELDS | {
    "raw_private_content_checked_in",
    "provider_text_checked_in",
    "local_absolute_paths_checked_in",
    "new_lolla_run_created",
    "new_interpretation_read_created",
    "builder_patched",
    "runtime_integration_implemented",
}
CASE_REVIEW_FIELDS = {
    "case_id",
    "builder_output_ref",
    "interpretation_read_ref",
    "source_review_ref",
    "decision_family",
    "action_consequence_readability",
    "uncertainty_preservation",
    "source_limit_preservation",
    "non_claim_preservation",
    "evidence_only_field_exclusion",
    "template_language_risk",
    "overclaim_risk",
    "human_review_need",
    "notes",
}
PRIVACY_MARKERS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)
FORBIDDEN_TRUE_CLAIMS = (
    "Product proof: yes",
    "Human validation: yes",
    "Answer-quality scoring: yes",
    "Agent action authorization: yes",
    "agent_action_authorized" + ": true",
    "product_proof" + ": true",
    "human_validated" + ": true",
)
EVIDENCE_ONLY_FIELD_NAMES = {
    "lost_value",
    "noisy_friction",
    "live_options",
    "abandoned_or_rejected_options",
}


def _review() -> dict[str, Any]:
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


def _collect_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        strings: list[str] = []
        for item in value:
            strings.extend(_collect_strings(item))
        return strings
    if isinstance(value, dict):
        strings = []
        for item in value.values():
            strings.extend(_collect_strings(item))
        return strings
    return []


def _collect_repo_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key.endswith("_ref") or key.endswith("_refs") or key == "ref":
                refs.update(_collect_strings(child))
            refs.update(_collect_repo_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.update(_collect_repo_refs(child))
    return {ref for ref in refs if ref.startswith(("docs/", "reviews/", "tests/"))}


def _main_enrichment_section(markdown: str) -> str:
    start = markdown.index("## What the interpretation adds")
    end = markdown.index("## What still might be wrong")
    return markdown[start:end]


def test_review_schema_and_conservative_metadata() -> None:
    review = _review()

    assert review["schema_version"] == SCHEMA_VERSION
    assert review["review_mode"] == "offline_three_builder_case_pattern_review"
    assert review["model_calls"] == 0
    for field in REQUIRED_FALSE_FIELDS:
        assert review[field] is False

    custody = review["custody_flags"]
    assert custody["model_calls"] == 0
    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False


def test_all_three_builder_outputs_are_referenced_and_exist() -> None:
    review = _review()
    source_outputs = review["source_builder_outputs"]

    assert {item["case_id"] for item in source_outputs} == EXPECTED_CASES
    for item in source_outputs:
        assert (REPO_ROOT / item["builder_output_ref"]) == BUILDER_OUTPUTS[item["case_id"]]
        assert (REPO_ROOT / item["builder_output_ref"]).exists()
        assert (REPO_ROOT / item["interpretation_read_ref"]).exists()
        assert (REPO_ROOT / item["source_review_ref"]).exists()

    for ref in _collect_repo_refs(review):
        assert (REPO_ROOT / ref).exists(), ref


def test_case_reviews_include_required_fields_for_each_case() -> None:
    case_reviews = _review()["case_reviews"]

    assert {item["case_id"] for item in case_reviews} == EXPECTED_CASES
    for item in case_reviews:
        assert CASE_REVIEW_FIELDS <= set(item)
        assert item["action_consequence_readability"]
        assert item["uncertainty_preservation"]
        assert item["source_limit_preservation"]
        assert item["non_claim_preservation"]
        assert item["evidence_only_field_exclusion"]
        assert item["template_language_risk"]
        assert item["overclaim_risk"]
        assert item["human_review_need"] == "required_before_user_facing_validation"


def test_builder_outputs_preserve_sections_and_non_claims() -> None:
    for path in BUILDER_OUTPUTS.values():
        markdown = path.read_text(encoding="utf-8")

        assert markdown.count("## What the interpretation adds") == 1
        assert "## What this does not prove" in markdown
        assert "## Evidence and limits" in markdown
        assert "Product proof: no" in markdown
        assert "Human validation: no" in markdown
        assert "Answer-quality scoring: no" in markdown
        assert "Agent action authorization: no" in markdown
        assert "does not prove Lolla improved the decision" in markdown


def test_builder_outputs_keep_evidence_only_fields_out_of_main_body() -> None:
    for path in BUILDER_OUTPUTS.values():
        main_body = _main_enrichment_section(path.read_text(encoding="utf-8"))

        for field_name in EVIDENCE_ONLY_FIELD_NAMES:
            assert field_name not in main_body


def test_pattern_findings_and_decision_gate() -> None:
    review = _review()

    assert review["cross_case_pattern"]["pattern_status"] == (
        "stable_enough_for_human_review_intake_plan"
    )
    assert review["readability_pattern"]["all_three_readable_enough"] is True
    assert review["action_consequence_pattern"]["all_three_preserve_action_consequence"] is True
    assert review["uncertainty_and_source_limit_pattern"]["uncertainty_visible_in_all_three"] is True
    assert review["overclaim_risk_pattern"]["product_proof_claimed"] is False
    assert review["builder_rule_stability_read"]["rules_stable_enough_for_next_step"] is True
    assert review["builder_rule_stability_read"]["human_review_intake_plan_recommended_now"] is True
    assert review["excluded_fields_check"]["lost_value_kept_evidence_only"] is True
    assert review["decision_gate"] in ALLOWED_DECISION_GATES
    assert review["decision_gate"] == "proceed_to_human_review_intake_plan"
    assert review["recommended_next_pr"] == (
        "PR150 Decision Work Brief Human Review Intake Plan v0"
    )


def test_no_private_markers_or_authority_claims() -> None:
    text = (
        REVIEW_PATH.read_text(encoding="utf-8")
        + "\n"
        + DOC_PATH.read_text(encoding="utf-8")
        + "\n"
        + "\n".join(path.read_text(encoding="utf-8") for path in BUILDER_OUTPUTS.values())
    )

    for marker in PRIVACY_MARKERS:
        assert marker not in text
    for claim in FORBIDDEN_TRUE_CLAIMS:
        assert claim not in text


def test_product_delta_boundary_lint_passes_for_pr149_artifacts() -> None:
    report = lint_product_delta_paths([DOC_PATH, REVIEW_PATH, *BUILDER_OUTPUTS.values()])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def test_skill_files_remain_untouched() -> None:
    status = subprocess.check_output(
        ["git", "status", "--short", "--", "SKILL.md", "scripts/skill"],
        cwd=REPO_ROOT,
        text=True,
    )

    assert status.strip() == ""
