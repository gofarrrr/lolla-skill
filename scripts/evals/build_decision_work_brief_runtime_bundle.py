#!/usr/bin/env python3
"""Build a manual post-archive Decision Work Brief runtime bundle."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ATTACHMENT_CONTRACT = Path(
    "docs/conversation-understanding/"
    "decision-work-brief-runtime-attachment-contract-v0.json"
)
DEFAULT_SIDECAR_CONTRACT = Path(
    "docs/conversation-understanding/decision-work-brief-runtime-sidecar-v0.json"
)


def _ensure_repo_root_on_path() -> None:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))


def main(argv: list[str] | None = None) -> int:
    _ensure_repo_root_on_path()
    from engine.system_b.decision_work_brief_runtime_bundle import (
        DecisionWorkBriefRuntimeBundleInputError,
        build_decision_work_brief_runtime_bundle,
        render_attachment_status_json,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Build a checked-in-safe manual post-archive Decision Work Brief "
            "runtime bundle. This command does not run Lolla, invoke the skill, "
            "call models, mutate the input archive, infer a new brief, score "
            "advice, or authorize action."
        )
    )
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument(
        "--attachment-contract",
        default=DEFAULT_ATTACHMENT_CONTRACT,
        type=Path,
    )
    parser.add_argument("--sidecar-contract", default=DEFAULT_SIDECAR_CONTRACT, type=Path)
    parser.add_argument(
        "--resolver-output",
        type=Path,
        help=(
            "Resolver-approved safe supply JSON from "
            "resolve_decision_work_brief_safe_supply.py. When supplied, this is "
            "the preferred source of safe brief/enriched/triage refs."
        ),
    )
    parser.add_argument("--brief-json", type=Path)
    parser.add_argument("--brief-markdown", type=Path)
    parser.add_argument("--enriched-brief", type=Path)
    parser.add_argument("--triage-packet", type=Path)
    parser.add_argument("--triage-read", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    try:
        status = build_decision_work_brief_runtime_bundle(
            run_dir=args.run_dir,
            output_dir=args.out,
            attachment_contract_path=args.attachment_contract,
            sidecar_contract_path=args.sidecar_contract,
            resolver_output_path=args.resolver_output,
            brief_json_path=args.brief_json,
            brief_markdown_path=args.brief_markdown,
            enriched_brief_path=args.enriched_brief,
            triage_packet_path=args.triage_packet,
            triage_read_path=args.triage_read,
        )
    except DecisionWorkBriefRuntimeBundleInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.pretty:
        print(render_attachment_status_json(status, pretty=True), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
