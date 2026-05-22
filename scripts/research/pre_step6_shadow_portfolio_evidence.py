#!/usr/bin/env python3
"""Build repeatable shadow evidence for the dormant pre-Step-6 portfolio.

This script spends no model calls. It either:

1. reads prior result JSON files and records cache-miss shadow artifacts; or
2. materializes fixed-suite card decks into a local cache, normalizes existing
   Step 6 replay ledgers, and records cache-hit shadow artifacts.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from engine.system_b.pre_step6_shadow_portfolio import (
    build_pre_step6_shadow_portfolio,
    validate_pre_step6_shadow_portfolio,
)

SCHEMA_VERSION = "pre_step6_shadow_portfolio_evidence.v1"
DEFAULT_FIXED_CASE_IDS = (
    "founder-grant-marcus-equity.high-clutter",
    "third-year-phd-student.v2",
    "mid-level-consultant-report-2",
    "mother-address-year",
)
DEFAULT_RESULT_GLOBS = (
    "research/test-cases/phase2d-lane2-equivalence-2026-04-24/_scratch/*_new_run2.json",
    "research/test-cases/phase2d-lane2-equivalence-2026-04-24/_scratch/*_new_run1.json",
    "research/test-cases/phase2d-lane2-equivalence-2026-04-24/_scratch/*_new_run0.json",
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _counter_dict(values: list[str]) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))


def _case_slug_from_result_path(path: Path) -> str:
    return path.stem.replace("_", "-")


def _deck_path(root: Path, case_id: str) -> Path:
    return root / "research" / "pre-step6-step6-card-decks" / f"{case_id}.step6-card-deck.v1.json"


def _replay_path(root: Path, case_id: str) -> Path:
    return (
        root
        / "research"
        / "pre-step6-card-deck-replays"
        / f"{case_id}.card-deck-replay.v1.json"
    )


def _payload_gate_path(root: Path, case_id: str) -> Path:
    return (
        root
        / "research"
        / "pre-step6-payload-omission-gates"
        / f"{case_id}.payload-omission.v1.json"
    )


def _problem_state_path(root: Path, case_id: str) -> Path:
    problem_case_id = case_id[:-3] if case_id.endswith(".v2") else case_id
    return (
        root
        / "research"
        / "pre-step6-problem-states"
        / f"{problem_case_id}.problem-state.v1.json"
    )


def _rendered_anchor_path(root: Path, case_id: str) -> Path:
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
            return candidate
    return candidates[0]


def _fixed_case_result_payload(root: Path, case_id: str) -> dict[str, Any]:
    problem = _read_json(_problem_state_path(root, case_id))
    anchor_path = _rendered_anchor_path(root, case_id)
    anchor = _read_json(anchor_path) if anchor_path.exists() else {}
    deck = _read_json(_deck_path(root, case_id))
    problem_read = deck.get("problem_read") if isinstance(deck.get("problem_read"), dict) else {}
    return {
        "extraction": {
            "decision_situation": problem.get("user_goal")
            or problem_read.get("user_goal")
            or problem.get("case_id")
            or case_id,
            "original_framing": problem.get("success_condition")
            or problem_read.get("suggested_next_move")
            or "",
        },
        "prompt_versions": {
            "pre_step6_shadow_portfolio": "v1",
            "pre_step6_card_deck": str(deck.get("schema_version") or ""),
            "source_case_id": case_id,
        },
        "v60_enrichment": {
            "status": "not_attached_to_shadow_research_fixture",
            "telemetry": {"selected_chunk_ids": []},
        },
        "revised_answer": anchor.get("answer_core") or "",
    }


def _normalize_replay_ledger(replay: dict[str, Any]) -> dict[str, Any]:
    raw_items = (
        replay.get("step6_output", {}).get("private_card_consideration_ledger")
        if isinstance(replay.get("step6_output"), dict)
        else []
    )
    items = []
    for raw_item in raw_items if isinstance(raw_items, list) else []:
        if not isinstance(raw_item, dict):
            continue
        source_id = raw_item.get("source_id") or raw_item.get("card_id") or ""
        if not source_id:
            continue
        items.append(
            {
                "source_id": str(source_id),
                "disposition": str(raw_item.get("disposition") or ""),
                "novelty_role": str(raw_item.get("novelty_role") or ""),
                "why": str(raw_item.get("why") or ""),
                "visible_effect": str(raw_item.get("visible_effect") or ""),
                "answer_delta": raw_item["answer_delta"]
                if isinstance(raw_item.get("answer_delta"), dict)
                else {},
            }
        )
    return {
        "schema_version": "pre_step6_shadow_step6_ledger.v1",
        "source": "normalized_from_pre_step6_card_deck_replay",
        "items": items,
    }


def _payload_gate_result(payload_gate: dict[str, Any]) -> str:
    return str(
        payload_gate.get("gate_result")
        or payload_gate.get("status")
        or "not_supplied"
    )


def _payload_category_outcome(category: dict[str, Any]) -> str:
    judgment = str(category.get("judgment") or "")
    if judgment == "preserved":
        missing = category.get("missing_anchor_evidence")
        if isinstance(missing, list) and missing:
            return "preserved_by_marker_anchor_entities_missing"
        return "preserved_marker_and_anchor_entities"
    if judgment == "introduced_omission":
        return "introduced_category_omission"
    if judgment == "deck_added_payload":
        return "deck_added_payload"
    return "case_n_a"


def _payload_preservation_outcomes(payload_gate: dict[str, Any]) -> dict[str, str]:
    categories = payload_gate.get("categories")
    if not isinstance(categories, list):
        return {}
    outcomes: dict[str, str] = {}
    for raw_category in categories:
        if not isinstance(raw_category, dict):
            continue
        category = str(raw_category.get("category") or "")
        if not category:
            continue
        outcomes[category] = _payload_category_outcome(raw_category)
    return dict(sorted(outcomes.items()))


def _candidate_flags(*, decision: str, marker_entity_loss_categories: list[str]) -> dict[str, bool]:
    return {
        "deck_visible_with_marker_entity_loss": bool(
            decision == "deck_visible_shadow_only" and marker_entity_loss_categories
        )
    }


def _write_shadow_artifact(
    *,
    output_dir: Path,
    arm: str,
    case_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    validate_pre_step6_shadow_portfolio(payload)
    path = output_dir / arm / f"{case_id}.pre-step6-shadow-portfolio.v1.json"
    _write_json(path, payload)
    payload_gate = payload.get("payload_gate") if isinstance(payload.get("payload_gate"), dict) else {}
    outcomes = _payload_preservation_outcomes(payload_gate)
    marker_entity_loss_categories = [
        category
        for category, outcome in outcomes.items()
        if outcome == "preserved_by_marker_anchor_entities_missing"
    ]
    decision = str((payload.get("shadow_visibility_decision") or {}).get("result") or "")
    return {
        "case_id": case_id,
        "artifact_ref": str(path),
        "status": str(payload.get("status") or ""),
        "cache_state": str((payload.get("cache") or {}).get("state") or ""),
        "step6_ledger_signal": str(payload.get("step6_ledger_signal") or ""),
        "answer_delta_specificity": str(payload.get("answer_delta_specificity") or ""),
        "decision": decision,
        "applied_to_user_visible_output": bool(
            (payload.get("shadow_visibility_decision") or {}).get(
                "applied_to_user_visible_output"
            )
        ),
        "payload_gate_result": _payload_gate_result(payload_gate),
        "payload_preservation_outcomes": outcomes,
        "payload_preservation_outcome_counts": _counter_dict(list(outcomes.values())),
        "marker_entity_loss_categories": marker_entity_loss_categories,
        "candidate_flags": _candidate_flags(
            decision=decision,
            marker_entity_loss_categories=marker_entity_loss_categories,
        ),
    }


def _aggregate(*, arm: str, output_dir: Path, case_records: list[dict[str, Any]]) -> dict[str, Any]:
    aggregate = {
        "schema_version": SCHEMA_VERSION,
        "arm": arm,
        "runtime_effect": "none_shadow_only",
        "output_dir": str(output_dir),
        "case_records": case_records,
        "aggregate": {
            "total_cases": len(case_records),
            "cache_states": _counter_dict([r["cache_state"] for r in case_records]),
            "ledger_signals": _counter_dict([r["step6_ledger_signal"] for r in case_records]),
            "answer_delta_specificity": _counter_dict(
                [r["answer_delta_specificity"] for r in case_records]
            ),
            "decisions": _counter_dict([r["decision"] for r in case_records]),
            "candidate_flags": {
                "deck_visible_with_marker_entity_loss": sum(
                    1
                    for r in case_records
                    if r["candidate_flags"]["deck_visible_with_marker_entity_loss"]
                )
            },
            "visible_output_applications": sum(
                1 for r in case_records if r["applied_to_user_visible_output"]
            ),
        },
    }
    _write_json(output_dir / f"{arm}.shadow-evidence-result.v1.json", aggregate)
    return aggregate


def write_result_cache_miss_shadow_evidence(
    *,
    output_dir: Path,
    result_paths: list[Path],
) -> dict[str, Any]:
    cache_dir = output_dir / "result-cache-miss-cache"
    case_records = []
    for path in result_paths:
        result_payload = _read_json(path)
        shadow = build_pre_step6_shadow_portfolio(
            result_payload=result_payload,
            mode="shadow",
            cache_dir=cache_dir,
        )
        case_records.append(
            _write_shadow_artifact(
                output_dir=output_dir,
                arm="result-cache-miss",
                case_id=_case_slug_from_result_path(path),
                payload=shadow,
            )
        )
    return _aggregate(arm="result-cache-miss", output_dir=output_dir, case_records=case_records)


def write_fixed_suite_shadow_evidence(
    *,
    root: Path,
    output_dir: Path,
    case_ids: list[str] | None = None,
) -> dict[str, Any]:
    selected_case_ids = case_ids or list(DEFAULT_FIXED_CASE_IDS)
    cache_dir = output_dir / "fixed-suite-card-cache"
    case_records = []
    for case_id in selected_case_ids:
        result_payload = _fixed_case_result_payload(root, case_id)
        miss_probe = build_pre_step6_shadow_portfolio(
            result_payload=result_payload,
            mode="shadow",
            cache_dir=cache_dir,
        )
        compiled_key = str(miss_probe["compiled_card_deck_key"])
        deck = _read_json(_deck_path(root, case_id))
        _write_json(cache_dir / f"{compiled_key}.pre-step6-shadow-card-deck.v1.json", deck)

        replay = _read_json(_replay_path(root, case_id))
        payload_gate_path = _payload_gate_path(root, case_id)
        payload_gate = (
            _read_json(payload_gate_path)
            if payload_gate_path.exists()
            else {"status": "preserved", "source": "fixed_suite_payload_gate_seed"}
        )
        shadow = build_pre_step6_shadow_portfolio(
            result_payload=result_payload,
            mode="shadow",
            cache_dir=cache_dir,
            step6_ledger=_normalize_replay_ledger(replay),
            payload_gate=payload_gate,
            custody_valid=True,
        )
        case_records.append(
            _write_shadow_artifact(
                output_dir=output_dir,
                arm="fixed-suite-cache-hit",
                case_id=case_id,
                payload=shadow,
            )
        )
    return _aggregate(arm="fixed-suite-cache-hit", output_dir=output_dir, case_records=case_records)


def _discover_default_result_paths(root: Path, limit: int) -> list[Path]:
    discovered: list[Path] = []
    for pattern in DEFAULT_RESULT_GLOBS:
        discovered.extend(sorted(root.glob(pattern)))
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in discovered:
        if path in seen:
            continue
        seen.add(path)
        unique.append(path)
        if len(unique) >= limit:
            break
    return unique


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("research/pre-step6-shadow-portfolio-evidence"),
    )
    parser.add_argument(
        "--mode",
        choices=("result-cache-miss", "fixed-suite-cache-hit", "all"),
        default="all",
    )
    parser.add_argument("--result-file", type=Path, action="append", default=[])
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--result-limit", type=int, default=8)
    args = parser.parse_args()

    root = args.root.resolve()
    output_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    runs: list[dict[str, Any]] = []

    if args.mode in {"result-cache-miss", "all"}:
        result_paths = args.result_file or _discover_default_result_paths(root, args.result_limit)
        runs.append(
            write_result_cache_miss_shadow_evidence(
                output_dir=output_dir,
                result_paths=[p if p.is_absolute() else root / p for p in result_paths],
            )
        )

    if args.mode in {"fixed-suite-cache-hit", "all"}:
        runs.append(
            write_fixed_suite_shadow_evidence(
                root=root,
                output_dir=output_dir,
                case_ids=args.case_id or None,
            )
        )

    combined = {
        "schema_version": SCHEMA_VERSION,
        "arm": "combined",
        "runtime_effect": "none_shadow_only",
        "runs": runs,
    }
    _write_json(output_dir / "combined.shadow-evidence-result.v1.json", combined)
    print(json.dumps(combined, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
