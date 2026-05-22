#!/usr/bin/env python3
"""Build a false-positive probe contract from shadow-harness candidates.

This is research-only glue. It turns shadow telemetry into a pre-registered
dual-reviewer probe packet; the telemetry itself remains non-adjudicative.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from pre_step6_false_positive_visibility_probe import (
    build_false_positive_probe_contract,
    validate_false_positive_probe_contract,
    write_false_positive_probe_contract,
)


DEFAULT_EVIDENCE_PATH = Path(
    "research/pre-step6-shadow-portfolio-evidence/fixed-suite-cache-hit.shadow-evidence-result.v1.json"
)
DEFAULT_OUT_DIR = Path("research/pre-step6-shadow-triggered-false-positive-probe")


class ShadowTriggeredProbeError(ValueError):
    pass


def build_shadow_triggered_false_positive_probe_contract(
    *,
    root: Path,
    evidence_path: Path = DEFAULT_EVIDENCE_PATH,
    max_cases: int = 3,
) -> dict[str, object]:
    root = Path(root)
    evidence_ref = evidence_path if evidence_path.is_absolute() else root / evidence_path
    evidence = _read_json(evidence_ref)
    records = _candidate_records(evidence)
    if len(records) < max_cases:
        raise ShadowTriggeredProbeError(
            f"need at least {max_cases} shadow-triggered candidates, found {len(records)}"
        )

    base = build_false_positive_probe_contract()
    base["probe_cases"] = [
        _probe_case(root=root, record=record) for record in records[:max_cases]
    ]
    base["notes"] = (
        "Shadow-triggered extension of false_positive_visibility_probe_v0. "
        "Cases were selected before reviewer calls because the shadow harness "
        "reported deck_visible_with_marker_entity_loss. Shadow telemetry is used "
        "only for candidate discovery, not adjudication."
    )
    validate_false_positive_probe_contract(base)
    return base


def _candidate_records(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    records = evidence.get("case_records")
    if not isinstance(records, list):
        raise ShadowTriggeredProbeError("evidence case_records missing")
    candidates: list[dict[str, Any]] = []
    for raw_record in records:
        if not isinstance(raw_record, dict):
            continue
        flags = raw_record.get("candidate_flags")
        if not isinstance(flags, dict):
            continue
        if flags.get("deck_visible_with_marker_entity_loss") is True:
            candidates.append(raw_record)
    return candidates


def _probe_case(*, root: Path, record: dict[str, Any]) -> dict[str, object]:
    case_id = str(record.get("case_id") or "")
    if not case_id:
        raise ShadowTriggeredProbeError("candidate record missing case_id")
    categories = [
        str(item)
        for item in record.get("marker_entity_loss_categories", [])
        if str(item).strip()
    ]
    categories_text = ", ".join(categories) if categories else "unspecified protected categories"
    anchor = _load_anchor_answer(root=root, case_id=case_id)
    deck = _load_deck_answer(root=root, case_id=case_id)
    brief = _load_case_brief(root=root, case_id=case_id)
    return {
        "case_id": case_id,
        "shape_id": "shadow_triggered_marker_entity_loss",
        "selection_timing": "pre_run",
        "case_brief": (
            f"{brief} Shadow telemetry flagged marker/entity-loss risk in: "
            f"{categories_text}."
        ),
        "pre_run_failure_hypothesis": (
            "If Step 6 marks the deck-aware answer additive and both reviewers "
            "prefer the anchor because concrete anchor payload was lost inside "
            "present-looking categories, this is a confirmed false positive."
        ),
        "expected_step6_signal": "additive_pressure_present",
        "false_positive_risk": [
            "Shadow harness flagged deck_visible_with_marker_entity_loss before reviewer calls.",
            f"Mechanistic payload telemetry flagged categories: {categories_text}.",
            (
                "The deck-aware answer may preserve category markers while losing "
                "specific anchor entities or sequencing details."
            ),
        ],
        "case_construction_status": "candidate_exemplar",
        "answer_candidates": {
            "anchor_visible": anchor,
            "deck_pressure": deck,
        },
    }


def _load_anchor_answer(*, root: Path, case_id: str) -> str:
    candidates = [
        root
        / "research"
        / "pre-step6-rendered-hybrid-answer-cores"
        / f"{case_id}.native.rendered-hybrid-answer-core.v1.json",
    ]
    if case_id.endswith(".v2"):
        candidates.append(
            root
            / "research"
            / "pre-step6-rendered-hybrid-answer-cores"
            / f"{case_id[:-3]}.native.rendered-hybrid-answer-core.v1.json"
        )
    for candidate in candidates:
        if candidate.exists():
            payload = _read_json(candidate)
            answer = str(payload.get("answer_core") or "")
            if answer.strip():
                return answer
    raise ShadowTriggeredProbeError(f"{case_id}: anchor answer missing")


def _load_deck_answer(*, root: Path, case_id: str) -> str:
    path = (
        root
        / "research"
        / "pre-step6-card-deck-replays"
        / f"{case_id}.card-deck-replay.v1.json"
    )
    payload = _read_json(path)
    output = payload.get("step6_output")
    if not isinstance(output, dict):
        raise ShadowTriggeredProbeError(f"{case_id}: deck replay output missing")
    answer = str(output.get("answer_core") or "")
    if not answer.strip():
        raise ShadowTriggeredProbeError(f"{case_id}: deck answer missing")
    return answer


def _load_case_brief(*, root: Path, case_id: str) -> str:
    problem_case_id = case_id[:-3] if case_id.endswith(".v2") else case_id
    path = (
        root
        / "research"
        / "pre-step6-problem-states"
        / f"{problem_case_id}.problem-state.v1.json"
    )
    if not path.exists():
        return f"Fixed-suite case {case_id}."
    payload = _read_json(path)
    parts = [
        str(payload.get("user_goal") or "").strip(),
        str(payload.get("success_condition") or "").strip(),
    ]
    brief = " ".join(part for part in parts if part)
    return brief or f"Fixed-suite case {case_id}."


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ShadowTriggeredProbeError(f"{path}: payload must be an object")
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--evidence-path", type=Path, default=DEFAULT_EVIDENCE_PATH)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    out_dir = args.out_dir if args.out_dir.is_absolute() else root / args.out_dir
    contract = build_shadow_triggered_false_positive_probe_contract(
        root=root,
        evidence_path=args.evidence_path,
    )
    if args.write:
        print(write_false_positive_probe_contract(payload=contract, out_dir=out_dir))
    else:
        print(json.dumps(contract, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
