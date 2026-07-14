import copy
import json
from pathlib import Path

import pytest

from engine.system_b.canonical_model_selection import build_assessment_cards
from engine.system_b.simulated_reliability_v1 import (
    SimulatedReliabilityError,
    build_direct_ledger,
    build_graph_ledger,
    build_mechanism_input_v1,
    build_mechanism_prompts_v1,
    compile_mechanism_response_v1,
    join_role_records_v1,
    mechanism_response_schema_v1,
    build_pressure_packet,
    build_pressure_prompts,
    build_position_wrapper,
    build_role_request_bundle,
    build_three_arm_bundle,
    compile_pressure_response,
    pressure_response_schema,
)


ROOT = Path(__file__).resolve().parents[1]
ROUTING = json.loads(
    (ROOT / "docs/conversation-understanding/reasoning-pattern-shadow-routing-v0.json").read_text()
)["mechanism_seed_models"]
KNOWLEDGE = json.loads((ROOT / "data/knowledge_graph.json").read_text())
CARDS = build_assessment_cards(KNOWLEDGE["models"])
CANONICAL = set(KNOWLEDGE["models"])
CONVERSATION = "[Turn 1] USER:\nQuestion\n[Turn 1] ASSISTANT:\nAnswer\n"


def direct(mechanisms=("missing_reversal_condition",)):
    return build_direct_ledger(
        unresolved_mechanism_ids=mechanisms,
        mechanism_seed_models=ROUTING,
        canonical_model_ids=CANONICAL,
    )


def test_direct_round_robin_preserves_provenance_and_overflow_without_semantic_rejection():
    ledger = build_direct_ledger(
        unresolved_mechanism_ids=tuple(ROUTING),
        mechanism_seed_models=ROUTING,
        canonical_model_ids=CANONICAL,
        active_cap=5,
    )
    assert len(ledger["active_candidates"]) == 5
    assert ledger["all_candidate_count"] == 19
    assert len(ledger["reserve_candidates"]) == 14
    assert all(not item["semantic_rejection_performed"] for item in ledger["reserve_candidates"])
    represented = {
        mechanism
        for item in ledger["active_candidates"]
        for mechanism in item["recalled_by_mechanism_ids"]
    }
    assert len(represented) >= 5


def test_full_conversation_role_projection_preserves_every_message_without_semantic_selection():
    source = ROOT / "research/simulated-reliability-corpus-v1-2026-07-12/naturalized-transfer-sources/v1-case01-flood-infrastructure.txt"
    wrapper = build_position_wrapper(
        case_id="v1-case01-flood-infrastructure",
        conversation=source.read_text(),
        source_path=str(source.relative_to(ROOT)),
        source_sha256="x" * 64,
    )
    assert wrapper["metrics"]["conversation_message_count"] == 24
    assert wrapper["packet"]["boundary"]["all_conversation_messages_projected"] is True
    assert wrapper["packet"]["boundary"]["semantic_prefilter_performed"] is False
    assert len(wrapper["focal_alias_map"]) > 24
    assert len({row["alias"] for row in wrapper["focal_alias_map"]}) == len(wrapper["focal_alias_map"])
    bundle = build_role_request_bundle(wrapper=wrapper)
    assert set(bundle["requests"]) == {"starting", "current_qualification"}
    assert bundle["boundary"]["maximum_provider_calls"] == 2
    assert bundle["boundary"]["provider_calls"] == 0


