#!/usr/bin/env python3
"""Research-only unified private-consideration ledger overlap fixture.

This proves the design rule: dedupe the hot context for attention, but preserve
every source item for custody. It does not alter V60 runtime, Step 6, or
Observatory wiring.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence

from pre_step6_private_reasoning_cards import (
    build_private_reasoning_card_interface,
    validate_private_reasoning_card_interface_payload,
)


SCHEMA_VERSION = "pre_step6_private_consideration_ledger_overlap.v1"
ITEM_SCHEMA_VERSION = "private_consideration_item.v1"
STATUS = "research_only"
RUNTIME_POLICY = "runtime_dormant"
EXPERIMENT_ID = "design_preamble_ledger_overlap_v0"
DEFAULT_OUT_DIR = Path("research/pre-step6-private-consideration-ledgers")
ALLOWED_ITEM_TYPES = frozenset({"reasoning_card", "v60_chunk"})
ALLOWED_PRESENTATION_STATES = frozenset({"primary_presented", "supporting_ref_not_repeated"})
ALLOWED_DISPOSITIONS = frozenset(
    {"used", "rejected", "deferred", "not_considered", "private_guardrail"}
)
ALLOWED_COMPOSITION_ROLES = frozenset({"solo", "combined", "confirming", "blocker"})
ALLOWED_NOVELTY_ROLES = frozenset(
    {"visible_backbone", "additive_pressure", "confirming_support", "private_guardrail"}
)
REQUIRED_LEDGER_ITEM_FIELDS = frozenset(
    {
        "item_schema_version",
        "item_id",
        "item_type",
        "source_ref",
        "overlap_group_id",
        "presentation_state",
        "disposition",
        "composition_role",
        "novelty_role",
        "why",
        "visible_effect",
        "private_effect",
        "not_considered_reason",
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
        "deterministic_limit",
        "overlap_groups",
        "hot_context_items",
        "ledger_items",
        "gates",
        "notes",
    }
)
OVERLAP_GROUP_FIELDS = frozenset(
    {
        "overlap_group_id",
        "primary_presented_item_id",
        "supporting_item_refs",
        "presentation_policy",
        "ledger_policy",
    }
)
GATE_FIELDS = frozenset({"runtime_wiring_allowed", "skill_update_allowed"})


class PrivateConsiderationLedgerValidationError(ValueError):
    pass


def build_ledger_overlap_fixture(*, case_id: str, repo_root: Path) -> dict[str, object]:
    card_interface = build_private_reasoning_card_interface(case_id=case_id, repo_root=repo_root)
    validate_private_reasoning_card_interface_payload(card_interface)
    card = _card_by_id(card_interface, "bevelin_card")
    overlap_group_id = _overlap_group_id(case_id)
    reasoning_item = _reasoning_card_item(card=card, overlap_group_id=overlap_group_id)
    v60_item = _v60_item(overlap_group_id=overlap_group_id)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "case_id": case_id,
        "source_refs": {
            "private_reasoning_cards": (
                "research/pre-step6-private-reasoning-cards/"
                f"{case_id}.private-reasoning-cards.v1.json"
            ),
            "v60_fixture": "synthetic_v60_overlap_fixture:overcommitment_without_evidence",
        },
        "deterministic_limit": (
            "Code groups overlap and preserves custody; Step 6 still decides usefulness."
        ),
        "overlap_groups": [
            {
                "overlap_group_id": overlap_group_id,
                "primary_presented_item_id": "reasoning_card:bevelin_card",
                "supporting_item_refs": [
                    "reasoning_card:bevelin_card",
                    "v60_chunk:overcommitment_without_evidence",
                ],
                "presentation_policy": "single_representative_with_supporting_refs",
                "ledger_policy": "all_source_items_preserved",
            }
        ],
        "hot_context_items": [reasoning_item],
        "ledger_items": [reasoning_item, v60_item],
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": (
            "Research-only overlap fixture. The V60-style item is synthetic and "
            "exists to test ledger shape, not to claim a real V60 selection."
        ),
    }
    validate_ledger_overlap_payload(payload)
    return payload


def build_non_overlap_fixture(*, case_id: str, repo_root: Path) -> dict[str, object]:
    card_interface = build_private_reasoning_card_interface(case_id=case_id, repo_root=repo_root)
    validate_private_reasoning_card_interface_payload(card_interface)
    card = _card_by_id(card_interface, "polya_card")
    reasoning_item = _non_overlap_reasoning_card_item(card=card)
    v60_item = _non_overlap_v60_item()
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "case_id": f"{case_id}.non-overlap",
        "source_refs": {
            "private_reasoning_cards": (
                "research/pre-step6-private-reasoning-cards/"
                f"{case_id}.private-reasoning-cards.v1.json"
            ),
            "v60_fixture": "synthetic_v60_non_overlap_fixture:absence_blocker_false_precision",
        },
        "deterministic_limit": (
            "Code groups overlap and preserves custody; Step 6 still decides usefulness."
        ),
        "overlap_groups": [],
        "hot_context_items": [reasoning_item, v60_item],
        "ledger_items": [reasoning_item, v60_item],
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": (
            "Research-only non-overlap fixture. Both items stay in hot context "
            "because no substantive overlap group applies."
        ),
    }
    validate_ledger_overlap_payload(payload)
    return payload


def build_v60_only_fixture(*, case_id: str) -> dict[str, object]:
    v60_item = _v60_only_item()
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "case_id": case_id,
        "source_refs": {
            "private_reasoning_cards": "",
            "v60_fixture": "synthetic_v60_only_fixture:standalone_margin_of_safety",
        },
        "deterministic_limit": (
            "Code groups overlap and preserves custody; Step 6 still decides usefulness."
        ),
        "overlap_groups": [],
        "hot_context_items": [v60_item],
        "ledger_items": [v60_item],
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": "Research-only V60-only fixture. No reasoning card deck is present.",
    }
    validate_ledger_overlap_payload(payload)
    return payload


def load_ledger_overlap_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise PrivateConsiderationLedgerValidationError(f"{path}: payload must be an object")
    return payload


def validate_ledger_overlap_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_ledger_overlap_errors(payload, path=Path(path)))
    if errors:
        raise PrivateConsiderationLedgerValidationError("; ".join(errors))


def validate_ledger_overlap_file(path: Path) -> None:
    validate_ledger_overlap_payload(load_ledger_overlap_payload(path), path=Path(path))


def iter_ledger_overlap_errors(
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
    if _string(payload.get("deterministic_limit")) != (
        "Code groups overlap and preserves custody; Step 6 still decides usefulness."
    ):
        yield f"{path / 'deterministic_limit'}: invalid deterministic limit"
    yield from _validate_overlap_groups(payload.get("overlap_groups"), path / "overlap_groups")
    yield from _validate_items(payload.get("hot_context_items"), path / "hot_context_items")
    yield from _validate_items(payload.get("ledger_items"), path / "ledger_items")
    yield from _validate_hot_context_subset(payload, path)
    yield from _validate_gates(payload.get("gates"), path / "gates")


def write_ledger_overlap_fixture(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_ledger_overlap_payload(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{_string(payload['case_id'])}.ledger-overlap.v1.json"
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return out_path


def _reasoning_card_item(*, card: dict[str, object], overlap_group_id: str) -> dict[str, object]:
    return {
        "item_schema_version": ITEM_SCHEMA_VERSION,
        "item_id": "reasoning_card:bevelin_card",
        "item_type": "reasoning_card",
        "source_ref": _string(card.get("source_ref")),
        "overlap_group_id": overlap_group_id,
        "presentation_state": "primary_presented",
        "disposition": "not_considered",
        "composition_role": "combined",
        "novelty_role": "additive_pressure",
        "why": (
            "Representative hot-context item for commitment-before-proof and "
            "overconfidence pressure."
        ),
        "visible_effect": "",
        "private_effect": "",
        "not_considered_reason": "Awaiting Step 6 consideration.",
    }


def _v60_item(*, overlap_group_id: str) -> dict[str, object]:
    return {
        "item_schema_version": ITEM_SCHEMA_VERSION,
        "item_id": "v60_chunk:overcommitment_without_evidence",
        "item_type": "v60_chunk",
        "source_ref": "synthetic_v60_overlap_fixture:overcommitment_without_evidence",
        "overlap_group_id": overlap_group_id,
        "presentation_state": "supporting_ref_not_repeated",
        "disposition": "not_considered",
        "composition_role": "confirming",
        "novelty_role": "confirming_support",
        "why": (
            "Preserved as custody support for the same overcommitment pressure "
            "without repeating it in hot context."
        ),
        "visible_effect": "",
        "private_effect": "",
        "not_considered_reason": "Awaiting Step 6 consideration.",
    }


def _non_overlap_reasoning_card_item(*, card: dict[str, object]) -> dict[str, object]:
    return {
        "item_schema_version": ITEM_SCHEMA_VERSION,
        "item_id": "reasoning_card:polya_card",
        "item_type": "reasoning_card",
        "source_ref": _string(card.get("source_ref")),
        "overlap_group_id": "",
        "presentation_state": "primary_presented",
        "disposition": "not_considered",
        "composition_role": "solo",
        "novelty_role": "additive_pressure",
        "why": "Problem-shape pressure is orthogonal to the synthetic V60 absence blocker.",
        "visible_effect": "",
        "private_effect": "",
        "not_considered_reason": "Awaiting Step 6 consideration.",
    }


def _non_overlap_v60_item() -> dict[str, object]:
    return {
        "item_schema_version": ITEM_SCHEMA_VERSION,
        "item_id": "v60_chunk:absence_blocker_false_precision",
        "item_type": "v60_chunk",
        "source_ref": "synthetic_v60_non_overlap_fixture:absence_blocker_false_precision",
        "overlap_group_id": "",
        "presentation_state": "primary_presented",
        "disposition": "not_considered",
        "composition_role": "blocker",
        "novelty_role": "private_guardrail",
        "why": "Standalone absence blocker should remain visible to Step 6 when it is not redundant with the card.",
        "visible_effect": "",
        "private_effect": "",
        "not_considered_reason": "Awaiting Step 6 consideration.",
    }


def _v60_only_item() -> dict[str, object]:
    return {
        "item_schema_version": ITEM_SCHEMA_VERSION,
        "item_id": "v60_chunk:standalone_margin_of_safety",
        "item_type": "v60_chunk",
        "source_ref": "synthetic_v60_only_fixture:standalone_margin_of_safety",
        "overlap_group_id": "",
        "presentation_state": "primary_presented",
        "disposition": "not_considered",
        "composition_role": "solo",
        "novelty_role": "additive_pressure",
        "why": "Standalone V60 item proves the unified ledger works without a card deck.",
        "visible_effect": "",
        "private_effect": "",
        "not_considered_reason": "Awaiting Step 6 consideration.",
    }


def _validate_overlap_groups(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, list):
        yield f"{path}: must be a list"
        return
    for index, group in enumerate(value):
        group_path = path / str(index)
        if not isinstance(group, dict):
            yield f"{group_path}: must be an object"
            continue
        yield from _unknown_fields(group, OVERLAP_GROUP_FIELDS, group_path)
        yield from _missing_fields(group, OVERLAP_GROUP_FIELDS, group_path)
        if not _string(group.get("overlap_group_id")):
            yield f"{group_path / 'overlap_group_id'}: must be non-empty"
        if not _string(group.get("primary_presented_item_id")):
            yield f"{group_path / 'primary_presented_item_id'}: must be non-empty"
        refs = group.get("supporting_item_refs")
        if not isinstance(refs, list) or len(refs) < 2:
            yield f"{group_path / 'supporting_item_refs'}: must contain at least two refs"
        if group.get("presentation_policy") != "single_representative_with_supporting_refs":
            yield f"{group_path / 'presentation_policy'}: invalid policy"
        if group.get("ledger_policy") != "all_source_items_preserved":
            yield f"{group_path / 'ledger_policy'}: invalid policy"


def _validate_items(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, list) or not value:
        yield f"{path}: must be a non-empty list"
        return
    for index, item in enumerate(value):
        item_path = path / str(index)
        if not isinstance(item, dict):
            yield f"{item_path}: must be an object"
            continue
        fields = set(item)
        if fields != REQUIRED_LEDGER_ITEM_FIELDS:
            missing = sorted(REQUIRED_LEDGER_ITEM_FIELDS - fields)
            extra = sorted(fields - REQUIRED_LEDGER_ITEM_FIELDS)
            if missing:
                yield f"{item_path}: missing item fields: {', '.join(missing)}"
            if extra:
                yield f"{item_path}: unknown item fields: {', '.join(extra)}"
        if item.get("item_schema_version") != ITEM_SCHEMA_VERSION:
            yield f"{item_path / 'item_schema_version'}: must be {ITEM_SCHEMA_VERSION}"
        if _string(item.get("item_type")) not in ALLOWED_ITEM_TYPES:
            yield f"{item_path / 'item_type'}: unsupported item type"
        if _string(item.get("presentation_state")) not in ALLOWED_PRESENTATION_STATES:
            yield f"{item_path / 'presentation_state'}: unsupported presentation state"
        if _string(item.get("disposition")) not in ALLOWED_DISPOSITIONS:
            yield f"{item_path / 'disposition'}: unsupported disposition"
        if _string(item.get("composition_role")) not in ALLOWED_COMPOSITION_ROLES:
            yield f"{item_path / 'composition_role'}: unsupported composition role"
        if _string(item.get("novelty_role")) not in ALLOWED_NOVELTY_ROLES:
            yield f"{item_path / 'novelty_role'}: unsupported novelty role"
        for field in ("item_id", "source_ref", "why", "not_considered_reason"):
            if not _string(item.get(field)).strip():
                yield f"{item_path / field}: must be non-empty"
        if item.get("presentation_state") == "supporting_ref_not_repeated" and not _string(
            item.get("overlap_group_id")
        ).strip():
            yield f"{item_path / 'overlap_group_id'}: supporting refs must name overlap group"


def _validate_hot_context_subset(payload: dict[str, object], path: Path) -> Iterable[str]:
    hot_items = payload.get("hot_context_items")
    ledger_items = payload.get("ledger_items")
    groups = payload.get("overlap_groups")
    if not isinstance(hot_items, list) or not isinstance(ledger_items, list) or not isinstance(groups, list):
        return
    hot_ids = {_string(item.get("item_id")) for item in hot_items if isinstance(item, dict)}
    ledger_ids = {_string(item.get("item_id")) for item in ledger_items if isinstance(item, dict)}
    if not hot_ids.issubset(ledger_ids):
        yield f"{path / 'hot_context_items'}: hot context items must be represented in ledger_items"
    for group in groups:
        if not isinstance(group, dict):
            continue
        primary = _string(group.get("primary_presented_item_id"))
        refs = group.get("supporting_item_refs")
        if primary not in hot_ids:
            yield f"{path / 'overlap_groups'}: primary item must be in hot context"
        if isinstance(refs, list) and set(_string(ref) for ref in refs) != ledger_ids:
            yield f"{path / 'overlap_groups'}: supporting refs must match ledger item ids"


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


def _card_by_id(payload: dict[str, object], card_id: str) -> dict[str, object]:
    cards = payload.get("cards")
    if not isinstance(cards, list):
        raise PrivateConsiderationLedgerValidationError("cards missing")
    for card in cards:
        if isinstance(card, dict) and card.get("card_id") == card_id:
            return card
    raise PrivateConsiderationLedgerValidationError(f"{card_id} missing")


def _overlap_group_id(case_id: str) -> str:
    if case_id == "founder-grant-marcus-equity.high-clutter":
        return "founder_overcommitment_without_evidence_001"
    return f"{case_id.replace('.', '_').replace('-', '_')}_overlap_001"


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
    parser.add_argument("paths", nargs="*", type=Path, help="Existing ledger-overlap payloads to validate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--case-id", default="founder-grant-marcus-equity.high-clutter")
    parser.add_argument("--fixture-kind", choices=("overlap", "non_overlap", "v60_only"), default="overlap")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.paths:
        for path in args.paths:
            validate_ledger_overlap_file(path)
        return 0
    if args.fixture_kind == "non_overlap":
        payload = build_non_overlap_fixture(case_id=args.case_id, repo_root=args.repo_root)
    elif args.fixture_kind == "v60_only":
        payload = build_v60_only_fixture(case_id=args.case_id)
    else:
        payload = build_ledger_overlap_fixture(case_id=args.case_id, repo_root=args.repo_root)
    if args.write:
        print(write_ledger_overlap_fixture(payload=payload, out_dir=args.out_dir))
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
