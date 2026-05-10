from __future__ import annotations

from collections import Counter
from typing import Any, Mapping


LEDGER_VERSION = "card_transaction_ledger.v1"
STATUS = "draft_review_only"
RUNTIME_POLICY = "runtime_dormant"
DISPOSITIONS = frozenset({"used", "rejected", "deferred"})
EFFECT_TYPES = frozenset(
    {
        "direct_answer_delta",
        "diagnostic_question",
        "guardrail",
        "counterframe",
        "speculative_probe",
        "no_effect",
    }
)
EVIDENCE_STATUSES = frozenset(
    {"quoted_exact", "inferred_from_turn", "missing", "conflicting", "not_needed"}
)
FINAL_ANSWER_VISIBILITIES = frozenset(
    {
        "silent_application",
        "visible_question",
        "visible_caveat",
        "visible_reframe",
        "not_visible",
    }
)
REJECTION_GROUNDS = frozenset(
    {
        "missing_case_evidence",
        "wrong_object",
        "guardrail_triggered",
        "stronger_competing_structure",
        "scope_mismatch",
        "user_facing_risk",
        "duplicate_of_existing_pressure",
        "low_source_support",
    }
)


class CardTransactionLedgerValidationError(ValueError):
    pass


def validate_card_transaction_ledger_payload(
    ledger: Mapping[str, Any],
    *,
    packet: Mapping[str, Any],
) -> None:
    """Validate ledger shape and trace IDs without judging semantic quality."""

    errors: list[str] = []
    if _text(ledger.get("ledger_version")) != LEDGER_VERSION:
        errors.append(f"ledger_version must be {LEDGER_VERSION}")
    if _text(ledger.get("packet_id")) != _text(packet.get("packet_id")):
        errors.append("packet_id must match packet.packet_id")
    if _text(ledger.get("status")) != STATUS:
        errors.append(f"status must be {STATUS}")
    if _text(ledger.get("runtime_policy")) != RUNTIME_POLICY:
        errors.append(f"runtime_policy must be {RUNTIME_POLICY}")
    if _text(packet.get("status")) != STATUS:
        errors.append(f"packet.status must be {STATUS}")
    if _text(packet.get("runtime_policy")) != RUNTIME_POLICY:
        errors.append(f"packet.runtime_policy must be {RUNTIME_POLICY}")

    cards = _cards_by_id(packet)
    transactions = [_mapping(item) for item in _list(ledger.get("card_transactions"))]
    if not isinstance(ledger.get("card_transactions"), list):
        errors.append("card_transactions must be a list")
        transactions = []

    transaction_card_ids = [_text(item.get("card_id")) for item in transactions]
    missing = sorted(set(cards) - set(transaction_card_ids))
    extra = sorted(set(transaction_card_ids) - set(cards))
    duplicates = sorted(
        card_id for card_id, count in Counter(transaction_card_ids).items() if count > 1
    )
    if missing:
        errors.append(f"missing card transactions: {missing}")
    if extra:
        errors.append(f"transactions reference unknown cards: {extra}")
    if duplicates:
        errors.append(f"duplicate card transactions: {duplicates}")

    for index, transaction in enumerate(transactions):
        errors.extend(_validate_transaction(index, transaction, cards=cards))

    summary = summarize_card_transactions(transactions)
    provided_summary = _mapping(ledger.get("summary"))
    if provided_summary:
        for key, value in summary.items():
            if int(provided_summary.get(key, -1) or 0) != value:
                errors.append(f"summary.{key} must be {value}")

    if errors:
        raise CardTransactionLedgerValidationError("; ".join(errors))


def summarize_card_transactions(transactions: list[Mapping[str, Any]]) -> dict[str, int]:
    dispositions = Counter(_text(item.get("disposition")) for item in transactions)
    visibilities = Counter(_text(item.get("final_answer_visibility")) for item in transactions)
    effect_types = Counter(_text(item.get("effect_type")) for item in transactions)
    return {
        "used_count": dispositions["used"],
        "rejected_count": dispositions["rejected"],
        "deferred_count": dispositions["deferred"],
        "visible_delta_count": (
            visibilities["visible_question"]
            + visibilities["visible_caveat"]
            + visibilities["visible_reframe"]
        ),
        "silent_delta_count": visibilities["silent_application"],
        "no_effect_count": effect_types["no_effect"],
    }


