#!/usr/bin/env python3
"""Build actual and reviewed-oracle semantic overlays without model calls."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

CONTRACT_SCHEMA = "lolla.semantic_overlay_counterfactual_contract.v0"
OUTPUT_SCHEMA = "lolla.semantic_overlay_counterfactual_packets.v0"


class OverlayError(ValueError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise OverlayError(f"expected JSON object: {path}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require_hash(path: Path, expected: str, label: str) -> None:
    if not path.is_file():
        raise OverlayError(f"{label} missing: {path}")
    if _sha256(path) != expected:
        raise OverlayError(f"{label} hash mismatch")


def _source_handle(event: Mapping[str, Any]) -> tuple[int, str, str]:
    source = event.get("source")
    if isinstance(source, Mapping):
        quote = str(source.get("quote") or "")
        if quote:
            return (
                int(source.get("turn_index") or 0),
                str(source.get("speaker") or ""),
                quote,
            )
    provenance = event.get("provenance")
    if isinstance(provenance, Mapping):
        span = provenance.get("span_ref")
        if isinstance(span, Mapping):
            return (
                int(span.get("turn_index") or event.get("turn_index") or 0),
                str(span.get("speaker") or event.get("speaker") or ""),
                str(event.get("text") or ""),
            )
    return 0, "", ""


def _event_role(event: Mapping[str, Any]) -> str:
    for field in (
        "stance",
        "kind",
        "question_function",
        "status",
        "family",
    ):
        value = str(event.get(field) or "").strip()
        if value:
            return value
    return "unlabeled"


def _validate_exact_source(
    *,
    turn_index: int,
    speaker: str,
    quote: str,
    turns: Mapping[tuple[int, str], str],
) -> None:
    source_text = str(turns.get((turn_index, speaker), ""))
    if not quote or quote not in source_text:
        raise OverlayError(
            f"invalid source handle turn={turn_index} speaker={speaker!r} quote={quote!r}"
        )


def build_packets(contract_path: Path) -> dict[str, Any]:
    from engine.system_b.core_semantic_comparison import _parse_turns

    contract = _load_json(contract_path)
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise OverlayError("unexpected counterfactual contract schema")
    if contract.get("status") != "no_cost_packet_design_no_calls_authorized":
        raise OverlayError("counterfactual contract status drifted")

    case = contract["case"]
    source_path = REPO_ROOT / case["source_path"]
    _require_hash(source_path, case["source_sha256"], "source")
    turns = _parse_turns(source_path.read_text(encoding="utf-8"))

    actual_contract = contract["actual_overlay"]
    shadow_path = REPO_ROOT / actual_contract["shadow_path"]
    _require_hash(shadow_path, actual_contract["shadow_sha256"], "shadow")
    shadow = _load_json(shadow_path)
    semantic_events = shadow.get("semantic_events", {})
    if not isinstance(semantic_events, dict):
        raise OverlayError("shadow semantic_events missing")

    actual_events: list[dict[str, Any]] = []
    family_counts: dict[str, int] = {}
    for family in sorted(semantic_events):
        events = semantic_events[family]
        if not isinstance(events, list):
            raise OverlayError(f"semantic family is not an array: {family}")
        for event in events:
            if not isinstance(event, dict):
                raise OverlayError(f"semantic event is not an object: {family}")
            if event.get("candidate_state") != "selected_for_current_view":
                continue
            turn_index, speaker, quote = _source_handle(event)
            _validate_exact_source(
                turn_index=turn_index,
                speaker=speaker,
                quote=quote,
                turns=turns,
            )
            actual_events.append(
                {
                    "family": family,
                    "role": _event_role(event),
                    "turn_index": turn_index,
                    "speaker": speaker,
                    "quote": quote,
                    "candidate_id": event.get("candidate_id"),
                }
            )
            family_counts[family] = family_counts.get(family, 0) + 1
    if len(actual_events) != int(actual_contract["expected_event_count"]):
        raise OverlayError("actual overlay event count mismatch")

    oracle_contract = contract["reviewed_oracle_addition"]
    observation_path = REPO_ROOT / oracle_contract["contract_path"]
    _require_hash(
        observation_path,
        oracle_contract["contract_sha256"],
        "observation contract",
    )
    observations = _load_json(observation_path).get("observations", [])
    observation = next(
        (
            item
            for item in observations
            if isinstance(item, dict)
            and item.get("qualified_observation_id")
            == oracle_contract["qualified_observation_id"]
        ),
        None,
    )
    if observation is None:
        raise OverlayError("reviewed oracle observation missing")
    if observation.get("review_status") != oracle_contract["allowed_review_status"]:
        raise OverlayError("oracle observation is not source reviewed")
    oracle_events: list[dict[str, Any]] = []
    for evidence in observation.get("evidence", []):
        if not isinstance(evidence, dict):
            continue
        turn_index = int(evidence["turn_index"])
        speaker = str(evidence["speaker"])
        quote = str(evidence["quote"])
        _validate_exact_source(
            turn_index=turn_index,
            speaker=speaker,
            quote=quote,
            turns=turns,
        )
        oracle_events.append(
            {
                "family": "reviewed_oracle_addition",
                "role": "+".join(map(str, evidence.get("semantic_roles", []))),
                "turn_index": turn_index,
                "speaker": speaker,
                "quote": quote,
                "qualified_observation_id": observation[
                    "qualified_observation_id"
                ],
                "temporal_role": evidence.get("temporal_role"),
            }
        )
    if not oracle_events:
        raise OverlayError("reviewed oracle has no exact evidence")

    actual_quote_set = {
        (item["turn_index"], item["speaker"], item["quote"])
        for item in actual_events
    }
    for item in oracle_events:
        item["missing_from_actual_overlay"] = (
            item["turn_index"], item["speaker"], item["quote"]
        ) not in actual_quote_set

    return {
        "schema_version": OUTPUT_SCHEMA,
        "status": "packets_built_no_model_calls",
        "case_id": case["case_id"],
        "source_sha256": case["source_sha256"],
        "actual_overlay": {
            "selection_rule": actual_contract["selection_rule"],
            "event_count": len(actual_events),
            "family_counts": family_counts,
            "events": actual_events,
        },
        "reviewed_oracle_addition": {
            "purpose": oracle_contract["purpose"],
            "event_count": len(oracle_events),
            "events": oracle_events,
        },
        "arms": contract["arms"],
        "future_call_budget_if_separately_authorized": contract[
            "future_call_budget_if_separately_authorized"
        ],
        "non_claims": contract["non_claims"],
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    payload = build_packets(args.contract)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "actual_event_count": payload["actual_overlay"]["event_count"],
                "oracle_event_count": payload["reviewed_oracle_addition"][
                    "event_count"
                ],
                "future_calls_authorized": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
