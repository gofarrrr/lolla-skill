#!/usr/bin/env python3
"""Validate the checked-in provider-free consumer-context case candidate."""
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.evals.build_consumer_context_case_freeze_candidate import (
    validate_checked_in,
)


def main() -> int:
    errors, receipt = validate_checked_in(root=ROOT)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
