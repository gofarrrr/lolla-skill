#!/usr/bin/env python3
"""Research-only generic private reasoning card interface.

This adapter proves that clean-hybrid, Bevelin, and Polya cards can satisfy one
generic card schema. It does not change the card-deck builder, visibility
policy, ledger semantics, runtime behavior, or `SKILL.md`.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence

from pre_step6_step6_card_deck import build_step6_card_deck, validate_step6_card_deck_payload


SCHEMA_VERSION = "pre_step6_private_reasoning_card_interface.v1"
CARD_SCHEMA_VERSION = "private_reasoning_card.v1"
STATUS = "research_only"
RUNTIME_POLICY = "runtime_dormant"
EXPERIMENT_ID = "design_preamble_card_interface_v0"
DEFAULT_OUT_DIR = Path("research/pre-step6-private-reasoning-cards")
ALLOWED_CARD_TYPES = frozenset({"anchor", "lens", "safety", "retrieval", "contradiction", "expansion"})
REQUIRED_CARD_FIELDS = frozenset(
    {
        "card_schema_version",
        "card_id",
        "card_type",
        "source_kind",
        "source_ref",
        "cognitive_role",
        "receipts",
        "handling_rule",
        "activation_scope",
        "misuse_guard",
        "standdown_condition",
        "public_hygiene_terms",
        "expansion_ref",
    }
)
TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "case_id",
        "source_refs",
        "cards",
        "synthetic_future_card",
        "interface_read",
        "gates",
        "notes",
    }
)
INTERFACE_READ_FIELDS = frozenset(
    {
        "bevelin_polya_special_cased",
        "new_card_requires_policy_change",
        "new_card_requires_ledger_change",
        "reason",
    }
)
GATE_FIELDS = frozenset({"runtime_wiring_allowed", "skill_update_allowed"})


class PrivateReasoningCardValidationError(ValueError):
    pass


def build_private_reasoning_card_interface(*, case_id: str, repo_root: Path) -> dict[str, object]:
    deck = build_step6_card_deck(case_id=case_id, repo_root=repo_root)
    validate_step6_card_deck_payload(deck)
    cards = [_from_deck_card(card) for card in deck["cards"] if isinstance(card, dict)]
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "case_id": case_id,
        "source_refs": dict(deck["source_refs"]),
        "cards": cards,
        "synthetic_future_card": build_synthetic_future_card(),
        "interface_read": {
            "bevelin_polya_special_cased": False,
            "new_card_requires_policy_change": False,
            "new_card_requires_ledger_change": False,
            "reason": (
                "Cards satisfy a generic private-card schema; policy and ledger "
                "consume card roles and consideration items, not Bevelin/Polya IDs."
            ),
        },
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": (
            "Research-only card-interface proof. This validates a generic schema "
            "without wiring a new runtime deck builder."
        ),
    }
    validate_private_reasoning_card_interface_payload(payload)
    return payload


def build_synthetic_future_card() -> dict[str, object]:
    return {
        "card_schema_version": CARD_SCHEMA_VERSION,
        "card_id": "future_decision_quality_card",
        "card_type": "lens",
        "source_kind": "synthetic_future_lens_fixture",
        "source_ref": "research/synthetic/future-decision-quality-card.fixture",
        "cognitive_role": (
            "Decision-quality pressure: inspect missing options, reversible tests, "
            "and what evidence would change the recommendation."
        ),
        "receipts": [
            "Forces a check for missing options before narrowing.",
            "Separates reversible experiments from irreversible commitments.",
        ],
        "handling_rule": (
            "Use only if it adds a concrete option, evidence gate, or reversal test; "
            "otherwise keep it private."
        ),
        "activation_scope": "Cases with high uncertainty, irreversible action, or sparse option exploration.",
        "misuse_guard": "Do not turn this into a generic decision worksheet or public taxonomy.",
        "standdown_condition": (
            "Stand down when the anchor already names the reversible next test and "
            "the card adds no new constraint."
        ),
        "public_hygiene_terms": ["card", "lens", "fixture", "deck", "schema"],
        "expansion_ref": "synthetic_future_card_fixture_only",
    }


def load_private_reasoning_card_interface_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise PrivateReasoningCardValidationError(f"{path}: payload must be an object")
    return payload


def validate_private_reasoning_card_interface_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_private_reasoning_card_interface_errors(payload, path=Path(path)))
    if errors:
        raise PrivateReasoningCardValidationError("; ".join(errors))


def validate_private_reasoning_card_payload(
    card: dict[str, object],
    *,
    path: Path = Path("<card>"),
) -> None:
    errors = list(iter_private_reasoning_card_errors(card, path=Path(path)))
    if errors:
        raise PrivateReasoningCardValidationError("; ".join(errors))


def validate_private_reasoning_card_interface_file(path: Path) -> None:
    validate_private_reasoning_card_interface_payload(
        load_private_reasoning_card_interface_payload(path),
        path=Path(path),
    )


def iter_private_reasoning_card_interface_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be an object"
        return
    required = tuple(TOP_LEVEL_FIELDS - {"notes"})
    yield from _unknown_fields(payload, TOP_LEVEL_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return
    if _string(payload.get("schema_version")) != SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {SCHEMA_VERSION}"
    if _string(payload.get("status")) != STATUS:
        yield f"{path / 'status'}: must be {STATUS}"
    if _string(payload.get("runtime_policy")) != RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: must be {RUNTIME_POLICY}"
    if _string(payload.get("experiment_id")) != EXPERIMENT_ID:
        yield f"{path / 'experiment_id'}: must be {EXPERIMENT_ID}"
    if not _string(payload.get("case_id")).strip():
        yield f"{path / 'case_id'}: must be non-empty"
    cards = payload.get("cards")
    if not isinstance(cards, list) or not cards:
        yield f"{path / 'cards'}: must be a non-empty list"
    elif len({_string(card.get("card_id")) for card in cards if isinstance(card, dict)}) != len(cards):
        yield f"{path / 'cards'}: card_id values must be unique"
    else:
        for index, card in enumerate(cards):
            if not isinstance(card, dict):
                yield f"{path / 'cards' / str(index)}: must be an object"
            else:
                yield from iter_private_reasoning_card_errors(
                    card,
                    path=path / "cards" / str(index),
                )
    future_card = payload.get("synthetic_future_card")
    if not isinstance(future_card, dict):
        yield f"{path / 'synthetic_future_card'}: must be an object"
    else:
        yield from iter_private_reasoning_card_errors(
            future_card,
            path=path / "synthetic_future_card",
        )
    yield from _validate_interface_read(payload.get("interface_read"), path / "interface_read")
    yield from _validate_gates(payload.get("gates"), path / "gates")


def iter_private_reasoning_card_errors(
    card: dict[str, object],
    *,
    path: Path = Path("<card>"),
) -> Iterable[str]:
    if not isinstance(card, dict):
        yield f"{path}: must be an object"
        return
    fields = set(card)
    if fields != REQUIRED_CARD_FIELDS:
        missing = sorted(REQUIRED_CARD_FIELDS - fields)
        extra = sorted(fields - REQUIRED_CARD_FIELDS)
        if missing:
            yield f"{path}: missing card fields: {', '.join(missing)}"
        if extra:
            yield f"{path}: unknown card fields: {', '.join(extra)}"
    if _string(card.get("card_schema_version")) != CARD_SCHEMA_VERSION:
        yield f"{path / 'card_schema_version'}: must be {CARD_SCHEMA_VERSION}"
    if not _string(card.get("card_id")).strip():
        yield f"{path / 'card_id'}: must be non-empty"
    if _string(card.get("card_type")) not in ALLOWED_CARD_TYPES:
        yield f"{path / 'card_type'}: unsupported card type"
    for field in (
        "source_kind",
        "source_ref",
        "cognitive_role",
        "handling_rule",
        "activation_scope",
        "misuse_guard",
        "standdown_condition",
        "expansion_ref",
    ):
        if not _string(card.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    if not _string(card.get("source_ref")).startswith(("research/", "synthetic_future")):
        yield f"{path / 'source_ref'}: must point to a research source"
    if not isinstance(card.get("receipts"), list) or not card.get("receipts"):
        yield f"{path / 'receipts'}: must be a non-empty list"
    if not isinstance(card.get("public_hygiene_terms"), list):
        yield f"{path / 'public_hygiene_terms'}: must be a list"


def write_private_reasoning_card_interface(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_private_reasoning_card_interface_payload(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{_string(payload['case_id'])}.private-reasoning-cards.v1.json"
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return out_path


def _from_deck_card(card: dict[str, object]) -> dict[str, object]:
    card_id = _string(card.get("card_id"))
    card_type = "anchor" if card_id == "clean_hybrid_card" else "lens"
    receipts = card.get("receipts")
    receipt_list = [receipt for receipt in receipts if isinstance(receipt, str)] if isinstance(receipts, list) else []
    if not receipt_list:
        receipt_list = ["Anchor answer core is the visible backbone."]
    return {
        "card_schema_version": CARD_SCHEMA_VERSION,
        "card_id": card_id,
        "card_type": card_type,
        "source_kind": _string(card.get("source_kind")),
        "source_ref": _string(card.get("source_ref")),
        "cognitive_role": _string(card.get("cognitive_role")),
        "receipts": receipt_list,
        "handling_rule": _string(card.get("handling_rule")),
        "activation_scope": _activation_scope(card_id),
        "misuse_guard": _misuse_guard(card_id),
        "standdown_condition": _standdown_condition(card_id),
        "public_hygiene_terms": ["card", "deck", "lens", "Bevelin", "Polya", "schema"],
        "expansion_ref": _string(card.get("source_ref")),
    }


def _activation_scope(card_id: str) -> str:
    if card_id == "clean_hybrid_card":
        return "Always present as concrete anchor and visible-backbone candidate."
    if card_id == "bevelin_card":
        return "Use when incentives, commitment, dependency, or false precision may hide edge pressure."
    if card_id == "polya_card":
        return "Use when problem shape, knowns/unknowns, or next informative move is unclear."
    return "Use only when source receipts match the case."


def _misuse_guard(card_id: str) -> str:
    if card_id == "clean_hybrid_card":
        return "Do not treat the anchor as immune from private challenge."
    if card_id == "bevelin_card":
        return "Do not force every problem into incentives, inversion, or commitment framing."
    if card_id == "polya_card":
        return "Do not turn the answer into a generic problem-solving worksheet."
    return "Do not force the card when it adds no case-specific pressure."


def _standdown_condition(card_id: str) -> str:
    if card_id == "clean_hybrid_card":
        return "Stand down only as sole public answer when Step 6 finds additive private pressure that improves the visible answer."
    if card_id == "bevelin_card":
        return "Stand down when it only confirms pressure already preserved by the anchor."
    if card_id == "polya_card":
        return "Stand down when the anchor already names the next real test and no problem-shape error is present."
    return "Stand down when receipts do not add a concrete pressure, guardrail, or test."


def _validate_interface_read(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, INTERFACE_READ_FIELDS, path)
    yield from _missing_fields(value, INTERFACE_READ_FIELDS, path)
    for field in (
        "bevelin_polya_special_cased",
        "new_card_requires_policy_change",
        "new_card_requires_ledger_change",
    ):
        if value.get(field) is not False:
            yield f"{path / field}: must be false"
    if not _string(value.get("reason")).strip():
        yield f"{path / 'reason'}: must be non-empty"


def _validate_gates(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, GATE_FIELDS, path)
    yield from _missing_fields(value, GATE_FIELDS, path)
    if value.get("runtime_wiring_allowed") is not False:
        yield f"{path / 'runtime_wiring_allowed'}: must be false"
    if value.get("skill_update_allowed") is not False:
        yield f"{path / 'skill_update_allowed'}: must be false"


def _unknown_fields(value: dict[str, object], allowed: frozenset[str], path: Path) -> Iterable[str]:
    for field in sorted(set(value) - allowed):
        yield f"{path / field}: unknown field"


def _missing_fields(value: dict[str, object], required: Iterable[str], path: Path) -> Iterable[str]:
    for field in sorted(set(required) - set(value)):
        yield f"{path / field}: missing required field"


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="Existing card-interface payloads to validate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--case-id", default="founder-grant-marcus-equity.high-clutter")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.paths:
        for path in args.paths:
            validate_private_reasoning_card_interface_file(path)
        return 0
    payload = build_private_reasoning_card_interface(case_id=args.case_id, repo_root=args.repo_root)
    if args.write:
        print(write_private_reasoning_card_interface(payload=payload, out_dir=args.out_dir))
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
