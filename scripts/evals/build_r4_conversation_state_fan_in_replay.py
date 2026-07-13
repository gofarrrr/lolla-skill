#!/usr/bin/env python3
"""Build and validate the provider-free R4 conversation-state fan-in replay."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.conversation_state_fan_in import (  # noqa: E402
    STATES,
    assemble_conversation_state_fan_in,
    build_reader_result,
    build_semantic_record,
    build_source_registry,
    planned_reader,
    validate_conversation_state_fan_in,
)
from engine.system_b.r3_fresh_consumer import value_sha256  # noqa: E402


CORPUS_ROOT = ROOT / "research/simulated-reliability-corpus-v1-2026-07-12"
SOURCE_ROOT = CORPUS_ROOT / "naturalized-transfer-sources"
PREFLIGHT_ROOT = CORPUS_ROOT / "provider-free-role-input-preflight/transfer"
TRANSFER_ROOT = ROOT / "research/simulated-reliability-v1-transfer-2026-07-12/t1"
CONTRACT_PATH = ROOT / "docs/evals/lolla-r4-conversation-state-fan-in-contract-v1.json"
OUTPUT_ROOT = ROOT / "research/lolla-r4-conversation-state-fan-in-2026-07-13"
SUMMARY_PATH = OUTPUT_ROOT / "replay-result.json"

CASE_IDS = (
    "v1-case01-flood-infrastructure",
    "v1-case02-discharge-transport",
    "v1-case06-industry-funded-lab",
    "v1-case09-software-migration",
)
COMPLETE_CASES = {
    "v1-case01-flood-infrastructure",
    "v1-case02-discharge-transport",
}
ROLE_JOIN_FAILURE = "v1-case06-industry-funded-lab"
TRANSPORT_FAILURE = "v1-case09-software-migration"


class R4FanInReplayError(RuntimeError):
    """Raised when the frozen fan-in replay or exact evidence drifts."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R4FanInReplayError(f"expected JSON object: {_relative(path)}")
    return value


def _relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _planned_readers() -> list[dict[str, str]]:
    actual = "google/gemini-3.5-flash-20260519"
    readers = [
        planned_reader(
            reader_id="legacy-current-position-reader",
            surface="current_position",
            producer_kind="simulated_reliability_v1",
            producer_id=actual,
        ),
        planned_reader(
            reader_id="legacy-qualification-reader",
            surface="qualification",
            producer_kind="simulated_reliability_v1",
            producer_id=actual,
        ),
        planned_reader(
            reader_id="legacy-starting-position-reader",
            surface="starting_position",
            producer_kind="simulated_reliability_v1",
            producer_id=actual,
        ),
        planned_reader(
            reader_id="planned-cross-thread-relationship-reader",
            surface="cross_thread_relationship",
            producer_kind="v1_contract_surface_unavailable",
            producer_id="not_implemented_in_primary_v1",
        ),
        planned_reader(
            reader_id="planned-reopen-condition-reader",
            surface="reopen_condition",
            producer_kind="v1_contract_surface_unavailable",
            producer_id="not_implemented_in_primary_v1",
        ),
        planned_reader(
            reader_id="planned-unresolved-matter-reader",
            surface="unresolved_matter",
            producer_kind="v1_contract_surface_unavailable",
            producer_id="not_implemented_in_primary_v1",
        ),
    ]
    return sorted(readers, key=lambda item: item["reader_id"])


def _semantic_record(
    *,
    registry: Mapping[str, Any],
    observation: Mapping[str, Any],
    surface: str,
) -> dict[str, Any]:
    record_id = str(observation.get("role_record_id") or observation.get("observation_id"))
    aliases = observation.get("source_evidence_ids")
    if not isinstance(aliases, list):
        raise R4FanInReplayError(f"role observation has no explicit aliases: {record_id}")
    return build_semantic_record(
        source_registry=registry,
        record_id=record_id,
        surface=surface,
        semantic_payload=observation,
        source_aliases=aliases,
    )


def _artifact_material(path: Path) -> tuple[str, bytes]:
    return _relative(path), path.read_bytes()


def _missing_result(
    *, reader: Mapping[str, Any], code: str, stage: str, detail: str
) -> dict[str, Any]:
    return build_reader_result(
        reader=reader,
        state="missing",
        records=[],
        issue_code=code,
        issue_stage=stage,
        safe_detail=detail,
    )


