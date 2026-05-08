from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V45_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v45.json"
)
AFFORDANCES_V46_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v46.json"
)

TARGET_RECORD_PATHS = {
    "game-theory-payoffs": MODEL_AFFORDANCE_DIR
    / "batch_5"
    / "game-theory-payoffs.json",
    "nash-equilibrium": MODEL_AFFORDANCE_DIR / "batch_6" / "nash-equilibrium.json",
    "signaling": MODEL_AFFORDANCE_DIR / "batch_7" / "signaling.json",
}

COMPRESSION_OK_MODEL_IDS = {
    "adverse-selection",
    "authority-bias",
    "batna",
    "incentives",
    "international-negotiation-and-diplomacy-models",
    "liking-principle",
    "prisoners-dilemma",
    "reciprocity-principle",
    "understanding-motivations",
}

NEW_AFFORDANCE_IDS = {
    "game-theory-payoffs.adverse-response-floor-test",
    "nash-equilibrium.dominant-strategy-mechanism-design",
    "signaling.create-actionable-coordination-signal",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr84_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr84_compiled_v46_adds_bounded_social_incentive_splits() -> None:
    affordances_v45 = _load_compiled(AFFORDANCES_V45_PATH)
    affordances_v46 = _load_compiled(AFFORDANCES_V46_PATH)

    assert affordances_v46["artifact"] == "model_affordances_v46"
    assert affordances_v46["status"] == "draft_review_only"
    assert _model_ids(affordances_v46) == _model_ids(affordances_v45)
    assert len(_model_ids(affordances_v46)) == 222

    assert NEW_AFFORDANCE_IDS.isdisjoint(_affordance_ids(affordances_v45))
    assert _affordance_ids(affordances_v46) - _affordance_ids(affordances_v45) == (
        NEW_AFFORDANCE_IDS
    )
    assert _absence_fields(affordances_v46) == _absence_fields(affordances_v45)

    v45_metadata = affordances_v45["compile_metadata"]
    v46_metadata = affordances_v46["compile_metadata"]
    assert v46_metadata["contributing_record_count"] == 222
    assert v46_metadata["affordance_count"] == v45_metadata["affordance_count"] + 3
    assert v46_metadata["affordance_count"] == 287
    assert v46_metadata["absence_record_count"] == v45_metadata["absence_record_count"]
    assert v46_metadata["absence_record_count"] == 555
    assert v46_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v46_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr84_signaling_split_preserves_proof_vs_coordination_identity() -> None:
    record = _load_record("signaling")
    proof = _affordance_by_id(record, "signaling.costly-proof-of-intent-test")
    coordination = _affordance_by_id(
        record,
        "signaling.create-actionable-coordination-signal",
    )

    assert "what costly proof of intent to demand next" in str(
        proof["source_evidence"]
    )
    assert "make-abstract-intent-concrete" in str(
        coordination["treatment_requirements"]
    )
    assert "accurate but useless" in str(coordination)
    assert "shared, actionable reality" in str(coordination["source_evidence"])
    assert "costly unstaged proof is needed" in str(coordination["misuse_guards"])


def test_pr84_strategic_splits_preserve_floor_and_rule_design_identity() -> None:
    game_theory = _load_record("game-theory-payoffs")
    nash = _load_record("nash-equilibrium")

    floor = _affordance_by_id(
        game_theory,
        "game-theory-payoffs.adverse-response-floor-test",
    )
    payoff_map = _affordance_by_id(
        game_theory,
        "game-theory-payoffs.counterparty-response-payoff-map",
    )
    rule_design = _affordance_by_id(
        nash,
        "nash-equilibrium.dominant-strategy-mechanism-design",
    )
    stable_map = _affordance_by_id(
        nash,
        "nash-equilibrium.stable-best-response-map",
    )

    assert "calculate-adverse-response-floor" in str(floor["treatment_requirements"])
    assert "opponent chooses their best strategy" in str(floor["source_evidence"])
    assert "expected or likely payoff" in str(floor["misuse_guards"])
    assert "adverse-response-floor-test" not in payoff_map["affordance_id"]

    assert "test-dominant-strategy-compatibility" in str(
        rule_design["treatment_requirements"]
    )
    assert "players **don\u2019t have to be strategic**" in str(
        rule_design["source_evidence"]
    )
    assert "stable equilibrium" in str(rule_design["misuse_guards"])
    assert "dominant-strategy" not in stable_map["affordance_id"]


def test_pr84_adjacent_social_incentive_records_remain_compressed() -> None:
    affordances_v45 = _load_compiled(AFFORDANCES_V45_PATH)
    affordances_v46 = _load_compiled(AFFORDANCES_V46_PATH)

    v45_counts = _affordance_counts_by_model(affordances_v45)
    v46_counts = _affordance_counts_by_model(affordances_v46)

    for model_id in COMPRESSION_OK_MODEL_IDS:
        assert v46_counts[model_id] == v45_counts[model_id]


def test_pr84_v46_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v46", "model_affordances_v46")

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


def _absence_fields(compiled: dict[str, object]) -> set[str]:
    return {
        absence["attempted_field"]
        for record in compiled["model_records"]
        for absence in record["absence_records"]
    }


def _affordance_counts_by_model(compiled: dict[str, object]) -> dict[str, int]:
    return {
        record["model_id"]: len(record["affordances"])
        for record in compiled["model_records"]
    }


def _affordance_by_id(
    record: dict[str, object],
    affordance_id: str,
) -> dict[str, object]:
    for affordance in record["affordances"]:
        if affordance["affordance_id"] == affordance_id:
            return affordance
    raise AssertionError(f"Missing affordance_id: {affordance_id}")
