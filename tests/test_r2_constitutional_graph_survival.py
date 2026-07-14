from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.constitutional_graph_survival import (
    ACTIVE_PACKET_MAX_ESTIMATED_TOKENS,
    RESERVE_PACKET_MAX_ESTIMATED_TOKENS,
    build_constitutional_graph_survival,
    finalize_constitutional_graph_survival_ledger,
    validate_constitutional_graph_survival,
    validate_constitutional_graph_survival_ledger,
)
from engine.system_b.pre_step6_private_table import build_pre_step6_private_table


ROOT = Path(__file__).resolve().parents[1]


def _graphs() -> tuple[dict, list]:
    return (
        json.loads((ROOT / "data" / "knowledge_graph.json").read_text(encoding="utf-8")),
        json.loads((ROOT / "data" / "relationship_graph.json").read_text(encoding="utf-8")),
    )


def _candidates(model_ids: list[str]) -> list[dict]:
    return [
        {
            "model_id": model_id,
            "model_name": model_id,
            "recall_source": "keyword",
            "final_rank": index,
        }
        for index, model_id in enumerate(model_ids, start=1)
    ]


def _portfolio() -> dict:
    knowledge, relations = _graphs()
    model_ids = list(knowledge["models"])
    protected = "black-swan-events"
    model_ids.remove(protected)
    selected = [protected, *model_ids[:59]]
    return build_constitutional_graph_survival(
        candidates=_candidates(selected),
        knowledge_graph=knowledge,
        relationship_graph=relations,
    )


def _completed_ledger(portfolio: dict, *, park_first: bool = False) -> dict:
    ledger = copy.deepcopy(portfolio["disposition_ledger_skeleton"])
    ledger["status"] = "completed"
    for index, item in enumerate(ledger["items"]):
        item["strongest_plausible_application"] = "Test the strongest case-specific use."
        item["attempted_application_condition"] = "The relevant mechanism must be source-supported."
        item["why"] = "The attempted condition is not established by this fixture."
        item["risk_if_forced"] = "It would turn a hypothesis into unsupported case evidence."
        item["risk_if_ignored"] = "A real but currently unsupported edge might remain untested."
        if park_first and index == 0:
            item["disposition"] = "park"
            item["reopen_condition"] = "Reopen when the conversation supplies direct mechanism evidence."
        else:
            item["disposition"] = "reject"
            item["failed_condition"] = "No source evidence establishes the mechanism here."
    return ledger


def test_all_admitted_direct_candidates_survive_active_or_reserve_before_verifier() -> None:
    portfolio = _portfolio()
    active = portfolio["active_pressure_items"]
    direct_active = {
        item["model_id"] for item in active if item["candidate_origin"] == "direct_seed"
    }
    direct_reserve = {
        item["model_id"]
        for item in portfolio["reserve_custody"]["direct_capacity_reserve"]
    }

    assert len(direct_active) == 6
    assert len(direct_active | direct_reserve) == 60
    assert "black-swan-events" in direct_active
    assert portfolio["selection_contract"]["probabilistic_applicability_gate"] is False
    assert portfolio["selection_contract"]["verifier_fields_used_for_survival"] == []
    assert portfolio["selection_contract"]["candidate_deletion"] is False
    assert portfolio["path_counts"]["graph_active"] > 0
    assert all(item["source_refs"] for item in active)
    assert all(
        item["strongest_plausible_application"]
        and item["concrete_test"]
        and item["force_boundary"]
        and item["ignore_boundary"]
        for item in active
    )


