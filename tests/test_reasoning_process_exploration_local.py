from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from engine.system_b.reasoning_process_contracts import schema_metrics
from engine.system_b.reasoning_process_exploration_local import (
    ViewSpecificInterfaceError,
    build_local_packets,
    build_local_prompts,
    compile_local_response,
    local_response_schema,
    validate_local_response,
)
from engine.system_b.reasoning_process_exploration_local_custody import (
    compile_local_response_recordwise,
)
from engine.system_b.reasoning_process_view_specific import (
    VIEW_QUESTIONS,
    build_annotated_reader_packet,
)
from scripts.evals.build_reasoning_process_exploration_local import build
from scripts.evals.build_reasoning_process_exploration_local_v2 import build_v2


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research/reasoning-process-exploration-local-2026-07-11"
CASE02 = "amb1-case02-nonprofit-scale"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _case02_fixture() -> tuple[dict, dict]:
    fixture = _load(OUTPUT / "cases" / CASE02 / "protected-fixture.json")
    wrapper = _load(OUTPUT / "cases" / CASE02 / "windows/turn-003.json")
    return fixture["response"], wrapper


def test_builder_compiles_expected_provider_free_corpus(tmp_path: Path) -> None:
    report = build(root=ROOT, output=tmp_path / "local")
    summary = report["summary"]
    assert report["status"] == "provider_free_local_exploration_representation_pass"
    assert summary["case_count"] == 5
    assert summary["window_count"] == 35
    assert summary["protected_fixture_count"] == 5
    assert summary["protected_fixture_pass_count"] == 5
    assert summary["future_max_calls_per_case"] == 7
    assert summary["future_max_records_per_case"] == 14
    assert summary["provider_calls"] == 0
    assert summary["graph_calls"] == 0
    assert report["decision"]["phase4_transfer_authorized"] is False


def test_schema_is_shallow_small_and_has_no_irrelevant_custody_fields() -> None:
    schema = local_response_schema()
    metrics = schema_metrics(schema)
    assert metrics["bytes"] <= 12000
    assert metrics["depth"] <= 8
    encoded = json.dumps(schema)
    assert "auxiliary_observation_ids" not in encoded
    assert "park_unselected_auxiliary_observations" not in encoded
    assert '"quote"' not in encoded
    assert schema["properties"]["records"]["maxItems"] == 2


def test_local_prompt_is_target_blind_and_enforces_focal_citation_boundary() -> None:
    _, wrapper = _case02_fixture()
    prompts = build_local_prompts(wrapper)
    assert "preceding pair is read-only context" in prompts["system_prompt"]
    assert "adjacent focal sentences" in prompts["system_prompt"]
    assert "Return not_found" in prompts["system_prompt"]
    assert "case02-exploration-alternative" not in prompts["user_prompt"]
    assert "not necessarily all the ownership" in prompts["user_prompt"]
    assert len(prompts["system_prompt_sha256"]) == 64
    assert len(prompts["user_prompt_sha256"]) == 64


def test_focal_aliases_partition_each_authoritative_source_exactly_once() -> None:
    report = _load(OUTPUT / "report.json")
    for case in report["cases"]:
        focal = []
        for artifact in case["window_artifacts"]:
            wrapper = _load(ROOT / artifact["path"])
            focal.extend(wrapper["packet"]["focal_pair"]["evidence_aliases"])
            assert not (
                set(wrapper["packet"]["focal_pair"]["evidence_aliases"])
                & set(wrapper["packet"]["prior_context"]["evidence_aliases"])
            )
        full = _load(
            ROOT
            / "research/reasoning-process-view-specific-interface-2026-07-11/cases"
            / case["case_id"]
            / "exploration_and_alternatives/reader-packet.json"
        )
        expected = [item["alias"] for item in full["evidence_alias_map"]]
        assert len(focal) == len(set(focal))
        assert set(focal) == set(expected)


def test_all_protected_fixtures_keep_alternative_and_attached_limit_separate() -> None:
    report = _load(OUTPUT / "report.json")
    for case in report["cases"]:
        fixture = _load(ROOT / case["protected_fixture_path"])
        record = fixture["response"]["records"][0]
        assert record["alternative_evidence_ids"]
        assert record["attached_condition_or_limit_evidence_ids"]
        compiled = fixture["compiled"]["observations"][0]
        assert compiled["role_source_span_ids"]["alternative_evidence_ids"]
        assert compiled["role_source_span_ids"][
            "attached_condition_or_limit_evidence_ids"
        ]
        assert compiled["graph_routing_eligible"] is False
        assert compiled["cross_window_semantic_duplicate_status"] == "not_assessed"
    response, _ = _case02_fixture()
    assert response["records"][0]["alternative_evidence_ids"] == ["e026"]
    assert response["records"][0]["attached_condition_or_limit_evidence_ids"] == [
        "e027"
    ]


