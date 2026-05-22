from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_founder_v60_symmetry_check import (  # noqa: E402
    build_founder_v60_symmetry_contract,
    build_founder_v60_symmetry_result,
    validate_founder_v60_symmetry_contract,
    validate_founder_v60_symmetry_result,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_founder_symmetry_contract_is_research_only_and_precommitted() -> None:
    contract = build_founder_v60_symmetry_contract(root=REPO_ROOT)

    validate_founder_v60_symmetry_contract(contract)

    assert contract["schema_version"] == "pre_step6_founder_v60_symmetry_contract.v1"
    assert contract["runtime_policy"] == "runtime_dormant"
    assert contract["promotion_effect"] == "none_research_only"
    assert contract["gates"] == {
        "runtime_wiring_allowed": False,
        "skill_update_allowed": False,
    }
    assert contract["case_family"] == "founder-grant-marcus-equity.high-clutter"
    assert "v60_on_specific_destabilization" in contract["precommitted_outcomes"]
    assert "base_case_borderline_or_model_noise" in contract["precommitted_outcomes"]


def test_founder_symmetry_result_compares_modes_without_visibility_promotion() -> None:
    contract = build_founder_v60_symmetry_contract(root=REPO_ROOT)

    result = build_founder_v60_symmetry_result(root=REPO_ROOT, contract=contract)

    validate_founder_v60_symmetry_result(result)

    assert result["schema_version"] == "pre_step6_founder_v60_symmetry_result.v1"
    assert result["gates"] == {
        "runtime_wiring_allowed": False,
        "skill_update_allowed": False,
    }
    matrix_keys = {
        (row["model_family"], row["v60_mode"]) for row in result["comparison_matrix"]
    }
    assert ("moonshotai", "on") in matrix_keys
    assert ("moonshotai", "off") in matrix_keys
    assert ("openai", "on") in matrix_keys
    assert result["aggregate"]["founder_family_count"] >= 1
    assert result["aggregate"]["recommended_next_action"] in {
        "audit_v60_private_context_before_architecture_choice",
        "treat_founder_as_case_shape_borderline_before_architecture_choice",
        "complete_missing_symmetry_samples_before_interpretation",
        "no_founder_specific_architecture_change",
    }
