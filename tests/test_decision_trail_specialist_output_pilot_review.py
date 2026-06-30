from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-trail-specialist-output-pilot-review-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-trail-specialist-output-pilot-review-v0/review.json"
)
PR97_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-trail-local-private-specialist-output-pilot-v0/review.json"
)
EXPECTED_SCHEMA_VERSION = "lolla.decision_trail_specialist_output_pilot_review.v0"
SPECIALIST_ROLES = {
    "conversation_shape_reader",
    "likely_action_reader",
    "friction_lost_value_reader",
    "conservative_fan_in_reader",
}
REQUIRED_CONTRACT_REVISIONS = {
    "likely_action_vanilla_overlap_read",
    "friction_lost_value_severity_read",
    "conversation_shape_assistant_influence_source_status",
    "all_roles_source_scope_and_truncation_impact",
    "fan_in_downgrade_triggers",
}
REQUIRED_PACKET_REVISIONS = {
    "packet_artifact_scope_summary",
    "packet_truncation_summary",
    "local_private_retention_status",
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


def _review() -> dict[str, Any]:
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


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


def test_review_shape_and_boundary_metadata() -> None:
    review = _review()

    assert review["schema_version"] == EXPECTED_SCHEMA_VERSION
    assert review["review_mode"] == "codex_assisted_pr97_contract_revision_gate"

    boundary = review["boundary"]
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
    assert boundary["fan_in_executed_as_verdict"] is False


def test_source_artifacts_are_checked_in_safe_and_resolve() -> None:
    review = _review()

    refs = [artifact["ref"] for artifact in review["source_artifacts"]]
    assert str(PR97_REVIEW_PATH.relative_to(REPO_ROOT)) in refs
    for artifact in review["source_artifacts"]:
        ref = artifact["ref"]
        assert not ref.startswith("/")
        assert (REPO_ROOT / ref).exists()
        assert artifact["raw_private_content_included"] is False

    summary = review["source_review_summary"]
    assert summary["pilot_case_count"] == 1
    assert summary["local_private_packet_checked_in"] is False
    assert summary["private_packet_deleted_after_review"] is True
    assert summary["review_uses_checked_in_summaries_only"] is True


def test_gate_decision_blocks_broadening_until_patch() -> None:
    decision = _review()["gate_decision"]

    assert decision["broad_batch_status"] == "blocked_until_contract_and_packet_patch"
    assert decision["second_one_case_pilot_status"] == "allowed_after_patch_only"
    assert decision["runtime_status"] == "not_allowed"
    assert decision["contract_patch_required"] is True
    assert decision["packet_patch_required"] is True
    assert decision["human_review_required_for_product_claim"] is True


def test_all_pr90_roles_reviewed_and_marked_for_revision() -> None:
    role_reviews = _review()["role_reviews"]

    assert {entry["role"] for entry in role_reviews} == SPECIALIST_ROLES
    for entry in role_reviews:
        assert entry["pr97_useful_signal"]
        assert entry["main_gap"]
        assert entry["revision_needed"] is True
        assert entry["revision_pressure"]
        assert entry["do_not_infer"]


def test_contract_and_packet_revision_queues_are_explicit() -> None:
    review = _review()
    contract_revision_ids = {
        entry["revision_id"] for entry in review["contract_revision_queue"]
    }
    packet_revision_ids = {
        entry["revision_id"] for entry in review["packet_revision_queue"]
    }

    assert REQUIRED_CONTRACT_REVISIONS.issubset(contract_revision_ids)
    assert REQUIRED_PACKET_REVISIONS.issubset(packet_revision_ids)
    assert all(
        entry["status"] == "required_before_second_pilot"
        for entry in review["contract_revision_queue"]
    )
    assert any(
        entry["status"] == "recommended_before_second_pilot"
        for entry in review["packet_revision_queue"]
    )


def test_next_slice_is_contract_packet_patch_not_second_pilot() -> None:
    next_slice = _review()["next_recommended_slice"]

    assert next_slice["recommended_slice"] == (
        "PR99 Decision Trail Specialist Contract And Packet Patch v0"
    )
    assert "Patch PR90 contracts" in next_slice["purpose"]
    assert "repeat known weaknesses" in next_slice["why_not_second_pilot_now"]
    must_not = set(next_slice["must_not_do"])
    assert "run_lolla" in must_not
    assert "invoke_lolla_skill" in must_not
    assert "mutate_archives" in must_not
    assert "fill_new_specialist_outputs" in must_not
    assert "measure_answer_quality" in must_not
    assert "create_automatic_labels" in must_not
    assert "authorize_agent_action" in must_not


def test_non_claims_and_falsification_surface_are_present() -> None:
    review = _review()
    non_claim_text = " ".join(review["non_claims"])

    assert "not human review" in non_claim_text
    assert "not product proof" in non_claim_text
    assert "not answer-quality measurement" in non_claim_text
    assert "not agent action authorization" in non_claim_text
    assert review["what_would_make_this_direction_wrong"]
    assert review["overtrust_risks"]


def test_no_private_markers_local_paths_or_authority_fields() -> None:
    combined_text = "\n".join(
        [
            REVIEW_PATH.read_text(encoding="utf-8"),
            DOC_PATH.read_text(encoding="utf-8"),
        ]
    )

    for marker in FORBIDDEN_MARKERS:
        assert marker not in combined_text
    assert "/tmp/" not in combined_text
    assert not FORBIDDEN_FIELD_NAMES.intersection(_walk_keys(_review()))


def test_pr78_lint_accepts_pr98_review_artifacts() -> None:
    report = lint_product_delta_paths([DOC_PATH, REVIEW_PATH])

    assert report["summary"]["blocking_error_count"] == 0
    assert report["summary"]["warning_count"] == 0
    assert report["summary"]["info_count"] == 0
