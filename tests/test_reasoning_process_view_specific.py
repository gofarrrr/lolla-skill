from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from engine.system_b.conversation_state_candidates import build_source_catalog
from engine.system_b.reasoning_process_contracts import schema_metrics
from engine.system_b.reasoning_process_view_specific import (
    ROLE_FIELDS,
    VIEW_QUESTIONS,
    ViewSpecificInterfaceError,
    build_annotated_reader_packet,
    build_view_specific_prompts,
    protected_fixture_response,
    validate_annotated_reader_packet,
    validate_view_specific_response,
    view_specific_response_schema,
)
from scripts.evals.build_reasoning_process_view_specific_interface import build


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT / "docs/evals/reasoning-process-view-specific-interface-contract-v1.json"
)
PHASE2_PATH = ROOT / "docs/evals/reasoning-process-phase2-coverage-contract-v1.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _target_context(case_index: int = 0, target_index: int = 0):
    case = _load(PHASE2_PATH)["cases"][case_index]
    target = case["targets"][target_index]
    source_text = (ROOT / case["source_path"]).read_text(encoding="utf-8")
    ledger = _load(ROOT / case["phase1_ledger_path"])
    wrapper = build_annotated_reader_packet(
        case_id=case["case_id"],
        view_kind=target["view_kind"],
        question=VIEW_QUESTIONS[target["view_kind"]],
        source_path=case["source_path"],
        source_text=source_text,
        base_observations=ledger["observations"],
    )
    catalog = build_source_catalog(
        source_text=source_text, source_path=case["source_path"]
    )
    response = protected_fixture_response(
        target=target, wrapper=wrapper, catalog=catalog
    )
    return case, target, source_text, wrapper, response


@pytest.fixture(scope="module")
def built_report(tmp_path_factory: pytest.TempPathFactory) -> dict:
    output = tmp_path_factory.mktemp("view-specific-interface")
    return build(root=ROOT, contract=_load(CONTRACT_PATH), output=output)


def test_all_25_protected_fixtures_compile_without_calls(built_report: dict) -> None:
    summary = built_report["summary"]
    assert built_report["status"] == "provider_free_view_specific_interface_pass"
    assert summary["case_count"] == 5
    assert summary["protected_target_count"] == 25
    assert summary["compiled_fixture_pass_count"] == 25
    assert summary["view_kind_count"] == 5
    assert summary["provider_calls"] == 0
    assert summary["embedding_calls"] == 0
    assert summary["graph_calls"] == 0
    assert summary["runtime_calls"] == 0
    assert built_report["decision"]["phase4_transfer_authorized"] is False
    assert built_report["decision"]["semantic_model_behavior_validated"] is False


def test_reader_packet_is_complete_target_blind_and_alias_stable() -> None:
    case, target, source_text, wrapper, _ = _target_context()
    validation = validate_annotated_reader_packet(wrapper, source_text=source_text)
    packet = wrapper["reader_packet"]
    assert validation["message_count"] == 14
    assert packet["boundary"]["complete_message_content_visible"] is True
    assert packet["boundary"]["protected_target_included"] is False
    assert target["target_id"] not in json.dumps(packet)
    assert "source_evidence" not in json.dumps(packet)
    aliases = wrapper["evidence_alias_map"]
    assert aliases[0]["alias"] == "e001"
    assert len({row["span_id"] for row in aliases}) == len(aliases)
    replay = build_annotated_reader_packet(
        case_id=case["case_id"],
        view_kind=target["view_kind"],
        question=VIEW_QUESTIONS[target["view_kind"]],
        source_path=case["source_path"],
        source_text=source_text,
        base_observations=_load(ROOT / case["phase1_ledger_path"])["observations"],
    )
    assert replay == wrapper


def test_five_schemas_are_shallow_role_specific_and_have_no_quote_field() -> None:
    gates = _load(CONTRACT_PATH)["gates"]
    schemas = {}
    for view_kind, roles in ROLE_FIELDS.items():
        schema = view_specific_response_schema(view_kind)
        schemas[view_kind] = schema
        metrics = schema_metrics(schema)
        assert metrics["bytes"] <= gates["max_provider_schema_bytes"]
        assert metrics["depth"] <= gates["max_provider_schema_depth"]
        encoded = json.dumps(schema)
        assert '"quote"' not in encoded
        record = schema["properties"]["records"]["items"]
        assert set(roles).issubset(record["required"])
        assert record["additionalProperties"] is False
    assert schemas["position_and_decision_trajectory"] != schemas[
        "exploration_and_alternatives"
    ]


