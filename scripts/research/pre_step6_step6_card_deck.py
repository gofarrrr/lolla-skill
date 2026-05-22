#!/usr/bin/env python3
"""Research-only private Step 6 card deck builder.

This artifact deliberately presents multiple cards to Step 6 instead of
selecting one. Deterministic code validates custody and renders the deck; Step 6
keeps cognitive authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence

from pre_step6_cognitive_gate_live import CASE_CONFIGS


CARD_DECK_SCHEMA_VERSION = "pre_step6_card_deck.v1"
CARD_DECK_RENDER_MAX_CHARS = 6200
STATUS = "research_only"
RUNTIME_POLICY = "runtime_dormant"
DEFAULT_OUT_DIR = Path("research/pre-step6-step6-card-decks")
CARD_IDS = ("clean_hybrid_card", "bevelin_card", "polya_card")
ALLOWED_SOURCE_KINDS = frozenset(
    {
        "rendered_hybrid_answer_core",
        "bevelin_lens_answer_core",
        "polya_lens_answer_core",
    }
)
ALLOWED_SELECTION_STATUS = frozenset({"presented_not_selected"})
ALLOWED_OVERLAP_HINTS = frozenset(
    {"literal_phrase_present_in_anchor", "not_a_literal_phrase_match"}
)
TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "source_refs",
        "problem_read",
        "deterministic_limit",
        "step6_consideration_contract",
        "cards",
        "render_policy",
        "gates",
        "notes",
    }
)
CONTRACT_FIELDS = frozenset(
    {
        "decision_authority",
        "consideration_standard",
        "public_hygiene",
        "beyond_obvious_rule",
        "novelty_discipline",
    }
)
PROBLEM_READ_FIELDS = frozenset(
    {
        "user_goal",
        "problem_type",
        "knowns",
        "unknowns",
        "constraints",
        "suggested_next_move",
    }
)
CARD_FIELDS = frozenset(
    {
        "card_id",
        "card_label",
        "source_kind",
        "source_ref",
        "cognitive_role",
        "selection_status",
        "anchor_text",
        "receipts",
        "receipt_annotations",
        "handling_rule",
    }
)
RECEIPT_ANNOTATION_FIELDS = frozenset(
    {"receipt", "deterministic_overlap_hint", "step6_question"}
)
RENDER_POLICY_FIELDS = frozenset(
    {"private_only", "max_chars", "include_all_cards", "allow_step6_to_reject_cards"}
)
GATE_FIELDS = frozenset({"runtime_wiring_allowed", "skill_update_allowed"})
FORBIDDEN_TERMS = (
    "best option",
    "correct answer",
    "final recommendation",
    "step 6 should conclude",
)


class Step6CardDeckValidationError(ValueError):
    pass


def build_step6_card_deck(*, case_id: str, repo_root: Path) -> dict[str, object]:
    config = _case_config(case_id)
    refs = _candidate_refs(config)
    problem_state_ref = _problem_state_ref(case_id=case_id, config=config, repo_root=repo_root)
    problem_state = _load_json(repo_root / problem_state_ref)
    rendered = _load_json(repo_root / refs["rendered_hybrid"])
    bevelin = _load_json(repo_root / refs["bevelin_lens"])
    polya = _load_json(repo_root / refs["polya_lens"])
    anchor_text = _answer_core(rendered)
    cards = [
        _clean_hybrid_card(anchor_text=anchor_text, source_ref=refs["rendered_hybrid"]),
        _lens_card(
            card_id="bevelin_card",
            card_label="Bevelin private card",
            source_kind="bevelin_lens_answer_core",
            source_ref=refs["bevelin_lens"],
            cognitive_role=(
                "Edge-pressure scan: incentives, dependency, false precision, "
                "commitment before proof, and inversion pressure."
            ),
            receipts=_lens_receipts(bevelin),
            anchor_text=anchor_text,
        ),
        _lens_card(
            card_id="polya_card",
            card_label="Polya private card",
            source_kind="polya_lens_answer_core",
            source_ref=refs["polya_lens"],
            cognitive_role=(
                "Problem-shape scan: knowns, unknowns, testable next move, "
                "sequence, and avoiding the wrong problem."
            ),
            receipts=_lens_receipts(polya),
            anchor_text=anchor_text,
        ),
    ]
    payload = {
        "schema_version": CARD_DECK_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "case_id": case_id,
        "source_refs": {**refs, "problem_state": problem_state_ref},
        "problem_read": _problem_read(problem_state),
        "deterministic_limit": (
            "Code validates custody, labels sources, and renders the deck; it does not decide cognitive usefulness."
        ),
        "step6_consideration_contract": {
            "decision_authority": (
                "Step 6 may use, reject, defer, or combine any card after serious consideration."
            ),
            "consideration_standard": (
                "For each card, form the strongest plausible application before setting it aside."
            ),
            "public_hygiene": (
                "Do not expose these private labels, source names, or card mechanics in the user-facing answer."
            ),
            "beyond_obvious_rule": (
                "Use the cards to go beyond the obvious when they reveal a non-obvious pressure, not to obey a template."
            ),
            "novelty_discipline": (
                "For each non-anchor card, decide whether it adds additive pressure, "
                "sharpens a condition, or is only confirming support. If it only "
                "confirms what the anchor already handles, keep it private unless "
                "restating it protects a concrete tripwire."
            ),
        },
        "cards": cards,
        "render_policy": {
            "private_only": True,
            "max_chars": CARD_DECK_RENDER_MAX_CHARS,
            "include_all_cards": True,
            "allow_step6_to_reject_cards": True,
        },
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": (
            "Research-only deck for testing whether Step 6 benefits from seeing "
            "clean hybrid, Bevelin, and Polya cards together without deterministic selection."
        ),
    }
    validate_step6_card_deck_payload(payload)
    return payload


def render_step6_card_deck(payload: dict[str, object]) -> str:
    validate_step6_card_deck_payload(payload)
    contract = payload["step6_consideration_contract"]
    assert isinstance(contract, dict)
    lines = [
        "STEP 6 PRIVATE CARD DECK",
        "",
        "Use this as private context: hints, not commands.",
        _string(contract["decision_authority"]),
        _string(contract["consideration_standard"]),
        _string(contract["beyond_obvious_rule"]),
        _string(contract["novelty_discipline"]),
        _string(contract["public_hygiene"]),
        "",
        f"DETERMINISTIC LIMIT: {_string(payload['deterministic_limit'])}",
        "",
    ]
    problem_read = payload["problem_read"]
    assert isinstance(problem_read, dict)
    lines.extend(
        [
            "PROBLEM READ",
            f"- Goal: {_string(problem_read['user_goal'])}",
            f"- Type: {_string(problem_read['problem_type'])}",
            f"- Move: {_string(problem_read['suggested_next_move'])}",
            "- Knowns:",
            *_render_list(problem_read["knowns"]),
            "- Unknowns:",
            *_render_list(problem_read["unknowns"]),
            "- Constraints:",
            *_render_list(problem_read["constraints"]),
            "",
        ]
    )
    for card in payload["cards"]:
        assert isinstance(card, dict)
        lines.extend(_render_card(card))
    rendered = "\n".join(lines).strip() + "\n"
    if len(rendered) > CARD_DECK_RENDER_MAX_CHARS:
        raise Step6CardDeckValidationError(
            f"rendered card deck exceeds {CARD_DECK_RENDER_MAX_CHARS} chars"
        )
    return rendered


def load_step6_card_deck_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise Step6CardDeckValidationError(f"{path}: payload must be an object")
    return payload


def validate_step6_card_deck_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_step6_card_deck_errors(payload, path=Path(path)))
    if errors:
        raise Step6CardDeckValidationError("; ".join(errors))


def validate_step6_card_deck_file(path: Path) -> None:
    validate_step6_card_deck_payload(load_step6_card_deck_payload(path), path=Path(path))


def iter_step6_card_deck_errors(
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

    if _string(payload.get("schema_version")) != CARD_DECK_SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {CARD_DECK_SCHEMA_VERSION}"
    if _string(payload.get("status")) != STATUS:
        yield f"{path / 'status'}: must be {STATUS}"
    if _string(payload.get("runtime_policy")) != RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: must be {RUNTIME_POLICY}"
    if not _string(payload.get("case_id")).strip():
        yield f"{path / 'case_id'}: must be non-empty"
    if _contains_forbidden_terms(payload):
        yield f"{path}: contains forbidden answer-selection language"

    yield from _validate_source_refs(payload.get("source_refs"), path / "source_refs")
    yield from _validate_problem_read(payload.get("problem_read"), path / "problem_read")
    if not _string(payload.get("deterministic_limit")).strip():
        yield f"{path / 'deterministic_limit'}: must be non-empty"
    yield from _validate_contract(
        payload.get("step6_consideration_contract"),
        path / "step6_consideration_contract",
    )
    yield from _validate_cards(payload.get("cards"), path / "cards")
    yield from _validate_render_policy(
        payload.get("render_policy"),
        path / "render_policy",
    )
    yield from _validate_gates(payload.get("gates"), path / "gates")


def _clean_hybrid_card(*, anchor_text: str, source_ref: str) -> dict[str, object]:
    return {
        "card_id": "clean_hybrid_card",
        "card_label": "Clean hybrid anchor",
        "source_kind": "rendered_hybrid_answer_core",
        "source_ref": source_ref,
        "cognitive_role": (
            "Concrete anchor: start from this because it preserves case-specific "
            "pressure in ordinary answer shape."
        ),
        "selection_status": "presented_not_selected",
        "anchor_text": anchor_text,
        "receipts": [],
        "receipt_annotations": [],
        "handling_rule": (
            "Use as the concrete starting anchor, but revise it if another card "
            "reveals pressure the anchor underweights."
        ),
    }


def _lens_card(
    *,
    card_id: str,
    card_label: str,
    source_kind: str,
    source_ref: str,
    cognitive_role: str,
    receipts: list[str],
    anchor_text: str,
) -> dict[str, object]:
    return {
        "card_id": card_id,
        "card_label": card_label,
        "source_kind": source_kind,
        "source_ref": source_ref,
        "cognitive_role": cognitive_role,
        "selection_status": "presented_not_selected",
        "anchor_text": "",
        "receipts": receipts,
        "receipt_annotations": [
            {
                "receipt": receipt,
                "deterministic_overlap_hint": _literal_overlap_hint(
                    receipt=receipt,
                    anchor_text=anchor_text,
                ),
                "step6_question": (
                    "Does this add decision pressure beyond the clean hybrid anchor, "
                    "or is it only a different wording of material already present?"
                ),
            }
            for receipt in receipts
        ],
        "handling_rule": (
            "Give this card a serious hearing. Use, reject, defer, or combine it; "
            "do not treat source identity as proof."
        ),
    }


def _render_card(card: dict[str, object]) -> list[str]:
    lines = [
        f"CARD: {_string(card['card_label'])}",
        f"- Private role: {_string(card['cognitive_role'])}",
        f"- Handling: {_string(card['handling_rule'])}",
    ]
    anchor = _string(card.get("anchor_text"))
    if anchor:
        lines.extend(["- Anchor text:", _indent_block(anchor)])
    receipts = card.get("receipts")
    if isinstance(receipts, list) and receipts:
        lines.append("- Receipts:")
        for annotation in card["receipt_annotations"]:
            assert isinstance(annotation, dict)
            lines.append(f"  - {_string(annotation['receipt'])}")
            lines.append(
                f"    deterministic hint: {_string(annotation['deterministic_overlap_hint'])}"
            )
            lines.append(f"    Step 6 question: {_string(annotation['step6_question'])}")
    lines.append("")
    return lines


def _case_config(case_id: str) -> dict[str, object]:
    if case_id in CASE_CONFIGS:
        return CASE_CONFIGS[case_id]
    aliases = {
        _string(config.get("case_id")): key
        for key, config in CASE_CONFIGS.items()
        if _string(config.get("case_id"))
    }
    if case_id in aliases:
        return CASE_CONFIGS[aliases[case_id]]
    raise Step6CardDeckValidationError(f"unknown fixed-suite case: {case_id}")


def _candidate_refs(config: dict[str, object]) -> dict[str, str]:
    refs = config.get("candidate_refs")
    if not isinstance(refs, dict):
        raise Step6CardDeckValidationError("case config candidate_refs must be an object")
    required = ("rendered_hybrid", "bevelin_lens", "polya_lens")
    result = {field: str(refs.get(field, "")) for field in required}
    for field, ref in result.items():
        if not ref:
            raise Step6CardDeckValidationError(f"missing candidate ref: {field}")
    return result


def _problem_state_ref(
    *,
    case_id: str,
    config: dict[str, object],
    repo_root: Path,
) -> str:
    candidates = [
        f"research/pre-step6-problem-states/{case_id}.problem-state.v1.json",
    ]
    config_case_id = _string(config.get("case_id"))
    if config_case_id:
        candidates.append(
            f"research/pre-step6-problem-states/{config_case_id}.problem-state.v1.json"
        )
    if case_id.endswith(".v2"):
        candidates.append(
            f"research/pre-step6-problem-states/{case_id.removesuffix('.v2')}.problem-state.v1.json"
        )
    for ref in candidates:
        if (repo_root / ref).exists():
            return ref
    raise Step6CardDeckValidationError(f"problem_state missing for case: {case_id}")


def _problem_read(problem_state: dict[str, object]) -> dict[str, object]:
    return {
        "user_goal": _string(problem_state.get("user_goal")),
        "problem_type": _string(problem_state.get("problem_type")),
        "knowns": _string_list(problem_state.get("knowns")),
        "unknowns": _string_list(problem_state.get("unknowns")),
        "constraints": _string_list(problem_state.get("constraints")),
        "suggested_next_move": _string(problem_state.get("suggested_next_move")),
    }


def _load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        raise Step6CardDeckValidationError(f"candidate artifact missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise Step6CardDeckValidationError(f"{path}: payload must be an object")
    return payload


def _answer_core(payload: dict[str, object]) -> str:
    answer = payload.get("answer_core")
    if not isinstance(answer, str) or not answer.strip():
        raise Step6CardDeckValidationError("answer_core must be non-empty")
    return answer


def _lens_receipts(payload: dict[str, object]) -> list[str]:
    effect = payload.get("lens_effect")
    if not isinstance(effect, dict):
        raise Step6CardDeckValidationError("lens_effect must be present")
    receipts = _string_list(effect.get("changed_by_lens"))
    if not receipts:
        raise Step6CardDeckValidationError("changed_by_lens must be non-empty")
    return receipts


def _literal_overlap_hint(*, receipt: str, anchor_text: str) -> str:
    return (
        "literal_phrase_present_in_anchor"
        if receipt.lower() in anchor_text.lower()
        else "not_a_literal_phrase_match"
    )


def _validate_source_refs(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: source_refs must be an object"
        return
    required = ("rendered_hybrid", "bevelin_lens", "polya_lens", "problem_state")
    yield from _missing_fields(value, required, path)
    for field in required:
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    for field in sorted(set(value) - set(required)):
        yield f"{path / field}: unknown field"


def _validate_problem_read(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: problem_read must be an object"
        return
    yield from _unknown_fields(value, PROBLEM_READ_FIELDS, path)
    yield from _missing_fields(value, tuple(PROBLEM_READ_FIELDS), path)
    if any(field not in value for field in PROBLEM_READ_FIELDS):
        return
    for field in ("user_goal", "problem_type", "suggested_next_move"):
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    for field in ("knowns", "unknowns", "constraints"):
        if not _string_list(value.get(field)):
            yield f"{path / field}: must be a non-empty string list"


def _validate_contract(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: step6_consideration_contract must be an object"
        return
    yield from _unknown_fields(value, CONTRACT_FIELDS, path)
    yield from _missing_fields(value, tuple(CONTRACT_FIELDS), path)
    for field in CONTRACT_FIELDS:
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"


def _validate_cards(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, list):
        yield f"{path}: cards must be a list"
        return
    ids = [
        _string(card.get("card_id")) if isinstance(card, dict) else ""
        for card in value
    ]
    if tuple(ids) != CARD_IDS:
        yield f"{path}: cards must be clean_hybrid_card, bevelin_card, polya_card"
    for index, card in enumerate(value):
        card_path = path / f"[{index}]"
        if not isinstance(card, dict):
            yield f"{card_path}: card must be an object"
            continue
        yield from _unknown_fields(card, CARD_FIELDS, card_path)
        yield from _missing_fields(card, tuple(CARD_FIELDS), card_path)
        if any(field not in card for field in CARD_FIELDS):
            continue
        for field in (
            "card_id",
            "card_label",
            "source_kind",
            "source_ref",
            "cognitive_role",
            "selection_status",
            "handling_rule",
        ):
            if not _string(card.get(field)).strip():
                yield f"{card_path / field}: must be non-empty"
        if _string(card.get("source_kind")) not in ALLOWED_SOURCE_KINDS:
            yield f"{card_path / 'source_kind'}: unknown source_kind"
        if _string(card.get("selection_status")) not in ALLOWED_SELECTION_STATUS:
            yield f"{card_path / 'selection_status'}: unknown selection_status"
        if _string(card.get("card_id")) == "clean_hybrid_card":
            if not _string(card.get("anchor_text")).strip():
                yield f"{card_path / 'anchor_text'}: clean hybrid card needs anchor_text"
            if card.get("receipts") != []:
                yield f"{card_path / 'receipts'}: clean hybrid card receipts must be empty"
        else:
            if _string(card.get("anchor_text")).strip():
                yield f"{card_path / 'anchor_text'}: lens cards should not duplicate anchor text"
            receipts = _string_list(card.get("receipts"))
            if not receipts:
                yield f"{card_path / 'receipts'}: lens cards need receipts"
            yield from _validate_annotations(
                card.get("receipt_annotations"),
                receipts=receipts,
                path=card_path / "receipt_annotations",
            )


def _validate_annotations(
    value: object,
    *,
    receipts: list[str],
    path: Path,
) -> Iterable[str]:
    if not isinstance(value, list):
        yield f"{path}: receipt_annotations must be a list"
        return
    if len(value) != len(receipts):
        yield f"{path}: one annotation is required per receipt"
    for index, annotation in enumerate(value):
        item_path = path / f"[{index}]"
        if not isinstance(annotation, dict):
            yield f"{item_path}: annotation must be an object"
            continue
        yield from _unknown_fields(annotation, RECEIPT_ANNOTATION_FIELDS, item_path)
        yield from _missing_fields(annotation, tuple(RECEIPT_ANNOTATION_FIELDS), item_path)
        if any(field not in annotation for field in RECEIPT_ANNOTATION_FIELDS):
            continue
        if index < len(receipts) and _string(annotation.get("receipt")) != receipts[index]:
            yield f"{item_path / 'receipt'}: must match receipt order"
        if _string(annotation.get("deterministic_overlap_hint")) not in ALLOWED_OVERLAP_HINTS:
            yield f"{item_path / 'deterministic_overlap_hint'}: unknown overlap hint"
        if not _string(annotation.get("step6_question")).strip():
            yield f"{item_path / 'step6_question'}: must be non-empty"


def _validate_render_policy(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: render_policy must be an object"
        return
    yield from _unknown_fields(value, RENDER_POLICY_FIELDS, path)
    yield from _missing_fields(value, tuple(RENDER_POLICY_FIELDS), path)
    if value.get("private_only") is not True:
        yield f"{path / 'private_only'}: must be true"
    if value.get("include_all_cards") is not True:
        yield f"{path / 'include_all_cards'}: must be true"
    if value.get("allow_step6_to_reject_cards") is not True:
        yield f"{path / 'allow_step6_to_reject_cards'}: must be true"
    if value.get("max_chars") != CARD_DECK_RENDER_MAX_CHARS:
        yield f"{path / 'max_chars'}: must match CARD_DECK_RENDER_MAX_CHARS"


def _validate_gates(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: gates must be an object"
        return
    yield from _unknown_fields(value, GATE_FIELDS, path)
    yield from _missing_fields(value, tuple(GATE_FIELDS), path)
    if value.get("runtime_wiring_allowed") is not False:
        yield f"{path / 'runtime_wiring_allowed'}: must be false"
    if value.get("skill_update_allowed") is not False:
        yield f"{path / 'skill_update_allowed'}: must be false"


def _contains_forbidden_terms(payload: dict[str, object]) -> bool:
    blob = json.dumps(payload, ensure_ascii=False).lower()
    return any(term in blob for term in FORBIDDEN_TERMS)


def _indent_block(text: str) -> str:
    return "\n".join(f"  {line}" if line else "" for line in text.splitlines())


def _render_list(value: object) -> list[str]:
    return [f"  - {item}" for item in _string_list(value)]


def _unknown_fields(
    payload: dict[str, object],
    allowed: frozenset[str],
    path: Path,
) -> Iterable[str]:
    for field in sorted(set(payload) - allowed):
        yield f"{path / field}: unknown field"


def _missing_fields(
    payload: dict[str, object],
    required: Sequence[str],
    path: Path,
) -> Iterable[str]:
    for field in required:
        if field not in payload:
            yield f"{path / field}: missing required field"


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _parse_case_ids(args: argparse.Namespace) -> list[str]:
    if args.all:
        return list(CASE_CONFIGS)
    if args.case_id:
        return args.case_id
    raise Step6CardDeckValidationError("provide --case-id or --all")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--render", action="store_true")
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args(argv)

    if args.paths:
        for path in args.paths:
            validate_step6_card_deck_file(path)
            if args.render:
                print(render_step6_card_deck(load_step6_card_deck_payload(path)))
        return 0

    outputs: list[Path] = []
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for case_id in _parse_case_ids(args):
        payload = build_step6_card_deck(case_id=case_id, repo_root=args.repo_root)
        artifact_slug = _string(_case_config(case_id).get("artifact_slug")) or case_id
        out_path = args.out_dir / f"{artifact_slug}.step6-card-deck.v1.json"
        out_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        validate_step6_card_deck_file(out_path)
        outputs.append(out_path)
        print(out_path)
        if args.render:
            print(render_step6_card_deck(payload))
    if outputs:
        print(f"wrote {len(outputs)} Step 6 card deck(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
