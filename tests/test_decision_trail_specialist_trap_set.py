from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
TRAP_JSON = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-trail-specialist-trap-set-v0.json"
)
TRAP_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-trail-specialist-trap-set-v0.md"
)

EXPECTED_SCHEMA_VERSION = "lolla.decision_trail_specialist_trap_set.v0"
REQUIRED_TRAP_FAMILIES = {
    "safe_fixture_thinness_must_block",
    "clean_custody_not_interpretation",
    "structural_delta_overtrust",
    "missing_report_json_must_remain_visible",
    "likely_action_over_inference",
    "option_status_collapse",
    "assistant_influence_not_visible",
    "lost_value_hidden_by_custody",
    "fan_in_smoothing",
    "local_private_needed_not_available",
}
PR90_SPECIALIST_ROLES = {
    "conversation_shape_reader",
    "likely_action_reader",
    "friction_lost_value_reader",
    "conservative_fan_in_reader",
}


def _trap_set() -> dict[str, Any]:
    return json.loads(TRAP_JSON.read_text(encoding="utf-8"))


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


def _rendered_trap_json() -> str:
    return json.dumps(_trap_set(), sort_keys=True)


def test_trap_json_parses_and_has_expected_version() -> None:
    payload = _trap_set()

    assert payload["schema_version"] == EXPECTED_SCHEMA_VERSION
    assert isinstance(payload["traps"], list)
    assert len(payload["traps"]) >= 10


def test_boundary_metadata_is_conservative() -> None:
    boundary = _trap_set()["boundary"]

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


def test_trap_policy_stays_checked_in_safe_and_unfilled() -> None:
    policy = _trap_set()["trap_policy"]

    assert policy["content_mode"] == "checked_in_safe_mode"
    assert policy["raw_transcripts_included"] is False
    assert policy["raw_revised_answers_included"] is False
    assert policy["raw_memos_included"] is False
    assert policy["provider_text_included"] is False
    assert policy["private_reasoning_included"] is False
    assert policy["local_absolute_paths_included"] is False
    assert policy["specialist_reads_filled"] is False
    assert policy["fan_in_executed"] is False
    assert policy["product_claims_allowed"] is False


def test_required_trap_families_exist() -> None:
    families = {trap["trap_family"] for trap in _trap_set()["traps"]}

    assert REQUIRED_TRAP_FAMILIES <= families


def test_every_trap_targets_at_least_one_pr90_specialist_role() -> None:
    for trap in _trap_set()["traps"]:
        roles = set(trap["specialist_roles_targeted"])

        assert roles, trap["trap_id"]
        assert roles <= PR90_SPECIALIST_ROLES, trap["trap_id"]


def test_every_trap_has_required_contract_expectation_fields() -> None:
    required = {
        "expected_future_behavior",
        "forbidden_behavior",
        "required_non_claims",
        "human_review_note",
    }

    for trap in _trap_set()["traps"]:
        assert required <= set(trap), trap["trap_id"]
        assert trap["expected_future_behavior"], trap["trap_id"]
        assert trap["forbidden_behavior"], trap["trap_id"]
        assert trap["required_non_claims"], trap["trap_id"]
        assert trap["human_review_note"], trap["trap_id"]


def test_no_forbidden_authority_or_answer_key_fields_exist() -> None:
    keys = _walk_keys(_trap_set())
    forbidden = {
        "safe" + "_for_" + "agent" + "_use",
        "quality_score",
        "answer_quality_score",
        "improvement_score",
        "judge_score",
        "winner",
        "approved",
        "certified",
        "pass_fail",
        "correct_label",
        "ground_truth_label",
        "gold_label",
        "answer_key",
    }

    assert not (forbidden & keys)


def test_trap_json_has_no_privacy_markers() -> None:
    rendered = _rendered_trap_json()

    for marker in (
        "/User" + "s/",
        "SEC" + "RET",
        "raw_message_" + "content",
        "fabricated_" + "passages",
        "FULL ASSISTANT " + "REASONING",
        "client_" + "secret",
        "api_" + "key",
        "pass" + "word",
    ):
        assert marker not in rendered


def test_pr78_lint_passes_trap_artifacts() -> None:
    report = lint_product_delta_paths([TRAP_DOC, TRAP_JSON])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
