#!/usr/bin/env python3
"""Seal an author-selected pressure draft with real shadow/run lineage.

The builder performs no semantic selection. It only binds an existing draft to
the supplied conversation, semantic-shadow, reasoning-pattern, and graph-trace
artifacts, then runs the deterministic handoff validator.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from engine.system_b.reasoning_pressure_handoff import (
    validate_reasoning_pressure_handoff,
)


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _sha256_json(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return _sha256_bytes(encoded)


def _semantic_event_ids(shadow: Mapping[str, Any]) -> set[str]:
    semantic_events = shadow.get("semantic_events")
    if not isinstance(semantic_events, Mapping):
        raise ValueError("semantic shadow is missing semantic_events")
    values: set[str] = set()
    for events in semantic_events.values():
        if not isinstance(events, list):
            continue
        for event in events:
            if not isinstance(event, Mapping):
                continue
            for field in ("event_id", "issue_id", "stance_id"):
                value = event.get(field)
                if isinstance(value, str) and value:
                    values.add(value)
    return values


def _graph_trace_refs(graph_report: Mapping[str, Any]) -> set[str]:
    candidates = graph_report.get("candidate_survival")
    if not isinstance(candidates, list):
        raise ValueError("graph report is missing candidate_survival")
    refs: set[str] = set()
    for candidate in candidates:
        if not isinstance(candidate, Mapping):
            continue
        model_id = candidate.get("model_id")
        if isinstance(model_id, str) and model_id:
            refs.add(f"graph_survival.model.{model_id}")
    return refs


def build_lineage_backed_handoff(
    *,
    draft_path: Path,
    conversation_path: Path,
    semantic_shadow_path: Path,
    reasoning_pattern_packet_path: Path,
    graph_report_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    draft = _load_object(draft_path)
    shadow = _load_object(semantic_shadow_path)
    pattern = _load_object(reasoning_pattern_packet_path)
    graph = _load_object(graph_report_path)

    shadow_hash = _sha256_file(semantic_shadow_path)
    if pattern.get("provenance", {}).get("source_interpretation_sha256") != (
        shadow_hash.removeprefix("sha256:")
    ):
        raise ValueError("pattern packet does not hash-link to the semantic shadow")
    if pattern.get("packet_metadata", {}).get("graph_runtime_modified") is not False:
        raise ValueError("pattern packet claims the graph runtime was modified")
    if pattern.get("routing_projection", {}).get("contains_case_context") is not False:
        raise ValueError("routing projection contains case context")
    if pattern.get("lint", {}).get("status") != "passed":
        raise ValueError("reasoning-pattern fact-boundary lint has not passed")

    source_ids = _semantic_event_ids(shadow)
    pattern_sources = pattern.get("provenance", {}).get("pattern_sources", [])
    for pattern_source in pattern_sources:
        for source_id in pattern_source.get("source_semantic_item_ids", []):
            if source_id not in source_ids:
                raise ValueError(
                    "pattern packet references an unknown semantic event: "
                    f"{source_id}"
                )

    graph_refs = _graph_trace_refs(graph)
    graph_version = graph.get("schema_version")
    if not isinstance(graph_version, str) or not graph_version:
        raise ValueError("graph report is missing schema_version")

    conversation_hash = _sha256_file(conversation_path)
    pattern_hash = _sha256_file(reasoning_pattern_packet_path)
    graph_hash = _sha256_file(graph_report_path)
    routing_hash = _sha256_json(pattern["routing_projection"])

    payload = json.loads(json.dumps(draft))
    payload["status"] = "research_candidate"
    payload["source"]["conversation_sha256"] = conversation_hash
    payload["lineage"] = {
        "reasoning_pattern_packet_sha256": pattern_hash,
        "graph_version": graph_version,
        "graph_trace_artifact_sha256": graph_hash,
        "routing_projection_sha256": routing_hash,
    }

    validation = validate_reasoning_pressure_handoff(
        payload,
        known_source_event_ids=source_ids,
        known_graph_trace_refs=graph_refs,
        expected_conversation_sha256=conversation_hash,
        expected_reasoning_pattern_packet_sha256=pattern_hash,
        expected_graph_version=graph_version,
        expected_graph_trace_artifact_sha256=graph_hash,
        expected_routing_projection_sha256=routing_hash,
    )
    validation["lineage"] = {
        "conversation_sha256": conversation_hash,
        "semantic_shadow_sha256": shadow_hash,
        "reasoning_pattern_packet_sha256": pattern_hash,
        "graph_trace_artifact_sha256": graph_hash,
        "routing_projection_sha256": routing_hash,
    }
    validation["known_source_event_count"] = len(source_ids)
    validation["known_graph_trace_ref_count"] = len(graph_refs)
    validation["draft_semantic_selection_preserved"] = True
    validation["builder_model_calls"] = 0
    return payload, validation


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--draft", type=Path, required=True)
    parser.add_argument("--conversation", type=Path, required=True)
    parser.add_argument("--semantic-shadow", type=Path, required=True)
    parser.add_argument("--reasoning-pattern-packet", type=Path, required=True)
    parser.add_argument("--graph-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--validation-output", type=Path, required=True)
    args = parser.parse_args()

    payload, validation = build_lineage_backed_handoff(
        draft_path=args.draft,
        conversation_path=args.conversation,
        semantic_shadow_path=args.semantic_shadow,
        reasoning_pattern_packet_path=args.reasoning_pattern_packet,
        graph_report_path=args.graph_report,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.validation_output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    args.validation_output.write_text(
        json.dumps(validation, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
