#!/usr/bin/env python3
"""Validate and print the normalized Lolla audit mode."""
from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.system_b.audit_mode import AuditModeError, audit_mode_from_env  # noqa: E402


def main() -> int:
    try:
        print(audit_mode_from_env())
    except AuditModeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