def test_mechanism_input_preserves_every_assistant_message_without_calling_mentions_resolution():
    legacy_joined = json.loads(
        (
            ROOT
            / "research/independent-quiet-library-v242-role-probe-2026-07-12/result.json"
        ).read_text()
    )["joined"]
    joined = {
        **legacy_joined,
        "role_observations": {
            role: ([] if value is None else [value])
            for role, value in legacy_joined["role_observations"].items()
        },
    }
    source = ROOT / "research/independent-phase5-cases-2026-07-12/quiet-library-laptop-case.txt"
    packet = build_mechanism_input_v1(
        case_id="quiet",
        arm_id="quiet-primary",
        joined=joined,
        conversation=source.read_text(),
        source_refs=[],
    )
    assert len(packet["assistant_contributions"]) == 7
    assert packet["boundary"]["assistant_semantic_prefilter"] is False
    assert packet["boundary"]["assistant_mentions_are_not_deterministic_resolution"] is True
    prompts = build_mechanism_prompts_v1(packet)
    assert "Acknowledgment without an actionable treatment is not operationalization" in prompts["system_prompt"]
    assert "do not mistake answer coverage for user adoption" in prompts["user_prompt"]
    schema = mechanism_response_schema_v1()
    assert schema["properties"]["assessments"]["minItems"] == 9
    role_id = packet["role_records"][0]["role_record_id"]
    assistant_id = packet["assistant_contributions"][-1]["contribution_id"]
    rows = []
    for mechanism_id in sorted(ROUTING):
        rows.append(
            {
                "mechanism_id": mechanism_id,
                "user_process_status": "unresolved" if mechanism_id == "counterpressure_acknowledged_not_integrated" else "not_observed",
                "vanilla_answer_coverage": "operationalized" if mechanism_id == "counterpressure_acknowledged_not_integrated" else "not_applicable",
                "routing_disposition": "preserve_no_route",
                "pattern_state": "present" if mechanism_id == "counterpressure_acknowledged_not_integrated" else "not_applicable",
                "source_role_record_ids": [role_id] if mechanism_id == "counterpressure_acknowledged_not_integrated" else [],
                "source_assistant_contribution_ids": [assistant_id] if mechanism_id == "counterpressure_acknowledged_not_integrated" else [],
            }
        )
    compiled = compile_mechanism_response_v1(
        response={"assessments": rows},
        packet=packet,
        producer_kind="test",
        producer_id="test",
    )
    assert compiled["routing_projection"]["pattern_nodes"] == []
    resolved_source = next(
        item
        for item in compiled["provenance"]["pattern_sources"]
        if assistant_id in item["source_assistant_contribution_ids"]
    )
    assert resolved_source["source_role_record_ids"] == [role_id]
    hypothesis = next(
        item
        for item in compiled["pattern_hypotheses"]
        if item["mechanism_id"] == "counterpressure_acknowledged_not_integrated"
    )
    assert hypothesis["user_process_status"] == "unresolved"
    assert hypothesis["vanilla_answer_coverage"] == "operationalized"
    assert hypothesis["routing_disposition"] == "preserve_no_route"
    not_observed = next(
        item for item in compiled["pattern_hypotheses"] if item["user_process_status"] == "not_observed"
    )
    assert not_observed["state"] == "not_applicable"


def test_mechanism_contract_routes_only_uncovered_user_pressure():
    legacy_joined = json.loads(
        (
            ROOT
            / "research/independent-quiet-library-v242-role-probe-2026-07-12/result.json"
        ).read_text()
    )["joined"]
    joined = {
        **legacy_joined,
        "role_observations": {
            role: ([] if value is None else [value])
            for role, value in legacy_joined["role_observations"].items()
        },
    }
    source = ROOT / "research/independent-phase5-cases-2026-07-12/quiet-library-laptop-case.txt"
    packet = build_mechanism_input_v1(
        case_id="uncovered",
        arm_id="uncovered-primary",
        joined=joined,
        conversation=source.read_text(),
        source_refs=[],
    )
    role_id = packet["role_records"][0]["role_record_id"]
    rows = []
    target = "counterpressure_acknowledged_not_integrated"
    for mechanism_id in sorted(ROUTING):
        rows.append(
            {
                "mechanism_id": mechanism_id,
                "user_process_status": "unresolved" if mechanism_id == target else "not_observed",
                "vanilla_answer_coverage": "not_covered" if mechanism_id == target else "not_applicable",
                "routing_disposition": "route_uncovered_pressure" if mechanism_id == target else "preserve_no_route",
                "pattern_state": "present" if mechanism_id == target else "not_applicable",
                "source_role_record_ids": [role_id] if mechanism_id == target else [],
                "source_assistant_contribution_ids": [],
            }
        )
    compiled = compile_mechanism_response_v1(
        response={"assessments": rows}, packet=packet, producer_kind="test", producer_id="test"
    )
    assert compiled["routing_projection"]["pattern_nodes"] == [
        {
            "pattern_id": next(
                item["pattern_id"]
                for item in compiled["pattern_hypotheses"]
                if item["mechanism_id"] == target
            ),
            "mechanism_id": target,
            "subject_scope": "joint_process",
            "state": "present",
        }
    ]

    contradictory = json.loads(json.dumps(rows))
    routed = next(item for item in contradictory if item["mechanism_id"] == target)
    routed["routing_disposition"] = "preserve_no_route"
    with pytest.raises(SimulatedReliabilityError, match="must route"):
        compile_mechanism_response_v1(
            response={"assessments": contradictory},
            packet=packet,
            producer_kind="test",
            producer_id="test",
        )