def test_prompts_preserve_probabilistic_semantics_and_product_boundary() -> None:
    _, target, _, wrapper, _ = _target_context()
    prompts = build_view_specific_prompts(wrapper)
    assert "Interpret messy conversation semantically" in prompts["system_prompt"]
    assert "do not score its quality" in prompts["system_prompt"]
    assert "complete annotated conversation chronologically" in prompts["system_prompt"]
    assert "Never copy or invent source quotes" in prompts["system_prompt"]
    assert target["target_id"] not in prompts["user_prompt"]
    assert "source_evidence" not in prompts["user_prompt"]
    assert len(prompts["system_prompt_sha256"]) == 64
    assert len(prompts["user_prompt_sha256"]) == 64


def test_validator_rejects_unknown_alias_and_missing_semantic_role() -> None:
    _, _, _, wrapper, response = _target_context()
    unknown = copy.deepcopy(response)
    unknown["records"][0]["position_evidence_ids"] = ["e999"]
    with pytest.raises(ViewSpecificInterfaceError, match="unknown evidence aliases"):
        validate_view_specific_response(unknown, wrapper=wrapper)
    missing = copy.deepcopy(response)
    missing["records"][0]["qualification_evidence_ids"] = []
    with pytest.raises(ViewSpecificInterfaceError, match="must not be empty"):
        validate_view_specific_response(missing, wrapper=wrapper)


def test_validator_rejects_unknown_auxiliary_and_duplicate_interpretation() -> None:
    _, _, _, wrapper, response = _target_context()
    unknown = copy.deepcopy(response)
    unknown["records"][0]["auxiliary_observation_ids"] = ["invented"]
    with pytest.raises(ViewSpecificInterfaceError, match="unknown IDs"):
        validate_view_specific_response(unknown, wrapper=wrapper)
    duplicate = copy.deepcopy(response)
    duplicate["records"].append(copy.deepcopy(duplicate["records"][0]))
    with pytest.raises(ViewSpecificInterfaceError, match="duplicate interpretations"):
        validate_view_specific_response(duplicate, wrapper=wrapper)


def test_challenge_contract_enforces_response_and_revision_semantics() -> None:
    _, _, _, wrapper, response = _target_context(target_index=4)
    missing_revision = copy.deepcopy(response)
    missing_revision["records"][0]["revision_evidence_ids"] = []
    with pytest.raises(ViewSpecificInterfaceError, match="revise requires revision"):
        validate_view_specific_response(missing_revision, wrapper=wrapper)
    false_no_response = copy.deepcopy(response)
    false_no_response["records"][0]["response_type"] = "no_response"
    with pytest.raises(ViewSpecificInterfaceError, match="cannot cite response evidence"):
        validate_view_specific_response(false_no_response, wrapper=wrapper)


def test_packet_detects_source_hash_drift() -> None:
    _, _, source_text, wrapper, _ = _target_context()
    with pytest.raises(ViewSpecificInterfaceError, match="source hash drifted"):
        validate_annotated_reader_packet(wrapper, source_text=source_text + " drift")


def test_real_24_message_stress_keeps_source_and_omits_auxiliary_whole(
    built_report: dict,
) -> None:
    stress = built_report["stress_fixtures"]
    assert len(stress) == 5
    assert all(item["metrics"]["source_message_count"] == 24 for item in stress)
    assert all(item["metrics"]["source_content_complete"] is True for item in stress)
    assert all(item["metrics"]["auxiliary_observation_count_available"] == 32 for item in stress)
    assert all(item["metrics"]["auxiliary_observation_count_included"] == 0 for item in stress)
    assert all(item["metrics"]["auxiliary_ledger_omitted_whole"] is True for item in stress)
    assert max(item["metrics"]["observed_input_utf8_bytes"] for item in stress) <= 24000


def test_compiled_fixtures_have_complete_dispositions_and_no_graph_seed(
    built_report: dict,
) -> None:
    for result in built_report["protected_fixtures"]:
        compiled = _load(ROOT / result["artifacts"]["compiled_fixture"])
        view = compiled["view"]
        assert len(view["dispositions"]) == len(
            view["input"]["ledger_observation_ids"]
        )
        assert view["budget"]["budget_exceeded"] is False
        assert compiled["boundary"]["graph_calls"] == 0
        assert all(
            observation["graph_routing_eligible"] is False
            for observation in compiled["fixture_addendum"]["observations"]
        )