def test_validator_rejects_context_and_unknown_aliases() -> None:
    response, wrapper = _case02_fixture()
    context_alias = wrapper["packet"]["prior_context"]["evidence_aliases"][0]
    context = copy.deepcopy(response)
    context["records"][0]["alternative_evidence_ids"] = [context_alias]
    with pytest.raises(ViewSpecificInterfaceError, match="read-only context"):
        validate_local_response(context, wrapper=wrapper)
    unknown = copy.deepcopy(response)
    unknown["records"][0]["attached_condition_or_limit_evidence_ids"] = ["e999"]
    with pytest.raises(ViewSpecificInterfaceError, match="unknown or non-focal"):
        validate_local_response(unknown, wrapper=wrapper)


def test_validator_rejects_missing_limit_and_exact_duplicate_pair() -> None:
    response, wrapper = _case02_fixture()
    missing = copy.deepcopy(response)
    missing["records"][0]["attached_condition_or_limit_evidence_ids"] = []
    with pytest.raises(ViewSpecificInterfaceError, match="is invalid"):
        validate_local_response(missing, wrapper=wrapper)
    duplicate = copy.deepcopy(response)
    duplicate["records"].append(copy.deepcopy(duplicate["records"][0]))
    duplicate["records"][1]["alternative_interpretation"] += " duplicate wording"
    with pytest.raises(ViewSpecificInterfaceError, match="duplicate evidence-role pairs"):
        validate_local_response(duplicate, wrapper=wrapper)


def test_valid_empty_window_compiles_without_claiming_unreviewed_source_is_empty() -> None:
    _, wrapper = _case02_fixture()
    response = {
        "status": "not_found",
        "records": [],
        "global_limitations": "No alternative-plus-limit pair found in this focal pair.",
    }
    validated = validate_local_response(response, wrapper=wrapper)
    assert validated["records"] == []
    compiled = compile_local_response(
        response=response,
        wrapper=wrapper,
        producer_kind="model",
        producer_id="test-model",
        record_identity="empty-test",
    )
    assert compiled["window_terminal_disposition"] == "reviewed_empty"
    assert compiled["observations"] == []
    receipt = _load(OUTPUT / "cases" / CASE02 / "case-receipt.json")
    unreviewed = [
        window
        for window in receipt["windows"]
        if window["provider_free_disposition"]
        == "not_semantically_reviewed_under_provider_free_contract"
    ]
    assert len(unreviewed) == 6
    assert receipt["custody"]["unreviewed_window_is_not_claimed_empty"] is True


def test_stress_windows_remain_bounded_and_partition_24_message_source() -> None:
    report = _load(OUTPUT / "report.json")
    summary = report["summary"]
    assert summary["stress_message_count"] == 24
    assert summary["stress_window_count"] == 12
    assert summary["stress_focal_source_alias_count"] == 292
    assert summary["stress_max_window_input_utf8_bytes"] <= 8000
    assert report["stress"]["focal_aliases_partition_source"] is True


def test_case_receipt_is_cold_readable_without_global_synthesis() -> None:
    receipt = _load(OUTPUT / "cases" / CASE02 / "case-receipt.json")
    assert [window["focal_turn_index"] for window in receipt["windows"]] == list(
        range(1, 8)
    )
    assert len(receipt["ordered_source_review_fixture_observations"]) == 1
    observation = receipt["ordered_source_review_fixture_observations"][0]
    assert observation["focal_turn_index"] == 3
    assert receipt["custody"]["semantic_deduplication_performed"] is False
    assert receipt["custody"]["global_synthesis_performed"] is False
    assert receipt["boundary"]["semantic_exhaustiveness_validated"] is False


