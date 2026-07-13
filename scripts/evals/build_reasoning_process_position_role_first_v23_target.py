#!/usr/bin/env python3
"""Compile a pre-written source-review target through role-first v2.3."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.evals import build_reasoning_process_position_role_first_v22_target as base
from engine.system_b.reasoning_process_position_role_first_v23 import (
    build_position_relation_packet_v23, build_position_role_packet_v23,
    compile_position_relation_response_v23, compile_position_role_response_v23,
    join_position_role_first_v23,
)


def main() -> int:
    base.build_position_role_packet_v22 = build_position_role_packet_v23
    base.compile_position_role_response_v22 = compile_position_role_response_v23
    base.build_position_relation_packet_v22 = build_position_relation_packet_v23
    base.compile_position_relation_response_v22 = compile_position_relation_response_v23
    base.join_position_role_first_v22 = join_position_role_first_v23
    return base.main()


if __name__ == "__main__":
    raise SystemExit(main())
