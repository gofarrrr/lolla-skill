from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_consultant_deck_composition_review import (  # noqa: E402
    build_consultant_deck_composition_contract,
    build_consultant_cleaning_variant,
    build_consultant_deck_composition_result,
    validate_consultant_deck_composition_contract,
    validate_consultant_cleaning_variant,
    validate_consultant_deck_composition_result,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_consultant_deck_contract_is_cleaning_review_not_gate_review() -> None:
    contract = build_consultant_deck_composition_contract(root=REPO_ROOT)

    validate_consultant_deck_composition_contract(contract)

    assert contract["schema_version"] == "pre_step6_consultant_deck_composition_contract.v1"
    assert contract["runtime_policy"] == "runtime_dormant"
    assert contract["promotion_effect"] == "none_research_only"
    assert contract["program_scope"] == "cleaning_review_not_visibility_gate"
    assert contract["case_id"] == "mid-level-consultant-report-2"
    assert contract["gates"] == {
        "runtime_wiring_allowed": False,
        "skill_update_allowed": False,
    }
    assert set(contract["precommitted_hypotheses"]) == {
        "anchor_sufficient_but_deck_compression_helpful",
        "deck_pressure_too_thin_or_generic",
        "lens_composition_misaligned",
        "case_intrinsically_ambiguous_after_cleaning",
        "v60_not_active_for_consultant",
    }
    assert "does_not_add_or_change_visibility_gates" in contract["explicit_limits"]
    assert "does_not_decide_legal_correctness" in contract["explicit_limits"]


def test_consultant_deck_result_characterizes_cleaning_material_not_visibility_policy() -> None:
    contract = build_consultant_deck_composition_contract(root=REPO_ROOT)

    result = build_consultant_deck_composition_result(root=REPO_ROOT, contract=contract)

    validate_consultant_deck_composition_result(result)

    aggregate = result["aggregate"]
    assert result["schema_version"] == "pre_step6_consultant_deck_composition_result.v1"
    assert result["program_scope"] == "cleaning_review_not_visibility_gate"
    assert aggregate["kimi_unlock_ratio"] == 0.5
    assert aggregate["gpt_stable_standdown_reviewer_supported"] is False
    assert aggregate["v60_status"] == "not_active"
    assert aggregate["cleaning_read"] == "anchor_strong_deck_pressure_thin_but_useful"
    assert aggregate["recommended_next_action"] == "build_consultant_cleaning_variant_v0"
    assert result["gates"] == {
        "runtime_wiring_allowed": False,
        "skill_update_allowed": False,
    }


def test_consultant_deck_result_preserves_material_diagnosis_channels() -> None:
    contract = build_consultant_deck_composition_contract(root=REPO_ROOT)
    result = build_consultant_deck_composition_result(root=REPO_ROOT, contract=contract)

    evidence = result["hypothesis_evidence"]

    assert set(evidence) == {
        "anchor_sufficient_but_deck_compression_helpful",
        "deck_pressure_too_thin_or_generic",
        "lens_composition_misaligned",
        "case_intrinsically_ambiguous_after_cleaning",
        "v60_not_active_for_consultant",
    }
    assert evidence["anchor_sufficient_but_deck_compression_helpful"]["evidence_state"] == "strong"
    assert evidence["deck_pressure_too_thin_or_generic"]["evidence_state"] == "plausible"
    assert evidence["v60_not_active_for_consultant"]["evidence_state"] == "strong"
    assert result["cleaning_variant_candidates"] == [
        "counsel_independence_and_channel_bias_card",
        "wednesday_tripwire_preservation_card",
        "reversibility_until_counsel_boundary_card",
    ]


def test_consultant_cleaning_variant_turns_generic_lenses_into_specific_micro_cards() -> None:
    contract = build_consultant_deck_composition_contract(root=REPO_ROOT)
    result = build_consultant_deck_composition_result(root=REPO_ROOT, contract=contract)

    variant = build_consultant_cleaning_variant(root=REPO_ROOT, review_result=result)

    validate_consultant_cleaning_variant(variant)

    assert variant["schema_version"] == "pre_step6_consultant_cleaning_variant.v1"
    assert variant["program_scope"] == "cleaning_variant_not_visibility_gate"
    assert variant["anchor_policy"]["policy"] == "keep_anchor_as_backbone"
    assert [card["card_id"] for card in variant["micro_cards"]] == [
        "counsel_independence_and_channel_bias_card",
        "wednesday_tripwire_preservation_card",
        "reversibility_until_counsel_boundary_card",
    ]
    rendered_cards = "\n".join(
        "\n".join(card["receipts"] + [card["misuse_guard"]]) for card in variant["micro_cards"]
    )
    assert "built-in bias" in rendered_cards
    assert "do not deny" in rendered_cards
    assert "until counsel guides" in rendered_cards
    assert "Bevelin" not in rendered_cards
    assert "Polya" not in rendered_cards
    assert variant["gates"] == {
        "runtime_wiring_allowed": False,
        "skill_update_allowed": False,
    }
