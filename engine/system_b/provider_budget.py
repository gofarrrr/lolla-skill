"""Durable provider-call budget custody for one Lolla run.

The ledger is deterministic infrastructure.  It never decides whether a call
is semantically useful; it only prevents an execution from exceeding the
declared call or worst-case USD envelope and preserves each reservation.
"""
from __future__ import annotations

import datetime as _dt
import fcntl
import json
import os
import threading
import uuid
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "lolla.provider_budget.v1"
DEFAULT_MAX_PROVIDER_CALLS = 96
DEFAULT_MAX_PROVIDER_COST_USD = 0.25


class ProviderBudgetExceeded(RuntimeError):
    """Raised before a network call when the frozen envelope is exhausted."""


_MEMORY_LOCK = threading.Lock()
_MEMORY_STATES: dict[str, dict[str, Any]] = {}


def budget_limits_from_env() -> tuple[int, float]:
    return (
        _positive_int(os.getenv("LOLLA_MAX_PROVIDER_CALLS"), DEFAULT_MAX_PROVIDER_CALLS),
        _positive_float(
            os.getenv("LOLLA_MAX_PROVIDER_COST_USD"), DEFAULT_MAX_PROVIDER_COST_USD
        ),
    )


def budget_path_for_run(run_id: str) -> Path | None:
    explicit = str(os.getenv("LOLLA_PROVIDER_BUDGET_STATE", "")).strip()
    if explicit:
        return Path(explicit).expanduser()
    safe = str(run_id or "").strip()
    if not safe:
        return None
    return Path("/tmp") / f"lolla_{safe}_provider_budget.json"


def reserve_provider_call(
    *,
    run_id: str,
    stage: str,
    requested_model: str,
    maximum_call_cost_usd: float,
    maximum_calls: int,
    maximum_run_cost_usd: float,
) -> tuple[str, dict[str, Any]]:
    reservation_id = uuid.uuid4().hex

    def mutate(state: dict[str, Any]) -> None:
        limits = state["limits"]
        if limits != {
            "maximum_provider_calls": maximum_calls,
            "maximum_accounted_cost_usd": maximum_run_cost_usd,
        }:
            raise ProviderBudgetExceeded("provider budget limits changed during the run")
        attempted = int(state.get("attempted_provider_calls", 0) or 0)
        if attempted >= maximum_calls:
            raise ProviderBudgetExceeded("provider call ceiling exhausted before request")
        accounted = float(state.get("accounted_cost_usd", 0.0) or 0.0)
        active = sum(
            float(item.get("maximum_call_cost_usd", 0.0) or 0.0)
            for item in state.get("reservations", [])
            if item.get("status") == "reserved"
        )
        if accounted + active + maximum_call_cost_usd > maximum_run_cost_usd + 1e-12:
            raise ProviderBudgetExceeded("provider USD ceiling exhausted before request")
        state["attempted_provider_calls"] = attempted + 1
        state.setdefault("reservations", []).append(
            {
                "reservation_id": reservation_id,
                "stage": stage or "unlabeled",
                "requested_model": requested_model,
                "status": "reserved",
                "maximum_call_cost_usd": round(maximum_call_cost_usd, 9),
                "reserved_at": _utc_now(),
            }
        )

    snapshot = _mutate_state(
        run_id=run_id,
        maximum_calls=maximum_calls,
        maximum_run_cost_usd=maximum_run_cost_usd,
        mutate=mutate,
    )
    return reservation_id, snapshot


def finalize_provider_call(
    *,
    run_id: str,
    reservation_id: str,
    status: str,
    response_id: str,
    exact_cost_usd: float | None,
    estimated_cost_usd: float | None,
    maximum_calls: int,
    maximum_run_cost_usd: float,
) -> dict[str, Any]:
    def mutate(state: dict[str, Any]) -> None:
        match = next(
            (
                item
                for item in state.get("reservations", [])
                if item.get("reservation_id") == reservation_id
            ),
            None,
        )
        if match is None:
            raise ProviderBudgetExceeded("provider reservation is missing")
        if match.get("status") != "reserved":
            raise ProviderBudgetExceeded("provider reservation was already finalized")
        if exact_cost_usd is not None:
            accounted = max(0.0, float(exact_cost_usd))
            accounting_basis = "provider_reported_exact"
        elif estimated_cost_usd is not None and str(status).startswith("ok"):
            accounted = max(0.0, float(estimated_cost_usd))
            accounting_basis = "local_token_estimate"
        else:
            accounted = float(match.get("maximum_call_cost_usd", 0.0) or 0.0)
            accounting_basis = "reserved_worst_case_unknown_charge"
        match.update(
            {
                "status": "finalized",
                "provider_status": status,
                "response_id": response_id,
                "exact_cost_usd": exact_cost_usd,
                "estimated_cost_usd": estimated_cost_usd,
                "accounted_cost_usd": round(accounted, 9),
                "accounting_basis": accounting_basis,
                "finalized_at": _utc_now(),
            }
        )
        state["accounted_cost_usd"] = round(
            sum(
                float(item.get("accounted_cost_usd", 0.0) or 0.0)
                for item in state.get("reservations", [])
                if item.get("status") == "finalized"
            ),
            9,
        )
        state["provider_reported_cost_usd"] = round(
            sum(
                float(item.get("exact_cost_usd", 0.0) or 0.0)
                for item in state.get("reservations", [])
                if item.get("exact_cost_usd") is not None
            ),
            9,
        )
        state["exact_cost_call_count"] = sum(
            1
            for item in state.get("reservations", [])
            if item.get("exact_cost_usd") is not None
        )

    return _mutate_state(
        run_id=run_id,
        maximum_calls=maximum_calls,
        maximum_run_cost_usd=maximum_run_cost_usd,
        mutate=mutate,
    )


def _mutate_state(
    *,
    run_id: str,
    maximum_calls: int,
    maximum_run_cost_usd: float,
    mutate,
) -> dict[str, Any]:
    path = budget_path_for_run(run_id)
    if path is None:
        key = run_id or "__process_without_run_id__"
        with _MEMORY_LOCK:
            state = _MEMORY_STATES.setdefault(
                key, _empty_state(run_id, maximum_calls, maximum_run_cost_usd)
            )
            mutate(state)
            return json.loads(json.dumps(state))

    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(path.suffix + ".lock")
    with lock_path.open("a+", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            state = _read_state(path) or _empty_state(
                run_id, maximum_calls, maximum_run_cost_usd
            )
            mutate(state)
            temp = path.with_suffix(path.suffix + ".tmp")
            temp.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
            os.replace(temp, path)
            return json.loads(json.dumps(state))
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def _empty_state(run_id: str, maximum_calls: int, maximum_cost: float) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "limits": {
            "maximum_provider_calls": maximum_calls,
            "maximum_accounted_cost_usd": maximum_cost,
        },
        "attempted_provider_calls": 0,
        "accounted_cost_usd": 0.0,
        "provider_reported_cost_usd": 0.0,
        "exact_cost_call_count": 0,
        "reservations": [],
    }


def _read_state(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _positive_int(value: str | None, default: int) -> int:
    try:
        parsed = int(str(value or ""))
    except ValueError:
        parsed = default
    return parsed if parsed > 0 else default


def _positive_float(value: str | None, default: float) -> float:
    try:
        parsed = float(str(value or ""))
    except ValueError:
        parsed = default
    return parsed if parsed > 0 else default


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
