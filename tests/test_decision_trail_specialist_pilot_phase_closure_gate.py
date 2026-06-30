from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-trail-specialist-pilot-phase-closure-gate-v0.md"
)
REPORT_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-trail-specialist-pilot-phase-closure-gate-v0/report.json"
)
EXPECTED_SCHEMA_VERSION = (
    "lolla.decision_trail_specialist_pilot_phase_closure_gate.v0"
)
EXPECTED_SOURCE_REFS = {
    "docs/conversation-understanding/decision-trail-local-private-specialist-output-pilot-v0.md",
    "reviews/codex-assisted/decision-trail-local-private-specialist-output-pilot-v0/review.json",
    "docs/conversation-understanding/decision-trail-second-one-case-specialist-pilot-v0.md",
    "reviews/codex-assisted/decision-trail-second-one-case-specialist-pilot-v0/review.json",
    "docs/conversation-understanding/decision-trail-specialist-pilot-comparison-gate-v0.md",
    "reviews/codex-assisted/decision-trail-specialist-pilot-comparison-gate-v0/report.json",
    "docs/conversation-understanding/decision-trail-third-one-case-diversity-pilot-v0.md",
    "reviews/codex-assisted/decision-trail-third-one-case-diversity-pilot-v0/review.json",
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
        "codex_assisted_pr103_specialist_pilot_phase_closure_gate"
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
    assert boundary["fourth_pilot_created"] is False
    assert boundary["broad_batch_created"] is False
    assert boundary["fan_in_executed_as_verdict"] is False


def test_sources_are_checked_in_summaries_and_resolve() -> None:
    report = _report()
    scope = report["closure_scope"]

    assert scope["source_mode"] == "checked_in_summary_only"
    assert scope["pilot_count"] == 3
    assert scope["local_private_shadow_review_status"] == "not_run"
    assert scope["new_local_private_packets_generated"] is False
    assert scope["new_specialist_outputs_generated"] is False
    assert scope["fourth_one_case_pilot_generated"] is False
    assert scope["broad_batch_generated"] is False

    refs = {artifact["ref"] for artifact in report["source_artifacts"]}
    assert refs == EXPECTED_SOURCE_REFS
    for artifact in report["source_artifacts"]:
        assert not artifact["ref"].startswith("/")
        assert (REPO_ROOT / artifact["ref"]).exists()
        assert artifact["raw_private_content_included"] is False


def test_compares_exactly_three_expected_pilots() -> None:
    pilots = {entry["slice"]: entry for entry in _report()["compared_pilots"]}

    assert set(pilots) == {"PR97", "PR100", "PR102"}
    assert pilots["PR97"]["case_ref"] == (
        "ceo-remove-founding-cofounder/20260627T093131Z_59d153"
    )
    assert pilots["PR97"]["contract_shape"] == "pre_pr99_specialist_contracts"
    assert pilots["PR97"]["net_read_candidate"] == (
        "local_private_specialist_read_useful_but_unvalidated"
    )

    assert pilots["PR100"]["case_ref"] == (
        "accept-founding-engineer-role/20260627T073034Z_a7c221"
    )
    assert pilots["PR100"]["contract_shape"] == "post_pr99_specialist_contracts"
    assert pilots["PR100"]["net_read_candidate"] == (
        "local_private_specialist_read_partly_useful"
    )
    assert "material_overlap_candidate" in pilots["PR100"][
        "strongest_useful_signal"
    ]

    assert pilots["PR102"]["case_ref"] == (
        "deploy-assisted-intake-routing/20260627T130339Z_4cd3cb"
    )
    assert pilots["PR102"]["decision_family"] == "deployment_controls"
    assert pilots["PR102"]["net_read_candidate"] == (
        "local_private_specialist_read_partly_useful"
    )
    assert "noisy" in pilots["PR102"]["strongest_useful_signal"]


def test_cross_pilot_findings_preserve_limits_and_closure_signal() -> None:
    findings = {entry["finding_id"]: entry for entry in _report()[
        "cross_pilot_findings"
    ]}

    assert "local_private_packets_make_decision_trail_more_concrete" in findings
    assert "pr99_fields_improve_downgrade_pressure" in findings
    assert "vanilla_overlap_is_load_bearing" in findings
    assert "useful_friction_can_mean_less_process" in findings
    assert "three_one_case_pilots_are_enough_for_this_phase" in findings
    assert "not validation" in findings[
        "local_private_packets_make_decision_trail_more_concrete"
    ]["limit"]
    assert "cannot be decided by deterministic string matching" in findings[
        "vanilla_overlap_is_load_bearing"
    ]["limit"]
    assert "momentum evidence" in findings[
        "three_one_case_pilots_are_enough_for_this_phase"
    ]["limit"]


def test_closure_decision_blocks_more_pilots_and_points_to_human_intake() -> None:
    decision = _report()["closure_decision"]

    assert decision["one_case_pilot_phase_status"] == "closed_after_three_pilots"
    assert decision["fourth_one_case_pilot_status"] == "blocked"
    assert decision["broad_batch_status"] == "blocked"
    assert decision["runtime_integration_status"] == "blocked"
    assert decision["contract_patch_status"] == (
        "no_immediate_patch_before_human_review_intake"
    )
    assert decision["human_review_intake_status"] == "recommended_next"
    assert decision["pause_status"] == "acceptable_if_human_review_capacity_unavailable"
    assert decision["recommended_next_slice"] == (
        "PR104 Decision Trail Human Review Intake Packet v0"
    )
    assert any("human-review intake" in item for item in decision[
        "resume_conditions"
    ])
    assert all("runtime integration" not in item or "Do not" in item for item in decision[
        "resume_conditions"
    ])


def test_pr104_recommendation_is_intake_not_another_pilot() -> None:
    recommendation = _report()["pr104_recommendation"]

    assert recommendation["recommended_slice"] == (
        "PR104 Decision Trail Human Review Intake Packet v0"
    )
    assert "without new specialist outputs" in recommendation["purpose"]
    must_include = set(recommendation["must_include"])
    assert "reviewer_correction_fields" in must_include
    assert "candidate_delta_and_vanilla_overlap_notes" in must_include

    must_not = set(recommendation["must_not_do"])
    assert "run_lolla" in must_not
    assert "invoke_lolla_skill" in must_not
    assert "read_new_local_private_packet_content" in must_not
    assert "mutate_archives" in must_not
    assert "create_a_fourth_one_case_pilot" in must_not
    assert "create_a_broad_batch" in must_not
    assert "score_answer_quality" in must_not
    assert "create_automatic_labels" in must_not
    assert "authorize_agent_action" in must_not


def test_non_claims_are_explicit() -> None:
    non_claims = " ".join(_report()["non_claims"])

    assert "not human review" in non_claims
    assert "not ground truth" in non_claims
    assert "not judge calibration" in non_claims
    assert "not product proof" in non_claims
    assert "not answer-quality measurement" in non_claims
    assert "not an automatic label" in non_claims
    assert "not agent action authorization" in non_claims
    assert "does not show that any revised answer was good advice" in non_claims


def test_no_private_markers_local_paths_or_authority_fields() -> None:
    combined_text = "\n".join(
        [
            REPORT_PATH.read_text(encoding="utf-8"),
            DOC_PATH.read_text(encoding="utf-8"),
        ]
    )

    for marker in FORBIDDEN_MARKERS:
        assert marker not in combined_text
    assert not FORBIDDEN_FIELD_NAMES.intersection(_walk_keys(_report()))


def test_pr78_lint_accepts_pr103_report_artifacts() -> None:
    report = lint_product_delta_paths([DOC_PATH, REPORT_PATH])

    assert report["summary"]["blocking_error_count"] == 0
    assert report["summary"]["warning_count"] == 0
    assert report["summary"]["info_count"] == 0
