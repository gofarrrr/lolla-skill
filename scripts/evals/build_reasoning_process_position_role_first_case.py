#!/usr/bin/env python3
"""Build a target-blind position endpoint packet for one frozen text case."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.conversation_state_candidates import build_source_catalog  # noqa: E402
from engine.system_b.reasoning_process_chronological_shards import (  # noqa: E402
    build_chronological_shard_packets,
)


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def build(*, case_id: str, source_path: str, output: Path) -> dict:
    source_text = (ROOT / source_path).read_text(encoding="utf-8")
    catalog = build_source_catalog(source_text=source_text, source_path=source_path)
    sentence_spans = [span for span in catalog.spans if span.kind == "sentence"]
    alias_map = [
        {
            "alias": f"e{index:03d}",
            "span_id": span.span_id,
            "speaker": span.speaker,
            "text_sha256": hashlib.sha256(span.text.encode("utf-8")).hexdigest(),
            "turn_index": span.turn_index,
        }
        for index, span in enumerate(sentence_spans, 1)
    ]
    packets = build_chronological_shard_packets(
        case_id=case_id,
        source_path=source_path,
        source_text=source_text,
        global_alias_map=alias_map,
    )
    endpoint = next(
        wrapper for wrapper in packets
        if wrapper["packet"]["view_kind"] == "position_and_decision_trajectory"
        and wrapper["packet"]["shard_kind"] == "position_endpoint_comparison"
    )
    packet_path = output / "position-endpoint.json"
    _write(packet_path, endpoint)
    report = {
        "schema_version": "lolla.reasoning_process_position_role_first_case.v1",
        "status": "target_blind_provider_free_case_built",
        "date": "2026-07-12",
        "case_id": case_id,
        "source_path": source_path,
        "source_sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
        "conversation_message_count": catalog.message_count,
        "sentence_alias_count": len(alias_map),
        "packet_path": str(packet_path.relative_to(ROOT)),
        "packet_sha256": hashlib.sha256(packet_path.read_bytes()).hexdigest(),
        "provider_calls": 0,
        "boundary": {
            "protected_target_included": False,
            "source_review_fixture_included": False,
            "provider_probe_authorized": False,
            "graph_or_runtime_authorized": False,
        },
    }
    _write(output / "case-report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--source-path", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build(
        case_id=args.case_id,
        source_path=args.source_path,
        output=args.output.resolve(),
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
