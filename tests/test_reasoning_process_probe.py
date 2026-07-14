from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.system_b.reasoning_process_contracts import schema_metrics
from engine.system_b.reasoning_process_probe import (
    ReasoningProcessProbeError,
    build_probe_prompts,
    catalog_from_packet,
    compile_probe_view,
    probe_response_schema,
    validate_probe_packet,
    validate_probe_response,
)
from engine.system_b.reasoning_process_probe_repair import (
    build_repair_prompts,
    rekey_compiled_repair,
)


ROOT = Path(__file__).resolve().parents[1]
CASE_ID = "amb1-case02-nonprofit-scale"
PACKET_PATH = (
    ROOT
    / "research/reasoning-process-phase2-views-2026-07-11/cases"
    / CASE_ID
    / "probe-inputs/challenge_and_revision_response.json"
)
LEDGER_PATH = (
    ROOT
    / "research/reasoning-process-phase1-ledger-2026-07-11/cases"
    / CASE_ID
    / "ledger.json"
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _packet() -> dict:
    return _load(PACKET_PATH)["packet"]


def _valid_response() -> dict:
    return {
        "status": "supported",
        "items": [
            {
                "interpretation": "The user corrected the assumption that variable attendance itself showed inconsistency, and the assistant accepted the correction and reframed consistency around availability and learning quality.",
                "status": "supported",
                "evidence_ids": ["e1", "e2", "e3"],
                "auxiliary_observation_ids": [],
                "limitations": "This captures the explicit correction and response, not whether the revised standard is substantively correct.",
            }
        ],
        "evidence": [
            {
                "evidence_id": "e1",
                "speaker": "user",
                "turn_index": 2,
                "quote": "You are treating the current variation as a warning sign, but some of it is normal.",
            },
            {
                "evidence_id": "e2",
                "speaker": "assistant",
                "turn_index": 2,
                "quote": "That is an important correction.",
            },
            {
                "evidence_id": "e3",
                "speaker": "assistant",
                "turn_index": 2,
                "quote": "Consistency in this setting may need to describe the program's availability and learning quality, not the same people attending every week.",
            },
        ],
        "park_unselected_auxiliary_observations": True,
        "global_limitations": "One bounded process read; no final-answer evaluation.",
    }


def test_phase3_packet_is_target_blind_and_complete() -> None:
    packet = _packet()
    result = validate_probe_packet(packet)
    assert result["case_id"] == CASE_ID
    assert result["auxiliary_observation_count"] == 26
    assert result["input_utf8_bytes"] < 24000
    encoded = json.dumps(packet)
    assert "An informal foundation comment is retained as weak reported evidence" not in encoded
    assert "phase2-source-review" not in encoded
    assert packet["boundary"]["source_review_addendum_included"] is False


def test_phase3_response_schema_stays_inside_frozen_limits() -> None:
    packet = _packet()
    ids = [
        item["observation_id"]
        for item in packet["auxiliary_phase1_ledger"]["observations"]
    ]
    schema = probe_response_schema(
        allowed_auxiliary_observation_ids=ids, max_turn_index=7
    )
    metrics = schema_metrics(schema)
    assert metrics["bytes"] < 12000
    assert metrics["depth"] <= 8
    assert schema["additionalProperties"] is False
    assert schema["properties"]["items"]["items"]["additionalProperties"] is False
    assert schema["properties"]["evidence"]["items"]["additionalProperties"] is False


def test_phase3_prompts_do_not_contain_gold_or_final_answer_evaluation() -> None:
    prompts = build_probe_prompts(_packet())
    assert "source-review addendum" not in prompts["user_prompt"]
    assert "whether the final recommendation is correct" in prompts["system_prompt"]
    assert "score quality" in prompts["system_prompt"]
    assert len(prompts["system_prompt_sha256"]) == 64
    assert len(prompts["user_prompt_sha256"]) == 64


def test_phase3_response_resolves_exact_quotes_and_compiles_append_only_view() -> None:
    packet = _packet()
    catalog = catalog_from_packet(packet)
    validated = validate_probe_response(
        _valid_response(), packet=packet, catalog=catalog
    )
    assert validated["source_custody_validated"] is True
    assert len(validated["items"][0]["source_span_ids"]) == 3
    base_ledger = _load(LEDGER_PATH)
    compiled = compile_probe_view(
        validated_response=validated,
        packet=packet,
        base_ledger=base_ledger,
        catalog=catalog,
        call_metadata={
            "call_id": "phase3-test-call",
            "requested_model": "google/gemini-3.1-flash-lite",
            "served_model": "google/gemini-3.1-flash-lite-20260507",
            "prompt_sha256": "sha256:" + "1" * 64,
            "base_ledger_sha256": "sha256:" + "2" * 64,
        },
    )
    assert compiled["status"] == "provider_response_compiled"
    assert len(compiled["model_addendum"]["observations"]) == 1
    assert compiled["model_addendum"]["observations"][0]["graph_routing_eligible"] is False
    assert compiled["model_addendum"]["boundary"]["phase1_ledger_modified"] is False
    view = compiled["view"]
    assert view["view_kind"] == "challenge_and_revision_response"
    assert view["budget"]["observed_input_observations"] == 27
    assert view["budget"]["budget_exceeded"] is False
    assert len(view["dispositions"]) == 27
    assert view["items"][0]["source_observation_ids"][0].startswith("phase3-")
    assert compiled["view_validation"]["exact_input_accounting"] is True


def test_phase3_valid_empty_response_is_preserved() -> None:
    packet = _packet()
    response = {
        "status": "not_found",
        "items": [],
        "evidence": [],
        "park_unselected_auxiliary_observations": True,
        "global_limitations": "No source-supported item found.",
    }
    validated = validate_probe_response(
        response, packet=packet, catalog=catalog_from_packet(packet)
    )
    assert validated["status"] == "not_found"
    assert validated["items"] == []


def test_phase3_rejects_inexact_quote() -> None:
    packet = _packet()
    response = _valid_response()
    response["evidence"][0]["quote"] = "A convincing paraphrase that never appeared."
    with pytest.raises(ReasoningProcessProbeError, match="not exact source evidence"):
        validate_probe_response(
            response, packet=packet, catalog=catalog_from_packet(packet)
        )


def test_phase3_rejects_unknown_auxiliary_observation() -> None:
    packet = _packet()
    response = _valid_response()
    response["items"][0]["auxiliary_observation_ids"] = ["invented-observation"]
    with pytest.raises(ReasoningProcessProbeError, match="unknown IDs"):
        validate_probe_response(
            response, packet=packet, catalog=catalog_from_packet(packet)
        )


def test_phase3_rejects_orphan_evidence_and_nonempty_not_found() -> None:
    packet = _packet()
    response = _valid_response()
    response["evidence"].append(
        {
            "evidence_id": "orphan",
            "speaker": "user",
            "turn_index": 1,
            "quote": "I cannot tell whether expansion would force us to become better or expose that the first site is not actually stable.",
        }
    )
    with pytest.raises(ReasoningProcessProbeError, match="every exact evidence"):
        validate_probe_response(
            response, packet=packet, catalog=catalog_from_packet(packet)
        )
    response = _valid_response()
    response["status"] = "not_found"
    with pytest.raises(ReasoningProcessProbeError, match="not_found"):
        validate_probe_response(
            response, packet=packet, catalog=catalog_from_packet(packet)
        )


def test_phase3_generic_repair_is_target_blind_and_scans_full_conversation() -> None:
    packet = _packet()
    baseline_prompts = build_probe_prompts(packet)
    repair_prompts = build_repair_prompts(packet)
    assert repair_prompts["system_prompt_sha256"] != baseline_prompts["system_prompt_sha256"]
    assert "scan the complete conversation chronologically" in repair_prompts["system_prompt"]
    assert "Do not stop at the latest" in repair_prompts["system_prompt"]
    assert "each explicit material challenge or correction" in repair_prompts["user_prompt"]
    assert "The user challenges stable attendance as an exclusionary standard" not in repair_prompts["user_prompt"]
    assert "phase2-source-review" not in repair_prompts["user_prompt"]


def test_phase3_generic_repair_rekeys_attempt_observations_without_losing_custody() -> None:
    baseline_call = _load(
        ROOT
        / "research/reasoning-process-phase3-development-2026-07-11/baseline/calls"
        / "position_and_decision_trajectory.json"
    )
    compiled = baseline_call["compiled"]
    packet_wrapper = _load(
        ROOT
        / "research/reasoning-process-phase2-views-2026-07-11/cases"
        / CASE_ID
        / "probe-inputs/position_and_decision_trajectory.json"
    )
    packet = packet_wrapper["packet"]
    ledger = _load(LEDGER_PATH)
    repaired = rekey_compiled_repair(
        compiled,
        catalog=catalog_from_packet(packet),
        known_base_observation_ids=[
            item["observation_id"] for item in ledger["observations"]
        ],
    )
    new_ids = [
        item["observation_id"]
        for item in repaired["model_addendum"]["observations"]
    ]
    assert all(item.startswith("phase3-repair-") for item in new_ids)
    assert not set(new_ids).intersection(
        item["observation_id"] for item in compiled["model_addendum"]["observations"]
    )
    assert repaired["view"]["view_id"].startswith("phase3-repair-view-")
    assert repaired["view_validation"]["exact_input_accounting"] is True
