#!/usr/bin/env python3
"""Build, import, or validate the bounded graph-replication result."""
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
    from engine.system_b.product_delta_graph_replication import SAMPLE_ALIASES
    from engine.system_b.product_delta_graph_replication_result import (
        ProductDeltaGraphReplicationResultError,
        build_blind_review_inputs,
        build_consolidation,
        build_post_reveal_packets,
        import_frozen_review,
        import_post_reveal_interpretation,
        import_terminal_output,
        render_json,
        validate_checked_in_blind_review_inputs,
        validate_checked_in_complete_result,
        validate_checked_in_post_reveal_packets,
        write_blind_review_inputs,
        write_consolidation,
        write_post_reveal_packets,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Import or validate first-terminal generation states, blind "
            "reviews, post-reveal interpretations, and the non-scalar graph "
            "replication consolidation. No provider, graph, runtime, private "
            "archive, or human-authority call is made."
        )
    )
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--import-output", action="store_true")
    action.add_argument("--write-blind-inputs", action="store_true")
    action.add_argument("--validate-blind-inputs", action="store_true")
    action.add_argument(
        "--import-review", choices=("primary", "skeptical")
    )
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
            "blind",
            "sealed",
            "post-reveal-primary",
            "post-reveal-skeptical",
            "consolidation",
        ),
    )
    parser.add_argument("--sample", choices=SAMPLE_ALIASES)
    parser.add_argument("--source", type=Path)
    args = parser.parse_args(argv)

    try:
        if args.import_output:
            if args.sample is None or args.source is None:
                parser.error(
                    "--sample and --source are required with --import-output"
                )
            import_terminal_output(
                repo_root=REPO_ROOT,
                sample_alias=args.sample,
                source_path=args.source,
            )
            print(f"Graph-replication {args.sample} output frozen.")
            return 0
        if args.import_review:
            if args.source is None:
                parser.error("--source is required with --import-review")
            terminal_state = import_frozen_review(
                repo_root=REPO_ROOT,
                lane=args.import_review,
                source_path=args.source,
            )
            print(
                "Graph-replication "
                f"{args.import_review} review terminal state frozen: "
                f"{terminal_state}."
            )
            return 0
        if args.import_interpretation:
            if args.source is None:
                parser.error(
                    "--source is required with --import-interpretation"
                )
            import_post_reveal_interpretation(
                repo_root=REPO_ROOT,
                lane=args.import_interpretation,
                source_path=args.source,
            )
            print(
                "Graph-replication "
                f"{args.import_interpretation} interpretation frozen."
            )
            return 0
        if args.sample is not None or args.source is not None:
            parser.error(
                "--sample/--source apply only to import operations"
            )
        if args.write_blind_inputs:
            write_blind_review_inputs(repo_root=REPO_ROOT)
            print("Graph-replication blind review inputs written.")
            return 0
        if args.validate_blind_inputs:
            errors = validate_checked_in_blind_review_inputs(
                repo_root=REPO_ROOT
            )
            return _report(errors, "blind review inputs")
        if args.write_post_reveal:
            write_post_reveal_packets(repo_root=REPO_ROOT)
            print("Graph-replication post-reveal packets written.")
            return 0
        if args.validate_post_reveal:
            errors = validate_checked_in_post_reveal_packets(
                repo_root=REPO_ROOT
            )
            return _report(errors, "post-reveal packets")
        if args.write_consolidation:
            write_consolidation(repo_root=REPO_ROOT)
            print("Graph-replication consolidation written.")
            return 0
        if args.validate_complete:
            errors = validate_checked_in_complete_result(repo_root=REPO_ROOT)
            return _report(errors, "complete result")
        if args.print_artifact == "consolidation":
            payload, errors = build_consolidation(repo_root=REPO_ROOT)
            if errors:
                raise ProductDeltaGraphReplicationResultError(
                    f"consolidation has {len(errors)} error(s)"
                )
            print(render_json(payload), end="")
            return 0
        if args.print_artifact in (
            "post-reveal-primary",
            "post-reveal-skeptical",
        ):
            lane = args.print_artifact.removeprefix("post-reveal-")
            payload = build_post_reveal_packets(repo_root=REPO_ROOT)[lane]
            print(render_json(payload), end="")
            return 0
        blind, sealed = build_blind_review_inputs(repo_root=REPO_ROOT)
        print(
            render_json(
                blind if args.print_artifact == "blind" else sealed
            ),
            end="",
        )
        return 0
    except ProductDeltaGraphReplicationResultError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def _report(errors: list[str], label: str) -> int:
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"Graph-replication {label} are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