def test_direct_graph_duplicate_cap_malformed_and_reserve_paths_are_distinct() -> None:
    knowledge, relations = _graphs()
    ids = list(knowledge["models"])
    candidates = _candidates(ids[:12])
    candidates.append(dict(candidates[0]))
    candidates.append({"model_id": "invented-model"})
    portfolio = build_constitutional_graph_survival(
        candidates=candidates,
        knowledge_graph=knowledge,
        relationship_graph=relations,
    )

    counts = portfolio["path_counts"]
    assert counts["direct_active"] == 6
    assert counts["direct_cap_reserve"] == 6
    assert counts["graph_active"] > 0
    assert counts["graph_cap_or_duplicate_reserve"] > 0
    assert counts["duplicate_input"] == 1
    assert counts["malformed_input"] == 1
    assert portfolio["reserve_custody"]["duplicate_candidates"][0][
        "custody_status"
    ] == "duplicate_of_direct_candidate"
    assert portfolio["reserve_custody"]["malformed_candidates"][0][
        "semantic_rejection_performed"
    ] is False


def test_active_and_reserve_fan_in_are_measured_under_frozen_bounds() -> None:
    portfolio = _portfolio()
    fan_in = portfolio["fan_in_measurement"]

    assert fan_in["active_item_count"] <= 9
    assert fan_in["active_estimated_tokens"] <= ACTIVE_PACKET_MAX_ESTIMATED_TOKENS
    assert fan_in["reserve_estimated_tokens"] <= RESERVE_PACKET_MAX_ESTIMATED_TOKENS
    assert fan_in["active_within_frozen_bound"] is True
    assert fan_in["reserve_within_frozen_bound"] is True


def test_portfolio_hash_detects_pressure_tampering() -> None:
    portfolio = _portfolio()
    tampered = copy.deepcopy(portfolio)
    tampered["active_pressure_items"][0]["concrete_test"] = "Substituted pressure"

    try:
        validate_constitutional_graph_survival(tampered)
    except ValueError as exc:
        assert "portfolio hash" in str(exc)
    else:
        raise AssertionError("tampered constitutional pressure was accepted")


def test_reject_and_park_are_valid_without_public_bloat_and_every_item_is_resolvable() -> None:
    portfolio = _portfolio()
    ledger = _completed_ledger(portfolio, park_first=True)

    validation = validate_constitutional_graph_survival_ledger(
        ledger,
        portfolio=portfolio,
    )

    assert validation["status"] == "valid"
    assert validation["disposition_counts"]["park"] == 1
    assert validation["disposition_counts"]["reject"] == len(
        portfolio["active_pressure_items"]
    ) - 1
    assert validation["public_use_required"] is False
    assert all(not item["visible_effect"] for item in ledger["items"])
    assert all(
        item["consumer_locator"]
        == portfolio["active_pressure_items"][index]["consumer_locator"]
        for index, item in enumerate(ledger["items"])
    )


def test_missing_or_not_considered_pressure_is_a_custody_failure() -> None:
    portfolio = _portfolio()
    ledger = _completed_ledger(portfolio)
    ledger["items"][0]["disposition"] = "not_considered"
    validation = validate_constitutional_graph_survival_ledger(
        ledger,
        portfolio=portfolio,
    )
    assert validation["status"] == "invalid"
    assert any("apply, reject, or park" in error for error in validation["errors"])


def test_finalizer_records_parked_path_and_private_table_can_remain_bounded() -> None:
    portfolio = _portfolio()
    ledger = _completed_ledger(portfolio, park_first=True)
    result = {
        "constitutional_graph_survival": portfolio,
        "run_health": {},
        "extraction": {"decision_situation": "Fixture decision"},
    }

    finalized = finalize_constitutional_graph_survival_ledger(result, ledger=ledger)
    assert finalized["run_health"]["constitutional_graph_survival_ledger"] == "valid"
    assert finalized["run_health"]["constitutional_graph_survival_disposition_counts"][
        "park"
    ] == 1

    table, rendered = build_pre_step6_private_table(
        result_payload=result,
        max_chars=1200,
    )
    assert len(rendered) <= 1200
    assert portfolio["consumer_delivery"][
        "every_active_item_fully_visible_or_exactly_resolvable"
    ] is True
    assert len(portfolio["disposition_ledger_skeleton"]["items"]) == len(
        portfolio["active_pressure_items"]
    )
    assert table["status"] == "ready"
