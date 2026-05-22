#!/usr/bin/env python3
"""Build the consultant-triggered false-positive probe contract.

The passive shadow harness surfaced a real case where the redesigned resolver
would record deck-visible in shadow: mid-level-consultant-report-2. This script
turns that discovery into a falsifiable false-positive probe batch using the
existing false-positive visibility probe schema and runner.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from pre_step6_false_positive_visibility_probe import (
    build_false_positive_probe_contract,
    validate_false_positive_probe_contract,
)

DEFAULT_OUT_DIR = Path("research/pre-step6-consultant-triggered-false-positive-probe")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _consultant_case(root: Path) -> dict[str, object]:
    anchor = _read_json(
        root
        / "research"
        / "pre-step6-rendered-hybrid-answer-cores"
        / "mid-level-consultant-report-2.native.rendered-hybrid-answer-core.v1.json"
    )
    replay = _read_json(
        root
        / "research"
        / "pre-step6-card-deck-replays"
        / "mid-level-consultant-report-2.card-deck-replay.v1.json"
    )
    return {
        "case_id": "mid-level-consultant-report-2",
        "shape_id": "consultant_shadow_triggered_positive_seed",
        "selection_timing": "pre_run",
        "case_brief": (
            "Mid-level consultant observed a partner's suspicious document-handling "
            "behavior in a legal/safety-sensitive reporting situation. "
            "pre-registered classification: positive_seed. The prior calibration "
            "manifest mislabeled this as negative_control_seed, but the card-deck "
            "comparison and the shadow harness fired deck_visible_shadow_only."
        ),
        "pre_run_failure_hypothesis": (
            "If both reviewers prefer the anchor over the deck-aware answer, the "
            "consultant reclassification is wrong and this is a confirmed false "
            "positive for the redesigned resolver on a real fixed-suite case."
        ),
        "expected_step6_signal": "additive_pressure_present",
        "false_positive_risk": [
            "The manifest previously mislabeled this as negative_control_seed.",
            "The deck-aware answer may be merely shorter rather than materially better.",
            "A counsel-first safety case can be harmed if additive pressure creates overconfidence.",
        ],
        "case_construction_status": "candidate_exemplar",
        "answer_candidates": {
            "anchor_visible": str(anchor.get("answer_core") or ""),
            "deck_pressure": str((replay.get("step6_output") or {}).get("answer_core") or ""),
        },
    }


def build_consultant_triggered_contract(*, root: Path) -> dict[str, object]:
    base = build_false_positive_probe_contract()
    old_cases = {case["case_id"]: case for case in base["probe_cases"]}
    base["probe_cases"] = [
        _consultant_case(root),
        old_cases["fp-marker-preserved-entity-lost"],
        old_cases["fp-bevelin-irrelevant-incentives"],
    ]
    base["notes"] = (
        "Consultant-triggered extension of false_positive_visibility_probe_v0. "
        "The consultant case is pinned as a positive_seed before reviewer calls; "
        "reviewers may still falsify that classification through the normal "
        "two-family false-positive rule."
    )
    validate_false_positive_probe_contract(base)
    return base


def write_consultant_triggered_contract(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_false_positive_probe_contract(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "false-positive-visibility-probe.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    out_dir = args.out_dir if args.out_dir.is_absolute() else root / args.out_dir
    payload = build_consultant_triggered_contract(root=root)
    if args.write:
        print(write_consultant_triggered_contract(payload=payload, out_dir=out_dir))
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
