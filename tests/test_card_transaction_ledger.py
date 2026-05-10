from __future__ import annotations

import copy
from pathlib import Path

import pytest

from engine.system_b.card_transaction_ledger import (
    CardTransactionLedgerValidationError,
    summarize_card_transactions,
    validate_card_transaction_ledger_payload,
)
from engine.system_b.reasoning_substrate_packet import (
    CandidateNomination,
    build_reasoning_substrate_packet_from_files,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
AFFORDANCES_V60 = REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v60.json"


def _packet() -> dict[str, object]:
    return build_reasoning_substrate_packet_from_files(
        root=REPO_ROOT,
        packet_id="ledger-fixture",
        transaction_context={"case_id": "ledger-fixture"},
        nominations=[
            CandidateNomination(
                model_id="opportunity-cost",
                pulled_by=("review_fixture",),
                why_pulled=({"source": "review_fixture", "reason": "Scarce yes/no choice."},),
                lane_order=1,
            ),
            CandidateNomination(
                model_id="batna",
                pulled_by=("review_fixture",),
                why_pulled=({"source": "review_fixture", "reason": "Fallback may matter."},),
                lane_order=2,
            ),
            CandidateNomination(
                model_id="chain-of-verification",
                pulled_by=("review_fixture",),
                why_pulled=({"source": "review_fixture", "reason": "Graph-only control."},),
                lane_order=3,
            ),
        ],
        affordances_path=AFFORDANCES_V60,
        snippet_target_max_per_card=2,
    )


def _ledger(packet: dict[str, object]) -> dict[str, object]:
    cards = packet["candidate_cards"]  # type: ignore[index]
    opp = cards[0]
    batna = cards[1]
    graph_only = cards[2]
    transactions = [
        {
            "card_id": opp["card_id"],
            "model_id": opp["model_id"],
            "disposition": "used",
            "effect_type": "direct_answer_delta",
            "affordance_ids_considered": [
                opp["reviewed_affordance_cards"][0]["affordance_id"]
            ],
            "strongest_plausible_application": "The yes displaces a concrete next-best alternative.",
            "grounding_check": {
                "case_quote": "take the current offer",
                "evidence_status": "inferred_from_turn",
                "missing_evidence": [],
            },
            "decision_reason": "The case is structured as a scarce commitment.",
            "risk_if_forced": "",
            "residue": "",
            "final_answer_delta": "Name the displaced alternative before recommending yes.",
            "final_answer_visibility": "visible_caveat",
        },
        {
            "card_id": batna["card_id"],
            "model_id": batna["model_id"],
            "disposition": "deferred",
            "effect_type": "diagnostic_question",
            "affordance_ids_considered": [
                batna["reviewed_affordance_cards"][0]["affordance_id"]
            ],
            "strongest_plausible_application": "A walk-away alternative may govern the deal.",
            "grounding_check": {
                "case_quote": "",
                "evidence_status": "missing",
                "missing_evidence": ["credible executable fallback"],
            },
            "decision_reason": "The transcript does not show the fallback quality.",
            "risk_if_forced": "Would imply walk-away leverage without evidence.",
            "residue": "Ask what fallback is executable this month.",
            "final_answer_delta": "",
            "final_answer_visibility": "visible_question",
        },
        {
            "card_id": graph_only["card_id"],
            "model_id": graph_only["model_id"],
            "disposition": "rejected",
            "effect_type": "no_effect",
            "affordance_ids_considered": [],
            "strongest_plausible_application": "A verification checklist could reduce execution errors.",
            "grounding_check": {
                "case_quote": "",
                "evidence_status": "missing",
                "missing_evidence": [],
            },
            "decision_reason": "The packet has graph-only material and no reviewed affordance depth.",
            "rejection_ground": "low_source_support",
            "risk_if_forced": "Would create process ceremony without source-backed transaction depth.",
            "residue": "",
            "final_answer_delta": "",
            "final_answer_visibility": "not_visible",
        },
    ]
    return {
        "ledger_version": "card_transaction_ledger.v1",
        "packet_id": packet["packet_id"],
        "status": "draft_review_only",
        "runtime_policy": "runtime_dormant",
        "card_transactions": transactions,
        "summary": summarize_card_transactions(transactions),
    }


def test_valid_ledger_allows_use_reject_and_defer() -> None:
    packet = _packet()
    ledger = _ledger(packet)

    validate_card_transaction_ledger_payload(ledger, packet=packet)
    assert ledger["summary"] == {
        "used_count": 1,
        "rejected_count": 1,
        "deferred_count": 1,
        "visible_delta_count": 2,
        "silent_delta_count": 0,
        "no_effect_count": 1,
    }


def test_ledger_requires_one_transaction_per_packet_card() -> None:
    packet = _packet()
    ledger = _ledger(packet)
    broken = copy.deepcopy(ledger)
    broken["card_transactions"] = broken["card_transactions"][:-1]  # type: ignore[index]
    broken["summary"] = summarize_card_transactions(broken["card_transactions"])  # type: ignore[arg-type,index]

    with pytest.raises(CardTransactionLedgerValidationError, match="missing card transactions"):
        validate_card_transaction_ledger_payload(broken, packet=packet)


def test_used_reviewed_card_requires_known_affordance_id_and_delta() -> None:
    packet = _packet()
    ledger = _ledger(packet)
    broken = copy.deepcopy(ledger)
    first = broken["card_transactions"][0]  # type: ignore[index]
    first["affordance_ids_considered"] = ["opportunity-cost.not-real"]
    first["final_answer_delta"] = ""

    with pytest.raises(CardTransactionLedgerValidationError) as exc:
        validate_card_transaction_ledger_payload(broken, packet=packet)
    message = str(exc.value)
    assert "unknown IDs" in message
    assert "used requires final_answer_delta" in message


def test_rejected_and_deferred_rules_are_shape_only_but_strict() -> None:
    packet = _packet()
    ledger = _ledger(packet)
    broken = copy.deepcopy(ledger)
    rejected = broken["card_transactions"][2]  # type: ignore[index]
    rejected["rejection_ground"] = "not_relevant"
    deferred = broken["card_transactions"][1]  # type: ignore[index]
    deferred["grounding_check"]["evidence_status"] = "quoted_exact"
    deferred["grounding_check"]["missing_evidence"] = []
    deferred["residue"] = ""

    with pytest.raises(CardTransactionLedgerValidationError) as exc:
        validate_card_transaction_ledger_payload(broken, packet=packet)
    message = str(exc.value)
    assert "allowed rejection_ground" in message
    assert "deferred requires missing" in message
    assert "missing_evidence or residue" in message


def test_summary_counts_must_match_transactions() -> None:
    packet = _packet()
    ledger = _ledger(packet)
    broken = copy.deepcopy(ledger)
    broken["summary"]["used_count"] = 99  # type: ignore[index]

    with pytest.raises(CardTransactionLedgerValidationError, match="summary.used_count"):
        validate_card_transaction_ledger_payload(broken, packet=packet)
