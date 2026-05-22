#!/usr/bin/env python3
"""Research-only visibility asymmetry policy.

This artifact names the runtime trade-off: broad private deck, anchor-biased
public output when unresolved, and no normal runtime reviewer loop.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence


SCHEMA_VERSION = "pre_step6_visibility_asymmetry.v1"
STATUS = "research_only"
RUNTIME_POLICY = "runtime_dormant"
EXPERIMENT_ID = "design_preamble_visibility_asymmetry_v0"
DEFAULT_OUT_DIR = Path("research/pre-step6-visibility-asymmetry-policies")
ALLOWED_MODES = frozenset({"runtime", "research", "experimental"})
ALLOWED_LEDGER_SIGNALS = frozenset(
    {"additive_pressure_present", "all_private_or_confirming", "unknown"}
)
ALLOWED_REVIEWER_SIGNALS = frozenset(
    {"deck_confirmed", "anchor_confirmed", "tie", "not_run", "unknown"}
)
ALLOWED_RESULTS = frozenset(
    {
        "anchor_visible_after_aligned_signals",
        "card_deck_visible_after_aligned_signals",
        "anchor_visible_deck_private",
        "retest_required",
    }
)
TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "case_id",
        "mode",
        "ledger_signal",
        "reviewer_signal",
        "runtime_asymmetry",
        "retest_policy",
        "visible_policy",
        "gates",
        "notes",
    }
)
ASYMMETRY_FIELDS = frozenset(
    {
        "private_default",
        "public_bias",
        "principle",
        "normal_runtime_comparison_loop",
    }
)
RETEST_FIELDS = frozenset(
    {
        "allowed",
        "max_retests",
        "normal_runtime_reviewer_calls",
        "second_reviewer_model_policy",
        "second_reviewer_prompt_policy",
        "deck_visible_threshold",
        "non_inferior_deck_result",
        "tie_after_retest_result",
    }
)
VISIBLE_POLICY_FIELDS = frozenset({"result", "why", "false_standdown_risk"})
GATE_FIELDS = frozenset({"runtime_wiring_allowed", "skill_update_allowed"})


class VisibilityAsymmetryValidationError(ValueError):
    pass


def build_visibility_asymmetry_policy(
    *,
    case_id: str,
    mode: str,
    ledger_signal: str,
    reviewer_signal: str,
) -> dict[str, object]:
    if mode not in ALLOWED_MODES:
        raise VisibilityAsymmetryValidationError(f"unsupported mode: {mode}")
    if ledger_signal not in ALLOWED_LEDGER_SIGNALS:
        raise VisibilityAsymmetryValidationError(f"unsupported ledger signal: {ledger_signal}")
    if reviewer_signal not in ALLOWED_REVIEWER_SIGNALS:
        raise VisibilityAsymmetryValidationError(f"unsupported reviewer signal: {reviewer_signal}")
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "case_id": case_id,
        "mode": mode,
        "ledger_signal": ledger_signal,
        "reviewer_signal": reviewer_signal,
        "runtime_asymmetry": {
            "private_default": "deck_private",
            "public_bias": "anchor_visible_when_unresolved",
            "principle": "broad_private_narrow_public",
            "normal_runtime_comparison_loop": False,
        },
        "retest_policy": _retest_policy(mode),
        "visible_policy": _visible_policy(
            mode=mode,
            ledger_signal=ledger_signal,
            reviewer_signal=reviewer_signal,
        ),
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": (
            "Research-only visibility-asymmetry policy. It names runtime anchor "
            "bias and bounded research retest behavior; it does not wire a live "
            "reviewer loop."
        ),
    }
    validate_visibility_asymmetry_payload(payload)
    return payload


def load_visibility_asymmetry_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise VisibilityAsymmetryValidationError(f"{path}: payload must be an object")
    return payload


def validate_visibility_asymmetry_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_visibility_asymmetry_errors(payload, path=Path(path)))
    if errors:
        raise VisibilityAsymmetryValidationError("; ".join(errors))


def validate_visibility_asymmetry_file(path: Path) -> None:
    validate_visibility_asymmetry_payload(load_visibility_asymmetry_payload(path), path=Path(path))


def iter_visibility_asymmetry_errors(
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
    if _string(payload.get("schema_version")) != SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {SCHEMA_VERSION}"
    if _string(payload.get("status")) != STATUS:
        yield f"{path / 'status'}: must be {STATUS}"
    if _string(payload.get("runtime_policy")) != RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: must be {RUNTIME_POLICY}"
    if _string(payload.get("experiment_id")) != EXPERIMENT_ID:
        yield f"{path / 'experiment_id'}: must be {EXPERIMENT_ID}"
    if not _string(payload.get("case_id")).strip():
        yield f"{path / 'case_id'}: must be non-empty"
    mode = _string(payload.get("mode"))
    ledger_signal = _string(payload.get("ledger_signal"))
    reviewer_signal = _string(payload.get("reviewer_signal"))
    if mode not in ALLOWED_MODES:
        yield f"{path / 'mode'}: unsupported mode"
    if ledger_signal not in ALLOWED_LEDGER_SIGNALS:
        yield f"{path / 'ledger_signal'}: unsupported ledger signal"
    if reviewer_signal not in ALLOWED_REVIEWER_SIGNALS:
        yield f"{path / 'reviewer_signal'}: unsupported reviewer signal"
    yield from _validate_runtime_asymmetry(
        payload.get("runtime_asymmetry"),
        path / "runtime_asymmetry",
    )
    yield from _validate_retest_policy(payload.get("retest_policy"), path / "retest_policy", mode=mode)
    yield from _validate_visible_policy(
        payload.get("visible_policy"),
        path / "visible_policy",
        mode=mode,
        ledger_signal=ledger_signal,
        reviewer_signal=reviewer_signal,
    )
    yield from _validate_gates(payload.get("gates"), path / "gates")


def write_visibility_asymmetry_policy(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_visibility_asymmetry_payload(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{_string(payload['case_id'])}.visibility-asymmetry.v1.json"
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return out_path


def _retest_policy(mode: str) -> dict[str, object]:
    allowed = mode in {"research", "experimental"}
    return {
        "allowed": allowed,
        "max_retests": 1 if allowed else 0,
        "normal_runtime_reviewer_calls": 0,
        "second_reviewer_model_policy": (
            "different_model_family_if_available" if allowed else "not_applicable"
        ),
        "second_reviewer_prompt_policy": "same_rubric_fresh_blind_shuffle" if allowed else "not_applicable",
        "deck_visible_threshold": "second_reviewer_prefers_deck" if allowed else "not_applicable",
        "non_inferior_deck_result": "keep_for_research_only" if allowed else "not_applicable",
        "tie_after_retest_result": "anchor_visible_deck_private" if allowed else "not_applicable",
    }


def _visible_policy(*, mode: str, ledger_signal: str, reviewer_signal: str) -> dict[str, str]:
    if mode == "runtime":
        return {
            "result": "anchor_visible_deck_private",
            "why": "Normal runtime has no reviewer loop; unresolved deck value stays private.",
            "false_standdown_risk": "primary_runtime_failure_mode",
        }
    if ledger_signal == "additive_pressure_present" and reviewer_signal == "deck_confirmed":
        return {
            "result": "card_deck_visible_after_aligned_signals",
            "why": "Step 6 found additive pressure and cognitive comparison preferred the deck.",
            "false_standdown_risk": "tracked_if_deck_later_suppressed",
        }
    if ledger_signal == "all_private_or_confirming" and reviewer_signal == "anchor_confirmed":
        return {
            "result": "anchor_visible_after_aligned_signals",
            "why": "Step 6 kept non-anchor cards private/confirming and cognitive comparison preferred the anchor.",
            "false_standdown_risk": "tracked_in_standdown_recall",
        }
    if reviewer_signal == "tie":
        return {
            "result": "retest_required",
            "why": "Tie requires one bounded research/experimental retest; runtime would default to anchor.",
            "false_standdown_risk": "tracked_if_retest_defaults_anchor",
        }
    return {
        "result": "retest_required",
        "why": "Ledger and cognitive comparison disagree; research mode may retest once.",
        "false_standdown_risk": "tracked_if_retest_defaults_anchor",
    }


def _validate_runtime_asymmetry(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, ASYMMETRY_FIELDS, path)
    yield from _missing_fields(value, ASYMMETRY_FIELDS, path)
    if value.get("private_default") != "deck_private":
        yield f"{path / 'private_default'}: must be deck_private"
    if value.get("public_bias") != "anchor_visible_when_unresolved":
        yield f"{path / 'public_bias'}: must be anchor_visible_when_unresolved"
    if value.get("principle") != "broad_private_narrow_public":
        yield f"{path / 'principle'}: must be broad_private_narrow_public"
    if value.get("normal_runtime_comparison_loop") is not False:
        yield f"{path / 'normal_runtime_comparison_loop'}: must be false"


def _validate_retest_policy(value: object, path: Path, *, mode: str) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, RETEST_FIELDS, path)
    yield from _missing_fields(value, RETEST_FIELDS, path)
    allowed = mode in {"research", "experimental"}
    if value.get("allowed") is not allowed:
        yield f"{path / 'allowed'}: invalid for mode"
    if value.get("max_retests") != (1 if allowed else 0):
        yield f"{path / 'max_retests'}: invalid for mode"
    if value.get("normal_runtime_reviewer_calls") != 0:
        yield f"{path / 'normal_runtime_reviewer_calls'}: must be 0"


def _validate_visible_policy(
    value: object,
    path: Path,
    *,
    mode: str,
    ledger_signal: str,
    reviewer_signal: str,
) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, VISIBLE_POLICY_FIELDS, path)
    yield from _missing_fields(value, VISIBLE_POLICY_FIELDS, path)
    expected = _visible_policy(
        mode=mode,
        ledger_signal=ledger_signal,
        reviewer_signal=reviewer_signal,
    )
    if value != expected:
        yield f"{path}: must match mode/ledger/reviewer policy"
    if _string(value.get("result")) not in ALLOWED_RESULTS:
        yield f"{path / 'result'}: unsupported result"


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


SCENARIOS = {
    "runtime-unresolved": {
        "mode": "runtime",
        "ledger_signal": "additive_pressure_present",
        "reviewer_signal": "not_run",
    },
    "deck-confirmed": {
        "mode": "research",
        "ledger_signal": "additive_pressure_present",
        "reviewer_signal": "deck_confirmed",
    },
    "anchor-confirmed": {
        "mode": "research",
        "ledger_signal": "all_private_or_confirming",
        "reviewer_signal": "anchor_confirmed",
    },
    "tie-retest": {
        "mode": "research",
        "ledger_signal": "additive_pressure_present",
        "reviewer_signal": "tie",
    },
    "ledger-reviewer-disagreement": {
        "mode": "research",
        "ledger_signal": "all_private_or_confirming",
        "reviewer_signal": "deck_confirmed",
    },
}


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="Existing visibility-asymmetry payloads to validate")
    parser.add_argument("--scenario", choices=sorted(SCENARIOS), default="runtime-unresolved")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.paths:
        for path in args.paths:
            validate_visibility_asymmetry_file(path)
        return 0
    scenario = SCENARIOS[args.scenario]
    payload = build_visibility_asymmetry_policy(
        case_id=args.scenario,
        mode=scenario["mode"],
        ledger_signal=scenario["ledger_signal"],
        reviewer_signal=scenario["reviewer_signal"],
    )
    if args.write:
        print(write_visibility_asymmetry_policy(payload=payload, out_dir=args.out_dir))
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
