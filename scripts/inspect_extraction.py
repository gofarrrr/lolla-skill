#!/usr/bin/env python3
"""Inspect a Lolla extraction JSON without tripping over nested envelope fields.

`run_extract.py` writes an envelope:

    {"status": "ok", "extraction": {"decision_situation": "..."}}

This helper always reads from the nested `extraction` object when present and
falls back to legacy top-level extraction-shaped payloads only when needed.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any


def unwrap_extraction_payload(payload: Mapping[str, Any]) -> tuple[dict[str, Any], str]:
    """Return `(extraction, source_path)` for envelope or legacy payloads."""
    nested = payload.get("extraction")
    if isinstance(nested, Mapping):
        return dict(nested), "$.extraction"
    if any(key in payload for key in ("decision_situation", "reasoning_passages", "live_constraints")):
        return dict(payload), "$"
    return {}, ""


def summarize_extraction_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    extraction, source_path = unwrap_extraction_payload(payload)
    capture_manifest = payload.get("capture_manifest")
    if not isinstance(capture_manifest, Mapping):
        capture_manifest = {}
    return {
        "status": str(payload.get("status") or "unknown"),
        "extraction_source_path": source_path,
        "decision_situation": str(extraction.get("decision_situation") or "").strip(),
        "reasoning_passage_count": len(_list(extraction.get("reasoning_passages"))),
        "live_constraint_count": len(_list(extraction.get("live_constraints"))),
        "dropped_thread_count": len(_list(extraction.get("dropped_threads"))),
        "turn_count": len(_list(extraction.get("turns"))),
        "capture_health": str(payload.get("capture_health") or "").strip() or "unknown",
        "capture_manifest": dict(capture_manifest),
        "warnings": _list(payload.get("capture_warnings")),
        "has_nested_extraction": source_path == "$.extraction",
    }


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("extraction file must contain a JSON object")
    return value


def _print_summary(summary: Mapping[str, Any]) -> None:
    print(f"status: {summary['status']}")
    print(f"extraction_source_path: {summary['extraction_source_path'] or 'missing'}")
    print(f"decision_situation: {summary['decision_situation']}")
    print(f"reasoning_passages: {summary['reasoning_passage_count']}")
    print(f"live_constraints: {summary['live_constraint_count']}")
    print(f"dropped_threads: {summary['dropped_thread_count']}")
    print(f"turns: {summary['turn_count']}")
    print(f"capture_health: {summary['capture_health']}")
    manifest = summary.get("capture_manifest") or {}
    if isinstance(manifest, Mapping) and manifest:
        user_turns = manifest.get("actual_user_turns")
        assistant_turns = manifest.get("actual_assistant_turns")
        chars = manifest.get("char_length")
        print(f"capture_manifest: user_turns={user_turns} assistant_turns={assistant_turns} chars={chars}")
    warnings = summary.get("warnings") or []
    if isinstance(warnings, list) and warnings:
        print(f"warnings: {len(warnings)}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect run_extract.py output using the nested extraction contract."
    )
    parser.add_argument("path", type=Path, help="Path to extraction JSON")
    parser.add_argument("--json", action="store_true", help="Print JSON summary")
    args = parser.parse_args()

    if not args.path.exists():
        print(f"ERROR: extraction file not found: {args.path}", file=sys.stderr)
        return 1
    try:
        summary = summarize_extraction_payload(_load_json(args.path))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: could not inspect extraction: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        _print_summary(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
