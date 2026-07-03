#!/usr/bin/env python3
"""Build deterministic Decision Work resolver-candidate sidecar update packet."""
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
    from engine.system_b.decision_work_resolver_candidate_sidecar_update_packet import (
        DecisionWorkResolverCandidateSidecarUpdatePacketError,
        build_resolver_candidate_sidecar_update_packet,
        render_resolver_candidate_sidecar_update_packet_json,
        write_resolver_candidate_sidecar_update_packet,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Build an offline proposed sidecar update packet from a "
            "resolver-supply candidate. This command does not write runtime "
            "sidecars, mutate archives, approve resolver refs, wire runtime, "
            "score advice, or authorize action."
        )
    )
    parser.add_argument("--resolver-supply", required=True, type=Path)
    parser.add_argument(
        "--source-resolver-supply-ref",
        help="Optional stable source ref to record instead of deriving one.",
    )
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    try:
        result = build_resolver_candidate_sidecar_update_packet(
            resolver_supply_path=args.resolver_supply,
            source_resolver_supply_ref=args.source_resolver_supply_ref,
        )
        payload = render_resolver_candidate_sidecar_update_packet_json(
            result,
            pretty=args.pretty,
        )
        write_resolver_candidate_sidecar_update_packet(args.out, payload)
    except DecisionWorkResolverCandidateSidecarUpdatePacketError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
