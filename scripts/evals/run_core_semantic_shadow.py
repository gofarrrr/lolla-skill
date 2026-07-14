#!/usr/bin/env python3
"""Run the offline core semantic shadow reader against one archived run."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load_env(path: Path) -> None:
    if not path.is_file():
        raise ValueError("env file was not found")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value


class _StageBoundary:
    def __init__(self, boundary: object) -> None:
        self.boundary = boundary

    def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
        if "LIVE CONSTRAINTS" in system_prompt:
            stage = "core_semantic_shadow.live_constraints"
        elif "STANCE EVENT" in system_prompt:
            stage = "core_semantic_shadow.assistant_stances"
        elif "DROPPED THREADS" in system_prompt:
            stage = "core_semantic_shadow.dropped_threads"
        elif "QUESTION TRAJECTORY SEMANTICS" in system_prompt:
            stage = "core_semantic_shadow.question_trajectory"
        elif "USER COUNTER-PRESSURE TEMPORAL SEMANTICS" in system_prompt:
            stage = "core_semantic_shadow.user_pressure"
        elif "USER COUNTER-PRESSURE SEMANTICS" in system_prompt:
            stage = "core_semantic_shadow.user_pressure"
        elif "USER PRESSURE SEMANTICS" in system_prompt:
            stage = "core_semantic_shadow.user_pressure"
        elif "OPTION AND EVIDENCE SEMANTICS" in system_prompt:
            stage = "core_semantic_shadow.option_evidence"
        else:
            stage = "core_semantic_shadow.unknown"
        return self.boundary.run_json(system_prompt, user_prompt, stage=stage)  # type: ignore[attr-defined]


def main() -> int:
    from engine.system_b.boundary_provider import load_boundary_client_from_env
    from engine.system_b.conversation_loader import load_conversation_context
    from engine.system_b.core_semantic_shadow import (
        build_core_semantic_shadow,
        render_core_semantic_shadow_json,
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--provider", default="openrouter")
    parser.add_argument("--real-boundary-approved", action="store_true")
    args = parser.parse_args()

    if not args.real_boundary_approved:
        print("error: real boundary approval flag is required", file=sys.stderr)
        return 2
    if args.env_file:
        _load_env(args.env_file.expanduser())
    run_dir = args.run_dir.expanduser().resolve()
    output = args.out.expanduser().resolve()
    if not run_dir.is_dir():
        print("error: run directory was not found", file=sys.stderr)
        return 2
    if output == run_dir or run_dir in output.parents:
        print("error: output must be outside the run archive", file=sys.stderr)
        return 2

    context = load_conversation_context(
        run_dir / "extraction.json",
        run_dir / "conversation.txt",
    )
    boundary = _StageBoundary(load_boundary_client_from_env(args.provider))
    payload = build_core_semantic_shadow(context=context, boundary=boundary)
    payload["model_usage"] = {
        "calls": [_safe_call(record.to_dict()) for record in boundary.boundary.call_log],  # type: ignore[attr-defined]
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_core_semantic_shadow_json(payload), encoding="utf-8")
    print(f"Core semantic shadow written to {output}")
    return 0


def _safe_call(record: dict[str, object]) -> dict[str, object]:
    """Keep usage/custody metadata without persisting provider message text."""
    return {
        key: value
        for key, value in record.items()
        if key not in {"raw_message_content"}
    }


if __name__ == "__main__":
    raise SystemExit(main())