def _case_material(case_id: str) -> tuple[dict[str, Any], dict[str, bytes], bytes]:
    source_path = SOURCE_ROOT / f"{case_id}.txt"
    source_bytes = source_path.read_bytes()
    wrapper = _load(PREFLIGHT_ROOT / case_id / "position-wrapper.json")
    aliases = wrapper.get("focal_alias_map")
    if not isinstance(aliases, list):
        raise R4FanInReplayError(f"source alias registry is unavailable: {case_id}")
    registry = build_source_registry(
        case_id=case_id,
        source_path=_relative(source_path),
        source_bytes=source_bytes,
        message_count=24,
        aliases=aliases,
    )
    readers = _planned_readers()
    reader_index = {item["reader_id"]: item for item in readers}
    artifacts: dict[str, bytes] = {}
    results: dict[str, dict[str, Any]] = {}

    if case_id in COMPLETE_CASES:
        joined_path = TRANSFER_ROOT / f"{case_id}-primary" / "joined-role-records.json"
        artifact_path, artifact_bytes = _artifact_material(joined_path)
        artifacts[artifact_path] = artifact_bytes
        joined = _load(joined_path)
        for role, reader_id, surface in (
            ("starting", "legacy-starting-position-reader", "starting_position"),
            ("current", "legacy-current-position-reader", "current_position"),
            ("qualification", "legacy-qualification-reader", "qualification"),
        ):
            observations = joined.get("role_observations", {}).get(role, [])
            if not isinstance(observations, list):
                raise R4FanInReplayError(f"role observations are invalid: {case_id}/{role}")
            records = [
                _semantic_record(registry=registry, observation=item, surface=surface)
                for item in observations
            ]
            results[reader_id] = build_reader_result(
                reader=reader_index[reader_id],
                state="complete" if records else "completed_zero",
                records=records,
                artifact_path=artifact_path,
                artifact_bytes=artifact_bytes,
            )
    elif case_id == ROLE_JOIN_FAILURE:
        result_path = TRANSFER_ROOT / f"{case_id}-primary" / "result.json"
        artifact_path, artifact_bytes = _artifact_material(result_path)
        artifacts[artifact_path] = artifact_bytes
        historical = _load(result_path)
        calls = historical.get("calls")
        if not isinstance(calls, list) or len(calls) != 2:
            raise R4FanInReplayError("Case 06 historical call custody drifted")
        results["legacy-starting-position-reader"] = build_reader_result(
            reader=reader_index["legacy-starting-position-reader"],
            state="failed",
            records=[],
            artifact_path=artifact_path,
            artifact_bytes=artifact_bytes,
            issue_code="schema_or_custody_failed",
            issue_stage="starting_role_custody",
            safe_detail="The provider output existed but its admitted starting-position record failed exact alias custody.",
        )
        observations = calls[1].get("compiled", {}).get("observations", [])
        for role, reader_id, surface in (
            ("current", "legacy-current-position-reader", "current_position"),
            ("qualification", "legacy-qualification-reader", "qualification"),
        ):
            records = [
                _semantic_record(registry=registry, observation=item, surface=surface)
                for item in observations
                if item.get("role") == role
            ]
            results[reader_id] = build_reader_result(
                reader=reader_index[reader_id],
                state="partial",
                records=records,
                artifact_path=artifact_path,
                artifact_bytes=artifact_bytes,
                issue_code="source_run_incomplete",
                issue_stage="system_role_join",
                safe_detail="Explicit admitted records survive, but the source run stopped after the starting-position custody failure.",
            )
    elif case_id == TRANSPORT_FAILURE:
        call_path = TRANSFER_ROOT / f"{case_id}-primary" / "call-01-starting-result.json"
        artifact_path, artifact_bytes = _artifact_material(call_path)
        artifacts[artifact_path] = artifact_bytes
        call = _load(call_path)
        if call.get("operational_status") != "http_error_402":
            raise R4FanInReplayError("Case 09 transport state drifted")
        results["legacy-starting-position-reader"] = build_reader_result(
            reader=reader_index["legacy-starting-position-reader"],
            state="failed",
            records=[],
            artifact_path=artifact_path,
            artifact_bytes=artifact_bytes,
            issue_code="transport_failed",
            issue_stage="starting_role_transport",
            safe_detail="The preserved request stopped before semantic inference; raw provider error details are not copied.",
        )
        for reader_id in ("legacy-current-position-reader", "legacy-qualification-reader"):
            results[reader_id] = _missing_result(
                reader=reader_index[reader_id],
                code="upstream_dependency_unavailable",
                stage="starting_role_transport",
                detail="This reader was not run after the starting-position transport failure.",
            )
    else:
        raise R4FanInReplayError(f"unsupported replay case: {case_id}")

    for reader_id, surface_name in (
        ("planned-cross-thread-relationship-reader", "cross-thread relationship"),
        ("planned-reopen-condition-reader", "reopen condition"),
        ("planned-unresolved-matter-reader", "unresolved matter"),
    ):
        results[reader_id] = _missing_result(
            reader=reader_index[reader_id],
            code="reader_not_implemented",
            stage="v1_primary_contract",
            detail=f"No distinct primary V1 {surface_name} reader contract exists.",
        )

    ordered_results = [results[item["reader_id"]] for item in readers]
    value = assemble_conversation_state_fan_in(
        source_registry=registry,
        planned_readers=readers,
        reader_results=ordered_results,
        source_bytes=source_bytes,
        artifact_bytes_by_path=artifacts,
    )
    return value, artifacts, source_bytes


