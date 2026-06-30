from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-trail-fixture-review-v0/review.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-trail-export-fixture-review-v0.md"
)

EXPECTED_SCHEMA_VERSION = "lolla.decision_trail_fixture_review.v0"
CLASSIFICATION_VALUES = {
    "clear_and_populated",
    "clear_but_missing",
    "confusing",
    "overclaim_risk",
    "requires_llm_interpretation",
    "requires_human_review",
    "not_applicable",
}
REQUIRED_BEHAVIORAL_FIELDS = {
    "what_changed_answerable",
    "evidence_support_answerable",
    "missingness_answerable",
    "non_claims_answerable",
    "more_careful_or_more_impressed",
}
FORBIDDEN_AUTHORITY_FIELDS = {
    "quality_score",
    "answer_quality_score",
    "improvement_score",
    "judge_score",
    "winner",
    "approved",
    "certified",
    "pass_fail",
    "safe" + "_for_" + "agent" + "_use",
}
PRIVACY_MARKERS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw" + "_message_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _review() -> dict[str, Any]:
    return _json(REVIEW_PATH)


def _walk_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key))
            keys.update(_walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_walk_keys(child))
    return keys


def _walk_strings(value: Any) -> list[str]:
    strings: list[str] = []
    if isinstance(value, str):
        strings.append(value)
    elif isinstance(value, dict):
        for child in value.values():
            strings.extend(_walk_strings(child))
    elif isinstance(value, list):
        for child in value:
            strings.extend(_walk_strings(child))
    return strings


def _classification_values(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        if "classification" in value:
            found.append(value["classification"])
        for child in value.values():
            found.extend(_classification_values(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(_classification_values(child))
    return found


def test_review_json_parses_and_has_expected_version() -> None:
    payload = _review()

    assert payload["schema_version"] == EXPECTED_SCHEMA_VERSION
    assert payload["review_mode"] == "checked_in_safe_fixture_review"
    assert payload["slice"] == "PR88 Decision Trail Fixture Review v0"


def test_boundary_metadata_is_conservative() -> None:
    boundary = _review()["boundary"]

    assert boundary["human_validated"] is False
    assert boundary["ground_truth"] is False
    assert boundary["judge_calibration_eligible"] is False
    assert boundary["product_proof"] is False
    assert boundary["answer_quality_scored"] is False
    assert boundary["agent_action_authorized"] is False
    assert boundary["model_calls"] == 0
    assert boundary["archive_mutated"] is False
    assert boundary["runtime_invoked"] is False
    assert boundary["skill_invoked"] is False
    assert boundary["raw_private_content_included"] is False
    assert boundary["automatic_labels_created"] is False


def test_evidence_scope_records_no_local_private_shadow_review() -> None:
    payload = _review()
    shadow = payload["local_private_shadow_review_status"]

    assert payload["evidence_scope"] == "safe_fixture_only"
    assert shadow["status"] == "not_run"
    assert "safe-fixture-only" in shadow["pr89_implication"]


def test_source_reports_are_explicitly_not_checked_in_or_resolve() -> None:
    for source in _review()["source_reports"]:
        if source["checked_in"]:
            assert (REPO_ROOT / source["report_ref"]).exists()
        else:
            assert source["report_ref"] == "temporary_pr87_cli_output_not_checked_in"
            assert source["reason_not_checked_in"]


def test_report_reviews_include_required_behavioral_fields() -> None:
    for report in _review()["report_reviews"]:
        assert set(report["behavioral_usefulness"]) == REQUIRED_BEHAVIORAL_FIELDS
        assert report["report_readability"]
        assert report["artifact_custody_read"]
        assert report["semantic_interpretation_adequacy_read"]
        assert report["product_delta_usefulness_read"] == "not_reviewed"
        assert report["human_validation_read"] == "not_human_validated"


def test_classification_values_use_pr88_vocabulary() -> None:
    classifications = _classification_values(_review())

    assert classifications
    assert set(classifications) <= CLASSIFICATION_VALUES
    assert "requires_llm_interpretation" in classifications
    assert "overclaim_risk" in classifications


def test_structured_fixture_preserves_interpretation_gaps() -> None:
    structured = {
        item["report_id"]: item for item in _review()["report_reviews"]
    }["structured_fixture_report"]

    assert structured["field_population_summary"]["clear_and_populated"] == 6
    assert structured["field_population_summary"]["requires_llm_interpretation"] == 8
    assert {item["section"] for item in structured["interpretation_needed_sections"]} == {
        "vanilla_likely_next_action",
        "revised_likely_next_action",
        "option_map",
        "stakeholders",
        "values_or_priorities",
        "assistant_influence",
        "useful_noisy_friction",
        "lost_value",
    }


def test_sparse_fixture_does_not_create_semantic_claims() -> None:
    sparse = {
        item["report_id"]: item for item in _review()["report_reviews"]
    }["sparse_missing_fixture_report"]

    assert sparse["field_population_summary"]["clear_and_populated"] == 0
    assert sparse["field_population_summary"]["clear_but_missing"] >= 4
    assert sparse["behavioral_usefulness"]["what_changed_answerable"]["answer"] == "no"
    assert sparse["overtrust_risk_sections"] == []


def test_positive_usefulness_notes_have_human_validation_caveats() -> None:
    notes = _review()["aggregate_observations"]["positive_usefulness_notes"]

    assert notes
    for note in notes:
        assert note["note"]
        assert "human validated" in note["human_validation_caveat"]


def test_no_forbidden_authority_field_names_exist() -> None:
    keys = _walk_keys(_review())

    assert not (FORBIDDEN_AUTHORITY_FIELDS & keys)


def test_no_privacy_markers_in_review_or_doc() -> None:
    combined = "\n".join(_walk_strings(_review()))
    combined += "\n" + DOC_PATH.read_text(encoding="utf-8")

    for marker in PRIVACY_MARKERS:
        assert marker not in combined


def test_pr78_boundary_lint_passes_for_pr88_artifacts() -> None:
    report = lint_product_delta_paths([DOC_PATH, REVIEW_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
