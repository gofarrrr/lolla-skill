from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable


ALLOWED_STATUS = frozenset({"draft_review_only"})
ALLOWED_RUNTIME_POLICY = frozenset({"runtime_dormant"})
ALLOWED_COVERAGE_STATUS = frozenset(
    {
        "fully_source_backed",
        "partially_source_backed",
        "coverage_transparency",
        "no_substrate_backed_pressure",
    }
)
ALLOWED_PROVENANCE = frozenset(
    {"source_backed", "case_grounded", "llm_synthesized", "user_to_verify"}
)
ALLOWED_USER_FACING_READINESS = frozenset(
    {"not_ready", "maybe_later", "candidate_after_review"}
)
ALLOWED_V4_CONTRIBUTION = frozenset({"none", "minor", "material"})
ALLOWED_SUPPRESSED_DISPOSITION = frozenset(
    {"merged_support", "observatory_only", "still_suppressed", "needs_generation_test"}
)

TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "trace_id",
        "status",
        "runtime_policy",
        "source_artifacts",
        "selected_pressures",
        "coverage_transparency_panels",
        "suppressed_candidates",
        "review_notes",
    }
)
SELECTED_PRESSURE_FIELDS = frozenset(
    {
        "pressure_id",
        "case_id",
        "route_ids",
        "pressure",
        "what_to_verify",
        "why_it_matters",
        "dismiss_if",
        "tripwire_or_next_action",
        "coverage_status",
        "provenance_by_field",
        "source_affordances",
        "v4_contribution",
        "suppressed_nearby_candidate_ids",
        "operator_note",
        "user_facing_readiness",
    }
)
REQUIRED_PROVENANCE_FIELDS = (
    "pressure",
    "what_to_verify",
    "why_it_matters",
    "dismiss_if",
    "tripwire_or_next_action",
    "coverage_status",
)
COVERAGE_PANEL_FIELDS = frozenset(
    {
        "panel_id",
        "case_id",
        "route_id",
        "coverage_status",
        "missing_model_ids",
        "operator_trace_copy",
        "do_not_smooth_over_with",
        "why_it_matters",
    }
)
SUPPRESSED_CANDIDATE_FIELDS = frozenset(
    {
        "candidate_id",
        "case_id",
        "route_id",
        "candidate_summary",
        "suppression_reason",
        "v4_made_stronger",
        "disposition",
        "related_selected_pressure_id",
    }
)
REVIEW_NOTE_FIELDS = frozenset(
    {
        "decision_label",
        "runtime_dormancy_note",
        "principal_agent_medium_confidence_caution",
        "blocked_surfaces",
        "open_questions",
    }
)
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
AFFORDANCE_ID_RE = re.compile(
    r"^[a-z0-9]+(?:-[a-z0-9]+)*(?:\.[a-z0-9]+(?:-[a-z0-9]+)*)+$"
)


class DecisionPressureTraceValidationError(ValueError):
    pass


def load_decision_pressure_trace_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise DecisionPressureTraceValidationError(f"{path}: payload must be an object")
    return payload


def validate_decision_pressure_trace_file(
    path: Path,
    *,
    compiled_affordances_path: Path | None = None,
) -> None:
    validate_decision_pressure_trace_payload(
        load_decision_pressure_trace_payload(path),
        path=Path(path),
        compiled_affordances_path=compiled_affordances_path,
    )


def validate_decision_pressure_trace_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    compiled_affordances_path: Path | None = None,
) -> None:
    known_affordance_ids = (
        _load_known_affordance_ids(compiled_affordances_path)
        if compiled_affordances_path is not None
        else None
    )
    errors = list(
        iter_decision_pressure_trace_errors(
            payload,
            path=Path(path),
            known_affordance_ids=known_affordance_ids,
        )
    )
    if errors:
        raise DecisionPressureTraceValidationError("; ".join(errors))


