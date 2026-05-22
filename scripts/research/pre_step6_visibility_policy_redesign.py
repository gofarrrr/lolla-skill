#!/usr/bin/env python3
"""Research-only visibility-policy redesign after false-standdown probe.

This artifact tests a ledger-mediated runtime visibility rule. Step 6's private
ledger supplies the cognitive signal; deterministic code only validates cache,
ledger, payload preservation, and custody.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence


SCHEMA_VERSION = "pre_step6_visibility_policy_redesign.v1"
STATUS = "research_only"
RUNTIME_POLICY = "runtime_dormant"
EXPERIMENT_ID = "design_preamble_visibility_policy_redesign_v0"
DEFAULT_OUT_DIR = Path("research/pre-step6-visibility-policy-redesign")
ALLOWED_CACHE_STATES = frozenset({"cache_hit", "cache_miss"})
ALLOWED_LEDGER_SIGNALS = frozenset(
    {"additive_pressure_present", "all_private_or_confirming", "missing_or_unclear"}
)
ALLOWED_PAYLOAD_RESULTS = frozenset({"preserved", "introduced_omission", "case_n_a"})
ALLOWED_BRIDGE_LABELS = frozenset(
    {"false_standdown", "true_standdown", "ambiguous_standdown", "not_observed"}
)
ALLOWED_RESULTS = frozenset(
    {
        "deck_visible_from_step6_additive_pressure",
        "anchor_visible_deck_private",
        "anchor_visible_payload_omission_guardrail",
        "anchor_visible_unclear_ledger_guardrail",
        "current_step6_visible_no_deck",
    }
)
DETERMINISTIC_ROLE = (
    "validate_cache_state",
    "validate_step6_ledger_schema",
    "validate_payload_preservation",
    "preserve_audit_custody",
)
TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "case_id",
        "inputs",
        "legacy_policy",
        "redesigned_policy",
        "deterministic_role",
        "bridge_probe_read",
        "gates",
        "notes",
    }
)
INPUT_FIELDS = frozenset(
    {"cache_state", "step6_ledger_signal", "payload_gate_result", "bridge_probe_label"}
)
LEGACY_POLICY_FIELDS = frozenset({"result", "would_suppress_deck", "why"})
REDESIGNED_POLICY_FIELDS = frozenset(
    {"result", "why", "cognitive_signal_source", "normal_runtime_reviewer_calls"}
)
BRIDGE_PROBE_FIELDS = frozenset({"case_was_false_standdown_probe", "design_pressure"})
GATE_FIELDS = frozenset({"runtime_wiring_allowed", "skill_update_allowed"})


class VisibilityPolicyRedesignValidationError(ValueError):
    pass


def build_visibility_policy_redesign(
    *,
    case_id: str,
    cache_state: str,
    step6_ledger_signal: str,
    payload_gate_result: str,
    bridge_probe_label: str,
) -> dict[str, object]:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "case_id": case_id,
        "inputs": {
            "cache_state": cache_state,
            "step6_ledger_signal": step6_ledger_signal,
            "payload_gate_result": payload_gate_result,
            "bridge_probe_label": bridge_probe_label,
        },
        "legacy_policy": _legacy_policy(bridge_probe_label=bridge_probe_label),
        "redesigned_policy": _redesigned_policy(
            cache_state=cache_state,
            step6_ledger_signal=step6_ledger_signal,
            payload_gate_result=payload_gate_result,
        ),
        "deterministic_role": list(DETERMINISTIC_ROLE),
        "bridge_probe_read": {
            "case_was_false_standdown_probe": bridge_probe_label == "false_standdown",
            "design_pressure": (
                "Do not use universal anchor fallback when Step 6 records additive pressure."
                if bridge_probe_label == "false_standdown"
                else "No bridge-probe false-standdown pressure recorded for this case."
            ),
        },
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": (
            "Research-only redesign. It does not add a runtime reviewer loop and "
            "does not wire product behavior."
        ),
    }
    validate_visibility_policy_redesign_payload(payload)
    return payload


def load_visibility_policy_redesign_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise VisibilityPolicyRedesignValidationError(f"{path}: payload must be an object")
    return payload


def validate_visibility_policy_redesign_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_visibility_policy_redesign_errors(payload, path=Path(path)))
    if errors:
        raise VisibilityPolicyRedesignValidationError("; ".join(errors))


def validate_visibility_policy_redesign_file(path: Path) -> None:
    validate_visibility_policy_redesign_payload(
        load_visibility_policy_redesign_payload(path),
        path=Path(path),
    )


def iter_visibility_policy_redesign_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be an object"
        return
    required = tuple(TOP_LEVEL_FIELDS - {"notes"})
    yield from _unknown_fields(payload, TOP_LEVEL_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return
    if payload.get("schema_version") != SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {SCHEMA_VERSION}"
    if payload.get("status") != STATUS:
        yield f"{path / 'status'}: must be {STATUS}"
    if payload.get("runtime_policy") != RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: must be {RUNTIME_POLICY}"
    if payload.get("experiment_id") != EXPERIMENT_ID:
        yield f"{path / 'experiment_id'}: must be {EXPERIMENT_ID}"
    if not _string(payload.get("case_id")).strip():
        yield f"{path / 'case_id'}: must be non-empty"
    inputs = _validate_inputs(payload.get("inputs"), path / "inputs")
    yield from inputs.errors
    if inputs.value is None:
        return
    yield from _validate_legacy_policy(
        payload.get("legacy_policy"),
        path / "legacy_policy",
        bridge_probe_label=inputs.value["bridge_probe_label"],
    )
    yield from _validate_redesigned_policy(
        payload.get("redesigned_policy"),
        path / "redesigned_policy",
        cache_state=inputs.value["cache_state"],
        step6_ledger_signal=inputs.value["step6_ledger_signal"],
        payload_gate_result=inputs.value["payload_gate_result"],
    )
    if payload.get("deterministic_role") != list(DETERMINISTIC_ROLE):
        yield f"{path / 'deterministic_role'}: invalid deterministic role"
    yield from _validate_bridge_probe_read(
        payload.get("bridge_probe_read"),
        path / "bridge_probe_read",
        bridge_probe_label=inputs.value["bridge_probe_label"],
    )
    yield from _validate_gates(payload.get("gates"), path / "gates")


def write_visibility_policy_redesign(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_visibility_policy_redesign_payload(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{_string(payload['case_id'])}.visibility-policy-redesign.v1.json"
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return out_path


def write_fixture_suite(*, out_dir: Path) -> list[Path]:
    paths: list[Path] = []
    for scenario in SCENARIOS:
        payload = build_visibility_policy_redesign(**scenario)
        paths.append(write_visibility_policy_redesign(payload=payload, out_dir=out_dir))
    return paths


def _legacy_policy(*, bridge_probe_label: str) -> dict[str, object]:
    return {
        "result": "anchor_visible_deck_private",
        "would_suppress_deck": bridge_probe_label == "false_standdown",
        "why": (
            "Legacy runtime unresolved policy defaults to anchor visible and deck private."
        ),
    }


def _redesigned_policy(
    *,
    cache_state: str,
    step6_ledger_signal: str,
    payload_gate_result: str,
) -> dict[str, object]:
    if cache_state == "cache_miss":
        return {
            "result": "current_step6_visible_no_deck",
            "why": "Cached card deck is unavailable; normal runtime does not generate cards live.",
            "cognitive_signal_source": "not_available_cache_miss",
            "normal_runtime_reviewer_calls": 0,
        }
    if payload_gate_result == "introduced_omission":
        return {
            "result": "anchor_visible_payload_omission_guardrail",
            "why": "Protected anchor payload was lost, so deck visibility is blocked.",
            "cognitive_signal_source": "step6_private_ledger_blocked_by_payload_gate",
            "normal_runtime_reviewer_calls": 0,
        }
    if step6_ledger_signal == "missing_or_unclear":
        return {
            "result": "anchor_visible_unclear_ledger_guardrail",
            "why": "Step 6 ledger is missing or unclear; deterministic code cannot infer cognition.",
            "cognitive_signal_source": "missing_or_unclear",
            "normal_runtime_reviewer_calls": 0,
        }
    if step6_ledger_signal == "additive_pressure_present":
        return {
            "result": "deck_visible_from_step6_additive_pressure",
            "why": "Step 6 recorded additive non-anchor pressure and protected payload is preserved.",
            "cognitive_signal_source": "step6_private_ledger",
            "normal_runtime_reviewer_calls": 0,
        }
    return {
        "result": "anchor_visible_deck_private",
        "why": "Step 6 did not record additive non-anchor pressure.",
        "cognitive_signal_source": "step6_private_ledger",
        "normal_runtime_reviewer_calls": 0,
    }


class _InputValidation:
    def __init__(self, value: dict[str, str] | None, errors: list[str]) -> None:
        self.value = value
        self.errors = errors


def _validate_inputs(value: object, path: Path) -> _InputValidation:
    errors: list[str] = []
    if not isinstance(value, dict):
        return _InputValidation(None, [f"{path}: must be an object"])
    errors.extend(_unknown_fields(value, INPUT_FIELDS, path))
    errors.extend(_missing_fields(value, INPUT_FIELDS, path))
    result = {
        "cache_state": _string(value.get("cache_state")),
        "step6_ledger_signal": _string(value.get("step6_ledger_signal")),
        "payload_gate_result": _string(value.get("payload_gate_result")),
        "bridge_probe_label": _string(value.get("bridge_probe_label")),
    }
    if result["cache_state"] not in ALLOWED_CACHE_STATES:
        errors.append(f"{path / 'cache_state'}: unsupported cache state")
    if result["step6_ledger_signal"] not in ALLOWED_LEDGER_SIGNALS:
        errors.append(f"{path / 'step6_ledger_signal'}: unsupported ledger signal")
    if result["payload_gate_result"] not in ALLOWED_PAYLOAD_RESULTS:
        errors.append(f"{path / 'payload_gate_result'}: unsupported payload result")
    if result["bridge_probe_label"] not in ALLOWED_BRIDGE_LABELS:
        errors.append(f"{path / 'bridge_probe_label'}: unsupported bridge label")
    return _InputValidation(None if errors else result, errors)


def _validate_legacy_policy(
    value: object,
    path: Path,
    *,
    bridge_probe_label: str,
) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, LEGACY_POLICY_FIELDS, path)
    yield from _missing_fields(value, LEGACY_POLICY_FIELDS, path)
    if value != _legacy_policy(bridge_probe_label=bridge_probe_label):
        yield f"{path}: must match legacy unresolved anchor fallback"


def _validate_redesigned_policy(
    value: object,
    path: Path,
    *,
    cache_state: str,
    step6_ledger_signal: str,
    payload_gate_result: str,
) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, REDESIGNED_POLICY_FIELDS, path)
    yield from _missing_fields(value, REDESIGNED_POLICY_FIELDS, path)
    expected = _redesigned_policy(
        cache_state=cache_state,
        step6_ledger_signal=step6_ledger_signal,
        payload_gate_result=payload_gate_result,
    )
    if value != expected:
        yield f"{path}: must match redesigned policy rule"
    if _string(value.get("result")) not in ALLOWED_RESULTS:
        yield f"{path / 'result'}: unsupported result"
    if value.get("normal_runtime_reviewer_calls") != 0:
        yield f"{path / 'normal_runtime_reviewer_calls'}: must be 0"


def _validate_bridge_probe_read(
    value: object,
    path: Path,
    *,
    bridge_probe_label: str,
) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, BRIDGE_PROBE_FIELDS, path)
    yield from _missing_fields(value, BRIDGE_PROBE_FIELDS, path)
    expected = bridge_probe_label == "false_standdown"
    if value.get("case_was_false_standdown_probe") is not expected:
        yield f"{path / 'case_was_false_standdown_probe'}: invalid bridge read"
    if not _string(value.get("design_pressure")).strip():
        yield f"{path / 'design_pressure'}: must be non-empty"


def _validate_gates(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, GATE_FIELDS, path)
    yield from _missing_fields(value, GATE_FIELDS, path)
    if value.get("runtime_wiring_allowed") is not False:
        yield f"{path / 'runtime_wiring_allowed'}: must be false"
    if value.get("skill_update_allowed") is not False:
        yield f"{path / 'skill_update_allowed'}: must be false"


def _unknown_fields(value: dict[str, object], allowed: frozenset[str], path: Path) -> Iterable[str]:
    for field in sorted(set(value) - allowed):
        yield f"{path / field}: unknown field"


def _missing_fields(value: dict[str, object], required: Iterable[str], path: Path) -> Iterable[str]:
    for field in sorted(set(required) - set(value)):
        yield f"{path / field}: missing required field"


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


SCENARIOS = [
    {
        "case_id": "bridge-high-clutter-sensitive-overlay",
        "cache_state": "cache_hit",
        "step6_ledger_signal": "additive_pressure_present",
        "payload_gate_result": "preserved",
        "bridge_probe_label": "false_standdown",
    },
    {
        "case_id": "bridge-sensitive-anchor-misses-tripwire",
        "cache_state": "cache_hit",
        "step6_ledger_signal": "additive_pressure_present",
        "payload_gate_result": "preserved",
        "bridge_probe_label": "false_standdown",
    },
    {
        "case_id": "bridge-sequencing-sensitive-boundary",
        "cache_state": "cache_hit",
        "step6_ledger_signal": "additive_pressure_present",
        "payload_gate_result": "preserved",
        "bridge_probe_label": "false_standdown",
    },
    {
        "case_id": "mother-address-year",
        "cache_state": "cache_hit",
        "step6_ledger_signal": "all_private_or_confirming",
        "payload_gate_result": "preserved",
        "bridge_probe_label": "not_observed",
    },
    {
        "case_id": "synthetic-cache-miss",
        "cache_state": "cache_miss",
        "step6_ledger_signal": "additive_pressure_present",
        "payload_gate_result": "preserved",
        "bridge_probe_label": "false_standdown",
    },
    {
        "case_id": "synthetic-missing-ledger",
        "cache_state": "cache_hit",
        "step6_ledger_signal": "missing_or_unclear",
        "payload_gate_result": "preserved",
        "bridge_probe_label": "not_observed",
    },
    {
        "case_id": "synthetic-payload-omission",
        "cache_state": "cache_hit",
        "step6_ledger_signal": "additive_pressure_present",
        "payload_gate_result": "introduced_omission",
        "bridge_probe_label": "false_standdown",
    },
]


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="Existing visibility-policy-redesign payloads to validate")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.paths:
        for path in args.paths:
            validate_visibility_policy_redesign_file(path)
        return 0
    if args.write:
        for path in write_fixture_suite(out_dir=args.out_dir):
            print(path)
        return 0
    print(
        json.dumps(
            build_visibility_policy_redesign(**SCENARIOS[0]),
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
