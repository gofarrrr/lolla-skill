from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = (
    REPO_ROOT / "reviews/codex-assisted/fan-in-disagreement-report-v0/report.json"
)
DOC_PATH = REPO_ROOT / "docs/evals/product-delta-fan-in-disagreement-report-v0.md"
PR76_PATH = REPO_ROOT / "reviews/codex-assisted/product-delta-batch-v0/review.json"
PR83_PATH = REPO_ROOT / "reviews/codex-assisted/specialist-review-batch-v0/review.json"

EXPECTED_SCHEMA_VERSION = "lolla.product_delta_fan_in_disagreement_report.v0"
EXPECTED_CASE_IDS = {
    "ceo-remove-founding-cofounder",
    "accept-operations-role-startup",
}
EXPECTED_TRAP_COUNTS = {
    "met_expected_behavior": 8,
    "partly_met_expected_behavior": 2,
    "missed_expected_behavior": 0,
    "inconclusive": 0,
}
FORBIDDEN_AUTHORITY_FIELDS = {
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
PRIVACY_MARKERS = (
    "/Users/",
    "SECRET",
    "raw_message_content",
    "fabricated_passages",
    "FULL ASSISTANT REASONING",
    "client_secret",
    "api_key",
    "password",
)


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _report() -> dict[str, Any]:
    return _json(REPORT_PATH)


def _pr83() -> dict[str, Any]:
    return _json(PR83_PATH)


def _pr76_cases() -> dict[str, dict[str, Any]]:
    return {case["case_id"]: case for case in _json(PR76_PATH)["cases"]}


def _report_cases() -> dict[str, dict[str, Any]]:
    return {case["case_id"]: case for case in _report()["case_comparisons"]}


def _pr83_cases() -> dict[str, dict[str, Any]]:
    return {
        case["case_id"]: case
        for case in _pr83()["real_case_specialist_pass"]["cases"]
    }


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


def test_report_json_parses_and_has_expected_version() -> None:
    payload = _report()

    assert payload["schema_version"] == EXPECTED_SCHEMA_VERSION
    assert payload["report_mode"] == "codex_assisted_provisional_report"


def test_boundary_metadata_is_conservative() -> None:
    boundary = _report()["boundary"]

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
    keys = _walk_keys(_report())

    assert not (FORBIDDEN_AUTHORITY_FIELDS & keys)


def test_report_uses_actual_pr83_shape_paths() -> None:
    paths = _report()["comparison_scope"]["pr83_shape_paths_used"]

    assert paths["trap_records"] == "trap_discipline_pass.results"
    assert (
        paths["pr76_comparison"]
        == "real_case_specialist_pass.cases[*].case_summary.pr76_comparison"
    )
    assert (
        paths["pr83_net_read"]
        == "real_case_specialist_pass.cases[*].case_summary.pr83_net_decision_read_candidate"
    )
    assert paths["specialist_reads"] == "real_case_specialist_pass.cases[*].specialist_reads"


def test_trap_discipline_summary_matches_pr83() -> None:
    report_summary = _report()["trap_discipline_summary"]
    pr83_counts = _pr83()["summary"]["trap_behavior_counts"]
    pr83_families = {
        item["trap_family"] for item in _pr83()["trap_discipline_pass"]["results"]
    }

    assert report_summary["source_path"] == "trap_discipline_pass.results"
    assert report_summary["trap_behavior_counts"] == EXPECTED_TRAP_COUNTS
    assert report_summary["trap_behavior_counts"] == pr83_counts
    assert set(_report()["comparison_scope"]["trap_families_summarized"]) == pr83_families


def test_case_comparisons_include_exactly_pr83_real_cases() -> None:
    assert set(_report_cases()) == EXPECTED_CASE_IDS
    assert set(_report_cases()) == set(_pr83_cases())


def test_case_comparisons_match_pr83_fan_in_fields() -> None:
    cases = _report_cases()
    pr83_cases = _pr83_cases()

    for case_id, report_case in cases.items():
        pr83_case = pr83_cases[case_id]
        case_summary = pr83_case["case_summary"]
        pr76_comparison = case_summary["pr76_comparison"]
        fan_in = pr83_case["specialist_reads"]["conservative_fan_in"]
        lost_value = pr83_case["specialist_reads"]["friction_lost_value"][
            "lost_value"
        ]
        interpretation = pr83_case["specialist_reads"]["interpretation_adequacy"][
            "overall_interpretation_adequacy"
        ]

        assert (
            report_case["pr76_net_decision_read_candidate"]
            == pr76_comparison["pr76_net_decision_read_candidate"]
        )
        assert (
            report_case["pr83_net_decision_read_candidate"]
            == case_summary["pr83_net_decision_read_candidate"]
        )
        assert (
            report_case["net_candidate_changed_from_pr76"]
            is pr76_comparison["net_candidate_changed_from_pr76"]
        )
        assert report_case["discipline_delta"] == pr76_comparison["discipline_delta"]
        assert report_case["specialist_disagreements"] == fan_in[
            "specialist_disagreements"
        ]
        assert report_case["downgraded_fields"] == fan_in["downgraded_fields"]
        assert report_case["high_uncertainty_fields"] == fan_in[
            "high_uncertainty_fields"
        ]
        assert report_case["lost_value_concern"] is case_summary[
            "lost_value_concern"
        ]
        assert report_case["lost_value_material"] == lost_value
        assert report_case["interpretation_adequacy_concern"] is case_summary[
            "interpretation_adequacy_concern"
        ]
        assert (
            report_case["interpretation_adequacy_material"][
                "overall_interpretation_adequacy"
            ]
            == interpretation
        )
        assert report_case["human_review_priorities"] == fan_in[
            "human_review_priorities"
        ]
        assert report_case["why_not_stronger"] == fan_in["why_not_stronger"]
        assert report_case["what_would_change_this_read"] == fan_in[
            "what_would_change_this_read"
        ]


def test_accept_operations_downgrade_is_represented() -> None:
    case = _report_cases()["accept-operations-role-startup"]

    assert case["pr76_net_decision_read_candidate"] == "material_improvement_candidate"
    assert case["pr83_net_decision_read_candidate"] == "partial_improvement_candidate"
    assert case["net_candidate_changed_from_pr76"] is True


def test_ceo_case_same_candidate_but_stricter_caveats() -> None:
    case = _report_cases()["ceo-remove-founding-cofounder"]
    pr76_case = _pr76_cases()["ceo-remove-founding-cofounder"]

    assert case["pr76_net_decision_read_candidate"] == pr76_case[
        "net_decision_read_provisional"
    ]["label"]
    assert case["pr83_net_decision_read_candidate"] == "material_improvement_candidate"
    assert case["net_candidate_changed_from_pr76"] is False
    assert case["lost_value_concern"] is True
    assert case["interpretation_adequacy_concern"] is True
    assert case["downgraded_fields"] == [
        {
            "field": "interpretation_adequacy",
            "from": "adequate",
            "to": "partly_adequate_candidate",
            "reason": (
                "Checked-in safe mode does not expose raw conversation options or "
                "assistant influence."
            ),
        }
    ]


def test_every_case_comparison_has_required_material() -> None:
    required_fields = {
        "specialist_disagreements",
        "downgraded_fields",
        "high_uncertainty_fields",
        "lost_value_concern",
        "interpretation_adequacy_concern",
        "human_review_priorities",
        "why_not_stronger",
        "what_would_change_this_read",
    }

    for case in _report_cases().values():
        assert required_fields <= set(case)
        assert case["specialist_disagreements"]
        assert case["downgraded_fields"] or case.get("downgraded_fields_explicit_none")
        assert case["high_uncertainty_fields"]
        assert case["lost_value_concern"] is True
        assert case["interpretation_adequacy_concern"] is True
        assert case["human_review_priorities"]
        assert case["why_not_stronger"]
        assert case["what_would_change_this_read"]


def test_thinness_and_selection_limits_are_explicit() -> None:
    limits = _report()["thinness_and_selection_limits"]

    assert limits["real_case_count"] == 2
    assert limits["prior_positive_fixture_cases"] is True
    assert limits["no_real_case_no_change_noise_worse_or_inconclusive"] is True
    assert limits["positive_distribution_risk_acknowledged"] is True
    assert limits["no_raw_private_content_read"] is True
    assert limits["human_validation_available"] is False


def test_pr84_does_not_introduce_new_semantic_reads() -> None:
    method = _report()["method"]

    assert method["new_specialist_reads_created"] is False
    assert method["new_codex_review_created"] is False
    assert method["semantic_read_source"] == "pr83_existing_review_only"


def test_report_records_cross_case_observations() -> None:
    observations = _report()["cross_case_observations"]

    assert observations["concrete_downgrade"] == {
        "case_id": "accept-operations-role-startup",
        "from": "material_improvement_candidate",
        "to": "partial_improvement_candidate",
        "meaning": "PR83 made the evidence more conservative in one real case.",
    }
    assert set(observations["lost_value_concern_cases"]) == EXPECTED_CASE_IDS
    assert set(observations["interpretation_adequacy_concern_cases"]) == EXPECTED_CASE_IDS
    assert observations["no_real_case_no_change_noise_worse_or_inconclusive"] is True
    assert observations["positive_distribution_risk_remains"] is True
    assert observations["pr76_broad_reads_used_as_source_context_not_truth"] is True


def test_pr84_docs_and_json_have_no_privacy_markers() -> None:
    rendered_json = json.dumps(_report(), sort_keys=True)
    rendered_doc = DOC_PATH.read_text(encoding="utf-8")

    for marker in PRIVACY_MARKERS:
        assert marker not in rendered_json
        assert marker not in rendered_doc


def test_pr78_lint_passes_pr84_artifacts() -> None:
    report = lint_product_delta_paths([DOC_PATH, REPORT_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
