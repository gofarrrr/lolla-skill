#!/usr/bin/env python3
"""Compile a pre-written source-review target through role-first v2.4.1."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.evals import build_reasoning_process_position_role_first_v24_target as base  # noqa: E402
from engine.system_b.reasoning_process_position_role_first_v241 import compile_position_current_qualification_response_v241  # noqa: E402


def main() -> int:
    base.compile_position_current_qualification_response_v24 = compile_position_current_qualification_response_v241
    return base.main()


if __name__ == "__main__":
    raise SystemExit(main())
