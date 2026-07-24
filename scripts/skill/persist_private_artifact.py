#!/usr/bin/env python3
"""Persist agent-authored Lolla runtime artifacts through private stdin."""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.system_b.constitutional_graph_survival import (  # noqa: E402
    finalize_constitutional_graph_survival_ledger,
)
from engine.system_b.pre_step6_private_table import (  # noqa: E402
    finalize_pre_step6_private_table_ledger,
)
from engine.system_b.private_runtime import (  # noqa: E402
    PrivateInputError,
    atomic_private_write_json,
    atomic_private_write_text,
    read_private_stdin,
)
from engine.system_b.run_events import append_run_event  # noqa: E402
from engine.system_b.run_state import (  # noqa: E402
    assert_expected_run_state,
    is_valid_run_id,
)
from engine.system_b.v60_enrichment import (  # noqa: E402
    finalize_v60_consideration,
)


GRAPH_MUTABLE_FIELDS = frozenset(
    {
        "disposition",
        "strongest_plausible_application",
        "attempted_application_condition",
        "why",
        "failed_condition",
        "reopen_condition",
        "visible_effect",
        "private_guardrail",
        "risk_if_forced",
        "risk_if_ignored",
    }
)
PRIVATE_TABLE_MUTABLE_FIELDS = frozenset(
    {"disposition", "why", "visible_effect", "private_guardrail"}
)
V60_MUTABLE_FIELDS = frozenset(
    {
        "disposition",
        "route",
        "strongest_plausible_application",
        "why",
        "visible_effect",
        "private_guardrail",
        "risk_if_forced",
        "technical_blocker",
        "blocked_or_guarded_claim",
        "uncertainty_boundary",
    }
)
MEMO_FIELDS = (
    "memo_substantive_title",
    "memo_orientation_note",
    "memo_what_changed",
    "memo_what_still_holds",
    "memo_take_back_or_set_aside",
    "memo_pressure_check",
)


class PacketValidationError(ValueError):
    """The private packet is structurally invalid."""

    def __init__(self, errors: list[str]):
        super().__init__("; ".join(errors))
        self.errors = errors


