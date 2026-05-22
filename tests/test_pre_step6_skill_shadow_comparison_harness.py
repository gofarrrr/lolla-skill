from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_skill_shadow_comparison_contract import (  # noqa: E402
    build_skill_shadow_comparison_contract,
)
from pre_step6_skill_shadow_comparison_harness import (  # noqa: E402
    build_skill_shadow_comparison_result,
    build_static_skill_shadow_case_record,
    load_case_records,
    validate_skill_shadow_comparison_case_record,
    validate_skill_shadow_comparison_result,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_harness_aggregates_step7_residual_work_without_authorizing_skill_change() -> None:
    contract = build_skill_shadow_comparison_contract(root=REPO_ROOT)
    records = [
        build_static_skill_shadow_case_record(
            case_id=f"{case_id}.sample-{sample_index}",
            case_role=case_role,
            legacy_meaningful=[1, 3],
            cleaner_meaningful=[],
            operator_label="supports_optional_pressure_check_trial",
            legacy_cost=1.2,
            cleaner_cost=1.2,
        )
        for case_id, case_role in (
            ("mid-level-consultant-report-2", "consultant_graduation_candidate"),
            ("third-year-phd-student.v2.v60-off", "phd_distributed_atom"),
            ("founder-grant-marcus-equity.high-clutter.v60-on", "founder_v60_destabilization"),
            ("mother-address-year", "negative_control"),
        )
        for sample_index in range(3)
    ]

    result = build_skill_shadow_comparison_result(contract=contract, case_records=records)

    validate_skill_shadow_comparison_result(result)
    assert result["schema_version"] == "pre_step6_skill_shadow_comparison_result.v1"
    assert result["skill_update_allowed"] is False
    assert result["runtime_visibility_change_allowed"] is False
    assert result["operator_review_required"] is True
    assert result["aggregate"]["case_count"] == 12
    assert result["aggregate"]["legacy_meaningful_divergence_count"] == 24
    assert result["aggregate"]["cleaner_meaningful_divergence_count"] == 0
    assert result["aggregate"]["meaningful_divergence_delta"] == 24
    assert result["aggregate"]["candidate_read"] == "supports_optional_pressure_check_trial"
    assert result["gates"] == {
        "skill_md_edit_allowed": False,
        "runtime_promotion_allowed": False,
        "automatic_optionalization_allowed": False,
    }


def test_harness_preserves_required_pressure_check_when_operator_review_says_so() -> None:
    contract = build_skill_shadow_comparison_contract(root=REPO_ROOT)
    records = [
        build_static_skill_shadow_case_record(
            case_id=f"third-year-phd-student.v2.v60-off.sample-{sample_index}",
            case_role="phd_distributed_atom",
            legacy_meaningful=[1, 2],
            cleaner_meaningful=[1, 3],
            operator_label="preserve_required_pressure_check",
        )
        for sample_index in range(2)
    ]

    result = build_skill_shadow_comparison_result(contract=contract, case_records=records)

    assert result["aggregate"]["candidate_read"] == "preserve_required_pressure_check"
    assert result["aggregate"]["operator_review_distribution"] == {
        "ambiguous_continue_research": 0,
        "preserve_required_pressure_check": 2,
        "supports_optional_pressure_check_trial": 0,
    }
    assert result["aggregate"]["preserve_labels_by_case_role"] == {"phd_distributed_atom": 2}


def test_harness_safety_blocks_support_even_when_operator_label_is_positive() -> None:
    contract = build_skill_shadow_comparison_contract(root=REPO_ROOT)
    record = build_static_skill_shadow_case_record(
        case_id="mother-address-year",
        case_role="negative_control",
        legacy_meaningful=[3],
        cleaner_meaningful=[],
        operator_label="supports_optional_pressure_check_trial",
        cleaner_payload_preserved=False,
    )

    result = build_skill_shadow_comparison_result(contract=contract, case_records=[record])

    assert result["aggregate"]["safety_blocked_count"] == 1
    assert result["aggregate"]["candidate_read"] == "preserve_required_pressure_check"


def test_case_record_requires_operator_review_label() -> None:
    record = build_static_skill_shadow_case_record(
        case_id="mid-level-consultant-report-2",
        case_role="consultant_graduation_candidate",
        legacy_meaningful=[1],
        cleaner_meaningful=[],
        operator_label="supports_optional_pressure_check_trial",
    )
    record["operator_review"] = {"rationale": "No label."}

    try:
        validate_skill_shadow_comparison_case_record(record)
    except ValueError as exc:
        assert "operator_review.label" in str(exc)
    else:
        raise AssertionError("expected validation failure")


def test_load_case_records_reads_json_records(tmp_path: Path) -> None:
    record = build_static_skill_shadow_case_record(
        case_id="mid-level-consultant-report-2",
        case_role="consultant_graduation_candidate",
        legacy_meaningful=[1],
        cleaner_meaningful=[],
        operator_label="supports_optional_pressure_check_trial",
    )
    path = tmp_path / "consultant.skill-shadow-comparison-case.v1.json"
    path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    loaded = load_case_records(tmp_path)

    assert loaded == [record]
