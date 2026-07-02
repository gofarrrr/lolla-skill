from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-third-builder-case-output-v0/review.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-third-builder-case-output-v0.md"
)
BUILDER_OUTPUT_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-builder-enriched-ceo-remove-founding-cofounder-v0.md"
)
SOURCE_BRIEF_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md"
)
INTERPRETATION_READ_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-conversation-interpretation-third-tiny-offline-read-v0/read.json"
)
RULES_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-enrichment-rules-contract-v0.json"
)
SCHEMA_VERSION = "lolla.decision_work_brief_third_builder_case_output.v0"
ALLOWED_DECISION_GATES = {
    "proceed_to_three_builder_case_pattern_review",
    "patch_builder_rules_again",
    "run_more_local_private_adequacy_checks",
    "proceed_to_human_review_intake",
    "pause_until_human_review",
    "stop_and_simplify",
}
REQUIRED_FALSE_FIELDS = {
    "human_validated",
    "product_proof",
    "answer_quality_scored",
    "agent_action_authorized",
    "archive_mutated",
    "runtime_invoked",
    "skill_invoked",
}
REQUIRED_CUSTODY_FALSE_FIELDS = REQUIRED_FALSE_FIELDS | {
    "raw_private_content_checked_in",
    "provider_text_checked_in",
    "local_absolute_paths_checked_in",
    "new_lolla_run_created",
    "new_interpretation_read_created",
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
FORBIDDEN_AUTHORITY_WORDS = (
    "approved",
    "certified",
    "winner",
    "quality score:",
    "improvement score:",
)


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
            if key.endswith("_ref") or key.endswith("_refs"):
                refs.update(_collect_strings(child))
            refs.update(_collect_repo_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.update(_collect_repo_refs(child))
    return {ref for ref in refs if ref.startswith(("docs/", "reviews/", "tests/", "engine/", "scripts/"))}


def _builder_output() -> str:
    return BUILDER_OUTPUT_PATH.read_text(encoding="utf-8")


def test_review_schema_and_conservative_metadata() -> None:
    review = _review()

    assert review["schema_version"] == SCHEMA_VERSION
    assert review["review_mode"] == "offline_deterministic_builder_output_review"
    assert review["case_id"] == "ceo-remove-founding-cofounder"
    assert review["decision_family"] == "founder_governance_or_authority_transition"
    for field in REQUIRED_FALSE_FIELDS:
        assert review[field] is False
    assert review["model_calls"] == 0

    custody = review["custody_flags"]
    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False
    assert custody["model_calls"] == 0
    assert custody["builder_invoked"] is True
    assert custody["builder_output_created"] is True


def test_source_refs_and_builder_output_exist() -> None:
    review = _review()

    assert (REPO_ROOT / review["source_brief_ref"]) == SOURCE_BRIEF_PATH
    assert (REPO_ROOT / review["interpretation_read_ref"]) == INTERPRETATION_READ_PATH
    assert (REPO_ROOT / review["rules_contract_ref"]) == RULES_PATH
    assert (REPO_ROOT / review["builder_output_ref"]) == BUILDER_OUTPUT_PATH
    for ref in _collect_repo_refs(review):
        assert (REPO_ROOT / ref).exists(), ref

    assert SOURCE_BRIEF_PATH.exists()
    assert INTERPRETATION_READ_PATH.exists()
    assert RULES_PATH.exists()
    assert BUILDER_OUTPUT_PATH.exists()
    assert review["builder_output_created"] is True
    assert review["builder_output_status"] == "created_checked_in_safe_deterministic_builder_output"


def test_builder_output_preserves_required_sections() -> None:
    markdown = _builder_output()

    assert markdown.count("## What the interpretation adds") == 1
    assert "## What this does not prove" in markdown
    assert "## Evidence and limits" in markdown
    assert "### Interpretation enrichment limits" in markdown
    assert "### Verification state" in markdown


def test_builder_output_contains_cofounder_action_consequence_and_uncertainty() -> None:
    markdown = _builder_output()

    assert "align with the COO" in markdown
    assert "move product execution authority first" in markdown
    assert "narrow the cofounder's transition role" in markdown
    assert "precommit to escalation triggers" in markdown
    assert "The starting point remains uncertain" in markdown
    assert "Checked-in-safe sources are compressed" in markdown
    assert "Human review required" in markdown
    assert "legal, equity, board, or employment constraints" in markdown


def test_builder_output_preserves_non_claims_and_excludes_evidence_only_main_body_fields() -> None:
    markdown = _builder_output()
    main_section = markdown[
        markdown.index("## What the interpretation adds") : markdown.index("## What still might be wrong")
    ]

    assert "Product proof: no" in markdown
    assert "Human validation: no" in markdown
    assert "Answer-quality scoring: no" in markdown
    assert "Agent action authorization: no" in markdown
    assert "does not prove Lolla improved the decision" in markdown
    assert "lost_value" not in main_section
    assert "noisy_friction" not in main_section
    assert "live_options" not in main_section
    assert "abandoned_or_rejected_options" not in main_section


def test_builder_output_has_no_private_markers_or_authority_claims() -> None:
    text = (
        _builder_output()
        + "\n"
        + REVIEW_PATH.read_text(encoding="utf-8")
        + "\n"
        + DOC_PATH.read_text(encoding="utf-8")
    )

    for marker in PRIVACY_MARKERS:
        assert marker not in text
    for claim in FORBIDDEN_TRUE_CLAIMS:
        assert claim not in text
    lowered = text.lower()
    for word in FORBIDDEN_AUTHORITY_WORDS:
        assert word not in lowered


def test_decision_gate_and_review_findings() -> None:
    review = _review()

    assert review["decision_gate"] in ALLOWED_DECISION_GATES
    assert review["decision_gate"] == "proceed_to_three_builder_case_pattern_review"
    assert review["recommended_next_pr"] == (
        "PR149 Decision Work Brief Three Builder Case Pattern Review v0"
    )
    assert review["readability_read"]["status"] == "readable_enough_for_pattern_review"
    assert review["uncertainty_read"]["status"] == "uncertainty_preserved"
    assert review["overclaim_read"]["status"] == "non_claims_preserved"
    assert review["field_boundary_read"]["status"] == "rules_boundary_preserved"
    assert review["source_depth_read"]["runtime_integration_recommended"] is False
    assert review["source_depth_read"]["human_review_still_required"] is True


def test_comparison_to_prior_builder_cases_includes_all_three() -> None:
    comparison = _review()["comparison_to_prior_builder_cases"]

    assert set(comparison) == {
        "launch_public_enterprise_beta",
        "deploy_assisted_intake_routing",
        "ceo_remove_founding_cofounder",
    }
    for item in comparison.values():
        assert (REPO_ROOT / item["builder_output_ref"]).exists()
        assert item["readability_pattern"]
        assert item["relative_note"]


def test_product_delta_boundary_lint_passes_for_pr148_artifacts() -> None:
    report = lint_product_delta_paths([DOC_PATH, REVIEW_PATH, BUILDER_OUTPUT_PATH])

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