def test_role_join_preserves_two_starting_threads_without_semantic_merge():
    base = ROOT / "research/simulated-reliability-v1-calibration-2026-07-12/a5/amb1-case03-creative-partnership-primary"
    starting = json.loads((base / "call-01-starting-result.json").read_text())["compiled"]
    paired = json.loads((base / "call-02-current_qualification-result.json").read_text())["compiled"]
    joined = join_role_records_v1(starting_compiled=starting, paired_compiled=paired)
    assert joined["record_counts"] == {"starting": 2, "current": 1, "qualification": 1}
    assert joined["boundary"]["semantic_record_merge_performed"] is False
    packet = build_mechanism_input_v1(
        case_id="creative",
        arm_id="creative-primary",
        joined=joined,
        conversation=(ROOT / "research/designed-ambiguous-pool-v1-2026-07-10/development-cases/amb1-case03-creative-partnership.txt").read_text(),
        source_refs=[],
    )
    assert [record["role"] for record in packet["role_records"]] == [
        "starting",
        "starting",
        "current",
        "qualification",
    ]


def test_direct_rejects_unknown_mechanisms_and_noncanonical_routes():
    with pytest.raises(SimulatedReliabilityError, match="unknown controlled"):
        direct(("invented",))
    bad = copy.deepcopy(ROUTING)
    bad["missing_reversal_condition"] = ["invented"]
    with pytest.raises(SimulatedReliabilityError, match="noncanonical"):
        build_direct_ledger(
            unresolved_mechanism_ids=("missing_reversal_condition",),
            mechanism_seed_models=bad,
            canonical_model_ids=CANONICAL,
        )


def test_graph_slots_are_structurally_diverse_replayable_and_no_deletion():
    d = direct()
    graph = {
        "edges": [
            {"source_model_id": "commitment-bias", "target_model_id": "anchoring", "edge_type": "ally"},
            {"source_model_id": "commitment-bias", "target_model_id": "active-listening", "edge_type": "tension"},
            {"source_model_id": "premortem", "target_model_id": "calculated-risk-taking", "edge_type": "antagonist"},
            {"source_model_id": "sunk-cost-fallacy", "target_model_id": "confirmation-bias", "edge_type": "ally"},
            {"source_model_id": "commitment-bias", "target_model_id": "premortem", "edge_type": "tension"},
        ]
    }
    one = build_graph_ledger(
        direct_ledger=d, relation_graph=graph, canonical_model_ids=CANONICAL
    )
    two = build_graph_ledger(
        direct_ledger=d,
        relation_graph={"edges": list(reversed(graph["edges"]))},
        canonical_model_ids=CANONICAL,
    )
    assert one == two
    assert [item["selected_relation_slot"] for item in one["active_candidates"]] == [
        "antagonist",
        "tension",
        "ally",
    ]
    assert any(item["custody_status"] == "duplicate_of_direct_candidate" for item in one["reserve_candidates"])
    assert one["eligible_edge_count"] == 5
    assert len(one["all_eligible_edges"]) == 5


def test_graph_eligible_noncanonical_edge_fails_closed():
    with pytest.raises(SimulatedReliabilityError, match="noncanonical"):
        build_graph_ledger(
            direct_ledger=direct(),
            relation_graph={
                "edges": [
                    {
                        "source_model_id": "commitment-bias",
                        "target_model_id": "invented",
                        "edge_type": "ally",
                    }
                ]
            },
            canonical_model_ids=CANONICAL,
        )


