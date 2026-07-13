#!/usr/bin/env python3
"""Build target-blind endpoint packets for new stance-object v4.1 cases."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.conversation_state_candidates import build_source_catalog  # noqa: E402
from engine.system_b.reasoning_process_chronological_shards import (  # noqa: E402
    build_chronological_shard_packets,
)

CASE_IDS = (
    "amb2-case01-career-transition",
    "amb2-case02-community-space",
    "amb2-case03-agency-acquisition",
)
SOURCE_ROOT = "research/stance-object-v41-fresh-corpus-2026-07-12/cases"


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _source_path(case_id: str) -> str:
    return f"{SOURCE_ROOT}/{case_id}.txt"


def build(output: Path) -> dict[str, Any]:
    cases = []
    for case_id in CASE_IDS:
        source_path = _source_path(case_id)
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
            for index, span in enumerate(sentence_spans, start=1)
        ]
        packets = build_chronological_shard_packets(
            case_id=case_id,
            source_path=source_path,
            source_text=source_text,
            global_alias_map=alias_map,
        )
        endpoint = next(
            wrapper
            for wrapper in packets
            if wrapper["packet"]["view_kind"] == "position_and_decision_trajectory"
            and wrapper["packet"]["shard_kind"] == "position_endpoint_comparison"
        )
        packet_path = output / "packets" / case_id / "position-endpoint.json"
        _write(packet_path, endpoint)
        cases.append(
            {
                "case_id": case_id,
                "source_path": source_path,
                "source_sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
                "conversation_message_count": catalog.message_count,
                "sentence_alias_count": len(alias_map),
                "packet_path": str(packet_path.relative_to(ROOT)),
                "packet_sha256": hashlib.sha256(
                    json.dumps(endpoint, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
                    + b"\n"
                ).hexdigest(),
                "packet_input_utf8_bytes": endpoint["metrics"]["input_utf8_bytes"],
                "selection_sha256": hashlib.sha256(case_id.encode("utf-8")).hexdigest(),
            }
        )
    ranking = sorted(cases, key=lambda item: item["selection_sha256"])
    report = {
        "schema_version": "lolla.reasoning_process_stance_object_v41_fresh_corpus.v1",
        "status": "target_blind_provider_free_fresh_corpus_built",
        "date": "2026-07-12",
        "cases": cases,
        "selection": {
            "rule": "ascending_sha256_of_case_id_take_first_after_all_cases_are_frozen",
            "eligible_case_ranking": [
                {
                    "case_id": item["case_id"],
                    "selection_sha256": item["selection_sha256"],
                }
                for item in ranking
            ],
            "selected_case_id": ranking[0]["case_id"],
            "selection_was_semantic": False,
        },
        "summary": {
            "case_count": len(cases),
            "conversation_messages_per_case": 14,
            "endpoint_packets_per_case": 1,
            "provider_calls": 0,
            "evaluator_calls": 0,
            "embedding_calls": 0,
            "graph_calls": 0,
            "runtime_calls": 0,
        },
        "boundary": {
            "protected_targets_included_in_packets": False,
            "source_review_fixtures_included_in_packets": False,
            "semantic_case_selection_performed": False,
            "provider_probe_authorized": False,
        },
    }
    _write(output / "report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build(args.output.resolve())
    print(json.dumps({"selection": report["selection"], "summary": report["summary"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
