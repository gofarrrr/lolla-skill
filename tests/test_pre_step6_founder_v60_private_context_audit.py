from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_founder_v60_private_context_audit import (  # noqa: E402
    build_founder_v60_private_context_audit_contract,
    build_founder_v60_private_context_audit_result,
    validate_founder_v60_private_context_audit_contract,
    validate_founder_v60_private_context_audit_result,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_v60_audit_contract_names_scope_limits_and_precommitted_outcomes() -> None:
    contract = build_founder_v60_private_context_audit_contract(root=REPO_ROOT)

    validate_founder_v60_private_context_audit_contract(contract)

    assert (
        contract["schema_version"]
        == "pre_step6_founder_v60_private_context_audit_contract.v1"
    )
    assert contract["runtime_policy"] == "runtime_dormant"
    assert contract["promotion_effect"] == "none_research_only"
    assert contract["program_scope"] == "v60_private_context_audit_not_pre_step6_portfolio"
    assert contract["gates"] == {
        "runtime_wiring_allowed": False,
        "skill_update_allowed": False,
    }
    assert set(contract["precommitted_outcomes"]) == {
        "genuine_edge_pressure_structurally_borderline",
        "selection_noise",
        "joint_overload",
        "cross_chunk_consideration_gap",
    }
    assert contract["queued_followups"] == [
        "consultant_case_ambiguity_design_review_v0",
        "kimi_phd_variance_diagnostic_v0",
    ]
    assert "does_not_decide_founder_answer_correctness" in contract["explicit_limits"]
    assert "does_not_resolve_consultant" in contract["explicit_limits"]
    assert "does_not_resolve_phd" in contract["explicit_limits"]
    assert "does_not_promote_runtime_or_skill" in contract["explicit_limits"]


def test_v60_audit_result_characterizes_destabilization_without_solving_founder() -> None:
    contract = build_founder_v60_private_context_audit_contract(root=REPO_ROOT)

    result = build_founder_v60_private_context_audit_result(
        root=REPO_ROOT,
        contract=contract,
    )

    validate_founder_v60_private_context_audit_result(result)

    aggregate = result["aggregate"]
    assert result["schema_version"] == "pre_step6_founder_v60_private_context_audit_result.v1"
    assert result["program_scope"] == "v60_private_context_audit_not_pre_step6_portfolio"
    assert aggregate["v60_on_variable_family_count"] == 2
    assert aggregate["v60_off_variable_family_count"] == 0
    assert aggregate["audit_read"] == "v60_context_related_but_destabilizing"
    assert aggregate["founder_answer_correctness"] == "not_decided"
    assert aggregate["consultant_followup_status"] == "queued_not_addressed"
    assert aggregate["phd_followup_status"] == "queued_not_addressed"
    assert result["gates"] == {
        "runtime_wiring_allowed": False,
        "skill_update_allowed": False,
    }


def test_v60_audit_keeps_all_outcome_channels_distinct() -> None:
    contract = build_founder_v60_private_context_audit_contract(root=REPO_ROOT)
    result = build_founder_v60_private_context_audit_result(
        root=REPO_ROOT,
        contract=contract,
    )

    evidence = result["outcome_evidence"]

    assert set(evidence) == {
        "genuine_edge_pressure_structurally_borderline",
        "selection_noise",
        "joint_overload",
        "cross_chunk_consideration_gap",
    }
    assert evidence["selection_noise"]["evidence_state"] in {
        "weak",
        "plausible",
        "strong",
        "insufficient",
    }
    assert evidence["joint_overload"]["evidence_state"] in {
        "weak",
        "plausible",
        "strong",
        "insufficient",
    }
    assert (
        evidence["selection_noise"]["evidence_state"]
        != evidence["joint_overload"]["evidence_state"]
    )
    assert result["aggregate"]["recommended_next_action"] in {
        "review_v60_selection_packet_before_architecture_choice",
        "audit_v60_packet_cap_or_ordering_before_architecture_choice",
        "inspect_step6_cross_chunk_consideration_before_architecture_choice",
        "treat_founder_as_structurally_borderline_and_continue_queued_followups",
    }