def test_pressure_packet_requires_graph_difference_and_preserves_every_active_candidate():
    d = direct()
    with pytest.raises(SimulatedReliabilityError, match="contains no graph"):
        build_pressure_packet(
            case_id="x",
            arm_id="graph_expanded_pressure",
            conversation=CONVERSATION,
            candidates=d["active_candidates"],
            challenge_cards=CARDS,
            portfolio_ledger_refs=[],
            source_refs=[],
        )


def test_pressure_response_requires_accountable_complete_dispositions():
    d = direct(("counterpressure_acknowledged_not_integrated",))
    packet = build_pressure_packet(
        case_id="x",
        arm_id="direct_pressure",
        conversation=CONVERSATION,
        candidates=d["active_candidates"],
        challenge_cards=CARDS,
        portfolio_ledger_refs=[],
        source_refs=[],
    )
    ids = [item["model_id"] for item in d["active_candidates"]]
    schema = pressure_response_schema(ids)
    assert schema["properties"]["candidate_dispositions"]["minItems"] == len(ids)
    prompts = build_pressure_prompts(packet)
    assert "not evidence about the case" in prompts["system_prompt"]
    assert "'no reopening condition' is not acceptable" in prompts["user_prompt"]
    rows = [
        {
            "model_id": model_id,
            "disposition": "reject",
            "source_turn_numbers": [1],
            "effect": "no_material_effect",
            "strongest_plausible_application": "The lens could challenge the stated position.",
            "disposition_reason": "The conversation already handles that condition.",
            "risk_if_forced": "It would add duplicate friction.",
            "reopen_condition": "Reopen if the existing safeguard disappears.",
        }
        for model_id in ids
    ]
    compiled = compile_pressure_response(
        response={
            "candidate_dispositions": rows,
            "reconsidered_answer": "The original answer remains proportionate.",
            "change_summary": "No material public change.",
        },
        packet=packet,
    )
    assert compiled["all_active_candidates_accounted_for"] is True
    rows[0]["risk_if_forced"] = ""
    with pytest.raises(SimulatedReliabilityError, match="explanation is empty"):
        compile_pressure_response(
            response={
                "candidate_dispositions": rows,
                "reconsidered_answer": "Answer",
                "change_summary": "Summary",
            },
            packet=packet,
        )


def test_three_arm_bundle_keeps_direct_candidates_identical_and_graph_candidates_additive():
    d = direct()
    relation = json.loads((ROOT / "data/relationship_graph.json").read_text())
    g = build_graph_ledger(
        direct_ledger=d, relation_graph=relation, canonical_model_ids=CANONICAL
    )
    bundle = build_three_arm_bundle(
        case_id="x",
        conversation=CONVERSATION,
        direct_ledger=d,
        graph_ledger=g,
        challenge_cards=CARDS,
        source_refs=[],
    )
    arms = bundle["arms"]
    assert all(arms[name]["call_required"] for name in arms)
    direct_ids = [item["model_id"] for item in arms["direct_pressure"]["packet"]["pressure_portfolio"]]
    graph_ids = [item["model_id"] for item in arms["graph_expanded_pressure"]["packet"]["pressure_portfolio"]]
    assert graph_ids[: len(direct_ids)] == direct_ids
    assert len(graph_ids) == len(direct_ids) + len(g["active_candidates"])
    assert len(graph_ids) <= 13
    assert arms["transcript_only"]["packet"]["authoritative_conversation"] == CONVERSATION


def test_empty_mechanism_result_stands_down_without_fake_pressure_calls():
    d = direct(())
    g = build_graph_ledger(
        direct_ledger=d, relation_graph={"edges": []}, canonical_model_ids=CANONICAL
    )
    bundle = build_three_arm_bundle(
        case_id="quiet",
        conversation=CONVERSATION,
        direct_ledger=d,
        graph_ledger=g,
        challenge_cards=CARDS,
        source_refs=[],
    )
    assert bundle["arms"]["transcript_only"]["call_required"] is True
    assert bundle["arms"]["direct_pressure"]["call_required"] is False
    assert bundle["arms"]["graph_expanded_pressure"]["call_required"] is False
    assert bundle["arms"]["direct_pressure"]["provider_attempted"] is False
    assert bundle["arms"]["direct_pressure"]["public_output"] == "Answer"