def _validate_transaction(
    index: int,
    transaction: Mapping[str, Any],
    *,
    cards: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    errors: list[str] = []
    prefix = f"card_transactions[{index}]"
    card_id = _text(transaction.get("card_id"))
    card = cards.get(card_id)
    if card is None:
        return [f"{prefix}.card_id is unknown: {card_id!r}"]

    if _text(transaction.get("model_id")) != _text(card.get("model_id")):
        errors.append(f"{prefix}.model_id must match packet card")

    disposition = _text(transaction.get("disposition"))
    effect_type = _text(transaction.get("effect_type"))
    visibility = _text(transaction.get("final_answer_visibility"))
    if disposition not in DISPOSITIONS:
        errors.append(f"{prefix}.disposition is invalid")
    if effect_type not in EFFECT_TYPES:
        errors.append(f"{prefix}.effect_type is invalid")
    if visibility not in FINAL_ANSWER_VISIBILITIES:
        errors.append(f"{prefix}.final_answer_visibility is invalid")

    grounding = _mapping(transaction.get("grounding_check"))
    evidence_status = _text(grounding.get("evidence_status"))
    if evidence_status not in EVIDENCE_STATUSES:
        errors.append(f"{prefix}.grounding_check.evidence_status is invalid")

    considered = _strings(transaction.get("affordance_ids_considered"))
    allowed_affordance_ids = _card_affordance_ids(card)
    unknown_affordance_ids = sorted(set(considered) - allowed_affordance_ids)
    if unknown_affordance_ids:
        errors.append(
            f"{prefix}.affordance_ids_considered contains unknown IDs: {unknown_affordance_ids}"
        )

    merged_with = _strings(transaction.get("merged_with_card_ids"))
    unknown_merged_ids = sorted(set(merged_with) - set(cards))
    if unknown_merged_ids:
        errors.append(f"{prefix}.merged_with_card_ids contains unknown IDs: {unknown_merged_ids}")

    if disposition == "used":
        if not _text(transaction.get("final_answer_delta")):
            errors.append(f"{prefix}.used requires final_answer_delta")
        if effect_type == "no_effect":
            errors.append(f"{prefix}.used must not have effect_type no_effect")
        if allowed_affordance_ids and not considered:
            errors.append(f"{prefix}.used reviewed card requires affordance_ids_considered")
    elif disposition == "rejected":
        if not _text(transaction.get("strongest_plausible_application")):
            errors.append(f"{prefix}.rejected requires strongest_plausible_application")
        if not _text(transaction.get("decision_reason")):
            errors.append(f"{prefix}.rejected requires decision_reason")
        if not _text(transaction.get("risk_if_forced")):
            errors.append(f"{prefix}.rejected requires risk_if_forced")
        if _text(transaction.get("rejection_ground")) not in REJECTION_GROUNDS:
            errors.append(f"{prefix}.rejected requires allowed rejection_ground")
    elif disposition == "deferred":
        if evidence_status not in {"missing", "conflicting", "inferred_from_turn"}:
            errors.append(
                f"{prefix}.deferred requires missing, conflicting, or inferred_from_turn evidence"
            )
        if not _strings(grounding.get("missing_evidence")) and not _text(
            transaction.get("residue")
        ):
            errors.append(f"{prefix}.deferred requires missing_evidence or residue")

    return errors


def _cards_by_id(packet: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        _text(card.get("card_id")): _mapping(card)
        for card in _list(packet.get("candidate_cards"))
        if _text(_mapping(card).get("card_id"))
    }


def _card_affordance_ids(card: Mapping[str, Any]) -> set[str]:
    grouped_ids = {
        _text(item.get("affordance_id"))
        for item in (_mapping(row) for row in _list(card.get("reviewed_affordance_cards")))
        if _text(item.get("affordance_id"))
    }
    if grouped_ids:
        return grouped_ids
    reviewed = _mapping(card.get("reviewed_affordance_fields"))
    return set(_strings(reviewed.get("affordance_ids")))


def _strings(value: Any) -> list[str]:
    return [_text(item) for item in _list(value) if _text(item)]


def _text(value: Any) -> str:
    return str(value or "").strip()


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
