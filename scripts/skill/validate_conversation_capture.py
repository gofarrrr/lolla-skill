#!/usr/bin/env python3
"""Validate the Step 1 conversation capture before paid extraction/pipeline calls."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


TURN_MARKER_RE = re.compile(r"^\[Turn (\d+)\] (USER|ASSISTANT):\s*$", re.MULTILINE)
HEADER_RE = re.compile(
    r"^CONVERSATION:\s*(\d+)\s*turns?,\s*(\d+)\s*user\s*messages?,\s*(\d+)\s*assistant\s*responses?",
    re.IGNORECASE,
)


def validate_capture(text: str) -> tuple[bool, list[str], dict[str, object]]:
    markers = TURN_MARKER_RE.findall(text)
    roles = [role for _, role in markers]
    actual_user = roles.count("USER")
    actual_assistant = roles.count("ASSISTANT")
    last_turn_role = roles[-1] if roles else None
    header = HEADER_RE.search(text.strip())

    manifest: dict[str, object] = {
        "actual_user_turns": actual_user,
        "actual_assistant_turns": actual_assistant,
        "last_turn_role": last_turn_role,
        "char_length": len(text),
    }
    errors: list[str] = []

    if not header:
        errors.append(
            "missing or unparseable CONVERSATION header; use 'CONVERSATION: N turns, X user messages, Y assistant responses'"
        )
        manifest["declared_turns"] = None
        manifest["declared_user"] = None
        manifest["declared_assistant"] = None
    else:
        declared_turns = int(header.group(1))
        declared_user = int(header.group(2))
        declared_assistant = int(header.group(3))
        manifest["declared_turns"] = declared_turns
        manifest["declared_user"] = declared_user
        manifest["declared_assistant"] = declared_assistant
        if declared_user != actual_user:
            errors.append(f"header declares {declared_user} user messages but body has {actual_user}")
        if declared_assistant != actual_assistant:
            errors.append(
                f"header declares {declared_assistant} assistant responses but body has {actual_assistant}"
            )

    if actual_user == 0:
        errors.append("no [Turn N] USER markers found")
    if actual_assistant == 0:
        errors.append("no [Turn N] ASSISTANT markers found")
    if last_turn_role != "ASSISTANT":
        errors.append("conversation must end with an assistant answer before audit")

    return not errors, errors, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--conversation-file", required=True)
    args = parser.parse_args()

    path = Path(args.conversation_file)
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        raise SystemExit(f"FATAL: conversation file missing or empty at {path}")

    ok, errors, manifest = validate_capture(path.read_text(encoding="utf-8"))
    if not ok:
        print("FATAL: conversation capture is not parseable for Lolla.")
        for error in errors:
            print(f"- {error}")
        return 2

    print(
        "CAPTURE_VALID: "
        f"user_turns={manifest['actual_user_turns']} "
        f"assistant_turns={manifest['actual_assistant_turns']} "
        f"chars={manifest['char_length']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
