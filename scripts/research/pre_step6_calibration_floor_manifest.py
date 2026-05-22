#!/usr/bin/env python3
"""Research-only calibration-floor manifest for pre-Step-6 card-deck design.

This artifact does not create new evaluation cases. It records the current
four-case suite as seed evidence, names the minimum calibration floor, and
blocks runtime promotion until the missing case buckets are curated.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence


SCHEMA_VERSION = "pre_step6_calibration_floor.v1"
STATUS = "research_only"
RUNTIME_POLICY = "runtime_dormant"
EXPERIMENT_ID = "design_preamble_calibration_floor_v0"
DEFAULT_OUT_DIR = Path("research/pre-step6-calibration-floor")
CASE_BUCKETS = (
    "high_clutter",
    "sequencing_or_problem_shape",
    "sensitive_safety_legal",
    "negative_control",
)
PAIR_BUCKET = "v60_on_off_pairs"
REQUIRED_BUCKETS = {
    "high_clutter": 3,
    "sequencing_or_problem_shape": 3,
    "sensitive_safety_legal": 3,
    "negative_control": 3,
    PAIR_BUCKET: 2,
}
REQUIRED_MIN_CASES = 12
TARGET_MAX_CASES = 20
STANDDOWN_VALUES = (
    "true_standdown",
    "false_standdown",
    "ambiguous_standdown",
    "not_observed",
)
PAYLOAD_PRESERVATION_OUTCOMES = (
    "case_n_a",
    "preserved_marker_and_anchor_entities",
    "preserved_by_marker_anchor_entities_missing",
    "introduced_category_omission",
    "deck_added_payload",
)
TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "manifest_id",
        "required_floor",
        "current_suite",
        "bucket_status",
        "case_curation_gaps",
        "standdown_recall",
        "next_bridge_probe",
        "calibration_floor_met",
        "promotion_read",
        "gates",
        "notes",
    }
)
REQUIRED_FLOOR_FIELDS = frozenset(
    {
        "min_cases",
        "target_max_cases",
        "bucket_minimums",
        "v60_toggle_requirement",
        "v60_pair_origin",
    }
)
V60_PAIR_ORIGIN_FIELDS = frozenset(
    {"primary_definition", "unit_of_pair", "substantive_vs_minimal_v60"}
)
CURRENT_SUITE_FIELDS = frozenset({"suite_role", "case_count", "cases"})
CASE_FIELDS = frozenset(
    {
        "case_id",
        "case_type_tags",
        "calibration_role",
        "visibility_policy_ref",
        "v60_toggle_pair_id",
    }
)
BUCKET_STATUS_FIELDS = frozenset({"bucket", "required", "observed", "missing", "met"})
CURATION_GAP_FIELDS = frozenset({"bucket", "missing", "why_it_matters"})
STANDDOWN_FIELDS = frozenset(
    {
        "primary_runtime_failure_mode",
        "measurement_status",
        "classification_values",
        "observed_standdowns",
        "audit_dimensions",
        "payload_preservation_outcomes",
        "promotion_condition",
    }
)
OBSERVED_STANDDOWN_FIELDS = frozenset(
    {"case_id", "visible_policy_ref", "current_label", "calibration_weight"}
)
NEXT_BRIDGE_PROBE_FIELDS = frozenset(
    {
        "probe_id",
        "status",
        "target_case_count_min",
        "target_case_count_max",
        "selection_rule",
        "case_shapes",
        "promotion_effect",
        "stop_condition",
    }
)
CASE_SHAPE_FIELDS = frozenset({"shape_id", "why_it_matters"})
GATE_FIELDS = frozenset({"runtime_wiring_allowed", "skill_update_allowed"})


class CalibrationFloorValidationError(ValueError):
    pass


def build_seed_calibration_manifest(*, repo_root: Path) -> dict[str, object]:
    cases = _seed_cases()
    bucket_status = _bucket_status(cases)
    gaps = _case_curation_gaps(cases=cases, bucket_status=bucket_status)
    floor_met = _floor_met(cases=cases, bucket_status=bucket_status)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "manifest_id": "seed-suite",
        "required_floor": {
            "min_cases": REQUIRED_MIN_CASES,
            "target_max_cases": TARGET_MAX_CASES,
            "bucket_minimums": dict(REQUIRED_BUCKETS),
            "v60_toggle_requirement": (
                "At least two cases must be evaluated as V60-on/V60-off pairs "
                "to separate card-deck effects from existing enrichment effects."
            ),
            "v60_pair_origin": _v60_pair_origin(),
        },
        "current_suite": {
            "suite_role": "seed_suite_not_calibration",
            "case_count": len(cases),
            "cases": cases,
        },
        "bucket_status": bucket_status,
        "case_curation_gaps": gaps,
        "standdown_recall": {
            "primary_runtime_failure_mode": "false_standdown",
            "measurement_status": "not_calibrated",
            "classification_values": list(STANDDOWN_VALUES),
            "observed_standdowns": _observed_standdowns(cases),
            "audit_dimensions": [
                "case_type",
                "card_type",
                "v60_overlap",
                "ledger_signal",
                "reviewer_signal",
                "protected_payload_preservation",
            ],
            "payload_preservation_outcomes": list(PAYLOAD_PRESERVATION_OUTCOMES),
            "promotion_condition": (
                "False-standdown recall must be measured on the calibration "
                "floor before runtime promotion."
            ),
        },
        "next_bridge_probe": _next_bridge_probe(),
        "calibration_floor_met": floor_met,
        "promotion_read": "promotion_eligible" if floor_met else "runtime_promotion_blocked",
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": (
            "Research-only manifest. It intentionally treats the current four "
            "cases as a seed suite and records the missing curation work instead "
            "of fabricating calibration coverage."
        ),
    }
    validate_calibration_floor_manifest(payload, repo_root=repo_root)
    return payload


def load_calibration_floor_manifest(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise CalibrationFloorValidationError(f"{path}: payload must be an object")
    return payload


def validate_calibration_floor_manifest(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> None:
    errors = list(iter_calibration_floor_errors(payload, path=Path(path), repo_root=repo_root))
    if errors:
        raise CalibrationFloorValidationError("; ".join(errors))


def validate_calibration_floor_file(path: Path) -> None:
    validate_calibration_floor_manifest(
        load_calibration_floor_manifest(path),
        path=Path(path),
        repo_root=Path.cwd(),
    )


def iter_calibration_floor_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
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
    if _string(payload.get("manifest_id")) != "seed-suite":
        yield f"{path / 'manifest_id'}: must be seed-suite"
    yield from _validate_required_floor(payload.get("required_floor"), path / "required_floor")
    current_suite = payload.get("current_suite")
    yield from _validate_current_suite(current_suite, path / "current_suite", repo_root=repo_root)
    cases = []
    if isinstance(current_suite, dict) and isinstance(current_suite.get("cases"), list):
        cases = [case for case in current_suite["cases"] if isinstance(case, dict)]
    yield from _validate_bucket_status(payload.get("bucket_status"), path / "bucket_status", cases=cases)
    yield from _validate_curation_gaps(payload.get("case_curation_gaps"), path / "case_curation_gaps")
    yield from _validate_standdown_recall(
        payload.get("standdown_recall"),
        path / "standdown_recall",
        cases=cases,
    )
    yield from _validate_next_bridge_probe(payload.get("next_bridge_probe"), path / "next_bridge_probe")
    floor_met = _floor_met(cases=cases, bucket_status=_safe_bucket_status(payload.get("bucket_status")))
    if payload.get("calibration_floor_met") is not floor_met:
        yield f"{path / 'calibration_floor_met'}: must match current suite and bucket status"
    expected_promotion = "promotion_eligible" if floor_met else "runtime_promotion_blocked"
    if payload.get("promotion_read") != expected_promotion:
        yield f"{path / 'promotion_read'}: must be {expected_promotion}"
    yield from _validate_gates(payload.get("gates"), path / "gates")


def write_calibration_floor_manifest(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_calibration_floor_manifest(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{_string(payload['manifest_id'])}.calibration-floor.v1.json"
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return out_path


def _seed_cases() -> list[dict[str, object]]:
    return [
        {
            "case_id": "founder-grant-marcus-equity.high-clutter",
            "case_type_tags": ["high_clutter"],
            "calibration_role": "positive_seed",
            "visibility_policy_ref": (
                "research/pre-step6-card-deck-visibility-policies/"
                "founder-grant-marcus-equity.high-clutter.card-deck-visibility-policy.v1.json"
            ),
            "v60_toggle_pair_id": "",
        },
        {
            "case_id": "third-year-phd-student.v2",
            "case_type_tags": ["sequencing_or_problem_shape"],
            "calibration_role": "positive_seed",
            "visibility_policy_ref": (
                "research/pre-step6-card-deck-visibility-policies/"
                "third-year-phd-student.v2.card-deck-visibility-policy.v1.json"
            ),
            "v60_toggle_pair_id": "",
        },
        {
            "case_id": "mid-level-consultant-report-2",
            "case_type_tags": ["sensitive_safety_legal"],
            "calibration_role": "positive_seed",
            "visibility_policy_ref": (
                "research/pre-step6-card-deck-visibility-policies/"
                "mid-level-consultant-report-2.card-deck-visibility-policy.v1.json"
            ),
            "v60_toggle_pair_id": "",
        },
        {
            "case_id": "mother-address-year",
            "case_type_tags": ["sensitive_safety_legal", "negative_control"],
            "calibration_role": "standdown_seed",
            "visibility_policy_ref": (
                "research/pre-step6-card-deck-visibility-policies/"
                "mother-address-year.card-deck-visibility-policy.v1.json"
            ),
            "v60_toggle_pair_id": "",
        },
    ]


def _v60_pair_origin() -> dict[str, str]:
    return {
        "primary_definition": "same_case_run_twice_v60_on_off",
        "unit_of_pair": (
            "Same case, same prompt contract, same card deck policy; one run "
            "with V60 selected items available and one run with V60 selected "
            "items withheld."
        ),
        "substantive_vs_minimal_v60": (
            "Useful stratification label, not a substitute for same-case "
            "on/off pairs."
        ),
    }


def _next_bridge_probe() -> dict[str, object]:
    return {
        "probe_id": "false_standdown_bridge_probe_v0",
        "status": "planned_non_promotional",
        "target_case_count_min": 2,
        "target_case_count_max": 3,
        "selection_rule": (
            "Choose cases deliberately likely to expose false stand-down: the "
            "anchor is plausible, runtime asymmetry would suppress the deck, "
            "and the deck plausibly adds concrete protected pressure."
        ),
        "case_shapes": [
            {
                "shape_id": "high_clutter_sensitive_overlay",
                "why_it_matters": (
                    "Tests whether runtime anchor bias suppresses useful deck "
                    "pressure when clutter and tone sensitivity coexist."
                ),
            },
            {
                "shape_id": "sensitive_anchor_misses_tripwire",
                "why_it_matters": (
                    "Tests the dangerous case where the deck adds a concrete "
                    "tripwire the anchor missed."
                ),
            },
            {
                "shape_id": "sequencing_sensitive_boundary",
                "why_it_matters": (
                    "Tests whether Polya-style sequencing survives when the "
                    "answer also needs careful safety or legal boundaries."
                ),
            },
        ],
        "promotion_effect": "none_bridge_only",
        "stop_condition": (
            "Any confirmed false_standdown triggers design review before an "
            "integration draft."
        ),
    }


def _bucket_status(cases: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for bucket, required in REQUIRED_BUCKETS.items():
        observed = _observed_count(bucket=bucket, cases=cases)
        rows.append(
            {
                "bucket": bucket,
                "required": required,
                "observed": observed,
                "missing": max(required - observed, 0),
                "met": observed >= required,
            }
        )
    return rows


def _case_curation_gaps(
    *,
    cases: list[dict[str, object]],
    bucket_status: list[dict[str, object]],
) -> list[dict[str, object]]:
    gaps = [
        {
            "bucket": "total_cases",
            "missing": max(REQUIRED_MIN_CASES - len(cases), 0),
            "why_it_matters": "Four cases are useful seed evidence, not a calibration floor.",
        }
    ]
    reasons = {
        "high_clutter": "Tests whether card decks improve cluttered edge-pressure cases.",
        "sequencing_or_problem_shape": "Tests Polya-style problem-shape and next-move pressure.",
        "sensitive_safety_legal": "Tests whether anchor bias avoids unsafe phrasing drift.",
        "negative_control": "Tests stand-down behavior when the anchor is already sufficient.",
        PAIR_BUCKET: "Separates card-deck effect from existing V60 enrichment effect.",
    }
    for row in bucket_status:
        missing = _int(row.get("missing"))
        if missing > 0:
            gaps.append(
                {
                    "bucket": _string(row.get("bucket")),
                    "missing": missing,
                    "why_it_matters": reasons[_string(row.get("bucket"))],
                }
            )
    return gaps


def _observed_standdowns(cases: list[dict[str, object]]) -> list[dict[str, str]]:
    return [
        {
            "case_id": _string(case["case_id"]),
            "visible_policy_ref": _string(case["visibility_policy_ref"]),
            "current_label": "true_standdown_candidate",
            "calibration_weight": "seed_only",
        }
        for case in cases
        if case.get("calibration_role") == "standdown_seed"
    ]


def _observed_count(*, bucket: str, cases: list[dict[str, object]]) -> int:
    if bucket == PAIR_BUCKET:
        pair_ids = {
            _string(case.get("v60_toggle_pair_id"))
            for case in cases
            if _string(case.get("v60_toggle_pair_id")).strip()
        }
        return len(pair_ids)
    count = 0
    for case in cases:
        tags = case.get("case_type_tags")
        if isinstance(tags, list) and bucket in tags:
            count += 1
    return count


def _floor_met(*, cases: list[dict[str, object]], bucket_status: list[dict[str, object]]) -> bool:
    if len(cases) < REQUIRED_MIN_CASES:
        return False
    if len(cases) > TARGET_MAX_CASES:
        return False
    return all(row.get("met") is True for row in bucket_status)


def _safe_bucket_status(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _validate_required_floor(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, REQUIRED_FLOOR_FIELDS, path)
    yield from _missing_fields(value, REQUIRED_FLOOR_FIELDS, path)
    if value.get("min_cases") != REQUIRED_MIN_CASES:
        yield f"{path / 'min_cases'}: must be {REQUIRED_MIN_CASES}"
    if value.get("target_max_cases") != TARGET_MAX_CASES:
        yield f"{path / 'target_max_cases'}: must be {TARGET_MAX_CASES}"
    minimums = value.get("bucket_minimums")
    if minimums != REQUIRED_BUCKETS:
        yield f"{path / 'bucket_minimums'}: must match required bucket minimums"
    if not _string(value.get("v60_toggle_requirement")).strip():
        yield f"{path / 'v60_toggle_requirement'}: must be non-empty"
    yield from _validate_v60_pair_origin(value.get("v60_pair_origin"), path / "v60_pair_origin")


def _validate_v60_pair_origin(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, V60_PAIR_ORIGIN_FIELDS, path)
    yield from _missing_fields(value, V60_PAIR_ORIGIN_FIELDS, path)
    if value != _v60_pair_origin():
        yield f"{path}: must define same-case V60 on/off pair origin"


def _validate_current_suite(
    value: object,
    path: Path,
    *,
    repo_root: Path | None,
) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, CURRENT_SUITE_FIELDS, path)
    yield from _missing_fields(value, CURRENT_SUITE_FIELDS, path)
    if value.get("suite_role") != "seed_suite_not_calibration":
        yield f"{path / 'suite_role'}: must be seed_suite_not_calibration"
    cases = value.get("cases")
    if not isinstance(cases, list):
        yield f"{path / 'cases'}: must be a list"
        return
    if value.get("case_count") != len(cases):
        yield f"{path / 'case_count'}: must match cases length"
    for index, case in enumerate(cases):
        yield from _validate_case(case, path / "cases" / str(index), repo_root=repo_root)


def _validate_case(value: object, path: Path, *, repo_root: Path | None) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, CASE_FIELDS, path)
    yield from _missing_fields(value, CASE_FIELDS, path)
    if not _string(value.get("case_id")).strip():
        yield f"{path / 'case_id'}: must be non-empty"
    tags = value.get("case_type_tags")
    if not isinstance(tags, list) or not tags:
        yield f"{path / 'case_type_tags'}: must be a non-empty list"
    elif any(tag not in CASE_BUCKETS for tag in tags):
        yield f"{path / 'case_type_tags'}: unsupported bucket"
    if _string(value.get("calibration_role")) not in {
        "positive_seed",
        "negative_control_seed",
        "standdown_seed",
        "v60_toggle_seed",
    }:
        yield f"{path / 'calibration_role'}: unsupported role"
    ref = _string(value.get("visibility_policy_ref"))
    if not ref.startswith("research/"):
        yield f"{path / 'visibility_policy_ref'}: must point to research artifact"
    elif repo_root is not None and not (repo_root / ref).exists():
        yield f"{path / 'visibility_policy_ref'}: referenced artifact does not exist"


def _validate_bucket_status(
    value: object,
    path: Path,
    *,
    cases: list[dict[str, object]],
) -> Iterable[str]:
    if not isinstance(value, list):
        yield f"{path}: must be a list"
        return
    buckets = [_string(item.get("bucket")) for item in value if isinstance(item, dict)]
    if buckets != list(REQUIRED_BUCKETS):
        yield f"{path}: buckets must be {list(REQUIRED_BUCKETS)}"
    expected = _bucket_status(cases)
    if value != expected:
        yield f"{path}: must match current suite counts"
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            yield f"{path / str(index)}: must be an object"
            continue
        yield from _unknown_fields(item, BUCKET_STATUS_FIELDS, path / str(index))
        yield from _missing_fields(item, BUCKET_STATUS_FIELDS, path / str(index))


def _validate_curation_gaps(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, list):
        yield f"{path}: must be a list"
        return
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            yield f"{path / str(index)}: must be an object"
            continue
        yield from _unknown_fields(item, CURATION_GAP_FIELDS, path / str(index))
        yield from _missing_fields(item, CURATION_GAP_FIELDS, path / str(index))
        if _int(item.get("missing")) < 0:
            yield f"{path / str(index) / 'missing'}: must be non-negative"
        if not _string(item.get("why_it_matters")).strip():
            yield f"{path / str(index) / 'why_it_matters'}: must be non-empty"


def _validate_standdown_recall(
    value: object,
    path: Path,
    *,
    cases: list[dict[str, object]],
) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, STANDDOWN_FIELDS, path)
    yield from _missing_fields(value, STANDDOWN_FIELDS, path)
    if value.get("primary_runtime_failure_mode") != "false_standdown":
        yield f"{path / 'primary_runtime_failure_mode'}: must be false_standdown"
    if value.get("measurement_status") != "not_calibrated":
        yield f"{path / 'measurement_status'}: must be not_calibrated"
    if value.get("classification_values") != list(STANDDOWN_VALUES):
        yield f"{path / 'classification_values'}: invalid values"
    expected_observed = _observed_standdowns(cases)
    if value.get("observed_standdowns") != expected_observed:
        yield f"{path / 'observed_standdowns'}: must match standdown seed cases"
    observed = value.get("observed_standdowns")
    if isinstance(observed, list):
        for index, item in enumerate(observed):
            yield from _validate_observed_standdown(item, path / "observed_standdowns" / str(index))
    dimensions = value.get("audit_dimensions")
    if not isinstance(dimensions, list) or not dimensions:
        yield f"{path / 'audit_dimensions'}: must be a non-empty list"
    if value.get("payload_preservation_outcomes") != list(PAYLOAD_PRESERVATION_OUTCOMES):
        yield f"{path / 'payload_preservation_outcomes'}: invalid outcomes"
    if not _string(value.get("promotion_condition")).strip():
        yield f"{path / 'promotion_condition'}: must be non-empty"


def _validate_observed_standdown(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, OBSERVED_STANDDOWN_FIELDS, path)
    yield from _missing_fields(value, OBSERVED_STANDDOWN_FIELDS, path)
    if value.get("current_label") not in {"true_standdown_candidate", "false_standdown_candidate"}:
        yield f"{path / 'current_label'}: unsupported label"
    if value.get("calibration_weight") != "seed_only":
        yield f"{path / 'calibration_weight'}: must be seed_only"


def _validate_next_bridge_probe(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, NEXT_BRIDGE_PROBE_FIELDS, path)
    yield from _missing_fields(value, NEXT_BRIDGE_PROBE_FIELDS, path)
    if value.get("probe_id") != "false_standdown_bridge_probe_v0":
        yield f"{path / 'probe_id'}: invalid probe"
    if value.get("status") != "planned_non_promotional":
        yield f"{path / 'status'}: must be planned_non_promotional"
    if value.get("target_case_count_min") != 2:
        yield f"{path / 'target_case_count_min'}: must be 2"
    if value.get("target_case_count_max") != 3:
        yield f"{path / 'target_case_count_max'}: must be 3"
    if not _string(value.get("selection_rule")).strip():
        yield f"{path / 'selection_rule'}: must be non-empty"
    if value.get("promotion_effect") != "none_bridge_only":
        yield f"{path / 'promotion_effect'}: must be none_bridge_only"
    if not _string(value.get("stop_condition")).startswith("Any confirmed false_standdown"):
        yield f"{path / 'stop_condition'}: must name false_standdown stop condition"
    case_shapes = value.get("case_shapes")
    if not isinstance(case_shapes, list) or len(case_shapes) != 3:
        yield f"{path / 'case_shapes'}: must contain three planned shapes"
        return
    for index, item in enumerate(case_shapes):
        if not isinstance(item, dict):
            yield f"{path / 'case_shapes' / str(index)}: must be an object"
            continue
        yield from _unknown_fields(item, CASE_SHAPE_FIELDS, path / "case_shapes" / str(index))
        yield from _missing_fields(item, CASE_SHAPE_FIELDS, path / "case_shapes" / str(index))
        if not _string(item.get("shape_id")).strip():
            yield f"{path / 'case_shapes' / str(index) / 'shape_id'}: must be non-empty"
        if not _string(item.get("why_it_matters")).strip():
            yield f"{path / 'case_shapes' / str(index) / 'why_it_matters'}: must be non-empty"


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


def _int(value: object) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="Existing calibration-floor payloads to validate")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.paths:
        for path in args.paths:
            validate_calibration_floor_file(path)
        return 0
    payload = build_seed_calibration_manifest(repo_root=Path.cwd())
    if args.write:
        print(write_calibration_floor_manifest(payload=payload, out_dir=args.out_dir))
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
