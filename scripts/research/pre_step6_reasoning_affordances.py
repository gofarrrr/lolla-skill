#!/usr/bin/env python3
"""Research-only validation and baseline conversion for reasoning affordances."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence


REASONING_AFFORDANCE_SCHEMA_VERSION = "reasoning_affordance.v1"
ALLOWED_STATUS = frozenset({"research_only"})
ALLOWED_RUNTIME_POLICY = frozenset({"runtime_dormant"})
ALLOWED_AFFORDANCE_CLASSES = frozenset(
    {
        "direct_pressure",
        "structural_lens",
        "contrarian_edge",
        "weak_signal",
        "negative_space",
        "duplicate_support",
        "false_friend",
        "parked_receipt",
    }
)
ALLOWED_PROTECTED_SLOTS = frozenset(
    {
        "inversion",
        "denominator",
        "incentive",
        "disconfirmation",
        "opportunity_cost",
        "lollapalooza",
        "model_forcing_risk",
        "sequence_stop_rule",
        "negative_space",
        "none",
    }
)
ALLOWED_ATTENTION_WEIGHTS = frozenset({"active", "brief", "scan", "parked"})
TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "artifact_id",
        "source_refs",
        "selection_basis",
        "affordance_class",
        "protected_slot",
        "what_it_might_reveal",
        "source_grounding",
        "cheap_test_for_step6",
        "hard_boundary",
        "relaxation_condition",
        "discard_condition",
        "risk_if_forced",
        "risk_if_ignored",
        "attention_weight",
        "expansion_ref",
    }
)
REQUIRED_FIELDS = tuple(TOP_LEVEL_FIELDS)
FORBIDDEN_LANGUAGE = (
    "best option",
    "correct answer",
    "final recommendation",
    "step 6 should conclude",
    "use this because it is correct",
    "drop this because it is not relevant",
    "add nuance",
    "improve clarity",
)


class ReasoningAffordanceValidationError(ValueError):
    pass


def load_reasoning_affordance_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ReasoningAffordanceValidationError(f"{path}: payload must be an object")
    return payload


def validate_reasoning_affordance_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_reasoning_affordance_errors(payload, path=Path(path)))
    if errors:
        raise ReasoningAffordanceValidationError("; ".join(errors))


def validate_reasoning_affordance_file(path: Path) -> None:
    validate_reasoning_affordance_payload(
        load_reasoning_affordance_payload(path),
        path=Path(path),
    )


def affordance_from_raw_artifact(
    artifact: dict[str, object],
    *,
    case_id: str,
    source_ref: str,
    protected_slot: str = "none",
) -> dict[str, object]:
    priority = _string(artifact.get("priority_hint"))
    attention_weight = "active" if priority in {"high", "medium"} else "scan"
    affordance_class = "direct_pressure" if attention_weight == "active" else "weak_signal"
    return {
        "schema_version": REASONING_AFFORDANCE_SCHEMA_VERSION,
        "status": "research_only",
        "runtime_policy": "runtime_dormant",
        "case_id": case_id,
        "artifact_id": _string(artifact.get("artifact_id")),
        "source_refs": [source_ref],
        "selection_basis": _first_text(
            artifact.get("why_provided"),
            artifact.get("priority_hint"),
            default="Raw artifact handoff preserved this candidate.",
        ),
        "affordance_class": affordance_class,
        "protected_slot": protected_slot,
        "what_it_might_reveal": _first_text(
            artifact.get("contribution"),
            artifact.get("source_grounding"),
            default="This artifact may preserve pressure Step 6 could lose.",
        ),
        "source_grounding": _first_text(
            artifact.get("source_grounding"),
            default="Grounding is available in the source artifact.",
        ),
        "cheap_test_for_step6": _first_text(
            artifact.get("discard_condition"),
            artifact.get("hard_boundary"),
            default="Check whether the answer depends on this pressure.",
        ),
        "hard_boundary": _first_text(
            artifact.get("hard_boundary"),
            default="Do not force this pressure beyond the source grounding.",
        ),
        "relaxation_condition": _first_text(
            artifact.get("relaxation_condition"),
            default="Relax if the source condition no longer applies.",
        ),
        "discard_condition": _first_text(
            artifact.get("discard_condition"),
            default="Discard if the answer no longer touches this pressure.",
        ),
        "risk_if_forced": _first_text(
            artifact.get("risk_if_forced"),
            default="The answer may overweight this pressure.",
        ),
        "risk_if_ignored": _first_text(
            artifact.get("risk_if_ignored"),
            default="The answer may lose a relevant pressure.",
        ),
        "attention_weight": attention_weight,
        "expansion_ref": source_ref,
    }


def parked_affordance_from_candidate(
    candidate: dict[str, object],
    *,
    case_id: str,
    protected_slot: str,
    discard_condition: str,
) -> dict[str, object]:
    source_refs = candidate.get("source_refs")
    if not isinstance(source_refs, list):
        source_refs = []
    expansion_ref = _string(candidate.get("expansion_ref"))
    return {
        "schema_version": REASONING_AFFORDANCE_SCHEMA_VERSION,
        "status": "research_only",
        "runtime_policy": "runtime_dormant",
        "case_id": case_id,
        "artifact_id": _string(candidate.get("candidate_id")),
        "source_refs": source_refs,
        "selection_basis": _first_text(
            candidate.get("selection_basis"),
            default="Candidate preserved by the inventory.",
        ),
        "affordance_class": "parked_receipt",
        "protected_slot": protected_slot,
        "what_it_might_reveal": _first_text(
            candidate.get("summary"),
            default="Parked material may become useful if the problem reactivates it.",
        ),
        "source_grounding": _first_text(
            candidate.get("summary"),
            default="Grounding is available through the expansion ref.",
        ),
        "cheap_test_for_step6": "Scan only if the answer touches the protected slot.",
        "hard_boundary": "Do not promote this parked receipt without source-grounded need.",
        "relaxation_condition": "Promote only if the active answer loses this protected pressure.",
        "discard_condition": discard_condition,
        "risk_if_forced": "The answer may become cluttered or overfit to a side issue.",
        "risk_if_ignored": "Step 6 may miss a protected edge pressure.",
        "attention_weight": "parked",
        "expansion_ref": expansion_ref,
    }


def iter_reasoning_affordance_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be an object"
        return

    yield from _unknown_fields(payload, TOP_LEVEL_FIELDS, path)
    yield from _missing_fields(payload, REQUIRED_FIELDS, path)
    if any(field not in payload for field in REQUIRED_FIELDS):
        return

    if _string(payload.get("schema_version")) != REASONING_AFFORDANCE_SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {REASONING_AFFORDANCE_SCHEMA_VERSION}"
    if _string(payload.get("status")) not in ALLOWED_STATUS:
        yield f"{path / 'status'}: status must be research_only"
    if _string(payload.get("runtime_policy")) not in ALLOWED_RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: runtime_policy must be runtime_dormant"
    if not _string(payload.get("case_id")).strip():
        yield f"{path / 'case_id'}: case_id must be non-empty"
    if not _string(payload.get("artifact_id")).strip():
        yield f"{path / 'artifact_id'}: artifact_id must be non-empty"
    if not _non_empty_string_list(payload.get("source_refs")):
        yield f"{path / 'source_refs'}: source_refs must be a non-empty string list"
    if _string(payload.get("affordance_class")) not in ALLOWED_AFFORDANCE_CLASSES:
        yield f"{path / 'affordance_class'}: unknown affordance_class"
    if _string(payload.get("protected_slot")) not in ALLOWED_PROTECTED_SLOTS:
        yield f"{path / 'protected_slot'}: unknown protected_slot"
    if _string(payload.get("attention_weight")) not in ALLOWED_ATTENTION_WEIGHTS:
        yield f"{path / 'attention_weight'}: unknown attention_weight"

    for field in (
        "selection_basis",
        "what_it_might_reveal",
        "source_grounding",
        "cheap_test_for_step6",
        "hard_boundary",
        "relaxation_condition",
        "discard_condition",
        "risk_if_forced",
        "risk_if_ignored",
        "expansion_ref",
    ):
        if not _string(payload.get(field)).strip():
            yield f"{path / field}: must be non-empty"
        elif _contains_forbidden_language(_string(payload.get(field))):
            yield f"{path / field}: forbidden language"


def _unknown_fields(
    payload: dict[str, object],
    allowed: frozenset[str],
    path: Path,
) -> Iterable[str]:
    for field in sorted(set(payload) - allowed):
        yield f"{path / field}: unknown field"


def _missing_fields(
    payload: dict[str, object],
    required: Sequence[str],
    path: Path,
) -> Iterable[str]:
    for field in required:
        if field not in payload:
            yield f"{path / field}: missing required field"


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def _non_empty_string_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and item.strip() for item in value
    )


def _contains_forbidden_language(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in FORBIDDEN_LANGUAGE)


def _first_text(*values: object, default: str) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return default


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args(argv)
    for path in args.paths:
        validate_reasoning_affordance_file(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
