from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V39_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v39.json"
)
AFFORDANCES_V40_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v40.json"
)

TARGET_RECORD_PATHS = {
    "bottlenecks": MODEL_AFFORDANCE_DIR / "batch_8" / "bottlenecks.json",
    "constraints": MODEL_AFFORDANCE_DIR / "batch_4" / "constraints.json",
    "leverage-points": MODEL_AFFORDANCE_DIR / "batch_1" / "leverage-points.json",
}

REMOVED_COMPRESSED_AFFORDANCE_IDS = {
    "constraints.scope-boundary-decision-filter",
    "leverage-points.hypothesis-bounded-analysis",
    "leverage-points.resistance-bias-execution-hardening",
}

NEW_SPLIT_AFFORDANCE_IDS = {
    "constraints.constraint-fit-stress-test",
    "constraints.scope-boundary-exclusion-filter",
    "leverage-points.assumption-antithesis-test",
    "leverage-points.execution-resistance-plan",
    "leverage-points.focus-check-stop-continue",
    "leverage-points.minimal-fact-threshold",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr78_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr78_compiled_v40_replaces_compressed_cards_with_splits() -> None:
    affordances_v39 = _load_compiled(AFFORDANCES_V39_PATH)
    affordances_v40 = _load_compiled(AFFORDANCES_V40_PATH)

    assert affordances_v40["artifact"] == "model_affordances_v40"
    assert affordances_v40["status"] == "draft_review_only"
    assert _model_ids(affordances_v40) == _model_ids(affordances_v39)
    assert len(_model_ids(affordances_v40)) == 222

    v39_ids = _affordance_ids(affordances_v39)
    v40_ids = _affordance_ids(affordances_v40)
    assert REMOVED_COMPRESSED_AFFORDANCE_IDS <= v39_ids
    assert REMOVED_COMPRESSED_AFFORDANCE_IDS.isdisjoint(v40_ids)
    assert NEW_SPLIT_AFFORDANCE_IDS.isdisjoint(v39_ids)
    assert NEW_SPLIT_AFFORDANCE_IDS <= v40_ids
    assert v40_ids - v39_ids == NEW_SPLIT_AFFORDANCE_IDS
    assert v39_ids - v40_ids == REMOVED_COMPRESSED_AFFORDANCE_IDS

    v39_metadata = affordances_v39["compile_metadata"]
    v40_metadata = affordances_v40["compile_metadata"]
    assert v40_metadata["contributing_record_count"] == 222
    assert v40_metadata["affordance_count"] == v39_metadata["affordance_count"] + 3
    assert v40_metadata["affordance_count"] == 276
    assert v40_metadata["absence_record_count"] == v39_metadata["absence_record_count"]
    assert v40_metadata["absence_record_count"] == 514
    assert v40_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v40_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr78_constraints_split_boundary_definition_from_fit_review() -> None:
    record = _load_record("constraints")
    boundary = _affordance_by_id(
        record,
        "constraints.scope-boundary-exclusion-filter",
    )
    fit = _affordance_by_id(record, "constraints.constraint-fit-stress-test")

    assert "deliberate exclusions" in str(boundary["mechanism"])
    assert "name-boundaries-and-exclusions" in str(boundary["treatment_requirements"])
    assert "If this was cut" in str(boundary["source_evidence"])
    assert "constraint-fit stress test" in str(boundary["activation_shape"])

    assert "loosen, tighten, drop, or reframe" in str(fit["activation_shape"])
    assert "test-framework-assumptions-and-external-factors" in str(
        fit["treatment_requirements"]
    )
    assert "What would you have to believe" in str(fit["source_evidence"])
    assert "Different frames yield different insights" in str(fit["source_evidence"])


def test_pr78_leverage_splits_fact_threshold_from_focus_check() -> None:
    record = _load_record("leverage-points")
    minimal = _affordance_by_id(record, "leverage-points.minimal-fact-threshold")
    focus = _affordance_by_id(record, "leverage-points.focus-check-stop-continue")

    assert "smallest fact set" in str(minimal["mechanism"])
    assert "minimal-fact-threshold" in str(minimal["treatment_requirements"])
    assert "low-leverage activities" in str(minimal["source_evidence"])
    assert "use the focus-check affordance instead" in str(minimal["activation_shape"])

    assert "stop or defer" in str(focus["mechanism"])
    assert "periodic-focus-check" in str(focus["treatment_requirements"])
    assert "How does what you" in str(focus["source_evidence"])
    assert "use the minimal fact threshold affordance instead" in str(
        focus["activation_shape"]
    )


def test_pr78_leverage_splits_antithesis_from_execution_resistance() -> None:
    record = _load_record("leverage-points")
    antithesis = _affordance_by_id(
        record,
        "leverage-points.assumption-antithesis-test",
    )
    execution = _affordance_by_id(record, "leverage-points.execution-resistance-plan")

    assert "familiar frame" in str(antithesis["mechanism"])
    assert "assumption-antithesis-test" in str(antithesis["treatment_requirements"])
    assert "disconfirming evidence" in str(antithesis["source_evidence"])
    assert "antithesis" in str(antithesis["source_evidence"])

    assert "strategic what into the execution how" in str(execution["mechanism"])
    assert "execution-resistance-plan" in str(execution["treatment_requirements"])
    assert "the more the system will resist changing it" in str(
        execution["source_evidence"]
    )
    assert "A great plan that cannot be implemented is useless" in str(
        execution["source_evidence"]
    )


def test_pr78_bottlenecks_requires_relief_execution_path() -> None:
    record = _load_record("bottlenecks")
    affordance = _affordance_by_id(
        record,
        "bottlenecks.binding-constraint-throughput-check",
    )
    requirement = _requirement_by_id(
        affordance,
        "plan-how-to-relieve-constraint",
    )

    assert "how the constrained step will actually be relieved" in str(
        requirement["description"]
    )
    assert "How will the constrained step actually improve" in str(
        affordance["diagnostic_questions"]
    )
    assert "figuring out *how* to execute the solution" in str(
        affordance["source_evidence"]
    )


def test_pr78_v40_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v40", "model_affordances_v40")

    for path in LIVE_RUNTIME_PATHS:
        text = path.read_text(encoding="utf-8")
        assert all(fragment not in text for fragment in forbidden)


def _load_record(model_id: str) -> dict[str, object]:
    return json.loads(TARGET_RECORD_PATHS[model_id].read_text(encoding="utf-8"))


def _load_compiled(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _model_ids(compiled: dict[str, object]) -> set[str]:
    return {record["model_id"] for record in compiled["model_records"]}


def _affordance_ids(compiled: dict[str, object]) -> set[str]:
    return {
        affordance["affordance_id"]
        for record in compiled["model_records"]
        for affordance in record["affordances"]
    }


def _affordance_by_id(
    record: dict[str, object],
    affordance_id: str,
) -> dict[str, object]:
    return next(
        affordance
        for affordance in record["affordances"]
        if affordance["affordance_id"] == affordance_id
    )


def _requirement_by_id(
    affordance: dict[str, object],
    requirement_id: str,
) -> dict[str, object]:
    return next(
        requirement
        for requirement in affordance["treatment_requirements"]
        if requirement["requirement_id"] == requirement_id
    )