def _summary(case_values: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    state_counts: Counter[str] = Counter()
    for value in case_values.values():
        state_counts.update(value["fan_in"]["reader_state_counts"])
    body = {
        "schema_version": "lolla.r4_conversation_state_fan_in_replay_result.v1",
        "status": "provider_free_fan_in_replay_complete",
        "date": "2026-07-13",
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "runtime_graph_prompt_or_model_changes": 0,
        "contract": {
            "path": _relative(CONTRACT_PATH),
            "sha256": _sha(CONTRACT_PATH),
        },
        "cases": [
            {
                "case_id": case_id,
                "fan_in_path": _relative(OUTPUT_ROOT / case_id / "fan-in.json"),
                "fan_in_file_sha256": _sha(OUTPUT_ROOT / case_id / "fan-in.json"),
                "fan_in_result_sha256": value["result_sha256"],
                "status": value["status"],
                "reader_state_counts": value["fan_in"]["reader_state_counts"],
                "total_record_count": value["fan_in"]["total_record_count"],
                "total_source_locator_count": value["fan_in"]["total_source_locator_count"],
                "handoff_payload_utf8_bytes": value["fan_in"]["handoff_payload_utf8_bytes"],
            }
            for case_id, value in case_values.items()
        ],
        "aggregate": {
            "case_count": len(case_values),
            "reader_result_count": sum(
                value["fan_in"]["planned_reader_count"] for value in case_values.values()
            ),
            "reader_state_counts": {state: state_counts[state] for state in STATES},
            "admitted_record_count": sum(
                value["fan_in"]["total_record_count"] for value in case_values.values()
            ),
            "source_locator_count": sum(
                value["fan_in"]["total_source_locator_count"] for value in case_values.values()
            ),
            "all_handoffs_within_bounds": all(
                value["fan_in"]["within_bounds"] for value in case_values.values()
            ),
        },
        "findings": [
            "The complete Case 01 path preserves three admitted role records and keeps all three unavailable surfaces explicitly missing.",
            "Case 02 preserves a completed-zero qualification reader separately from three missing reader contracts.",
            "Case 06 preserves two admitted partial surfaces beside one failed custody surface; no record is fabricated for the failure.",
            "Case 09 preserves one transport failure separately from five missing downstream or unimplemented readers without copying raw provider error content.",
            "Every preserved record retains its provider-authored payload, canonical payload hash, exact source locators, speaker, and turn index.",
            "The fan-in measures overlap and load but performs no semantic merge, absence inference, graph routing, or quality scoring."
        ],
        "expected_changed_measurement": {
            "status": "passed_provider_free",
            "observation": "Every planned reader has one inspectable tagged result, and completed-zero, partial, failed, and missing states remain mechanically distinguishable in the same handoff.",
            "semantic_improvement_claimed": False
        },
        "next_experiment_decision": {
            "provider_free_preparation_earned": True,
            "provider_call_authorized": False,
            "runtime_integration_authorized": False,
            "proposal": "Freeze one bounded complementary unresolved-matter/reopen-condition read and one exact-ID relationship read over an exposed false-stand-down case plus a restraint control, then authorize no call until source-first targets, schemas, cost, provider policy, and fan-in gates pass locally.",
            "reason": "The assembly defect is repaired provider-free, while the primary V1 evidence still contains no distinct records for the three newly visible semantic surfaces. Their usefulness and effect on false stand-down remain unknown."
        },
        "non_claims": [
            "not semantic correctness or coverage proof",
            "not evidence that the missing readers will recover the reviewed material pressure",
            "not graph, answer, decision, trust, or real-user usefulness evidence",
            "not authorization for a provider call or runtime integration"
        ]
    }
    return {**body, "result_sha256": value_sha256(body)}


def build() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    case_values = {}
    for case_id in CASE_IDS:
        value, _artifacts, _source_bytes = _case_material(case_id)
        case_values[case_id] = value
        _write(OUTPUT_ROOT / case_id / "fan-in.json", value)
    summary = _summary(case_values)
    _write(SUMMARY_PATH, summary)
    return summary, case_values


def validate() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    case_values = {}
    for case_id in CASE_IDS:
        expected, artifacts, source_bytes = _case_material(case_id)
        checked_in = _load(OUTPUT_ROOT / case_id / "fan-in.json")
        validate_conversation_state_fan_in(
            checked_in,
            source_bytes=source_bytes,
            artifact_bytes_by_path=artifacts,
        )
        if checked_in != expected:
            raise R4FanInReplayError(f"checked-in fan-in replay drifted: {case_id}")
        case_values[case_id] = checked_in
    summary = _load(SUMMARY_PATH)
    expected_summary = _summary(case_values)
    if summary != expected_summary:
        raise R4FanInReplayError("checked-in fan-in summary drifted")
    if summary.get("result_sha256") != value_sha256(
        {key: item for key, item in summary.items() if key != "result_sha256"}
    ):
        raise R4FanInReplayError("fan-in summary self-hash drifted")
    return summary, case_values


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    summary, _cases = validate() if args.validate_only else build()
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
