from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = REPO_ROOT / "reviews/codex-assisted/specialist-review-batch-v0/review.json"
DOC_PATH = REPO_ROOT / "docs/evals/codex-assisted-specialist-review-batch-v0.md"
TRAP_JSON = REPO_ROOT / "docs/evals/provisional-reviewer-trap-set-v0.json"
PR81_PACKETS = (
    REPO_ROOT / "reviews/codex-assisted/product-delta-specialist-packets-v0/packets.json"
)

EXPECTED_SCHEMA_VERSION = "lolla.codex_assisted_specialist_review_batch.v0"
ALLOWED_TRAP_RESULTS = {
    "met_expected_behavior",
    "partly_met_expected_behavior",
    "missed_expected_behavior",
    "inconclusive",
}
SPECIALIST_ROLES = {
    "conversation_interpretation",
    "vanilla_likely_next_action",
    "lolla_likely_next_action",
    "structural_delta",
    "friction_lost_value",
    "interpretation_adequacy",
    "advisory_overclaim",
    "conservative_fan_in",
}
NET_CANDIDATES = {
    "material_improvement_candidate",
    "partial_improvement_candidate",
    "no_material_change_candidate",
    "lolla_added_noise_candidate",
    "lolla_worse_candidate",
    "inconclusive",
    "not_reviewed",
}


def _review() -> dict[str, Any]:
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


def _trap_families() -> set[str]:
    payload = json.loads(TRAP_JSON.read_text(encoding="utf-8"))
    return {trap["trap_family"] for trap in payload["traps"]}


def _packet_case_ids() -> set[str]:
    payload = json.loads(PR81_PACKETS.read_text(encoding="utf-8"))
    return {case["case_id"] for case in payload["cases"]}


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


def test_no_forbidden_authority_field_names_exist() -> None:
    keys = _walk_keys(_review())
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


def test_trap_discipline_covers_all_pr82_trap_families() -> None:
    results = _review()["trap_discipline_pass"]["results"]
    families = {item["trap_family"] for item in results}

    assert families == _trap_families()


def test_trap_discipline_results_use_allowed_values() -> None:
    results = _review()["trap_discipline_pass"]["results"]

    assert results
    for item in results:
        assert item["discipline_result"] in ALLOWED_TRAP_RESULTS


def test_real_case_pass_uses_only_pr81_packet_fixture_cases() -> None:
    cases = _review()["real_case_specialist_pass"]["cases"]
    case_ids = {case["case_id"] for case in cases}

    assert case_ids
    assert case_ids <= _packet_case_ids()


def test_every_real_case_has_all_specialist_reads() -> None:
    cases = _review()["real_case_specialist_pass"]["cases"]

    for case in cases:
        assert set(case["specialist_reads"]) == SPECIALIST_ROLES
        for role, read in case["specialist_reads"].items():
            assert read["read_status"]
            assert read["source_status"]
            assert read["source_refs"]
            assert read["uncertainty_notes"]
            assert read["what_would_make_this_wrong"], role
            assert read["required_non_claims"], role


def test_conservative_fan_in_preserves_disagreement_and_why_not_stronger() -> None:
    cases = _review()["real_case_specialist_pass"]["cases"]

    for case in cases:
        fan_in = case["specialist_reads"]["conservative_fan_in"]
        assert fan_in["why_not_stronger"]
        assert fan_in["human_review_priorities"]
        assert fan_in["net_decision_read_candidate"] in NET_CANDIDATES
        assert (
            fan_in["specialist_disagreements"]
            or fan_in.get("no_disagreement_observed") is True
        )


def test_every_real_case_includes_lost_value_and_interpretation_material() -> None:
    cases = _review()["real_case_specialist_pass"]["cases"]

    for case in cases:
        friction = case["specialist_reads"]["friction_lost_value"]
        interpretation = case["specialist_reads"]["interpretation_adequacy"]
        assert friction["lost_value"]["present"] is True
        assert friction["lost_value"]["categories"]
        assert interpretation["overall_interpretation_adequacy"]
        assert case["case_summary"]["lost_value_concern"] is True
        assert case["case_summary"]["interpretation_adequacy_concern"] is True


def test_net_decision_read_candidates_are_allowed() -> None:
    cases = _review()["real_case_specialist_pass"]["cases"]

    for case in cases:
        candidate = case["case_summary"]["pr83_net_decision_read_candidate"]
        fan_in_candidate = case["specialist_reads"]["conservative_fan_in"][
            "net_decision_read_candidate"
        ]
        assert candidate in NET_CANDIDATES
        assert fan_in_candidate in NET_CANDIDATES
        assert candidate == fan_in_candidate


def test_batch_records_at_least_one_caution_or_downgrade_signal() -> None:
    summary = _review()["summary"]
    trap_counts = summary["trap_behavior_counts"]
    real_candidate_counts = summary["real_case_net_decision_candidate_counts"]
    cautionary_real_case_count = sum(
        real_candidate_counts[candidate]
        for candidate in (
            "no_material_change_candidate",
            "lolla_added_noise_candidate",
            "lolla_worse_candidate",
            "inconclusive",
        )
    )

    assert (
        summary["pr76_broad_read_downgrade_count"] >= 1
        or trap_counts["partly_met_expected_behavior"] >= 1
        or cautionary_real_case_count >= 1
    )
    if cautionary_real_case_count == 0:
        assert summary["positive_distribution_risk_acknowledged"] is True


def test_summary_records_pr78_lint_result_as_boundary_hygiene() -> None:
    lint_result = _review()["summary"]["pr78_lint_result"]

    assert lint_result == {
        "status": "passed",
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
        "checked_artifacts": [
            "docs/evals/codex-assisted-specialist-review-batch-v0.md",
            "reviews/codex-assisted/specialist-review-batch-v0/review.json",
        ],
        "meaning": (
            "Evidence-boundary lint passed for PR83 artifacts; this is boundary "
            "hygiene, not semantic validation or product proof."
        ),
    }


def test_review_json_has_no_privacy_markers() -> None:
    rendered = json.dumps(_review(), sort_keys=True)

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


def test_pr78_lint_passes_pr83_artifacts() -> None:
    report = lint_product_delta_paths([DOC_PATH, REVIEW_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
