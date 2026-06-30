from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-trail-specialist-dry-run-v0/review.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-trail-specialist-dry-run-v0.md"
)
TRAP_JSON = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-trail-specialist-trap-set-v0.json"
)
PACKET_FIXTURE = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-trail-specialist-packets-v0/packets.json"
)

EXPECTED_SCHEMA_VERSION = "lolla.decision_trail_specialist_dry_run.v0"
ALLOWED_TRAP_RESULTS = {
    "met_expected_behavior",
    "partly_met_expected_behavior",
    "missed_expected_behavior",
    "inconclusive",
}
ALLOWED_ROLE_READINESS = {
    "ready_for_gap_preserving_review",
    "partly_ready_with_overtrust_risk",
    "blocked_checked_in_safe_thinness",
    "blocked_requires_private_context",
    "not_applicable",
}
SPECIALIST_ROLES = {
    "conversation_shape_reader",
    "likely_action_reader",
    "friction_lost_value_reader",
    "conservative_fan_in_reader",
}


def _review() -> dict[str, Any]:
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


def _trap_families() -> set[str]:
    payload = json.loads(TRAP_JSON.read_text(encoding="utf-8"))
    return {trap["trap_family"] for trap in payload["traps"]}


def _packet_report_ids() -> set[str]:
    payload = json.loads(PACKET_FIXTURE.read_text(encoding="utf-8"))
    return {report["report_id"] for report in payload["reports"]}


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


def test_review_json_parses_and_has_expected_version() -> None:
    payload = _review()

    assert payload["schema_version"] == EXPECTED_SCHEMA_VERSION
    assert payload["review_mode"] == "codex_assisted_provisional"
    assert payload["method"]["contract_conforming_specialist_outputs_created"] is False
    assert payload["method"]["fan_in_executed"] is False


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


def test_trap_discipline_covers_all_pr92_trap_families() -> None:
    results = _review()["trap_discipline_dry_run"]["results"]
    families = {item["trap_family"] for item in results}

    assert families == _trap_families()


def test_trap_discipline_results_use_allowed_values_and_include_partial_warnings() -> None:
    results = _review()["trap_discipline_dry_run"]["results"]
    result_values = {item["discipline_result"] for item in results}

    assert result_values <= ALLOWED_TRAP_RESULTS
    assert "partly_met_expected_behavior" in result_values
    assert "missed_expected_behavior" not in result_values


def test_packet_surface_uses_only_pr91_packet_reports() -> None:
    reports = _review()["packet_surface_dry_run"]["reports"]
    report_ids = {report["report_id"] for report in reports}

    assert report_ids
    assert report_ids <= _packet_report_ids()


def test_every_packet_surface_report_has_all_role_dry_runs() -> None:
    reports = _review()["packet_surface_dry_run"]["reports"]

    for report in reports:
        assert set(report["role_dry_runs"]) == SPECIALIST_ROLES
        for role, dry_run in report["role_dry_runs"].items():
            assert dry_run["readiness_result"] in ALLOWED_ROLE_READINESS, role
            assert dry_run["dry_run_observations"], role
            assert dry_run["must_not_fill"], role
            assert dry_run["required_next_context"], role


def test_dry_run_does_not_create_contract_conforming_specialist_outputs() -> None:
    payload = _review()

    assert payload["packet_surface_dry_run"][
        "contract_conforming_specialist_outputs_created"
    ] is False
    assert payload["summary"]["contract_conforming_specialist_outputs_created"] is False
    assert payload["summary"]["fan_in_executed"] is False
    rendered = json.dumps(payload, sort_keys=True)
    assert '"vanilla_likely_next_action":' not in rendered
    assert '"useful_friction":' not in rendered
    assert '"lost_value":' not in rendered


def test_summary_counts_match_fixture_shape() -> None:
    summary = _review()["summary"]

    assert summary["trap_behavior_counts"] == {
        "met_expected_behavior": 7,
        "partly_met_expected_behavior": 3,
        "missed_expected_behavior": 0,
        "inconclusive": 0,
    }
    assert summary["packet_report_count"] == 2
    assert summary["packet_role_readiness_counts"][
        "blocked_checked_in_safe_thinness"
    ] >= 1
    assert summary["packet_role_readiness_counts"][
        "blocked_requires_private_context"
    ] >= 1


def test_no_forbidden_authority_field_names_exist() -> None:
    keys = _walk_keys(_review())
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


def test_review_json_has_no_privacy_markers() -> None:
    rendered = json.dumps(_review(), sort_keys=True)

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


def test_pr78_lint_passes_pr93_artifacts() -> None:
    report = lint_product_delta_paths([DOC_PATH, REVIEW_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
