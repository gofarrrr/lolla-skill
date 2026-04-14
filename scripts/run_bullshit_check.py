#!/usr/bin/env python3
"""Standalone bullshit index check for internal quality signals.

Used by Step 6 (internal review) and Step 8 (gap check) to evaluate
Lolla's own output for bullshit subtypes before presenting to the user.

Usage:
    python3 scripts/run_bullshit_check.py --text-file /tmp/step6_output.txt
    python3 scripts/run_bullshit_check.py --text "Some passage to evaluate..."
    echo "passage" | python3 scripts/run_bullshit_check.py --stdin

Output: JSON to stdout with bullshit_profile.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
ENGINE_DIR = SKILL_ROOT / "engine"

if (ENGINE_DIR / "system_b" / "__init__.py").exists():
    sys.path.insert(0, str(ENGINE_DIR))
elif os.environ.get("LOLLA_REPO_ROOT"):
    sys.path.insert(0, os.environ["LOLLA_REPO_ROOT"])
else:
    print("ERROR: Cannot find the Lolla engine.", file=sys.stderr)
    sys.exit(1)


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        if key not in os.environ:
            os.environ[key] = value


def main() -> int:
    parser = argparse.ArgumentParser(description="Run bullshit index check")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text-file", help="Path to text file to evaluate")
    group.add_argument("--text", help="Text string to evaluate")
    group.add_argument("--stdin", action="store_true", help="Read text from stdin")
    parser.add_argument("--context", help="Decision context summary (prevents false unverified_claims)")
    parser.add_argument("--output-file", help="Write JSON to file instead of stdout")
    args = parser.parse_args()

    # Load env
    for candidate in [
        SKILL_ROOT / ".env",
        Path.home() / ".config" / "lolla" / ".env",
    ]:
        if candidate.exists():
            _load_env_file(candidate)
            break

    # Get text
    if args.text_file:
        text_path = Path(args.text_file)
        if not text_path.exists():
            print(json.dumps({"status": "error", "error": f"File not found: {text_path}"}))
            return 1
        text = text_path.read_text(encoding="utf-8")
    elif args.stdin:
        text = sys.stdin.read()
    else:
        text = args.text

    if not text or not text.strip():
        print(json.dumps({"status": "error", "error": "Empty text"}))
        return 1

    from system_b.boundary_provider import load_boundary_client_from_env
    from system_b.bullshit_index import evaluate_text

    try:
        client = load_boundary_client_from_env("openrouter")
    except Exception as exc:
        print(json.dumps({"status": "error", "error": f"Failed to load boundary client: {exc}"}))
        return 1

    profile = evaluate_text(
        text, client,
        context_summary=args.context or "",
    )

    output = {
        "status": "ok",
        "bullshit_profile": profile.to_payload(),
    }

    output_text = json.dumps(output, indent=2, ensure_ascii=False)
    if args.output_file:
        Path(args.output_file).write_text(output_text, encoding="utf-8")
        print(f"BI check written to {args.output_file}")
    else:
        print(output_text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
