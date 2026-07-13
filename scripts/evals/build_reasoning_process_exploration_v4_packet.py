#!/usr/bin/env python3
"""Build the target-blind conversation-only exploration ablation packet."""
from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_views import canonical_json_bytes  # noqa: E402


SOURCE = ROOT / "research/reasoning-process-view-specific-interface-2026-07-11/cases/amb1-case02-nonprofit-scale/exploration_and_alternatives/reader-packet.json"
OUTPUT = ROOT / "research/reasoning-process-exploration-v4-conversation-only-2026-07-11/reader-packet.json"


def main() -> int:
    original = json.loads(SOURCE.read_text(encoding="utf-8"))
    wrapper = deepcopy(original)
    auxiliary = wrapper["reader_packet"]["auxiliary_phase1_ledger"]
    available = len(auxiliary["observations"])
    auxiliary["included"] = False
    auxiliary["observations"] = []
    auxiliary["omission_reason"] = (
        "prospectively frozen conversation-only ablation; the complete optional "
        "Phase-1 ledger is omitted whole and remains recoverable"
    )
    metrics = wrapper["metrics"]
    metrics["auxiliary_observation_count_available"] = available
    metrics["auxiliary_observation_count_included"] = 0
    metrics["auxiliary_ledger_omitted_whole"] = True
    metrics["observed_input_utf8_bytes"] = len(
        canonical_json_bytes(wrapper["reader_packet"])
    )
    wrapper["ablation"] = {
        "kind": "conversation_only_auxiliary_ledger_omitted_whole",
        "semantic_selection_performed_by_code": False,
        "protected_target_included": False,
        "provider_calls": 0,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(wrapper, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(wrapper["metrics"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
