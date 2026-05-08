from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V32_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v32.json"
)
AFFORDANCES_V33_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v33.json"
)

TARGET_RECORD_PATHS = {
    "inversion": MODEL_AFFORDANCE_DIR / "pilot" / "inversion.json",
    "leverage-points": MODEL_AFFORDANCE_DIR / "batch_1" / "leverage-points.json",
    "lindy-effect": MODEL_AFFORDANCE_DIR / "batch_1" / "lindy-effect.json",
    "premortem": MODEL_AFFORDANCE_DIR / "pilot" / "premortem.json",
    "second-order-thinking": MODEL_AFFORDANCE_DIR
    / "pilot"
    / "second-order-thinking.json",
    "sunk-cost-fallacy": MODEL_AFFORDANCE_DIR
    / "batch_1"
    / "sunk-cost-fallacy.json",
}

TARGET_ABSENCE_FIELDS = {
    "after-commitment-criticism-theater",
    "age-as-proof-of-superiority",
    "avoidance-only-inversion-without-forward-action",
    "lindy-for-perishable-or-fast-baseline-break-context",
    "obvious-worry-list-without-owner-or-plan-change",
    "ordinary-option-comparison-without-prior-investment-pressure",
    "preferred-initiative-as-leverage-point-without-mechanism",
    "reckless-abandonment-as-anti-sunk-cost-discipline",
    "speculative-consequence-chain-without-mechanism",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr71_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr71_compiled_v33_is_v32_plus_nine_absence_records() -> None:
    affordances_v32 = _load_compiled(AFFORDANCES_V32_PATH)
    affordances_v33 = _load_compiled(AFFORDANCES_V33_PATH)

    assert affordances_v33["artifact"] == "model_affordances_v33"
    assert affordances_v33["status"] == "draft_review_only"
    assert _model_ids(affordances_v33) == _model_ids(affordances_v32)
    assert len(_model_ids(affordances_v33)) == 222
    assert _affordance_ids(affordances_v33) == _affordance_ids(affordances_v32)
    assert TARGET_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v32))
    assert TARGET_ABSENCE_FIELDS.issubset(_absence_fields(affordances_v33))
    assert _absence_fields(affordances_v33) - _absence_fields(affordances_v32) == (
        TARGET_ABSENCE_FIELDS
    )

    v32_metadata = affordances_v32["compile_metadata"]
    v33_metadata = affordances_v33["compile_metadata"]
    assert v33_metadata["contributing_record_count"] == 222
    assert v33_metadata["affordance_count"] == v32_metadata["affordance_count"]
    assert v33_metadata["affordance_count"] == 268
    assert v33_metadata["absence_record_count"] == v32_metadata["absence_record_count"] + 9
    assert v33_metadata["absence_record_count"] == 495
    assert v33_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v33_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr71_absences_create_minimum_overclaim_floor() -> None:
    lindy = _load_record("lindy-effect")
    assert _absence_by_field(lindy, "age-as-proof-of-superiority")[
        "runtime_policy"
    ] == "do_not_promote"
    assert _absence_by_field(
        lindy,
        "lindy-for-perishable-or-fast-baseline-break-context",
    )["runtime_policy"] == "do_not_promote"

    premortem = _load_record("premortem")
    assert _absence_by_field(premortem, "after-commitment-criticism-theater")[
        "runtime_policy"
    ] == "do_not_promote"
    assert _absence_by_field(
        premortem,
        "obvious-worry-list-without-owner-or-plan-change",
    )["runtime_policy"] == "do_not_promote"

    sunk_cost = _load_record("sunk-cost-fallacy")
    assert _absence_by_field(
        sunk_cost,
        "reckless-abandonment-as-anti-sunk-cost-discipline",
    )["runtime_policy"] == "do_not_promote"
    assert _absence_by_field(
        sunk_cost,
        "ordinary-option-comparison-without-prior-investment-pressure",
    )["runtime_policy"] == "do_not_promote"

    inversion = _load_record("inversion")
    assert _absence_by_field(
        inversion,
        "avoidance-only-inversion-without-forward-action",
    )["runtime_policy"] == "do_not_promote"

    leverage = _load_record("leverage-points")
    assert _absence_by_field(
        leverage,
        "preferred-initiative-as-leverage-point-without-mechanism",
    )["runtime_policy"] == "do_not_promote"

    second_order = _load_record("second-order-thinking")
    assert _absence_by_field(
        second_order,
        "speculative-consequence-chain-without-mechanism",
    )["runtime_policy"] == "do_not_promote"


