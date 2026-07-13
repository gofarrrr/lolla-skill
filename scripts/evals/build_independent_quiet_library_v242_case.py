#!/usr/bin/env python3
"""Build and source-compile the new quiet v2.4.2 library holdout."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_position_role_first_v24 import (
    build_position_starting_packet_v24,
    compile_position_starting_response_v24,
)
from engine.system_b.reasoning_process_position_role_first_v242 import (
    build_packet_v242,
    compile_response_v242,
    join_v242,
)


CASE_ID = "phase5-independent-quiet-library-laptop-pilot"
SOURCE = ROOT / "research/independent-phase5-cases-2026-07-12/quiet-library-laptop-case.txt"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selected_sentences() -> list[tuple[str, int, str, str]]:
    return [
        ("e001", 1, "user", "Our busiest library branch has twelve shared laptops and long queues after school."),
        ("e002", 1, "user", "We are considering allowing reservations, but staff worry that an app-first system could disadvantage walk-in patrons and people who need help booking."),
        ("e003", 1, "user", "I want to test whether reservations reduce waiting without quietly making access less equal or committing us to a permanent platform."),
        ("e004", 1, "assistant", "Treat this as a reversible access experiment, not a software rollout."),
        ("e005", 1, "assistant", "Define what should improve, what must not worsen, which booking alternatives remain available, what data is necessary, and what would restore the current system."),
        ("e034", 7, "user", "Agreed."),
        ("e035", 7, "user", "We will run the six weeks at one branch, keep half the laptops walk-in, preserve phone, desk, and assisted booking, publish weekly results by access path, restore walk-in use under the predefined triggers, and make no permanence decision before the full review."),
        ("e036", 7, "user", "No material decision question or unresolved concern remains for me before launch."),
        ("e037", 7, "assistant", "Then the reasoning is complete enough to proceed."),
        ("e038", 7, "assistant", "The trial has prior evidence, multiple access paths, minimal data, an operational fallback, protected stakeholder input, explicit success and failure conditions, an early restoration rule, and a fixed final review."),
        ("e039", 7, "assistant", "Execute the protocol as written; no additional reasoning pressure is presently warranted."),
    ]


def build_wrapper() -> dict[str, Any]:
    source_text = SOURCE.read_text(encoding="utf-8")
    rows = selected_sentences()
    for _alias, _turn, _speaker, text in rows:
        if source_text.count(text) != 1:
            raise ValueError(f"selected sentence is absent or duplicated: {text}")
    groups: list[str] = []
    previous: tuple[int, str] | None = None
    for alias, turn, speaker, text in rows:
        key = (turn, speaker)
        if key != previous:
            groups.append(f"[Turn {turn} {speaker.upper()}]")
            previous = key
        groups.append(f"{alias}\t{text}")
    annotated = "\n".join(groups)
    alias_map = [
        {
            "alias": alias,
            "span_id": "span-" + digest(f"{turn}|{speaker}|{text}")[:16],
            "speaker": speaker,
            "text_sha256": digest(text),
            "turn_index": turn,
        }
        for alias, turn, speaker, text in rows
    ]
    packet = {
        "boundary": {
            "auxiliary_ledger_included": False,
            "deterministic_semantic_gate_performed": False,
            "direct_graph_routing_allowed": False,
            "global_synthesis_requested": False,
            "protected_target_included": False,
            "semantic_prefilter_performed": False,
            "source_review_fixture_included": False,
        },
        "case_id": CASE_ID,
        "focal_region": {"annotated_sentence_text": annotated, "citation_allowed": True, "evidence_aliases": [row[0] for row in rows]},
        "focal_turn_indices": [1, 7],
        "prior_context": {"annotated_sentence_text": "", "evidence_aliases": [], "general_citation_allowed": False, "included": False, "role_limited_citation_policy": "none"},
        "question": "How did the working position or decision change, and does any unresolved qualification remain capable of changing it?",
        "response_contract": {"auxiliary_observation_ids_allowed": False, "free_form_source_quotes_allowed": False, "global_synthesis_requested": False, "maximum_records": 2, "relationship_roles_unchanged_from_v3": True, "valid_empty_output_allowed": True},
        "schema_version": "lolla.reasoning_process_chronological_shard_packet.v1",
        "shard_id": CASE_ID + "-position_and_decision_trajectory-shard-01",
        "shard_kind": "position_endpoint_comparison",
        "source": {"conversation_message_count": len(re.findall(r"(?m)^\[Turn \d+\] (?:USER|ASSISTANT):", source_text)), "source_path": str(SOURCE.relative_to(ROOT)), "source_sha256": "sha256:" + file_sha(SOURCE)},
        "status": "target_blind_provider_free_chronological_shard",
        "view_kind": "position_and_decision_trajectory",
    }
    return {
        "context_alias_map": [],
        "focal_alias_map": alias_map,
        "metrics": {"context_sentence_count": 0, "focal_sentence_count": len(rows), "future_max_records": 2, "input_utf8_bytes": len(annotated.encode())},
        "packet": packet,
    }


def build(output: Path) -> dict[str, Any]:
    wrapper = build_wrapper()
    target = load(output / "source-review-target.json")
    packet_path = output / "position-endpoint.json"
    write(packet_path, wrapper)
    starting_packet = build_position_starting_packet_v24(wrapper=wrapper, role="starting")
    starting = compile_position_starting_response_v24(
        response=target["starting_response"],
        packet=starting_packet,
        producer_kind="source_reviewer",
        producer_id="pre-execution-v242-quiet-target",
    )
    paired_packet = build_packet_v242(wrapper=wrapper)
    paired = compile_response_v242(
        response=target["paired_response"],
        wrapper=wrapper,
        producer_kind="source_reviewer",
        producer_id="pre-execution-v242-quiet-target",
    )
    joined = join_v242(starting_compiled=starting, paired_compiled=paired)
    gate = (
        len(starting["observations"]) == 1
        and len(paired["role_compiled"]["current"]["observations"]) == 1
        and not paired["role_compiled"]["qualification"]["observations"]
        and paired["qualification_review"]["outcome"] == "no_unresolved_qualification_observed"
        and joined["role_observations"]["qualification"] is None
    )
    fixture = {
        "schema_version": "lolla.reasoning_process_position_role_first_v242_quiet_target_fixture.v1",
        "status": "pre_execution_source_review_target_compiled" if gate else "pre_execution_source_review_target_failed",
        "case_id": CASE_ID,
        "starting_compiled": starting,
        "paired_packet": paired_packet,
        "paired_compiled": paired,
        "joined": joined,
        "source_review_gates": target["source_first_gates"],
        "protected_target": target["protected_target"],
        "mechanism_targets": target["mechanism_targets"],
        "boundary": target["boundary"],
    }
    fixture_path = output / "compiled-source-review-target.json"
    write(fixture_path, fixture)
    report = {
        "schema_version": "lolla.reasoning_process_position_role_first_v242_quiet_target_report.v1",
        "status": "pre_execution_target_gate_pass" if gate else "pre_execution_target_gate_fail",
        "case_id": CASE_ID,
        "packet_sha256": file_sha(packet_path),
        "target_sha256": file_sha(output / "source-review-target.json"),
        "compiled_target_sha256": file_sha(fixture_path),
        "admitted_role_record_count": 2,
        "qualification_record_count": 0,
        "qualification_review_outcome": paired["qualification_review"]["outcome"],
        "join_status": joined["status"],
        "provider_calls": 0,
        "provider_probe_authorized": False,
    }
    write(output / "target-report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build(args.output.resolve())
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pre_execution_target_gate_pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
