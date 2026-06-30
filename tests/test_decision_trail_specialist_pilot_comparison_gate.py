from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-trail-specialist-pilot-comparison-gate-v0.md"
)
REPORT_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-trail-specialist-pilot-comparison-gate-v0/report.json"
)
EXPECTED_SCHEMA_VERSION = (
    "lolla.decision_trail_specialist_pilot_comparison_gate.v0"
)
EXPECTED_SOURCE_REFS = {
    "docs/conversation-understanding/decision-trail-local-private-specialist-output-pilot-v0.md",
    "reviews/codex-assisted/decision-trail-local-private-specialist-output-pilot-v0/review.json",
    "docs/conversation-understanding/decision-trail-specialist-output-pilot-review-v0.md",
    "reviews/codex-assisted/decision-trail-specialist-output-pilot-review-v0/review.json",
    "docs/conversation-understanding/decision-trail-specialist-contract-and-packet-patch-v0.md",
    "docs/conversation-understanding/decision-trail-second-one-case-specialist-pilot-v0.md",
    "reviews/codex-assisted/decision-trail-second-one-case-specialist-pilot-v0/review.json",
}
FORBIDDEN_MARKERS = (
    "/" + "Users/",
    "SEC" + "RET",
    "raw" + "_message_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT " + "REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)
FORBIDDEN_FIELD_NAMES = {
    "safe_for_agent_use",
    "quality" + "_score",
    "answer_quality" + "_score",
    "improvement" + "_score",
    "judge" + "_score",
    "winner",
    "approved",
    "certified",
    "pass_fail",
}


def _report() -> dict[str, Any]:
    return json.loads(REPORT_PATH.read_text(encoding="utf-8"))


def _walk_keys(value: Any) -> list[str]:
    keys: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            keys.append(str(key))
            keys.extend(_walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.extend(_walk_keys(child))
    return keys


def test_report_shape_and_boundary_metadata() -> None:
    report = _report()

    assert report["schema_version"] == EXPECTED_SCHEMA_VERSION
    assert report["review_mode"] == (
        "codex_assisted_pr101_specialist_pilot_comparison_gate"
    )
    boundary = report["boundary"]
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
    assert boundary["automatic_labels_created"] is False
    assert boundary["raw_private_content_included"] is False
    assert boundary["new_specialist_outputs_created"] is False
    assert boundary["local_private_packet_content_read"] is False
    assert boundary["fan_in_executed_as_verdict"] is False


def test_sources_are_checked_in_summaries_and_resolve() -> None:
    report = _report()
    scope = report["comparison_scope"]

    assert scope["source_mode"] == "checked_in_summary_only"
    assert scope["pilot_count"] == 2
    assert scope["local_private_shadow_review_status"] == "not_run"
    assert scope["new_local_private_packets_generated"] is False
    assert scope["new_specialist_outputs_generated"] is False

    refs = {artifact["ref"] for artifact in report["source_artifacts"]}
    assert refs == EXPECTED_SOURCE_REFS
    for artifact in report["source_artifacts"]:
        assert not artifact["ref"].startswith("/")
        assert (REPO_ROOT / artifact["ref"]).exists()
        assert artifact["raw_private_content_included"] is False


def test_compares_pr97_and_pr100_with_expected_directional_difference() -> None:
    pilots = {entry["slice"]: entry for entry in _report()["compared_pilots"]}

    assert set(pilots) == {"PR97", "PR100"}
    assert pilots["PR97"]["contract_shape"] == "pre_pr99_specialist_contracts"
    assert pilots["PR97"]["vanilla_overlap_handling"] == "not_first_class"
    assert pilots["PR97"]["net_read_candidate"] == (
        "local_private_specialist_read_useful_but_unvalidated"
    )

    assert pilots["PR100"]["contract_shape"] == "post_pr99_specialist_contracts"
    assert pilots["PR100"]["vanilla_overlap_handling"] == (
        "first_class_and_downgrading"
    )
    assert pilots["PR100"]["net_read_candidate"] == (
        "local_private_specialist_read_partly_useful"
    )
    assert "material_overlap_candidate" in pilots["PR100"][
        "strongest_useful_signal"
    ]


def test_findings_preserve_downgrade_pressure_and_limits() -> None:
    findings = {entry["finding_id"]: entry for entry in _report()["comparison_findings"]}

    assert "pr99_fields_improved_downgrade_pressure" in findings
    assert "vanilla_overlap_is_load_bearing" in findings
    assert "two_pilots_are_not_broad_batch_evidence" in findings
    assert "less positive" in findings[
        "pr99_fields_improved_downgrade_pressure"
    ]["read"]
    assert "cannot be deterministically inferred" in findings[
        "vanilla_overlap_is_load_bearing"
    ]["limit"]


def test_gate_decision_allows_only_diversity_targeted_third_pilot() -> None:
    decision = _report()["gate_decision"]

    assert decision["broad_batch_status"] == "not_ready"
    assert decision["third_one_case_pilot_status"] == (
        "allowed_if_diversity_targeted"
    )
    assert decision["runtime_status"] == "not_allowed"
    assert decision["human_review_status"] == "still_required_for_product_claim"
    assert decision["recommended_next_slice"] == (
        "PR102 Decision Trail Third One-Case Diversity Pilot v0"
    )
    assert any("If no safe completed run" in item for item in decision[
        "stop_or_simplify_conditions"
    ])

    recommendation = _report()["pr102_recommendation"]
    assert recommendation["recommended_slice"] == (
        "PR102 Decision Trail Third One-Case Diversity Pilot v0"
    )
    assert recommendation["preferred_case_shape"] == (
        "deployment_controls_or_enterprise_beta_or_pricing_or_another_non_cofounder_non_career_completed_run"
    )
    must_not = set(recommendation["must_not_do"])
    assert "run_lolla" in must_not
    assert "invoke_lolla_skill" in must_not
    assert "mutate_archives" in must_not
    assert "score_answer_quality" in must_not
    assert "create_automatic_labels" in must_not
    assert "authorize_agent_action" in must_not
    assert "turn_pr102_into_a_broad_batch" in must_not


def test_non_claims_are_explicit() -> None:
    non_claims = " ".join(_report()["non_claims"])

    assert "not human review" in non_claims
    assert "not ground truth" in non_claims
    assert "not judge calibration" in non_claims
    assert "not product proof" in non_claims
    assert "not answer-quality measurement" in non_claims
    assert "not an automatic label" in non_claims
    assert "not agent action authorization" in non_claims


def test_no_private_markers_local_paths_or_authority_fields() -> None:
    combined_text = "\n".join(
        [
            REPORT_PATH.read_text(encoding="utf-8"),
            DOC_PATH.read_text(encoding="utf-8"),
        ]
    )

    for marker in FORBIDDEN_MARKERS:
        assert marker not in combined_text
    assert "/tmp/" not in combined_text
    assert not FORBIDDEN_FIELD_NAMES.intersection(_walk_keys(_report()))


def test_pr78_lint_accepts_pr101_report_artifacts() -> None:
    report = lint_product_delta_paths([DOC_PATH, REPORT_PATH])

    assert report["summary"]["blocking_error_count"] == 0
    assert report["summary"]["warning_count"] == 0
    assert report["summary"]["info_count"] == 0
