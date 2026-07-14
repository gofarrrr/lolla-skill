from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from engine.system_b.reasoning_process_ledger import (
    FAMILY_PROJECTION_STATUS,
    ReasoningProcessLedgerError,
    build_case_ledger,
    build_phase1_aggregate,
    load_case_inputs,
    validate_case_ledger,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs/evals/reasoning-process-phase1-ledger-contract-v1.json"


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def _inputs(case: dict):
    return load_case_inputs(
        root=ROOT,
        case_id=case["case_id"],
        source_path=case["source_path"],
        event_ledger_path=case["event_ledger_path"],
        synthesis_ledger_path=case["synthesis_ledger_path"],
    )


def _build(case: dict, *, event_mutator=None, synthesis_mutator=None):
    source, event, event_ref, synthesis, synthesis_ref = _inputs(case)
    event = copy.deepcopy(event)
    synthesis = copy.deepcopy(synthesis)
    if event_mutator:
        event_mutator(event)
        synthesis["event_ledger_sha256"] = _json_sha(event)
    if synthesis_mutator:
        synthesis_mutator(synthesis)
    return build_case_ledger(
        case_id=case["case_id"],
        source_text=source,
        source_path=case["source_path"],
        event_ledger=event,
        event_artifact=event_ref,
        synthesis_ledger=synthesis,
        synthesis_artifact=synthesis_ref,
    )


def _json_sha(value: object) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _known_spans(ledger: dict) -> set[str]:
    return {
        span_id
        for observation in ledger["observations"]
        for span_id in observation["source_span_ids"]
    }


def test_phase1_contract_locks_five_sources_and_zero_calls() -> None:
    contract = _contract()
    assert contract["status"] == "frozen_provider_free"
    assert len(contract["cases"]) == 5
    for case in contract["cases"]:
        for field in ("source_path", "event_ledger_path", "synthesis_ledger_path"):
            path = ROOT / case[field]
            expected = case[field.replace("path", "sha256")]
            assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
    for field in (
        "provider_calls",
        "embedding_calls",
        "evaluator_calls",
        "graph_calls",
        "pipeline_calls",
        "runtime_calls",
    ):
        assert contract["exit_gates"][field] == 0


def test_all_five_cases_build_losslessly_and_match_frozen_aggregate() -> None:
    contract = _contract()
    reports = []
    ledgers = []
    for case in contract["cases"]:
        ledger, report = _build(case)
        ledgers.append(ledger)
        reports.append(report)
        assert report["status"] == "provider_free_pass"
        assert ledger["metrics"]["failure_count"] == 0
        assert ledger["metrics"]["direct_graph_seed_count"] == 0
        assert ledger["boundary"]["raw_import_records_preserved"] is True
        assert ledger["boundary"]["semantic_relevance_inferred_by_code"] is False
    aggregate = build_phase1_aggregate(reports)
    required = contract["required_aggregate"]
    assert aggregate["case_count"] == required["case_count"]
    for field in ("observation_count", "scope_outcome_count", "failure_count"):
        assert aggregate["totals"][field] == required[field]
    assert aggregate["counts_by_family"] == required["counts_by_family"]
    assert aggregate["known_family_gaps"] == required["known_family_gaps"]
    assert aggregate["direct_graph_seed_count"] == 0
    assert sum(item["source"]["message_count"] for item in ledgers) == 70


def test_raw_records_original_states_and_scoped_absence_survive_import() -> None:
    case = _contract()["cases"][0]
    ledger, _report = _build(case)
    event = ledger["observations"][0]
    assert event["raw_record"] == _inputs(case)[1]["events"][0]
    assert event["raw_record_sha256"] == "sha256:" + _json_sha(event["raw_record"])
    assert event["state_history"][0]["state"] == "proposed"
    assert event["state_history"][-1]["state"] == "admitted"
    assert all(
        item["family_projection_status"] == FAMILY_PROJECTION_STATUS
        for item in ledger["observations"]
    )
    absent = [item for item in ledger["scope_outcomes"] if item["status"] == "not_found"]
    assert absent
    assert all(item["absence_is_observed"] is True for item in absent)
    assert ledger["metrics"]["observed_absence_count"] == len(absent)


def test_synthesis_relations_are_exact_source_declared_event_lineage() -> None:
    case = _contract()["cases"][0]
    ledger, _report = _build(case)
    synthesis = next(
        item for item in ledger["observations"] if item["source_family"] == "positions"
    )
    declared = [
        item["event_id"]
        for item in synthesis["raw_record"]["event_snapshot"]["contributions"]
    ]
    observed = [item["target_observation_id"] for item in synthesis["relations"]]
    assert observed == declared
    assert all(item["authority"] == "source_reviewer" for item in synthesis["relations"])


def test_unknown_source_span_is_quarantined_with_terminal_failure() -> None:
    case = _contract()["cases"][0]

    def mutate(event: dict) -> None:
        row = event["events"][0]
        row["event_snapshot"]["resolved_source"][0]["span_id"] = "span-unknown"
        if isinstance(row["event_snapshot"]["evidence"], list):
            row["event_snapshot"]["evidence"][0]["span_id"] = "span-unknown"
        else:
            row["event_snapshot"]["evidence"]["span_id"] = "span-unknown"

    ledger, report = _build(case, event_mutator=mutate)
    assert report["status"] == "provider_free_quarantined"
    quarantined = next(
        item for item in ledger["observations"] if item["terminal_state"] != "admitted"
    )
    assert quarantined["terminal_state"] == "quarantined_invalid_source"
    assert ledger["failures"][0]["observation_id"] == quarantined["observation_id"]
    assert ledger["failures"][0]["code"] == "RP1"
    assert report["ledger_validation"]["candidate_terminal_custody_complete"] is True


def test_raw_proposal_hash_mismatch_is_preserved_and_quarantined() -> None:
    case = _contract()["cases"][0]

    def mutate(event: dict) -> None:
        event["events"][0]["raw_proposal"]["position_fragment"] += " changed"

    ledger, report = _build(case, event_mutator=mutate)
    assert report["status"] == "provider_free_quarantined"
    assert ledger["failures"][0]["code"] == "RP0"
    assert "raw_proposal_hash_mismatch" in ledger["failures"][0]["detail"]


def test_unknown_synthesis_event_reference_fails_closed() -> None:
    case = _contract()["cases"][0]

    def mutate(synthesis: dict) -> None:
        row = synthesis["syntheses"][0]
        row["event_snapshot"]["contributions"][0]["event_id"] = "event-unknown"

    ledger, report = _build(case, synthesis_mutator=mutate)
    assert report["status"] == "provider_free_quarantined"
    failed = next(
        item for item in ledger["failures"] if item["source_record_id"].startswith("csynth-")
    )
    assert "synthesis_event_reference_unknown" in failed["detail"]


def test_family_projection_uses_declared_family_not_candidate_words() -> None:
    case = _contract()["cases"][0]

    def mutate(event: dict) -> None:
        row = next(item for item in event["events"] if item["family"] == "contributions")
        row["raw_proposal"]["position_fragment"] = "War, soil, election, and weather."
        row["event_snapshot"]["position_fragment"] = "War, soil, election, and weather."
        row["raw_proposal_sha256"] = _json_sha(row["raw_proposal"])

    ledger, _report = _build(case, event_mutator=mutate)
    changed = next(
        item
        for item in ledger["observations"]
        if item["interpretation"] == "War, soil, election, and weather."
    )
    assert changed["family"] == "position_and_decision_trajectory"
    assert changed["family_projection_status"] == FAMILY_PROJECTION_STATUS


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda ledger: ledger["boundary"].update(
                {"direct_graph_routing_allowed": True}
            ),
            "direct_graph_routing_allowed must be false",
        ),
        (
            lambda ledger: ledger["observations"][0]["raw_record"].update(
                {"unexpected": "change"}
            ),
            "raw_record hash mismatch",
        ),
        (
            lambda ledger: ledger["observations"][-1]["relations"][0].update(
                {"authority": "deterministic_validator"}
            ),
            "authority must be source_reviewer",
        ),
    ],
)
def test_validator_rejects_custody_semantic_authority_and_graph_breaches(
    mutate, message
) -> None:
    case = _contract()["cases"][0]
    ledger, _report = _build(case)
    mutate(ledger)
    with pytest.raises(ReasoningProcessLedgerError, match=message):
        validate_case_ledger(
            ledger,
            known_span_ids=_known_spans(ledger),
            expected_source_sha256=ledger["source"]["source_sha256"],
        )


def test_provider_free_build_is_deterministic() -> None:
    case = _contract()["cases"][2]
    first = _build(case)
    second = _build(case)
    assert first == second
