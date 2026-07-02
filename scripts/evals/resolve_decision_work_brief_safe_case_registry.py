#!/usr/bin/env python3
"""Resolve one checked-in-safe Decision Work Brief registry entry."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = Path(
    "docs/conversation-understanding/"
    "decision-work-brief-runtime-checked-in-safe-case-registry-v0.json"
)


def _ensure_repo_root_on_path() -> None:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))


def main(argv: list[str] | None = None) -> int:
    _ensure_repo_root_on_path()
    from engine.system_b.decision_work_brief_safe_case_registry import (
        DecisionWorkBriefSafeCaseRegistryError,
        render_safe_case_registry_entry_json,
        resolve_safe_case_registry_entry,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Resolve one checked-in-safe Decision Work Brief case registry entry. "
            "This command returns safe refs and status only; it does not run "
            "Lolla, call models, mutate archives, score advice, or authorize action."
        )
    )
    parser.add_argument("--case-registry", default=DEFAULT_REGISTRY, type=Path)
    parser.add_argument("--case-key", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    try:
        result = resolve_safe_case_registry_entry(
            case_key=args.case_key,
            registry_path=args.case_registry,
        )
    except DecisionWorkBriefSafeCaseRegistryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        render_safe_case_registry_entry_json(result, pretty=args.pretty),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
