#!/usr/bin/env python3
"""Resolve safe Decision Work Brief runtime bundle inputs."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTRACT = Path(
    "docs/conversation-understanding/"
    "decision-work-brief-runtime-safe-supply-resolver-contract-v0.json"
)


def _ensure_repo_root_on_path() -> None:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))


def main(argv: list[str] | None = None) -> int:
    _ensure_repo_root_on_path()
    from engine.system_b.decision_work_brief_safe_supply_resolver import (
        DecisionWorkBriefSafeSupplyResolverError,
        resolve_decision_work_brief_safe_supply,
        write_resolver_json,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Resolve safe refs for Decision Work Brief runtime attachment. "
            "This command validates refs and emits status only; it does not "
            "run Lolla, call models, infer a brief, mutate archives, score "
            "advice, or authorize action."
        )
    )
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--contract", default=DEFAULT_CONTRACT, type=Path)
    parser.add_argument("--case-registry", type=Path)
    parser.add_argument("--case-key")
    parser.add_argument("--brief-json", type=Path)
    parser.add_argument("--brief-markdown", type=Path)
    parser.add_argument("--enriched-brief", type=Path)
    parser.add_argument("--interpretation-read", type=Path)
    parser.add_argument("--triage-packet", type=Path)
    parser.add_argument("--triage-read", type=Path)
    parser.add_argument("--eligibility-result", type=Path)
    parser.add_argument("--attachment-status", type=Path)
    parser.add_argument("--mode", default="manual_ref_supply_only")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    try:
        result = resolve_decision_work_brief_safe_supply(
            run_dir=args.run_dir,
            contract_path=args.contract,
            mode=args.mode,
            case_registry_path=args.case_registry,
            case_key=args.case_key,
            brief_json_path=args.brief_json,
            brief_markdown_path=args.brief_markdown,
            enriched_brief_path=args.enriched_brief,
            interpretation_read_path=args.interpretation_read,
            triage_packet_path=args.triage_packet,
            triage_read_path=args.triage_read,
            eligibility_result_path=args.eligibility_result,
            attachment_status_path=args.attachment_status,
        )
    except DecisionWorkBriefSafeSupplyResolverError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    write_resolver_json(args.out, result, pretty=args.pretty)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
