#!/usr/bin/env python3
"""Inventory archived live runs eligible for reasoning-portfolio review.

The inventory is metadata-only. It reads custody artifacts and counts their
shape, but it does not copy conversation, revised-answer, table, or graph text.
It makes no semantic relevance or answer-quality decision.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "lolla.reasoning_portfolio_live_surface_inventory.v0"
REQUIRED_ARTIFACTS = (
    "graph_survival_report.json",
    "pre_step6_private_table.json",
    "pre_step6_private_table_ledger.json",
    "v60_ledger.json",
    "revised.txt",
)


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _hash_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _disposition_counts(items: object) -> dict[str, int]:
    if not isinstance(items, list):
        return {}
    counts = Counter(
        str(item.get("disposition") or "missing")
        for item in items
        if isinstance(item, Mapping)
    )
    return dict(sorted(counts.items()))


def _candidate_state_counts(items: object) -> dict[str, int]:
    if not isinstance(items, list):
        return {}
    counts = Counter(
        str(item.get("survival_state") or "missing")
        for item in items
        if isinstance(item, Mapping)
    )
    return dict(sorted(counts.items()))


def inspect_run(run_dir: Path, *, archive_root: Path) -> dict[str, Any]:
    relative = run_dir.relative_to(archive_root)
    if len(relative.parts) != 2:
        raise ValueError("run directory must be archive_root/case_id/run_id")
    case_id, run_id = relative.parts
    missing = [name for name in REQUIRED_ARTIFACTS if not (run_dir / name).is_file()]
    artifact_hashes = {
        name: _hash_file(run_dir / name)
        for name in REQUIRED_ARTIFACTS
        if (run_dir / name).is_file()
    }
    result: dict[str, Any] = {
        "case_id": case_id,
        "run_id": run_id,
        "eligibility": "ineligible_missing_artifacts" if missing else "eligible",
        "missing_artifacts": missing,
        "artifact_hashes": artifact_hashes,
        "raw_text_included": False,
        "absolute_paths_included": False,
    }
    if missing:
        return result

    graph = _load_object(run_dir / "graph_survival_report.json")
    table = _load_object(run_dir / "pre_step6_private_table.json")
    table_ledger = _load_object(run_dir / "pre_step6_private_table_ledger.json")
    v60_ledger = _load_object(run_dir / "v60_ledger.json")
    candidates = graph.get("candidate_survival", [])
    source_items = table.get("source_items", [])
    table_items = table_ledger.get("items", [])
    v60_items = v60_ledger.get("transactions", [])
    result.update(
        {
            "graph": {
                "schema_version": graph.get("schema_version"),
                "status": graph.get("status"),
                "candidate_count": len(candidates) if isinstance(candidates, list) else 0,
                "selected_for_v60_count": sum(
                    item.get("selected_for_v60") is True
                    for item in candidates
                    if isinstance(item, Mapping)
                ),
                "survival_state_counts": _candidate_state_counts(candidates),
            },
            "private_table": {
                "schema_version": table.get("schema_version"),
                "status": table.get("status"),
                "character_count": table.get("table_char_count"),
                "section_count": table.get("table_section_count"),
                "source_item_count": len(source_items)
                if isinstance(source_items, list)
                else 0,
                "cache_state": table.get("cache", {}).get("state")
                if isinstance(table.get("cache"), Mapping)
                else None,
            },
            "private_table_ledger": {
                "schema_version": table_ledger.get("schema_version"),
                "status": table_ledger.get("status"),
                "item_count": len(table_items) if isinstance(table_items, list) else 0,
                "disposition_counts": _disposition_counts(table_items),
            },
            "v60_ledger": {
                "schema_version": v60_ledger.get("schema_version"),
                "status": v60_ledger.get("status"),
                "transaction_count": len(v60_items)
                if isinstance(v60_items, list)
                else 0,
                "disposition_counts": _disposition_counts(v60_items),
            },
            "revised_answer_character_count": len(
                (run_dir / "revised.txt").read_text(encoding="utf-8")
            ),
        }
    )
    if (
        graph.get("status") != "ready"
        or table.get("status") != "ready"
        or table_ledger.get("status") != "completed"
        or v60_ledger.get("status") != "completed"
    ):
        result["eligibility"] = "ineligible_incomplete_custody"
    return result


def build_inventory(archive_root: Path) -> dict[str, Any]:
    runs = [
        inspect_run(run_dir, archive_root=archive_root)
        for run_dir in sorted(archive_root.glob("*/*"))
        if run_dir.is_dir()
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "metadata_inventory_only",
        "run_count": len(runs),
        "eligible_run_count": sum(item["eligibility"] == "eligible" for item in runs),
        "runs": runs,
        "semantic_relevance_reviewed": False,
        "answer_quality_reviewed": False,
        "model_calls": 0,
        "runtime_integration_authorized": False,
        "non_claims": [
            "artifact_presence_is_not_semantic_novelty",
            "candidate_count_is_not_reasoning_quality",
            "ledger_completion_is_not_answer_quality",
            "not_a_live_corpus_completeness_claim",
        ],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    inventory = build_inventory(args.archive_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(inventory, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
