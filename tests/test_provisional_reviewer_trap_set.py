from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
TRAP_JSON = REPO_ROOT / "docs/evals/provisional-reviewer-trap-set-v0.json"
TRAP_DOC = REPO_ROOT / "docs/evals/provisional-reviewer-trap-set-v0.md"

EXPECTED_SCHEMA_VERSION = "lolla.provisional_reviewer_trap_set.v0"
REQUIRED_TRAP_FAMILIES = {
    "thin_context_should_stay_inconclusive",
    "longer_revised_no_action_change",
    "caution_without_decision_leverage",
    "gate_already_present_in_vanilla",
    "lost_live_option",
    "ambition_buried_by_generic_prudence",
    "assistant_influence_blindness",
    "specialist_disagreement_must_survive",
    "clean_artifact_not_quality_proof",
    "provisional_language_hardening",
}
PR80_SPECIALIST_ROLES = {
    "conversation_interpretation",
    "vanilla_likely_next_action",
    "lolla_likely_next_action",
    "structural_delta",
    "friction_lost_value",
    "interpretation_adequacy",
    "advisory_overclaim",
    "conservative_fan_in",
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


def test_required_trap_families_exist() -> None:
    families = {trap["trap_family"] for trap in _trap_set()["traps"]}

    assert REQUIRED_TRAP_FAMILIES <= families


def test_no_forbidden_authority_field_names_exist() -> None:
    keys = _walk_keys(_trap_set())
    forbidden = {
        "safe_for_agent_use",
        "quality_score",
        "answer_quality_score",
        "improvement_score",
        "judge_score",
        "winner",
        "approved",
        "certified",
        "pass_fail",
    }

    assert not (forbidden & keys)


def test_no_banned_proof_label_field_names_exist() -> None:
    keys = _walk_keys(_trap_set())
    banned = {
        "correct_label",
        "ground_truth_label",
        "gold_label",
        "answer_key",
    }

    assert not (banned & keys)


def test_every_trap_has_required_review_contract_fields() -> None:
    required_fields = {
        "expected_provisional_behavior",
        "forbidden_behavior",
        "required_non_claims",
        "human_review_note",
    }

    for trap in _trap_set()["traps"]:
        assert required_fields <= set(trap), trap["trap_id"]
        assert trap["expected_provisional_behavior"], trap["trap_id"]
        assert trap["forbidden_behavior"], trap["trap_id"]
        assert trap["required_non_claims"], trap["trap_id"]
        assert trap["human_review_note"], trap["trap_id"]


def test_every_trap_targets_at_least_one_pr80_specialist_role() -> None:
    for trap in _trap_set()["traps"]:
        roles = set(trap["specialist_roles_targeted"])

        assert roles, trap["trap_id"]
        assert roles <= PR80_SPECIALIST_ROLES, trap["trap_id"]


def test_trap_json_has_no_privacy_markers() -> None:
    rendered = _rendered_trap_json()

    for marker in (
        "/Users/",
        "SECRET",
        "raw_message_content",
        "fabricated_passages",
        "FULL ASSISTANT REASONING",
        "client_secret",
        "api_key",
        "password",
    ):
        assert marker not in rendered


def test_pr78_lint_passes_trap_artifacts() -> None:
    report = lint_product_delta_paths([TRAP_DOC, TRAP_JSON])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