def _mapping(value: object, *, field: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise PacketValidationError([f"{field} must be an object"])
    return {str(key): item for key, item in value.items()}


def _require_exact_keys(
    payload: Mapping[str, Any],
    *,
    allowed: set[str] | frozenset[str],
    required: set[str] | frozenset[str],
    field: str,
) -> None:
    observed = set(payload)
    errors: list[str] = []
    unknown = sorted(observed - set(allowed))
    missing = sorted(set(required) - observed)
    if unknown:
        errors.append(f"{field} contains unknown fields: {unknown}")
    if missing:
        errors.append(f"{field} is missing fields: {missing}")
    if errors:
        raise PacketValidationError(errors)


def _fill_items(
    *,
    skeleton_items: list[dict[str, Any]],
    decisions: object,
    identity_field: str,
    mutable_fields: frozenset[str],
    field: str,
) -> list[dict[str, Any]]:
    decision_map = _mapping(decisions, field=field)
    expected_ids = [str(item.get(identity_field) or "") for item in skeleton_items]
    if any(not value for value in expected_ids):
        raise PacketValidationError([f"{field} skeleton identity is incomplete"])
    if set(decision_map) != set(expected_ids):
        missing = sorted(set(expected_ids) - set(decision_map))
        unknown = sorted(set(decision_map) - set(expected_ids))
        errors = []
        if missing:
            errors.append(f"{field} is missing {len(missing)} skeleton items")
        if unknown:
            errors.append(f"{field} contains {len(unknown)} unknown items")
        raise PacketValidationError(errors)

    filled: list[dict[str, Any]] = []
    for skeleton in skeleton_items:
        identity = str(skeleton[identity_field])
        decision = _mapping(decision_map[identity], field=f"{field}.{identity}")
        row_mutable_fields = mutable_fields.intersection(skeleton)
        _require_exact_keys(
            decision,
            allowed=row_mutable_fields,
            required=row_mutable_fields,
            field=f"{field}.{identity}",
        )
        row = copy.deepcopy(skeleton)
        for key in row_mutable_fields:
            value = decision.get(key, "")
            if not isinstance(value, str):
                raise PacketValidationError(
                    [f"{field}.{identity}.{key} must be a string"]
                )
            row[key] = value.strip()
        filled.append(row)
    return filled


def _build_graph_ledger(result: Mapping[str, Any], decisions: object) -> dict[str, Any] | None:
    portfolio = result.get("constitutional_graph_survival")
    if not isinstance(portfolio, Mapping) or portfolio.get("status") != "active":
        if decisions not in ({}, None):
            raise PacketValidationError(
                ["graph_decisions must be empty when graph pressure is not active"]
            )
        return None
    skeleton = copy.deepcopy(portfolio.get("disposition_ledger_skeleton"))
    if not isinstance(skeleton, dict):
        raise PacketValidationError(["graph ledger skeleton is missing"])
    skeleton["status"] = "completed"
    skeleton["items"] = _fill_items(
        skeleton_items=[dict(item) for item in skeleton.get("items") or []],
        decisions=decisions,
        identity_field="pressure_id",
        mutable_fields=GRAPH_MUTABLE_FIELDS,
        field="graph_decisions",
    )
    return skeleton


def _build_private_table_ledger(
    result: Mapping[str, Any], decisions: object
) -> dict[str, Any] | None:
    table = result.get("pre_step6_private_table")
    if not isinstance(table, Mapping) or table.get("status") != "ready":
        if decisions not in ({}, None):
            raise PacketValidationError(
                [
                    "private_table_decisions must be empty when the private table "
                    "is not ready"
                ]
            )
        return None
    skeleton = copy.deepcopy(table.get("consideration_ledger_skeleton"))
    if not isinstance(skeleton, dict):
        raise PacketValidationError(["private-table ledger skeleton is missing"])
    skeleton["status"] = "completed"
    skeleton["items"] = _fill_items(
        skeleton_items=[dict(item) for item in skeleton.get("items") or []],
        decisions=decisions,
        identity_field="source_id",
        mutable_fields=PRIVATE_TABLE_MUTABLE_FIELDS,
        field="private_table_decisions",
    )
    return skeleton


def _build_v60_ledger(result: Mapping[str, Any], decisions: object) -> dict[str, Any] | None:
    enrichment = result.get("v60_enrichment")
    if not isinstance(enrichment, Mapping) or enrichment.get("status") != "active":
        if decisions not in ({}, None):
            raise PacketValidationError(
                ["v60_decisions must be empty when V60 enrichment is not active"]
            )
        return None
    skeleton = copy.deepcopy(enrichment.get("consideration_ledger_skeleton"))
    if not isinstance(skeleton, dict):
        raise PacketValidationError(["V60 ledger skeleton is missing"])
    skeleton["transactions"] = _fill_items(
        skeleton_items=[dict(item) for item in skeleton.get("transactions") or []],
        decisions=decisions,
        identity_field="chunk_id",
        mutable_fields=V60_MUTABLE_FIELDS,
        field="v60_decisions",
    )
    return skeleton


def _persist_step6(
    *,
    run_id: str,
    tmp_dir: Path,
    packet: Mapping[str, Any],
) -> str:
    required = {
        "revised_answer",
        "graph_decisions",
        "private_table_decisions",
        "v60_decisions",
    }
    _require_exact_keys(
        packet,
        allowed=required,
        required=required,
        field="step6",
    )
    revised = packet.get("revised_answer")
    if not isinstance(revised, str) or not revised.strip():
        raise PacketValidationError(["revised_answer must be non-empty text"])
    revised = revised.strip()

    result_path = tmp_dir / f"lolla_{run_id}_result.json"
    if not result_path.exists():
        raise PacketValidationError(["result artifact is missing"])
    result = json.loads(result_path.read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise PacketValidationError(["result artifact must contain an object"])

    graph_ledger = _build_graph_ledger(result, packet["graph_decisions"])
    private_ledger = _build_private_table_ledger(
        result, packet["private_table_decisions"]
    )
    v60_ledger = _build_v60_ledger(result, packet["v60_decisions"])

    prospective = copy.deepcopy(result)
    prospective["revised_answer"] = revised
    prospective["revised_answer_source"] = "agent_step6_private_runtime"
    prospective["revised_answer_present"] = True
    prospective["revised_answer_written_at"] = dt.datetime.now(
        dt.timezone.utc
    ).strftime("%Y-%m-%dT%H:%M:%SZ")
    prospective = finalize_constitutional_graph_survival_ledger(
        prospective,
        ledger=graph_ledger,
    )
    prospective = finalize_pre_step6_private_table_ledger(
        prospective,
        ledger=private_ledger,
    )
    prospective = finalize_v60_consideration(
        prospective,
        ledger=v60_ledger,
    )
    validations = {
        "graph": (
            prospective.get("constitutional_graph_survival_ledger_validation")
            or {}
        ).get("status", "not_required"),
        "private_table": (
            prospective.get("pre_step6_private_table_ledger_validation") or {}
        ).get("status", "not_required"),
        "v60": (
            prospective.get("v60_consideration_validation") or {}
        ).get(
            "status",
            "not_required"
            if (prospective.get("v60_enrichment") or {}).get("status") != "active"
            else "missing",
        ),
    }
    errors: list[str] = []
    for name, status in validations.items():
        if status not in {"valid", "not_required"}:
            validation_key = {
                "graph": "constitutional_graph_survival_ledger_validation",
                "private_table": "pre_step6_private_table_ledger_validation",
                "v60": "v60_consideration_validation",
            }[name]
            validation = prospective.get(validation_key) or {}
            reported = validation.get("errors") or [f"{name} ledger is {status}"]
            errors.extend(str(item) for item in reported)
    if errors:
        raise PacketValidationError(errors)

    # Everything above is in-memory. No runtime artifact is replaced until all
    # three ledgers and the revised answer pass deterministic validation.
    atomic_private_write_text(tmp_dir / f"lolla_{run_id}_revised.txt", revised + "\n")
    if graph_ledger is not None:
        atomic_private_write_json(
            tmp_dir / f"lolla_{run_id}_constitutional_graph_survival_ledger.json",
            graph_ledger,
        )
    if private_ledger is not None:
        atomic_private_write_json(
            tmp_dir / f"lolla_{run_id}_pre_step6_private_table_ledger.json",
            private_ledger,
        )
    if v60_ledger is not None:
        atomic_private_write_json(
            tmp_dir / f"lolla_{run_id}_v60_ledger.json",
            v60_ledger,
        )
    atomic_private_write_json(result_path, prospective)

    transcript_path = Path(
        os.getenv("LOLLA_LIVE_TRANSCRIPT")
        or tmp_dir / f"lolla_{run_id}_live_transcript.txt"
    )
    existing = (
        transcript_path.read_text(encoding="utf-8")
        if transcript_path.exists()
        else ""
    )
    if revised not in existing:
        separator = "" if not existing or existing.endswith("\n\n") else "\n\n"
        atomic_private_write_text(
            transcript_path,
            existing + separator + revised + "\n",
        )
    elif transcript_path.exists():
        transcript_path.chmod(0o600)

    return (
        "PRIVATE_PERSIST_STATUS: step6 valid; "
        f"graph={validations['graph']}; "
        f"private_table={validations['private_table']}; "
        f"v60={validations['v60']}"
    )


def _persist_narration(
    *, run_id: str, tmp_dir: Path, source: str
) -> str:
    text = source.strip()
    if not text:
        raise PacketValidationError(["narration must be non-empty"])
    transcript_path = Path(
        os.getenv("LOLLA_LIVE_TRANSCRIPT")
        or tmp_dir / f"lolla_{run_id}_live_transcript.txt"
    )
    existing = (
        transcript_path.read_text(encoding="utf-8")
        if transcript_path.exists()
        else ""
    )
    if existing.rstrip("\n").endswith(text):
        transcript_path.chmod(0o600)
    else:
        separator = "" if not existing or existing.endswith("\n\n") else "\n\n"
        atomic_private_write_text(
            transcript_path,
            existing + separator + text + "\n",
        )
    return "PRIVATE_PERSIST_STATUS: narration ready"


def _persist_memo(
    *, run_id: str, tmp_dir: Path, packet: Mapping[str, Any]
) -> str:
    _require_exact_keys(
        packet,
        allowed=set(MEMO_FIELDS),
        required=set(MEMO_FIELDS),
        field="memo",
    )
    note: dict[str, str] = {}
    for key in MEMO_FIELDS:
        value = packet.get(key)
        if not isinstance(value, str):
            raise PacketValidationError([f"memo.{key} must be a string"])
        note[key] = value.strip()

    result_path = tmp_dir / f"lolla_{run_id}_result.json"
    try:
        result = json.loads(result_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PacketValidationError(
            ["memo requires the exact run's result artifact"]
        ) from exc
    if not isinstance(result, dict):
        raise PacketValidationError(["the exact run result must be an object"])
    for key in MEMO_FIELDS:
        result[key] = note[key]
    result["memo_note_written_at"] = dt.datetime.now(
        dt.timezone.utc
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

    atomic_private_write_json(
        tmp_dir / f"lolla_{run_id}_memo_note.json",
        note,
    )
    atomic_private_write_json(result_path, result)
    return "PRIVATE_PERSIST_STATUS: memo_note ready"


def _persist_receipt_override(
    *, run_id: str, tmp_dir: Path, source: str
) -> str:
    text = source.strip()
    if not text:
        raise PacketValidationError(["receipt override must be non-empty"])
    atomic_private_write_text(
        tmp_dir / f"lolla_{run_id}_final_receipt_override.txt",
        text + "\n",
    )
    return "PRIVATE_PERSIST_STATUS: receipt_override ready"


def _safe_failure(
    *,
    run_id: str,
    tmp_dir: Path,
    kind: str,
    error_class: str,
    errors: list[str],
) -> str:
    operator_path = Path(
        os.getenv("LOLLA_OPERATOR_LOG")
        or tmp_dir / f"lolla_{run_id}_operator.log"
    )
    lines = [
        f"private persistence failure: kind={kind}",
        f"error_class={error_class}",
        f"error_count={len(errors)}",
        *[f"- {error}" for error in errors],
    ]
    operator_recorded = False
    try:
        existing = (
            operator_path.read_text(encoding="utf-8")
            if operator_path.exists()
            else ""
        )
        atomic_private_write_text(
            operator_path,
            existing + ("" if not existing or existing.endswith("\n") else "\n")
            + "\n".join(lines)
            + "\n",
        )
        operator_recorded = True
    except Exception:
        # This is the outer privacy boundary. A secondary diagnostic failure
        # must not expose a traceback or the private payload.
        operator_recorded = False

    events_path = tmp_dir / f"lolla_{run_id}_run_events.json"
    event_recorded = False
    try:
        append_run_event(
            run_id=run_id,
            event_type="private_persistence_failed",
            actor="skill",
            path=events_path,
            details={
                "error_class": error_class,
                "error_count": len(errors),
                "kind": kind,
                "private_payload_visible": False,
                "replacement_status": "not_written",
            },
        )
        events_path.chmod(0o600)
        event_recorded = True
    except Exception:
        event_recorded = False

    if operator_recorded and event_recorded:
        return "recorded"
    if operator_recorded or event_recorded:
        return "partial"
    return "failed"


def _record_success_event(*, run_id: str, tmp_dir: Path, kind: str) -> bool:
    events_path = tmp_dir / f"lolla_{run_id}_run_events.json"
    try:
        append_run_event(
            run_id=run_id,
            event_type="private_persistence_completed",
            actor="skill",
            path=events_path,
            details={
                "kind": kind,
                "private_payload_visible": False,
                "replacement_status": "written",
            },
        )
        events_path.chmod(0o600)
        return True
    except Exception:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument(
        "--kind",
        required=True,
        choices=("narration", "step6", "memo", "receipt"),
    )
    parser.add_argument("--tmp-dir", default=os.getenv("LOLLA_TMP_DIR", "/tmp"))
    args = parser.parse_args()

    run_id = str(args.run_id).strip()
    tmp_dir = Path(args.tmp_dir).expanduser()
    if not is_valid_run_id(run_id):
        print("PRIVATE_PERSIST_STATUS: invalid_run; replacement=none", file=sys.stderr)
        return 2
    try:
        assert_expected_run_state(
            actual_run_id=run_id,
            phase=f"persist_private_{args.kind}",
        )
    except SystemExit:
        print("PRIVATE_PERSIST_STATUS: run_mismatch; replacement=none", file=sys.stderr)
        return 2

    try:
        source = read_private_stdin()
    except PrivateInputError:
        print(
            f"PRIVATE_PERSIST_STATUS: {args.kind} unavailable; replacement=none",
            file=sys.stderr,
        )
        return 2

    try:
        if args.kind == "narration":
            receipt = _persist_narration(
                run_id=run_id,
                tmp_dir=tmp_dir,
                source=source,
            )
        elif args.kind == "receipt":
            receipt = _persist_receipt_override(
                run_id=run_id,
                tmp_dir=tmp_dir,
                source=source,
            )
        else:
            raw = json.loads(source)
            packet = _mapping(raw, field=args.kind)
            if args.kind == "step6":
                receipt = _persist_step6(
                    run_id=run_id,
                    tmp_dir=tmp_dir,
                    packet=packet,
                )
            else:
                receipt = _persist_memo(
                    run_id=run_id,
                    tmp_dir=tmp_dir,
                    packet=packet,
                )
    except (json.JSONDecodeError, PacketValidationError, OSError, ValueError) as exc:
        if isinstance(exc, PacketValidationError):
            errors = exc.errors
            error_class = "validation_error"
        elif isinstance(exc, json.JSONDecodeError):
            errors = ["private input was not valid JSON"]
            error_class = "json_error"
        else:
            errors = [type(exc).__name__]
            error_class = "runtime_error"
        _safe_failure(
            run_id=run_id,
            tmp_dir=tmp_dir,
            kind=args.kind,
            error_class=error_class,
            errors=errors,
        )
        print(
            f"PRIVATE_PERSIST_STATUS: {args.kind} invalid; "
            f"error_count={len(errors)}; replacement=none",
            file=sys.stderr,
        )
        return 2

    if not _record_success_event(run_id=run_id, tmp_dir=tmp_dir, kind=args.kind):
        print(
            f"PRIVATE_PERSIST_STATUS: {args.kind} incomplete; "
            "replacement=written; event_custody=failed",
            file=sys.stderr,
        )
        return 2
    print(receipt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