def iter_decision_pressure_trace_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    known_affordance_ids: set[str] | None = None,
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be an object"
        return

    required = (
        "schema_version",
        "trace_id",
        "status",
        "runtime_policy",
        "source_artifacts",
        "selected_pressures",
        "coverage_transparency_panels",
        "suppressed_candidates",
        "review_notes",
    )
    yield from _unknown_fields(payload, TOP_LEVEL_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    if _string(payload.get("schema_version")) != "decision_pressure_trace.v1":
        yield f"{path}: schema_version must be decision_pressure_trace.v1"
    trace_id = _string(payload.get("trace_id"))
    if not SLUG_RE.match(trace_id):
        yield f"{path}: trace_id must be a lowercase slug"
    status = _string(payload.get("status"))
    if status not in ALLOWED_STATUS:
        yield f"{path}: status must be draft_review_only"
    runtime_policy = _string(payload.get("runtime_policy"))
    if runtime_policy not in ALLOWED_RUNTIME_POLICY:
        yield f"{path}: runtime_policy must be runtime_dormant"

    yield from _validate_string_list(
        payload.get("source_artifacts"),
        path=path / "source_artifacts",
        required_non_empty=True,
    )
    yield from _validate_review_notes(payload.get("review_notes"), path=path / "review_notes")

    selected_pressures = payload.get("selected_pressures")
    if not isinstance(selected_pressures, list):
        yield f"{path / 'selected_pressures'}: selected_pressures must be a list"
        selected_pressures = []
    elif len(selected_pressures) > 3:
        yield f"{path / 'selected_pressures'}: selected_pressures must not exceed 3"
    elif not selected_pressures:
        yield f"{path / 'selected_pressures'}: selected_pressures must not be empty"

    pressure_ids: set[str] = set()
    for index, pressure in enumerate(selected_pressures):
        item_path = path / f"selected_pressures[{index}]"
        if not isinstance(pressure, dict):
            yield f"{item_path}: selected pressure must be an object"
            continue
        pressure_id = _string(pressure.get("pressure_id"))
        if pressure_id in pressure_ids:
            yield f"{item_path}: duplicate pressure_id '{pressure_id}'"
        pressure_ids.add(pressure_id)
        yield from _validate_selected_pressure(
            pressure,
            path=item_path,
            review_notes=payload.get("review_notes"),
            known_affordance_ids=known_affordance_ids,
        )

    coverage_panels = payload.get("coverage_transparency_panels")
    if not isinstance(coverage_panels, list):
        yield (
            f"{path / 'coverage_transparency_panels'}: "
            "coverage_transparency_panels must be a list"
        )
        coverage_panels = []
    for index, panel in enumerate(coverage_panels):
        item_path = path / f"coverage_transparency_panels[{index}]"
        if not isinstance(panel, dict):
            yield f"{item_path}: coverage transparency panel must be an object"
            continue
        yield from _validate_coverage_panel(panel, path=item_path)

    suppressed_candidates = payload.get("suppressed_candidates")
    if not isinstance(suppressed_candidates, list):
        yield f"{path / 'suppressed_candidates'}: suppressed_candidates must be a list"
        suppressed_candidates = []
    for index, candidate in enumerate(suppressed_candidates):
        item_path = path / f"suppressed_candidates[{index}]"
        if not isinstance(candidate, dict):
            yield f"{item_path}: suppressed candidate must be an object"
            continue
        yield from _validate_suppressed_candidate(
            candidate,
            path=item_path,
            selected_pressure_ids=pressure_ids,
        )


def _validate_selected_pressure(
    pressure: dict[str, object],
    *,
    path: Path,
    review_notes: object,
    known_affordance_ids: set[str] | None,
) -> Iterable[str]:
    required = (
        "pressure_id",
        "case_id",
        "route_ids",
        "pressure",
        "what_to_verify",
        "why_it_matters",
        "dismiss_if",
        "tripwire_or_next_action",
        "coverage_status",
        "provenance_by_field",
        "source_affordances",
        "v4_contribution",
        "suppressed_nearby_candidate_ids",
        "operator_note",
        "user_facing_readiness",
    )
    yield from _unknown_fields(pressure, SELECTED_PRESSURE_FIELDS, path)
    yield from _missing_fields(pressure, required, path)
    if any(field not in pressure for field in required):
        return

    for field in ("pressure_id", "case_id"):
        value = _string(pressure.get(field))
        if not SLUG_RE.match(value):
            yield f"{path}: {field} must be a lowercase slug"

    yield from _validate_slug_list(
        pressure.get("route_ids"),
        path=path / "route_ids",
        required_non_empty=True,
    )
    yield from _validate_slug_list(
        pressure.get("suppressed_nearby_candidate_ids"),
        path=path / "suppressed_nearby_candidate_ids",
        required_non_empty=False,
    )

    for field in (
        "pressure",
        "what_to_verify",
        "why_it_matters",
        "dismiss_if",
        "tripwire_or_next_action",
        "operator_note",
    ):
        text = _string(pressure.get(field))
        if len(text) < 20:
            yield f"{path}: {field} must be a meaningful string"

    coverage_status = _string(pressure.get("coverage_status"))
    if coverage_status not in ALLOWED_COVERAGE_STATUS:
        yield f"{path}: unknown coverage_status '{coverage_status}'"

    yield from _validate_provenance_by_field(
        pressure.get("provenance_by_field"),
        path=path / "provenance_by_field",
    )

    source_affordances = pressure.get("source_affordances")
    source_affordance_ids: list[str] = []
    if not isinstance(source_affordances, list):
        yield f"{path / 'source_affordances'}: source_affordances must be a list"
    else:
        for index, source_affordance in enumerate(source_affordances):
            item_path = path / f"source_affordances[{index}]"
            affordance_id = _string(source_affordance)
            source_affordance_ids.append(affordance_id)
            if not AFFORDANCE_ID_RE.match(affordance_id):
                yield f"{item_path}: source_affordance must be '<model-id>.<slug>'"
            elif (
                known_affordance_ids is not None
                and affordance_id not in known_affordance_ids
            ):
                yield f"{item_path}: unknown source_affordance '{affordance_id}'"

    v4_contribution = _string(pressure.get("v4_contribution"))
    if v4_contribution not in ALLOWED_V4_CONTRIBUTION:
        yield f"{path}: unknown v4_contribution '{v4_contribution}'"
    user_facing_readiness = _string(pressure.get("user_facing_readiness"))
    if user_facing_readiness not in ALLOWED_USER_FACING_READINESS:
        yield f"{path}: unknown user_facing_readiness '{user_facing_readiness}'"

    if any(
        affordance_id.startswith("principal-agent-problem.")
        for affordance_id in source_affordance_ids
    ):
        caution_text = " ".join(
            (
                _string(pressure.get("operator_note")),
                _principal_agent_caution_text(review_notes),
            )
        ).lower()
        has_medium_confidence = (
            "medium-confidence" in caution_text or "medium confidence" in caution_text
        )
        if not has_medium_confidence or "caution" not in caution_text:
            yield (
                f"{path}: principal-agent-problem support requires "
                "medium-confidence caution in operator_note or review_notes"
            )


def _validate_provenance_by_field(
    provenance: object,
    *,
    path: Path,
) -> Iterable[str]:
    if not isinstance(provenance, dict):
        yield f"{path}: provenance_by_field must be an object"
        return

    allowed = frozenset(REQUIRED_PROVENANCE_FIELDS)
    yield from _unknown_fields(provenance, allowed, path)
    yield from _missing_fields(provenance, REQUIRED_PROVENANCE_FIELDS, path)
    for field in REQUIRED_PROVENANCE_FIELDS:
        if field not in provenance:
            continue
        item = provenance.get(field)
        if not isinstance(item, list) or not item:
            yield f"{path / field}: provenance must be a non-empty list"
            continue
        for index, provenance_class in enumerate(item):
            value = _string(provenance_class)
            if value not in ALLOWED_PROVENANCE:
                yield f"{path / field / str(index)}: unknown provenance '{value}'"


def _validate_coverage_panel(
    panel: dict[str, object],
    *,
    path: Path,
) -> Iterable[str]:
    required = (
        "panel_id",
        "case_id",
        "route_id",
        "coverage_status",
        "missing_model_ids",
        "operator_trace_copy",
        "do_not_smooth_over_with",
        "why_it_matters",
    )
    yield from _unknown_fields(panel, COVERAGE_PANEL_FIELDS, path)
    yield from _missing_fields(panel, required, path)
    if any(field not in panel for field in required):
        return

    for field in ("panel_id", "case_id", "route_id"):
        value = _string(panel.get(field))
        if not SLUG_RE.match(value):
            yield f"{path}: {field} must be a lowercase slug"

    coverage_status = _string(panel.get("coverage_status"))
    if coverage_status not in ALLOWED_COVERAGE_STATUS:
        yield f"{path}: unknown coverage_status '{coverage_status}'"

    missing_model_ids = panel.get("missing_model_ids")
    yield from _validate_slug_list(
        missing_model_ids,
        path=path / "missing_model_ids",
        required_non_empty=coverage_status == "no_substrate_backed_pressure",
    )
    yield from _validate_slug_list(
        panel.get("do_not_smooth_over_with"),
        path=path / "do_not_smooth_over_with",
        required_non_empty=False,
    )
    for field in ("operator_trace_copy", "why_it_matters"):
        text = _string(panel.get(field))
        if len(text) < 20:
            yield f"{path}: {field} must be a meaningful string"


def _validate_suppressed_candidate(
    candidate: dict[str, object],
    *,
    path: Path,
    selected_pressure_ids: set[str],
) -> Iterable[str]:
    required = (
        "candidate_id",
        "case_id",
        "route_id",
        "candidate_summary",
        "suppression_reason",
        "v4_made_stronger",
        "disposition",
        "related_selected_pressure_id",
    )
    yield from _unknown_fields(candidate, SUPPRESSED_CANDIDATE_FIELDS, path)
    yield from _missing_fields(candidate, required, path)
    if any(field not in candidate for field in required):
        return

    for field in ("candidate_id", "case_id", "route_id", "related_selected_pressure_id"):
        value = _string(candidate.get(field))
        if not SLUG_RE.match(value):
            yield f"{path}: {field} must be a lowercase slug"

    for field in ("candidate_summary", "suppression_reason"):
        text = _string(candidate.get(field))
        if len(text) < 20:
            yield f"{path}: {field} must be a meaningful string"

    if not isinstance(candidate.get("v4_made_stronger"), bool):
        yield f"{path}: v4_made_stronger must be a boolean"

    disposition = _string(candidate.get("disposition"))
    if disposition not in ALLOWED_SUPPRESSED_DISPOSITION:
        yield f"{path}: unknown disposition '{disposition}'"

    related_pressure_id = _string(candidate.get("related_selected_pressure_id"))
    if disposition == "merged_support" and related_pressure_id not in selected_pressure_ids:
        yield (
            f"{path}: merged_support candidate must reference an existing "
            "selected pressure"
        )


def _validate_review_notes(review_notes: object, *, path: Path) -> Iterable[str]:
    required = (
        "decision_label",
        "runtime_dormancy_note",
        "principal_agent_medium_confidence_caution",
        "blocked_surfaces",
    )
    if not isinstance(review_notes, dict):
        yield f"{path}: review_notes must be an object"
        return
    yield from _unknown_fields(review_notes, REVIEW_NOTE_FIELDS, path)
    yield from _missing_fields(review_notes, required, path)
    if any(field not in review_notes for field in required):
        return

    if _string(review_notes.get("decision_label")) != "decision_pressure_trace_contract_ready":
        yield f"{path}: decision_label must be decision_pressure_trace_contract_ready"
    for field in ("runtime_dormancy_note", "principal_agent_medium_confidence_caution"):
        text = _string(review_notes.get(field))
        if len(text) < 20:
            yield f"{path}: {field} must be a meaningful string"
    yield from _validate_string_list(
        review_notes.get("blocked_surfaces"),
        path=path / "blocked_surfaces",
        required_non_empty=True,
    )
    if "open_questions" in review_notes:
        yield from _validate_string_list(
            review_notes.get("open_questions"),
            path=path / "open_questions",
            required_non_empty=False,
        )


def _load_known_affordance_ids(path: Path) -> set[str]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    affordances = payload.get("affordances") if isinstance(payload, dict) else None
    if not isinstance(affordances, list):
        raise DecisionPressureTraceValidationError(
            f"{path}: compiled affordances must include an affordances list"
        )

    ids: set[str] = set()
    for index, affordance in enumerate(affordances):
        if not isinstance(affordance, dict):
            raise DecisionPressureTraceValidationError(
                f"{path}: affordances[{index}] must be an object"
            )
        affordance_id = _string(affordance.get("affordance_id"))
        if affordance_id:
            ids.add(affordance_id)
    return ids


def _validate_slug_list(
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
        text = _string(item)
        if not SLUG_RE.match(text):
            yield f"{path / str(index)}: must be a lowercase slug"


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
        text = _string(item)
        if not text:
            yield f"{path / str(index)}: must be a non-empty string"


def _unknown_fields(
    payload: dict[str, object],
    allowed: frozenset[str],
    path: Path,
) -> Iterable[str]:
    for field in sorted(set(payload) - allowed):
        yield f"{path}: unknown field '{field}'"


def _missing_fields(
    payload: dict[str, object],
    required: Iterable[str],
    path: Path,
) -> Iterable[str]:
    for field in required:
        if field not in payload:
            yield f"{path}: missing required field '{field}'"


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def _principal_agent_caution_text(review_notes: object) -> str:
    if not isinstance(review_notes, dict):
        return ""
    return _string(review_notes.get("principal_agent_medium_confidence_caution"))
