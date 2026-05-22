#!/usr/bin/env python3
"""Research-only validation for pre-Step-6 pressure-card consumption.

This module validates pressure-card answer cores and pressure-vs-raw comparison
fixtures. It is deliberately outside the live pipeline. It does not launch
workers, select truth, change /lolla behavior, or promote product docs.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence

from pre_step6_raw_artifacts import (
    MAX_ANSWER_CORE_CHARS,
    RawArtifactValidationError,
    load_answer_comparison_payload,
    load_answer_core_payload,
    validate_answer_comparison_payload,
    validate_answer_core_payload,
    validate_public_answer_hygiene,
)
from pre_step6_workpacks import (
    load_json_payload,
    validate_pressure_card_payload,
)
from pre_step6_hybrid_handoffs import (
    load_handoff_payload,
    validate_hybrid_handoff_payload,
)


PRESSURE_ANSWER_CORE_SCHEMA_VERSION = "pre_step6_pressure_answer_core.v1"
PRESSURE_VS_RAW_COMPARISON_SCHEMA_VERSION = (
    "pre_step6_pressure_vs_raw_comparison.v1"
)
HYBRID_ANSWER_CORE_SCHEMA_VERSION = "pre_step6_hybrid_answer_core.v1"
HYBRID_VS_RAW_COMPARISON_SCHEMA_VERSION = "pre_step6_hybrid_vs_raw_comparison.v1"
RENDERED_HYBRID_ANSWER_CORE_SCHEMA_VERSION = (
    "pre_step6_rendered_hybrid_answer_core.v1"
)
ALLOWED_STATUS = frozenset({"research_only"})
ALLOWED_RUNTIME_POLICY = frozenset({"runtime_dormant"})
ALLOWED_PRESSURE_CRITERION_WINNERS = frozenset({"raw", "pressure", "tie"})
ALLOWED_PRESSURE_AGGREGATE_DECISIONS = frozenset(
    {"raw_wins", "pressure_wins", "tie_stop"}
)
ALLOWED_HYBRID_CRITERION_WINNERS = frozenset({"raw", "hybrid", "tie"})
ALLOWED_HYBRID_AGGREGATE_DECISIONS = frozenset(
    {"raw_wins", "hybrid_wins", "tie_stop"}
)
ALLOWED_RENDERED_HANDOFF_MODES = frozenset({"card_first", "no_extra_pressure"})
PRESSURE_ANSWER_CORE_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "source_pressure_card",
        "source_control_comparison",
        "answer_core",
        "expected_inclusions",
        "expected_exclusions",
        "comparison_to_control",
        "notes",
    }
)
COMPARISON_TO_CONTROL_FIELDS = frozenset(
    {"preserved_from_control", "changed_from_pressure_card", "kept_private_or_discarded"}
)
PRESSURE_VS_RAW_COMPARISON_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "raw_answer_core_ref",
        "pressure_answer_core_ref",
        "criteria",
        "tie_break_rule",
        "aggregate_decision",
        "notes",
    }
)
PRESSURE_CRITERION_FIELDS = frozenset(
    {
        "criterion_id",
        "question",
        "winner",
        "raw_evidence",
        "pressure_evidence",
        "rationale",
    }
)
HYBRID_ANSWER_CORE_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "answer_core",
        "used_pressure_card",
        "inspected_raw_for",
        "recovered_from_raw",
        "expected_inclusions",
        "expected_exclusions",
        "notes",
    }
)
HYBRID_VS_RAW_COMPARISON_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "raw_answer_core_ref",
        "pressure_answer_core_ref",
        "hybrid_answer_core_ref",
        "criteria",
        "tie_break_rule",
        "aggregate_decision",
        "notes",
    }
)
HYBRID_CRITERION_FIELDS = frozenset(
    {
        "criterion_id",
        "question",
        "winner",
        "raw_evidence",
        "pressure_evidence",
        "hybrid_evidence",
        "rationale",
    }
)
RENDERED_HYBRID_ANSWER_CORE_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "source_hybrid_handoff",
        "handoff_mode",
        "answer_core",
        "expected_inclusions",
        "expected_exclusions",
        "renderer_followed",
        "notes",
    }
)
CARD_FIRST_RENDERER_FOLLOWED_FIELDS = frozenset(
    {
        "card_used_first",
        "inspected_raw_only_for_named_nuance",
        "no_extra_sections_from_inspect_more",
    }
)
QUIET_RENDERER_FOLLOWED_FIELDS = frozenset(
    {
        "quiet_mode_respected",
        "no_card_pressure_added",
        "no_raw_inspection_used",
        "no_extra_sections_from_inspect_more",
    }
)


class PressureCardConsumptionValidationError(ValueError):
    pass


def load_pressure_consumption_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise PressureCardConsumptionValidationError(f"{path}: payload must be an object")
    return payload


def validate_pressure_answer_core_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> None:
    errors = list(
        iter_pressure_answer_core_errors(payload, path=Path(path), repo_root=repo_root)
    )
    if errors:
        raise PressureCardConsumptionValidationError("; ".join(errors))


def validate_pressure_answer_core_file(
    path: Path,
    *,
    repo_root: Path | None = None,
) -> None:
    validate_pressure_answer_core_payload(
        load_pressure_consumption_payload(path),
        path=Path(path),
        repo_root=repo_root,
    )


def validate_pressure_vs_raw_comparison_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> None:
    errors = list(
        iter_pressure_vs_raw_comparison_errors(
            payload,
            path=Path(path),
            repo_root=repo_root,
        )
    )
    if errors:
        raise PressureCardConsumptionValidationError("; ".join(errors))


def validate_pressure_vs_raw_comparison_file(
    path: Path,
    *,
    repo_root: Path | None = None,
) -> None:
    validate_pressure_vs_raw_comparison_payload(
        load_pressure_consumption_payload(path),
        path=Path(path),
        repo_root=repo_root,
    )


def validate_hybrid_answer_core_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_hybrid_answer_core_errors(payload, path=Path(path)))
    if errors:
        raise PressureCardConsumptionValidationError("; ".join(errors))


def validate_hybrid_answer_core_file(path: Path) -> None:
    validate_hybrid_answer_core_payload(
        load_pressure_consumption_payload(path),
        path=Path(path),
    )


def validate_hybrid_vs_raw_comparison_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> None:
    errors = list(
        iter_hybrid_vs_raw_comparison_errors(
            payload,
            path=Path(path),
            repo_root=repo_root,
        )
    )
    if errors:
        raise PressureCardConsumptionValidationError("; ".join(errors))


def validate_hybrid_vs_raw_comparison_file(
    path: Path,
    *,
    repo_root: Path | None = None,
) -> None:
    validate_hybrid_vs_raw_comparison_payload(
        load_pressure_consumption_payload(path),
        path=Path(path),
        repo_root=repo_root,
    )


def validate_rendered_hybrid_answer_core_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> None:
    errors = list(
        iter_rendered_hybrid_answer_core_errors(
            payload,
            path=Path(path),
            repo_root=repo_root,
        )
    )
    if errors:
        raise PressureCardConsumptionValidationError("; ".join(errors))


def validate_rendered_hybrid_answer_core_file(
    path: Path,
    *,
    repo_root: Path | None = None,
) -> None:
    validate_rendered_hybrid_answer_core_payload(
        load_pressure_consumption_payload(path),
        path=Path(path),
        repo_root=repo_root,
    )


def iter_pressure_answer_core_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> Iterable[str]:
    required = (
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "source_pressure_card",
        "source_control_comparison",
        "answer_core",
        "expected_inclusions",
        "expected_exclusions",
        "comparison_to_control",
    )
    yield from _unknown_fields(payload, PRESSURE_ANSWER_CORE_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    if _string(payload.get("schema_version")) != PRESSURE_ANSWER_CORE_SCHEMA_VERSION:
        yield f"{path}: schema_version must be {PRESSURE_ANSWER_CORE_SCHEMA_VERSION}"
    yield from _validate_common_policy(payload, path=path)

    case_id = _string(payload.get("case_id"))
    source_card = _string(payload.get("source_pressure_card"))
    if not source_card:
        yield f"{path / 'source_pressure_card'}: must be non-empty"
    elif repo_root is not None:
        card_path = repo_root / source_card
        if not card_path.exists():
            yield f"{path / 'source_pressure_card'}: source card does not exist"
        else:
            card_payload = load_json_payload(card_path)
            validate_pressure_card_payload(card_payload, path=card_path)
            if not card_path.name.startswith(case_id):
                yield f"{path / 'source_pressure_card'}: source card case_id mismatch"

    source_control = _string(payload.get("source_control_comparison"))
    if not source_control:
        yield f"{path / 'source_control_comparison'}: must be non-empty"
    elif repo_root is not None:
        control_path = repo_root / source_control
        if not control_path.exists():
            yield f"{path / 'source_control_comparison'}: source comparison does not exist"
        else:
            control_payload = load_answer_comparison_payload(control_path)
            validate_answer_comparison_payload(
                control_payload,
                path=control_path,
                repo_root=repo_root,
            )
            if _string(control_payload.get("case_id")) != case_id:
                yield f"{path / 'source_control_comparison'}: case_id mismatch"

    answer_core = _string(payload.get("answer_core"))
    if not answer_core.strip():
        yield f"{path / 'answer_core'}: answer_core must be non-empty"
    elif len(answer_core) > MAX_ANSWER_CORE_CHARS:
        yield (
            f"{path / 'answer_core'}: "
            f"answer_core must not exceed {MAX_ANSWER_CORE_CHARS} chars"
        )
    try:
        validate_public_answer_hygiene(answer_core)
    except RawArtifactValidationError as exc:
        yield f"{path / 'answer_core'}: {exc}"

    yield from _validate_string_list(
        payload.get("expected_inclusions"),
        path=path / "expected_inclusions",
        required_non_empty=True,
    )
    if isinstance(payload.get("expected_inclusions"), list):
        lower_answer = answer_core.lower()
        for index, expected in enumerate(payload["expected_inclusions"]):
            if isinstance(expected, str) and expected.lower() not in lower_answer:
                yield (
                    f"{path / 'expected_inclusions' / str(index)}: "
                    "expected inclusion missing from answer_core"
                )

    yield from _validate_string_list(
        payload.get("expected_exclusions"),
        path=path / "expected_exclusions",
        required_non_empty=False,
    )
    if isinstance(payload.get("expected_exclusions"), list):
        lower_answer = answer_core.lower()
        for index, forbidden in enumerate(payload["expected_exclusions"]):
            if isinstance(forbidden, str) and forbidden.lower() in lower_answer:
                yield (
                    f"{path / 'expected_exclusions' / str(index)}: "
                    "expected exclusion appears in answer_core"
                )

    yield from _validate_comparison_to_control(
        payload.get("comparison_to_control"),
        path=path / "comparison_to_control",
    )


def iter_pressure_vs_raw_comparison_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> Iterable[str]:
    required = (
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "raw_answer_core_ref",
        "pressure_answer_core_ref",
        "criteria",
        "tie_break_rule",
        "aggregate_decision",
    )
    yield from _unknown_fields(payload, PRESSURE_VS_RAW_COMPARISON_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    if _string(payload.get("schema_version")) != PRESSURE_VS_RAW_COMPARISON_SCHEMA_VERSION:
        yield f"{path}: schema_version must be {PRESSURE_VS_RAW_COMPARISON_SCHEMA_VERSION}"
    yield from _validate_common_policy(payload, path=path)
    case_id = _string(payload.get("case_id"))

    raw_ref = _string(payload.get("raw_answer_core_ref"))
    if not raw_ref:
        yield f"{path / 'raw_answer_core_ref'}: must be non-empty"
    elif repo_root is not None:
        raw_path = repo_root / raw_ref
        if not raw_path.exists():
            yield f"{path / 'raw_answer_core_ref'}: raw answer core does not exist"
        else:
            raw_payload = load_answer_core_payload(raw_path)
            validate_answer_core_payload(raw_payload, path=raw_path, repo_root=repo_root)
            if _string(raw_payload.get("case_id")) != case_id:
                yield f"{path / 'raw_answer_core_ref'}: case_id mismatch"

    pressure_ref = _string(payload.get("pressure_answer_core_ref"))
    if not pressure_ref:
        yield f"{path / 'pressure_answer_core_ref'}: must be non-empty"
    elif repo_root is not None:
        pressure_path = repo_root / pressure_ref
        if not pressure_path.exists():
            yield f"{path / 'pressure_answer_core_ref'}: pressure answer core does not exist"
        else:
            pressure_payload = load_pressure_consumption_payload(pressure_path)
            validate_pressure_answer_core_payload(
                pressure_payload,
                path=pressure_path,
                repo_root=repo_root,
            )
            if _string(pressure_payload.get("case_id")) != case_id:
                yield f"{path / 'pressure_answer_core_ref'}: case_id mismatch"

    if _string(payload.get("tie_break_rule")) != "pressure_tie_with_raw_stops":
        yield f"{path / 'tie_break_rule'}: must be pressure_tie_with_raw_stops"

    criteria = payload.get("criteria")
    if not isinstance(criteria, list):
        yield f"{path / 'criteria'}: criteria must be a list"
        criteria = []
    elif not criteria:
        yield f"{path / 'criteria'}: criteria must not be empty"
    elif len(criteria) > 8:
        yield f"{path / 'criteria'}: criteria must not exceed 8"
    for index, criterion in enumerate(criteria):
        item_path = path / f"criteria[{index}]"
        if not isinstance(criterion, dict):
            yield f"{item_path}: criterion must be an object"
            continue
        yield from _validate_criterion(criterion, path=item_path)

    decision = _string(payload.get("aggregate_decision"))
    if decision not in ALLOWED_PRESSURE_AGGREGATE_DECISIONS:
        yield f"{path / 'aggregate_decision'}: unknown aggregate_decision '{decision}'"
    else:
        expected = score_pressure_vs_raw_comparison(payload)["aggregate_decision"]
        if decision != expected:
            yield (
                f"{path / 'aggregate_decision'}: aggregate_decision must be "
                f"{expected} from criterion winners"
            )


def score_pressure_vs_raw_comparison(payload: dict[str, object]) -> dict[str, object]:
    criteria = payload.get("criteria")
    raw = pressure = tie = 0
    if isinstance(criteria, list):
        for criterion in criteria:
            if not isinstance(criterion, dict):
                continue
            winner = _string(criterion.get("winner"))
            if winner == "raw":
                raw += 1
            elif winner == "pressure":
                pressure += 1
            elif winner == "tie":
                tie += 1
    if pressure > raw:
        aggregate = "pressure_wins"
    elif raw > pressure:
        aggregate = "raw_wins"
    else:
        aggregate = "tie_stop"
    return {
        "raw": raw,
        "pressure": pressure,
        "tie": tie,
        "aggregate_decision": aggregate,
    }


def iter_hybrid_answer_core_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    required = (
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "answer_core",
        "used_pressure_card",
        "inspected_raw_for",
        "recovered_from_raw",
        "expected_inclusions",
        "expected_exclusions",
    )
    yield from _unknown_fields(payload, HYBRID_ANSWER_CORE_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    if _string(payload.get("schema_version")) != HYBRID_ANSWER_CORE_SCHEMA_VERSION:
        yield f"{path}: schema_version must be {HYBRID_ANSWER_CORE_SCHEMA_VERSION}"
    yield from _validate_common_policy(payload, path=path)
    if payload.get("used_pressure_card") is not True:
        yield f"{path / 'used_pressure_card'}: must be true"

    answer_core = _string(payload.get("answer_core"))
    if not answer_core.strip():
        yield f"{path / 'answer_core'}: answer_core must be non-empty"
    elif len(answer_core) > MAX_ANSWER_CORE_CHARS:
        yield (
            f"{path / 'answer_core'}: "
            f"answer_core must not exceed {MAX_ANSWER_CORE_CHARS} chars"
        )
    try:
        validate_public_answer_hygiene(answer_core)
    except RawArtifactValidationError as exc:
        yield f"{path / 'answer_core'}: {exc}"

    for field in ("inspected_raw_for", "recovered_from_raw"):
        yield from _validate_string_or_string_list(
            payload.get(field),
            path=path / field,
        )

    yield from _validate_string_list(
        payload.get("expected_inclusions"),
        path=path / "expected_inclusions",
        required_non_empty=True,
    )
    if isinstance(payload.get("expected_inclusions"), list):
        lower_answer = answer_core.lower()
        for index, expected in enumerate(payload["expected_inclusions"]):
            if isinstance(expected, str) and expected.lower() not in lower_answer:
                yield (
                    f"{path / 'expected_inclusions' / str(index)}: "
                    "expected inclusion missing from answer_core"
                )

    yield from _validate_string_list(
        payload.get("expected_exclusions"),
        path=path / "expected_exclusions",
        required_non_empty=False,
    )
    if isinstance(payload.get("expected_exclusions"), list):
        lower_answer = answer_core.lower()
        for index, forbidden in enumerate(payload["expected_exclusions"]):
            if isinstance(forbidden, str) and forbidden.lower() in lower_answer:
                yield (
                    f"{path / 'expected_exclusions' / str(index)}: "
                    "expected exclusion appears in answer_core"
                )


def iter_hybrid_vs_raw_comparison_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> Iterable[str]:
    required = (
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "raw_answer_core_ref",
        "pressure_answer_core_ref",
        "hybrid_answer_core_ref",
        "criteria",
        "tie_break_rule",
        "aggregate_decision",
    )
    yield from _unknown_fields(payload, HYBRID_VS_RAW_COMPARISON_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    if _string(payload.get("schema_version")) != HYBRID_VS_RAW_COMPARISON_SCHEMA_VERSION:
        yield f"{path}: schema_version must be {HYBRID_VS_RAW_COMPARISON_SCHEMA_VERSION}"
    yield from _validate_common_policy(payload, path=path)
    case_id = _string(payload.get("case_id"))

    raw_ref = _string(payload.get("raw_answer_core_ref"))
    if not raw_ref:
        yield f"{path / 'raw_answer_core_ref'}: must be non-empty"
    elif repo_root is not None:
        raw_path = repo_root / raw_ref
        if not raw_path.exists():
            yield f"{path / 'raw_answer_core_ref'}: raw answer core does not exist"
        else:
            raw_payload = load_answer_core_payload(raw_path)
            validate_answer_core_payload(raw_payload, path=raw_path, repo_root=repo_root)
            if _string(raw_payload.get("case_id")) != case_id:
                yield f"{path / 'raw_answer_core_ref'}: case_id mismatch"

    pressure_ref = _string(payload.get("pressure_answer_core_ref"))
    if not pressure_ref:
        yield f"{path / 'pressure_answer_core_ref'}: must be non-empty"
    elif repo_root is not None:
        pressure_path = repo_root / pressure_ref
        if not pressure_path.exists():
            yield f"{path / 'pressure_answer_core_ref'}: pressure answer core does not exist"
        else:
            pressure_payload = load_pressure_consumption_payload(pressure_path)
            validate_pressure_answer_core_payload(
                pressure_payload,
                path=pressure_path,
                repo_root=repo_root,
            )
            if _string(pressure_payload.get("case_id")) != case_id:
                yield f"{path / 'pressure_answer_core_ref'}: case_id mismatch"

    hybrid_ref = _string(payload.get("hybrid_answer_core_ref"))
    if not hybrid_ref:
        yield f"{path / 'hybrid_answer_core_ref'}: must be non-empty"
    elif repo_root is not None:
        hybrid_path = repo_root / hybrid_ref
        if not hybrid_path.exists():
            yield f"{path / 'hybrid_answer_core_ref'}: hybrid answer core does not exist"
        else:
            hybrid_payload = load_pressure_consumption_payload(hybrid_path)
            validate_hybrid_answer_core_payload(hybrid_payload, path=hybrid_path)
            if _string(hybrid_payload.get("case_id")) != case_id:
                yield f"{path / 'hybrid_answer_core_ref'}: case_id mismatch"

    if _string(payload.get("tie_break_rule")) != "hybrid_tie_with_raw_stops":
        yield f"{path / 'tie_break_rule'}: must be hybrid_tie_with_raw_stops"

    criteria = payload.get("criteria")
    if not isinstance(criteria, list):
        yield f"{path / 'criteria'}: criteria must be a list"
        criteria = []
    elif not criteria:
        yield f"{path / 'criteria'}: criteria must not be empty"
    elif len(criteria) > 8:
        yield f"{path / 'criteria'}: criteria must not exceed 8"
    for index, criterion in enumerate(criteria):
        item_path = path / f"criteria[{index}]"
        if not isinstance(criterion, dict):
            yield f"{item_path}: criterion must be an object"
            continue
        yield from _validate_hybrid_criterion(criterion, path=item_path)

    decision = _string(payload.get("aggregate_decision"))
    if decision not in ALLOWED_HYBRID_AGGREGATE_DECISIONS:
        yield f"{path / 'aggregate_decision'}: unknown aggregate_decision '{decision}'"
    else:
        expected = score_hybrid_vs_raw_comparison(payload)["aggregate_decision"]
        if decision != expected:
            yield (
                f"{path / 'aggregate_decision'}: aggregate_decision must be "
                f"{expected} from criterion winners"
            )


def score_hybrid_vs_raw_comparison(payload: dict[str, object]) -> dict[str, object]:
    criteria = payload.get("criteria")
    raw = hybrid = tie = 0
    if isinstance(criteria, list):
        for criterion in criteria:
            if not isinstance(criterion, dict):
                continue
            winner = _string(criterion.get("winner"))
            if winner == "raw":
                raw += 1
            elif winner == "hybrid":
                hybrid += 1
            elif winner == "tie":
                tie += 1
    if hybrid > raw:
        aggregate = "hybrid_wins"
    elif raw > hybrid:
        aggregate = "raw_wins"
    else:
        aggregate = "tie_stop"
    return {
        "raw": raw,
        "hybrid": hybrid,
        "tie": tie,
        "aggregate_decision": aggregate,
    }


def iter_rendered_hybrid_answer_core_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> Iterable[str]:
    required = (
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "source_hybrid_handoff",
        "handoff_mode",
        "answer_core",
        "expected_inclusions",
        "expected_exclusions",
        "renderer_followed",
    )
    yield from _unknown_fields(payload, RENDERED_HYBRID_ANSWER_CORE_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    if _string(payload.get("schema_version")) != RENDERED_HYBRID_ANSWER_CORE_SCHEMA_VERSION:
        yield f"{path}: schema_version must be {RENDERED_HYBRID_ANSWER_CORE_SCHEMA_VERSION}"
    yield from _validate_common_policy(payload, path=path)
    case_id = _string(payload.get("case_id"))
    handoff_mode = _string(payload.get("handoff_mode"))
    if handoff_mode not in ALLOWED_RENDERED_HANDOFF_MODES:
        yield f"{path / 'handoff_mode'}: unknown handoff_mode '{handoff_mode}'"

    source_handoff = _string(payload.get("source_hybrid_handoff"))
    if not source_handoff:
        yield f"{path / 'source_hybrid_handoff'}: must be non-empty"
    elif repo_root is not None:
        handoff_path = repo_root / source_handoff
        if not handoff_path.exists():
            yield f"{path / 'source_hybrid_handoff'}: source handoff does not exist"
        else:
            handoff_payload = load_handoff_payload(handoff_path)
            validate_hybrid_handoff_payload(
                handoff_payload,
                path=handoff_path,
                repo_root=repo_root,
            )
            if _string(handoff_payload.get("case_id")) != case_id:
                yield f"{path / 'source_hybrid_handoff'}: case_id mismatch"
            if _string(handoff_payload.get("handoff_mode")) != handoff_mode:
                yield f"{path / 'handoff_mode'}: source handoff mode mismatch"

    answer_core = _string(payload.get("answer_core"))
    if not answer_core.strip():
        yield f"{path / 'answer_core'}: answer_core must be non-empty"
    elif len(answer_core) > MAX_ANSWER_CORE_CHARS:
        yield (
            f"{path / 'answer_core'}: "
            f"answer_core must not exceed {MAX_ANSWER_CORE_CHARS} chars"
        )
    try:
        validate_public_answer_hygiene(answer_core)
    except RawArtifactValidationError as exc:
        yield f"{path / 'answer_core'}: {exc}"

    yield from _validate_string_list(
        payload.get("expected_inclusions"),
        path=path / "expected_inclusions",
        required_non_empty=True,
    )
    if isinstance(payload.get("expected_inclusions"), list):
        lower_answer = answer_core.lower()
        for index, expected in enumerate(payload["expected_inclusions"]):
            if isinstance(expected, str) and expected.lower() not in lower_answer:
                yield (
                    f"{path / 'expected_inclusions' / str(index)}: "
                    "expected inclusion missing from answer_core"
                )

    yield from _validate_string_list(
        payload.get("expected_exclusions"),
        path=path / "expected_exclusions",
        required_non_empty=False,
    )
    if isinstance(payload.get("expected_exclusions"), list):
        lower_answer = answer_core.lower()
        for index, forbidden in enumerate(payload["expected_exclusions"]):
            if isinstance(forbidden, str) and forbidden.lower() in lower_answer:
                yield (
                    f"{path / 'expected_exclusions' / str(index)}: "
                    "expected exclusion appears in answer_core"
                )

    yield from _validate_renderer_followed(
        payload.get("renderer_followed"),
        path=path / "renderer_followed",
        handoff_mode=handoff_mode,
    )


def _validate_common_policy(
    payload: dict[str, object],
    *,
    path: Path,
) -> Iterable[str]:
    if _string(payload.get("status")) not in ALLOWED_STATUS:
        yield f"{path / 'status'}: status must be research_only"
    if _string(payload.get("runtime_policy")) not in ALLOWED_RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: runtime_policy must be runtime_dormant"
    if not _string(payload.get("case_id")).strip():
        yield f"{path / 'case_id'}: case_id must be non-empty"


def _validate_comparison_to_control(
    comparison: object,
    *,
    path: Path,
) -> Iterable[str]:
    if not isinstance(comparison, dict):
        yield f"{path}: comparison_to_control must be an object"
        return
    yield from _unknown_fields(comparison, COMPARISON_TO_CONTROL_FIELDS, path)
    yield from _missing_fields(
        comparison,
        (
            "preserved_from_control",
            "changed_from_pressure_card",
            "kept_private_or_discarded",
        ),
        path,
    )
    for field in COMPARISON_TO_CONTROL_FIELDS:
        if field in comparison:
            yield from _validate_string_list(
                comparison.get(field),
                path=path / field,
                required_non_empty=True,
            )


def _validate_criterion(
    criterion: dict[str, object],
    *,
    path: Path,
) -> Iterable[str]:
    required = (
        "criterion_id",
        "question",
        "winner",
        "raw_evidence",
        "pressure_evidence",
        "rationale",
    )
    yield from _unknown_fields(criterion, PRESSURE_CRITERION_FIELDS, path)
    yield from _missing_fields(criterion, required, path)
    if any(field not in criterion for field in required):
        return
    if not _string(criterion.get("criterion_id")).strip():
        yield f"{path / 'criterion_id'}: criterion_id must be non-empty"
    winner = _string(criterion.get("winner"))
    if winner not in ALLOWED_PRESSURE_CRITERION_WINNERS:
        yield f"{path / 'winner'}: unknown winner '{winner}'"
    for field in ("question", "raw_evidence", "pressure_evidence", "rationale"):
        if not _string(criterion.get(field)).strip():
            yield f"{path / field}: {field} must be non-empty"


def _validate_hybrid_criterion(
    criterion: dict[str, object],
    *,
    path: Path,
) -> Iterable[str]:
    required = (
        "criterion_id",
        "question",
        "winner",
        "raw_evidence",
        "pressure_evidence",
        "hybrid_evidence",
        "rationale",
    )
    yield from _unknown_fields(criterion, HYBRID_CRITERION_FIELDS, path)
    yield from _missing_fields(criterion, required, path)
    if any(field not in criterion for field in required):
        return
    if not _string(criterion.get("criterion_id")).strip():
        yield f"{path / 'criterion_id'}: criterion_id must be non-empty"
    winner = _string(criterion.get("winner"))
    if winner not in ALLOWED_HYBRID_CRITERION_WINNERS:
        yield f"{path / 'winner'}: unknown winner '{winner}'"
    for field in (
        "question",
        "raw_evidence",
        "pressure_evidence",
        "hybrid_evidence",
        "rationale",
    ):
        if not _string(criterion.get(field)).strip():
            yield f"{path / field}: {field} must be non-empty"


def _validate_renderer_followed(
    value: object,
    *,
    path: Path,
    handoff_mode: str,
) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: renderer_followed must be an object"
        return
    if handoff_mode == "card_first":
        required = (
            "card_used_first",
            "inspected_raw_only_for_named_nuance",
            "no_extra_sections_from_inspect_more",
        )
        allowed = CARD_FIRST_RENDERER_FOLLOWED_FIELDS
    elif handoff_mode == "no_extra_pressure":
        required = (
            "quiet_mode_respected",
            "no_card_pressure_added",
            "no_raw_inspection_used",
            "no_extra_sections_from_inspect_more",
        )
        allowed = QUIET_RENDERER_FOLLOWED_FIELDS
    else:
        return
    yield from _unknown_fields(value, allowed, path)
    yield from _missing_fields(value, required, path)
    for field in required:
        if value.get(field) is not True:
            yield f"{path / field}: must be true"


def _missing_fields(
    payload: dict[str, object],
    required: Sequence[str],
    path: Path,
) -> Iterable[str]:
    for field in required:
        if field not in payload:
            yield f"{path}: missing required field '{field}'"


def _unknown_fields(
    payload: dict[str, object],
    allowed: frozenset[str],
    path: Path,
) -> Iterable[str]:
    for field in sorted(set(payload) - allowed):
        yield f"{path}: unknown field '{field}'"


def _validate_string_list(
    value: object,
    *,
    path: Path,
    required_non_empty: bool,
) -> Iterable[str]:
    if not isinstance(value, list):
        yield f"{path}: must be a list"
        return
    if required_non_empty and not value:
        yield f"{path}: must not be empty"
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            yield f"{path / str(index)}: item must be a non-empty string"


def _validate_string_or_string_list(value: object, *, path: Path) -> Iterable[str]:
    if isinstance(value, str):
        if not value.strip():
            yield f"{path}: must be non-empty"
        return
    yield from _validate_string_list(value, path=path, required_non_empty=True)


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate research-only pre-Step-6 pressure-card consumption fixtures."
    )
    parser.add_argument("path", type=Path)
    parser.add_argument("--answer-core", action="store_true")
    parser.add_argument("--comparison", action="store_true")
    parser.add_argument("--hybrid-answer-core", action="store_true")
    parser.add_argument("--hybrid-comparison", action="store_true")
    parser.add_argument("--rendered-hybrid-answer-core", action="store_true")
    parser.add_argument("--repo-root", type=Path)
    args = parser.parse_args(argv)

    if args.answer_core:
        validate_pressure_answer_core_file(args.path, repo_root=args.repo_root)
        print(f"valid pressure answer core: {args.path}")
        return 0

    if args.comparison:
        validate_pressure_vs_raw_comparison_file(args.path, repo_root=args.repo_root)
        score = score_pressure_vs_raw_comparison(
            load_pressure_consumption_payload(args.path)
        )
        print(
            f"valid pressure-vs-raw comparison: {args.path} "
            f"pressure={score['pressure']} raw={score['raw']} tie={score['tie']} "
            f"decision={score['aggregate_decision']}"
        )
        return 0

    if args.hybrid_answer_core:
        validate_hybrid_answer_core_file(args.path)
        print(f"valid hybrid answer core: {args.path}")
        return 0

    if args.hybrid_comparison:
        validate_hybrid_vs_raw_comparison_file(args.path, repo_root=args.repo_root)
        score = score_hybrid_vs_raw_comparison(
            load_pressure_consumption_payload(args.path)
        )
        print(
            f"valid hybrid-vs-raw comparison: {args.path} "
            f"hybrid={score['hybrid']} raw={score['raw']} tie={score['tie']} "
            f"decision={score['aggregate_decision']}"
        )
        return 0

    if args.rendered_hybrid_answer_core:
        validate_rendered_hybrid_answer_core_file(args.path, repo_root=args.repo_root)
        print(f"valid rendered hybrid answer core: {args.path}")
        return 0

    parser.error(
        "choose --answer-core, --comparison, --hybrid-answer-core, "
        "--hybrid-comparison, or --rendered-hybrid-answer-core"
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