def test_pr71_treatment_repairs_stay_inside_existing_affordances() -> None:
    lindy = _load_record("lindy-effect")
    lindy_affordance = _affordance_by_id(
        lindy,
        "lindy-effect.longevity-prior-with-baseline-break-check",
    )
    assert any(
        "relationship" in str(use_when)
        for use_when in lindy_affordance["activation_shape"]["use_when"]
    )
    stress_old_baseline = _requirement_by_id(
        lindy_affordance,
        "stress-test-old-baseline",
    )
    assert "legacy implementation" in str(stress_old_baseline["evidence_required"])
    assert "baseline-breaking alternative" in str(stress_old_baseline["good_output_shape"])

    premortem = _load_record("premortem")
    premortem_affordance = _affordance_by_id(
        premortem,
        "premortem.simulated-failure-to-plan-change",
    )
    bind_risks = _requirement_by_id(premortem_affordance, "bind-risks-to-changes")
    assert "known unknown" in str(bind_risks["evidence_required"])
    assert "severe tail outcomes" in str(bind_risks["good_output_shape"])

    sunk_cost = _load_record("sunk-cost-fallacy")
    sunk_affordance = _affordance_by_id(
        sunk_cost,
        "sunk-cost-fallacy.future-value-recommitment",
    )
    bind_next_phase = _requirement_by_id(
        sunk_affordance,
        "bind-next-phase-to-evidence",
    )
    assert "before investment creates sunk-cost pressure" in str(
        bind_next_phase["good_output_shape"]
    )
    assert "cash-flow reality" in str(bind_next_phase["good_output_shape"])
    assert any(
        "high-cost commitment" in str(use_when)
        for use_when in sunk_affordance["activation_shape"]["use_when"]
    )

    second_order = _load_record("second-order-thinking")
    second_affordance = _affordance_by_id(
        second_order,
        "second-order-thinking.downstream-reversal-stress-test",
    )
    assert _requirement_by_id(
        second_affordance,
        "bound-chain-with-structure-and-action-threshold",
    )
    assert "rework, fragility, lock-in" in str(
        second_affordance["activation_shape"]["case_evidence_needed"]
    )


def test_pr71_v33_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v33", "model_affordances_v33")

    for path in LIVE_RUNTIME_PATHS:
        text = path.read_text(encoding="utf-8")
        assert all(fragment not in text for fragment in forbidden)


def _load_record(model_id: str) -> dict[str, object]:
    return json.loads(TARGET_RECORD_PATHS[model_id].read_text(encoding="utf-8"))


def _load_compiled(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _model_ids(compiled: dict[str, object]) -> set[str]:
    return {
        str(record["model_id"])
        for record in compiled.get("model_records", [])
        if isinstance(record, dict)
    }


def _affordance_ids(compiled: dict[str, object]) -> set[str]:
    return {
        str(affordance["affordance_id"])
        for record in compiled.get("model_records", [])
        if isinstance(record, dict)
        for affordance in record.get("affordances", [])
        if isinstance(affordance, dict)
    }


def _absence_fields(compiled: dict[str, object]) -> set[str]:
    return {
        str(absence["attempted_field"])
        for record in compiled.get("model_records", [])
        if isinstance(record, dict)
        for absence in record.get("absence_records", [])
        if isinstance(absence, dict)
    }


def _absence_by_field(
    record: dict[str, object],
    attempted_field: str,
) -> dict[str, object]:
    for absence in record.get("absence_records", []):
        if isinstance(absence, dict) and absence.get("attempted_field") == attempted_field:
            return absence
    raise AssertionError(f"missing absence record: {attempted_field}")


def _affordance_by_id(
    record: dict[str, object],
    affordance_id: str,
) -> dict[str, object]:
    for affordance in record.get("affordances", []):
        if isinstance(affordance, dict) and affordance.get("affordance_id") == affordance_id:
            return affordance
    raise AssertionError(f"missing affordance: {affordance_id}")


def _requirement_by_id(
    affordance: dict[str, object],
    requirement_id: str,
) -> dict[str, object]:
    for requirement in affordance.get("treatment_requirements", []):
        if isinstance(requirement, dict) and requirement.get("requirement_id") == requirement_id:
            return requirement
    raise AssertionError(f"missing requirement: {requirement_id}")
