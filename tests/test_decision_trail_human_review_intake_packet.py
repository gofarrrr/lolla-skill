from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-trail-human-review-intake-packet-v0.md"
)
INTAKE_PATH = (
    REPO_ROOT
    / "reviews/human/decision-trail-human-review-intake-packet-v0/intake.json"
)
EXPECTED_SCHEMA_VERSION = "lolla.decision_trail_human_review_intake_packet.v0"
EXPECTED_CASES = {
    "PR97": "ceo-remove-founding-cofounder/20260627T093131Z_59d153",
    "PR100": "accept-founding-engineer-role/20260627T073034Z_a7c221",
    "PR102": "deploy-assisted-intake-routing/20260627T130339Z_4cd3cb",
}
EXPECTED_SOURCE_REFS = {
    "docs/conversation-understanding/decision-trail-local-private-specialist-output-pilot-v0.md",
    "reviews/codex-assisted/decision-trail-local-private-specialist-output-pilot-v0/review.json",
    "docs/conversation-understanding/decision-trail-second-one-case-specialist-pilot-v0.md",
    "reviews/codex-assisted/decision-trail-second-one-case-specialist-pilot-v0/review.json",
    "docs/conversation-understanding/decision-trail-third-one-case-diversity-pilot-v0.md",
    "reviews/codex-assisted/decision-trail-third-one-case-diversity-pilot-v0/review.json",
    "docs/conversation-understanding/decision-trail-specialist-pilot-phase-closure-gate-v0.md",
    "reviews/codex-assisted/decision-trail-specialist-pilot-phase-closure-gate-v0/report.json",
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
    "approval",
    "certified",
    "pass",
    "passed",
    "pass_fail",
    "rating",
    "score",
}


def _intake() -> dict[str, Any]:
    return json.loads(INTAKE_PATH.read_text(encoding="utf-8"))


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


def test_intake_shape_and_boundary_metadata() -> None:
    intake = _intake()

    assert intake["schema_version"] == EXPECTED_SCHEMA_VERSION
    assert intake["intake_mode"] == "future_human_review_queue_not_filled"
    boundary = intake["boundary"]
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
    assert boundary["human_fields_filled"] is False


def test_scope_sources_resolve_and_are_checked_in_summaries() -> None:
    intake = _intake()
    scope = intake["scope"]

    assert scope["source_mode"] == "checked_in_summary_only"
    assert scope["case_count"] == 3
    assert scope["human_review_state"] == "blank_intake_not_filled"
    assert "does not validate" in scope["evidence_limit"]

    refs = {artifact["ref"] for artifact in intake["source_artifacts"]}
    assert refs == EXPECTED_SOURCE_REFS
    for artifact in intake["source_artifacts"]:
        assert not artifact["ref"].startswith("/")
        assert (REPO_ROOT / artifact["ref"]).exists()
        assert artifact["raw_private_content_included"] is False


def test_packet_contains_exact_three_prior_pilots() -> None:
    cases = {case["slice"]: case for case in _intake()["case_intake"]}

    assert set(cases) == set(EXPECTED_CASES)
    for slice_name, case_ref in EXPECTED_CASES.items():
        assert cases[slice_name]["case_ref"] == case_ref
        assert cases[slice_name]["candidate_read_summary"][
            "candidate_net_read"
        ].startswith("local_private_specialist_read_")
        assert cases[slice_name]["candidate_read_summary"][
            "candidate_useful_signal"
        ]
        assert cases[slice_name]["candidate_read_summary"]["candidate_limit"]
        assert cases[slice_name]["candidate_read_summary"][
            "vanilla_overlap_question"
        ]
        assert cases[slice_name]["candidate_read_summary"]["lost_value_question"]
        assert cases[slice_name]["minimum_human_questions"]


def test_human_correction_fields_are_blank_and_not_filled() -> None:
    for case in _intake()["case_intake"]:
        fields = case["future_human_correction_fields"]
        assert fields["human_fields_filled"] is False
        for key, value in fields.items():
            if key == "human_fields_filled":
                continue
            assert value == "", key


def test_non_claims_are_preserved_at_case_and_packet_level() -> None:
    intake = _intake()
    packet_non_claims = " ".join(intake["non_claims"])

    for fragment in (
        "not completed human review",
        "not ground truth",
        "not judge calibration",
        "not product proof",
        "not answer-quality measurement",
        "not an automatic label",
        "not agent action authorization",
    ):
        assert fragment in packet_non_claims

    for case in intake["case_intake"]:
        non_claims = " ".join(case["non_claims"])
        assert "not human review" in non_claims
        assert "not ground truth" in non_claims
        assert "not product proof" in non_claims
        assert "not answer-quality measurement" in non_claims
        assert "not automatic label" in non_claims
        assert "not agent action authorization" in non_claims


def test_next_state_pauses_until_human_review_not_more_codex_pilots() -> None:
    next_state = _intake()["next_state"]

    assert next_state["recommended_status"] == (
        "pause_until_human_review_capacity_returns"
    )
    assert "human_fields_are_filled" in next_state["next_numbered_slice_policy"]
    do_not_start = set(next_state["do_not_start"])
    assert "fourth_one_case_specialist_pilot" in do_not_start
    assert "broad_specialist_output_batch" in do_not_start
    assert "runtime_integration" in do_not_start
    assert "automatic_decision_trail_generation" in do_not_start
    assert "answer_quality_judge" in do_not_start
    assert "agent_action_authorization" in do_not_start


def test_no_private_markers_local_paths_or_authority_fields() -> None:
    combined_text = "\n".join(
        [
            INTAKE_PATH.read_text(encoding="utf-8"),
            DOC_PATH.read_text(encoding="utf-8"),
        ]
    )

    for marker in FORBIDDEN_MARKERS:
        assert marker not in combined_text
    assert not FORBIDDEN_FIELD_NAMES.intersection(_walk_keys(_intake()))


def test_pr78_lint_accepts_pr104_intake_artifacts() -> None:
    report = lint_product_delta_paths([DOC_PATH, INTAKE_PATH])

    assert report["summary"]["blocking_error_count"] == 0
    assert report["summary"]["warning_count"] == 0
    assert report["summary"]["info_count"] == 0
