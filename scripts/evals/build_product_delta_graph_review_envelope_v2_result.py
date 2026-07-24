#!/usr/bin/env python3
"""Import, gate, consolidate, or validate the authorized v2 review run."""
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
    from engine.system_b.product_delta_graph_review_envelope_v2_result import (
        ProductDeltaGraphReviewEnvelopeV2ResultError,
        build_consolidation,
        build_post_reveal_packets,
        import_blind_review,
        import_post_reveal_interpretation,
        render_json,
        validate_complete_result,
        validate_post_reveal_packets,
        validate_preflight,
        write_consolidation,
        write_post_reveal_packets,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Preserve first-terminal v2 review outputs and build the bounded "
            "non-scalar result. This command never invokes Codex or a provider."
        )
    )
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--validate-preflight", action="store_true")
    action.add_argument("--import-blind", choices=("primary", "skeptical"))
    action.add_argument("--write-post-reveal", action="store_true")
    action.add_argument("--validate-post-reveal", action="store_true")
    action.add_argument(
        "--import-interpretation", choices=("primary", "skeptical")
    )
    action.add_argument("--write-consolidation", action="store_true")
    action.add_argument("--validate-complete", action="store_true")
    action.add_argument(
        "--print",
        dest="print_artifact",
        choices=(
            "post-reveal-primary",
            "post-reveal-skeptical",
            "consolidation",
        ),
    )
    parser.add_argument("--source", type=Path)
    parser.add_argument("--process-exit-code", type=int)
    parser.add_argument("--codex-cli-version")
    args = parser.parse_args(argv)

    try:
        if args.import_blind or args.import_interpretation:
            if (
                args.source is None
                or args.process_exit_code is None
                or not args.codex_cli_version
            ):
                parser.error(
                    "--source, --process-exit-code, and --codex-cli-version "
                    "are required for imports"
                )
            if args.import_blind:
                state = import_blind_review(
                    repo_root=REPO_ROOT,
                    lane=args.import_blind,
                    source_path=args.source,
                    process_exit_code=args.process_exit_code,
                    codex_cli_version=args.codex_cli_version,
                )
                print(
                    f"V2 {args.import_blind} blind terminal state: {state}."
                )
                return 0
            state = import_post_reveal_interpretation(
                repo_root=REPO_ROOT,
                lane=args.import_interpretation,
                source_path=args.source,
                process_exit_code=args.process_exit_code,
                codex_cli_version=args.codex_cli_version,
            )
            print(
                "V2 "
                f"{args.import_interpretation} post-reveal terminal state: "
                f"{state}."
            )
            return 0
        if (
            args.source is not None
            or args.process_exit_code is not None
            or args.codex_cli_version is not None
        ):
            parser.error("execution metadata applies only to imports")
        if args.validate_preflight:
            return _report(
                validate_preflight(repo_root=REPO_ROOT), "preflight"
            )
        if args.write_post_reveal:
            write_post_reveal_packets(repo_root=REPO_ROOT)
            print("V2 post-reveal packets frozen.")
            return 0
        if args.validate_post_reveal:
            return _report(
                validate_post_reveal_packets(repo_root=REPO_ROOT),
                "post-reveal packets",
            )
        if args.write_consolidation:
            write_consolidation(repo_root=REPO_ROOT)
            print("V2 consolidation frozen.")
            return 0
        if args.validate_complete:
            return _report(
                validate_complete_result(repo_root=REPO_ROOT),
                "complete result",
            )
        if args.print_artifact == "consolidation":
            print(
                render_json(build_consolidation(repo_root=REPO_ROOT)),
                end="",
            )
            return 0
        lane = args.print_artifact.removeprefix("post-reveal-")
        print(
            render_json(
                build_post_reveal_packets(repo_root=REPO_ROOT)[lane]
            ),
            end="",
        )
        return 0
    except ProductDeltaGraphReviewEnvelopeV2ResultError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def _report(errors: list[str], label: str) -> int:
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"V2 graph-review {label} are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
