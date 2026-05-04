#!/usr/bin/env python3
"""CLI wrapper for the offline stakeholder-assumption check harness."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINE_DIR = ROOT / "engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from system_b.stakeholder_assumption_check import (  # noqa: E402,F401
    evaluate_trigger,
    gate_surface,
    load_annotation,
    main,
    run_stakeholder_assumption_check,
    score_check,
)


if __name__ == "__main__":
    raise SystemExit(main())
