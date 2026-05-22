from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_variable_case_diagnostic import (  # noqa: E402
    build_variable_case_diagnostic_contract,
    build_variable_case_diagnostic_result,
    validate_variable_case_diagnostic_contract,
    validate_variable_case_diagnostic_result,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_variable_contract_selects_only_quarantined_cases_and_blocks_promotion() -> None:
    contract = build_variable_case_diagnostic_contract(root=REPO_ROOT)

    validate_variable_case_diagnostic_contract(contract)

    assert contract["schema_version"] == "pre_step6_variable_case_diagnostic_contract.v1"
    assert contract["runtime_policy"] == "runtime_dormant"
    assert contract["promotion_effect"] == "none_research_only"
    assert set(contract["variable_case_ids"]) == {
        "founder-grant-marcus-equity.high-clutter.v60-on",
        "mid-level-consultant-report-2",
        "third-year-phd-student.v2.v60-off",
        "third-year-phd-student.v2.v60-on",
    }
    assert contract["gates"] == {
        "runtime_wiring_allowed": False,
        "skill_update_allowed": False,
    }


def test_variable_result_characterizes_saved_sample_variance_without_policy_choice() -> None:
    contract = build_variable_case_diagnostic_contract(root=REPO_ROOT)

    result = build_variable_case_diagnostic_result(root=REPO_ROOT, contract=contract)

    validate_variable_case_diagnostic_result(result)

    assert result["aggregate"]["variable_case_count"] == 4
    assert result["aggregate"]["total_sample_count"] >= 21
    assert result["aggregate"]["balanced_or_near_balanced_case_count"] >= 2
    assert result["gates"] == {
        "runtime_wiring_allowed": False,
        "skill_update_allowed": False,
    }
    by_case = {row["case_id"]: row for row in result["case_diagnostics"]}
    assert by_case["mid-level-consultant-report-2"]["unlock_ratio"] == 0.5
    assert by_case["third-year-phd-student.v2.v60-on"]["unlock_ratio"] > 0.8
    assert all(row["sample_observations"] for row in result["case_diagnostics"])
