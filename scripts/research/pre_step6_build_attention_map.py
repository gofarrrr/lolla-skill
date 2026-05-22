#!/usr/bin/env python3
"""Assemble a research-only Step 6 attention map from affordance records."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from pre_step6_attention_maps import (
    STEP6_ATTENTION_MAP_SCHEMA_VERSION,
    validate_step6_attention_map_payload,
)


def build_step6_attention_map(
    *,
    case_id: str,
    problem_state: dict[str, object],
    affordances: Sequence[dict[str, object]],
    full_archive_refs: Sequence[str],
) -> dict[str, object]:
    source_refs = _unique(
        [
            *[_string(ref) for ref in problem_state.get("source_refs", [])],
            *[
                _string(ref)
                for affordance in affordances
                for ref in affordance.get("source_refs", [])
            ],
        ]
    )
    full_archive = _unique([_string(ref) for ref in full_archive_refs if _string(ref)])
    if not full_archive:
        full_archive = _unique(
            [
                _string(affordance.get("expansion_ref"))
                for affordance in affordances
                if _string(affordance.get("expansion_ref"))
            ]
        )

    active: list[dict[str, object]] = []
    edge: list[dict[str, object]] = []
    weak: list[dict[str, object]] = []
    parked: list[dict[str, object]] = []

    for affordance in affordances:
        weight = _string(affordance.get("attention_weight"))
        protected_slot = _string(affordance.get("protected_slot"))
        affordance_class = _string(affordance.get("affordance_class"))
        if weight == "active":
            active.append(_active_item(affordance))
        elif weight == "parked":
            parked.append(_parked_item(affordance))
        elif protected_slot != "none" and affordance_class != "negative_space":
            edge.append(_edge_item(affordance))
        elif affordance_class == "negative_space":
            weak.append(_weak_item(affordance))
        else:
            weak.append(_weak_item(affordance))

    if not active:
        active.append(
            {
                "artifact_id": "no_active_pressure",
                "why_available": "No active affordance was provided; preserve a no-extra-pressure receipt.",
                "step6_use": "Answer from the problem read and scan reserves before finalizing.",
                "boundary": "Do not invent active pressure just because the map exists.",
                "risk_if_ignored": "The answer may add unnecessary conceptual burden.",
                "expansion_ref": full_archive[0] if full_archive else source_refs[0],
            }
        )
    if not edge:
        edge.append(
            {
                "artifact_id": "no_edge_pressure",
                "protected_slot": "none",
                "why_available": "No protected edge affordance was provided.",
                "cheap_test": "Confirm no protected slot is needed before finalizing.",
                "risk_if_forced": "The answer may become cluttered.",
                "risk_if_ignored": "No known protected edge is lost.",
                "expansion_ref": full_archive[0] if full_archive else source_refs[0],
            }
        )
    if not weak:
        weak.append(
            {
                "artifact_id": "no_weak_receipt",
                "why_preserved": "No weak or negative-space receipt was provided.",
                "reactivate_if": "New uncertainty appears during Step 6 drafting.",
                "expansion_ref": full_archive[0] if full_archive else source_refs[0],
            }
        )
    if not parked:
        parked.append(
            {
                "artifact_id": "no_parked_receipt",
                "park_reason": "No parked receipt was provided.",
                "reactivate_if": "A protected edge is needed but absent from active material.",
                "expansion_ref": full_archive[0] if full_archive else source_refs[0],
            }
        )

    payload: dict[str, object] = {
        "schema_version": STEP6_ATTENTION_MAP_SCHEMA_VERSION,
        "status": "research_only",
        "runtime_policy": "runtime_dormant",
        "case_id": case_id,
        "source_refs": source_refs,
        "problem_read": {
            "user_goal": _string(problem_state.get("user_goal")),
            "problem_type": _string(problem_state.get("problem_type")),
            "suggested_next_move": _string(problem_state.get("suggested_next_move")),
        },
        "active_working_set": active,
        "edge_latticework_reserve": edge,
        "weak_or_negative_space_receipts": weak,
        "parked_but_preserved": parked,
        "ask_user_if_any": [],
        "review_admission": "none",
        "full_archive_refs": full_archive,
        "step6_instruction": (
            "Use this as an attention map, not as a verdict. Consider active "
            "pressure, scan the edge reserve before finalizing, and reject any "
            "item that fails its boundary. Do not expose internal labels."
        ),
    }
    validate_step6_attention_map_payload(payload)
    return payload


def _active_item(affordance: dict[str, object]) -> dict[str, object]:
    return {
        "artifact_id": _string(affordance.get("artifact_id")),
        "why_available": _string(affordance.get("selection_basis")),
        "step6_use": _string(affordance.get("cheap_test_for_step6")),
        "boundary": _string(affordance.get("hard_boundary")),
        "risk_if_ignored": _string(affordance.get("risk_if_ignored")),
        "expansion_ref": _string(affordance.get("expansion_ref")),
    }


def _edge_item(affordance: dict[str, object]) -> dict[str, object]:
    return {
        "artifact_id": _string(affordance.get("artifact_id")),
        "protected_slot": _string(affordance.get("protected_slot")),
        "why_available": _string(affordance.get("selection_basis")),
        "cheap_test": _string(affordance.get("cheap_test_for_step6")),
        "risk_if_forced": _string(affordance.get("risk_if_forced")),
        "risk_if_ignored": _string(affordance.get("risk_if_ignored")),
        "expansion_ref": _string(affordance.get("expansion_ref")),
    }


def _weak_item(affordance: dict[str, object]) -> dict[str, object]:
    return {
        "artifact_id": _string(affordance.get("artifact_id")),
        "why_preserved": _string(affordance.get("what_it_might_reveal")),
        "reactivate_if": _string(affordance.get("relaxation_condition")),
        "expansion_ref": _string(affordance.get("expansion_ref")),
    }


def _parked_item(affordance: dict[str, object]) -> dict[str, object]:
    return {
        "artifact_id": _string(affordance.get("artifact_id")),
        "park_reason": _string(affordance.get("selection_basis")),
        "reactivate_if": _string(affordance.get("relaxation_condition")),
        "expansion_ref": _string(affordance.get("expansion_ref")),
    }


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def _unique(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            output.append(value)
    return output


def _load_json(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: payload must be an object")
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--problem-state-file", required=True, type=Path)
    parser.add_argument("--affordance-file", action="append", type=Path, default=[])
    parser.add_argument("--full-archive-ref", action="append", default=[])
    parser.add_argument("--output-file", type=Path)
    args = parser.parse_args(argv)
    payload = build_step6_attention_map(
        case_id=args.case_id,
        problem_state=_load_json(args.problem_state_file),
        affordances=[_load_json(path) for path in args.affordance_file],
        full_archive_refs=args.full_archive_ref,
    )
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.output_file:
        args.output_file.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