def test_cross_turn_relationship_requires_role_specific_prior_carry_forward() -> None:
    source_path = "tests/fixtures/reasoning_process_exploration_local/cross_turn_relationship.txt"
    source_text = (ROOT / source_path).read_text(encoding="utf-8")
    full = build_annotated_reader_packet(
        case_id="exploration-local-cross-turn",
        view_kind="exploration_and_alternatives",
        question=VIEW_QUESTIONS["exploration_and_alternatives"],
        source_path=source_path,
        source_text=source_text,
        base_observations=[],
    )
    v1_packets = build_local_packets(
        case_id="exploration-local-cross-turn",
        source_path=source_path,
        source_text=source_text,
        global_alias_map=full["evidence_alias_map"],
        allow_prior_alternative_citation=False,
    )
    v2_packets = build_local_packets(
        case_id="exploration-local-cross-turn",
        source_path=source_path,
        source_text=source_text,
        global_alias_map=full["evidence_alias_map"],
        allow_prior_alternative_citation=True,
    )
    v1 = v1_packets[1]
    v2 = v2_packets[1]
    prior_alternative = next(
        line.split("\t", 1)[0]
        for line in v2["packet"]["prior_context"]["annotated_sentence_text"].splitlines()
        if "small pilot" in line
    )
    focal_limit = v2["packet"]["focal_pair"]["evidence_aliases"][0]
    response = {
        "status": "supported",
        "records": [
            {
                "alternative_interpretation": "Launch a small pilot next month.",
                "alternative_evidence_ids": [prior_alternative],
                "attached_condition_or_limit_interpretation": "A named operator must commit before announcement.",
                "attached_condition_or_limit_evidence_ids": [focal_limit],
                "relationship_type": "condition",
                "status": "supported",
                "limitations": "Provider-free cross-turn custody fixture.",
            }
        ],
        "global_limitations": "Synthetic boundary fixture.",
    }
    with pytest.raises(ViewSpecificInterfaceError, match="read-only context"):
        validate_local_response(response, wrapper=v1)
    validated = validate_local_response(response, wrapper=v2)
    assert validated["records"][0]["role_source_span_ids"][
        "alternative_evidence_ids"
    ]
    assert validated["records"][0]["role_source_span_ids"][
        "attached_condition_or_limit_evidence_ids"
    ]
    assert v2["packet"]["prior_context"]["alternative_citation_allowed"] is True
    assert v2["packet"]["prior_context"]["attached_limit_citation_allowed"] is False


def test_v2_builder_passes_same_pair_and_cross_turn_fixtures(tmp_path: Path) -> None:
    report = build_v2(root=ROOT, output=tmp_path / "local-v2")
    assert report["status"] == "provider_free_local_exploration_v2_representation_pass"
    assert report["summary"]["protected_fixture_pass_count"] == 5
    assert report["summary"]["cross_turn_adversarial_fixture_pass_count"] == 1
    assert report["summary"]["prior_context_alternative_citation_enabled"] is True
    assert report["decision"][
        "same_pair_and_one_pair_later_relationships_representable"
    ] is True
    assert report["decision"]["provider_call_authorized"] is False


def test_v2_never_allows_prior_context_to_supply_attached_limit() -> None:
    fixture = _load(
        ROOT
        / "research/reasoning-process-exploration-local-v2-2026-07-11/adversarial-cross-turn/fixture.json"
    )
    wrapper = _load(
        ROOT
        / "research/reasoning-process-exploration-local-v2-2026-07-11/adversarial-cross-turn/turn-002-packet.json"
    )
    invalid = copy.deepcopy(fixture["response"])
    invalid["records"][0]["attached_condition_or_limit_evidence_ids"] = invalid[
        "records"
    ][0]["alternative_evidence_ids"]
    with pytest.raises(ViewSpecificInterfaceError, match="read-only context"):
        validate_local_response(invalid, wrapper=wrapper)
    prompts = build_local_prompts(wrapper)
    assert "Prior-context aliases may be cited only in alternative_evidence_ids" in prompts[
        "system_prompt"
    ]
    assert "attached condition or limit must always use focal aliases" in prompts[
        "system_prompt"
    ]


def test_v2_cold_reader_gate_authorizes_only_one_development_window() -> None:
    review = _load(
        ROOT
        / "docs/evals/reasoning-process-exploration-local-cold-reader-review-v2.json"
    )
    assert review["status"] == (
        "provider_free_gate_pass_one_development_window_may_be_probed"
    )
    assert all(item["result"] == "pass" for item in review["cold_reader_questions"])
    assert review["decision"]["provider_free_gate_passed"] is True
    assert review["decision"][
        "one_target_blind_case02_turn3_development_call_may_be_authorized"
    ] is True
    assert review["decision"]["full_seven_window_case_run_authorized"] is False
    assert review["decision"]["phase4_transfer_authorized"] is False


def test_record_level_custody_keeps_valid_turn4_sibling_without_healing() -> None:
    call = _load(
        ROOT
        / "research/reasoning-process-exploration-local-case02-2026-07-11/calls/turn-004.json"
    )
    wrapper = _load(
        ROOT
        / "research/reasoning-process-exploration-local-v2-2026-07-11/cases/amb1-case02-nonprofit-scale/windows/turn-004.json"
    )
    compiled = compile_local_response_recordwise(
        response=call["candidate_payload"],
        wrapper=wrapper,
        producer_kind="model",
        producer_id=call["requested_model"],
        record_identity="turn4-replay-test",
        call_metadata={
            "call_id": call["call_id"],
            "model": call["served_model"],
            "prompt_sha256": "sha256:" + call["user_prompt_sha256"],
        },
    )
    assert compiled["window_terminal_disposition"] == "partially_compiled"
    assert [item["terminal_state"] for item in compiled["records"]] == [
        "admitted",
        "quarantined",
    ]
    assert len(compiled["observations"]) == 1
    assert "read-only context" in compiled["records"][1]["reason"]
    assert compiled["boundary"]["model_records_changed"] is False
    assert compiled["boundary"]["record_level_validation_weakened"] is False
