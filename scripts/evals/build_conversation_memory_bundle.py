#!/usr/bin/env python3
"""Build a self-explaining conversation-memory bundle for a completed run."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _ensure_repo_root_on_path() -> None:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))


def main(argv: list[str] | None = None) -> int:
    _ensure_repo_root_on_path()
    from engine.system_b.conversation_memory_packet import (
        ConversationMemoryInputError,
        PRIVACY_MODES,
        build_conversation_memory_bundle,
        render_bundle_write_result_json,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Build an offline conversation-memory packet and Markdown file from "
            "a completed Lolla archive run. This command does not run Lolla, "
            "call providers, mutate the input archive, score advice, or "
            "authorize action."
        )
    )
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument(
        "--privacy-mode",
        choices=sorted(PRIVACY_MODES),
        default="user_private",
    )
    parser.add_argument(
        "--include-raw-conversation",
        action="store_true",
        help=(
            "Include conversation.txt in the Markdown appendix. Rejected in "
            "public_safe mode."
        ),
    )
    parser.add_argument("--created-at", default=None)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    try:
        result = build_conversation_memory_bundle(
            run_dir=args.run_dir,
            output_dir=args.out,
            privacy_mode=args.privacy_mode,
            include_raw_conversation=args.include_raw_conversation,
            created_at=args.created_at,
        )
    except ConversationMemoryInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(render_bundle_write_result_json(result, pretty=args.pretty), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
