from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V38_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v38.json"
)
AFFORDANCES_V39_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v39.json"
)

TARGET_RECORD_PATHS = {
    "game-theory-payoffs": MODEL_AFFORDANCE_DIR
    / "batch_5"
    / "game-theory-payoffs.json",
    "information-asymmetry": MODEL_AFFORDANCE_DIR
    / "batch_1"
    / "information-asymmetry.json",
    "moral-hazard": MODEL_AFFORDANCE_DIR / "batch_2" / "moral-hazard.json",
    "prisoners-dilemma": MODEL_AFFORDANCE_DIR
    / "batch_6"
    / "prisoners-dilemma.json",
    "signaling": MODEL_AFFORDANCE_DIR / "batch_7" / "signaling.json",
}

NEW_AFFORDANCE_IDS = {
    "game-theory-payoffs.credible-sequencing-commitment-device",
    "information-asymmetry.knowledge-authority-risk-map",
}

NEW_ABSENCE_FIELDS = {
    "known-facts-without-authority-or-incentive-as-information-gap",
    "low-cost-commercial-signal-as-actual-buying-intent",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr77_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr77_compiled_v39_adds_bounded_incentive_enrichment() -> None:
    affordances_v38 = _load_compiled(AFFORDANCES_V38_PATH)
    affordances_v39 = _load_compiled(AFFORDANCES_V39_PATH)

    assert affordances_v39["artifact"] == "model_affordances_v39"
    assert affordances_v39["status"] == "draft_review_only"
    assert _model_ids(affordances_v39) == _model_ids(affordances_v38)
    assert len(_model_ids(affordances_v39)) == 222

    assert NEW_AFFORDANCE_IDS.isdisjoint(_affordance_ids(affordances_v38))
    assert _affordance_ids(affordances_v39) - _affordance_ids(affordances_v38) == (
        NEW_AFFORDANCE_IDS
    )
    assert NEW_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v38))
    assert _absence_fields(affordances_v39) - _absence_fields(affordances_v38) == (
        NEW_ABSENCE_FIELDS
    )

    v38_metadata = affordances_v38["compile_metadata"]
    v39_metadata = affordances_v39["compile_metadata"]
    assert v39_metadata["contributing_record_count"] == 222
    assert v39_metadata["affordance_count"] == v38_metadata["affordance_count"] + 2
    assert v39_metadata["affordance_count"] == 273
    assert (
        v39_metadata["absence_record_count"]
        == v38_metadata["absence_record_count"] + 2
    )
    assert v39_metadata["absence_record_count"] == 514
    assert v39_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v39_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr77_information_asymmetry_splits_knowledge_authority_risk_map() -> None:
    record = _load_record("information-asymmetry")
    affordance = _affordance_by_id(
        record,
        "information-asymmetry.knowledge-authority-risk-map",
    )
    guard = _absence_by_field(
        record,
        "known-facts-without-authority-or-incentive-as-information-gap",
    )

    assert "not the same actors" in str(affordance["mechanism"])
    assert "map-knowledge-risk-and-authority" in str(
        affordance["treatment_requirements"]
    )
    assert "different fact sets" in str(affordance["diagnostic_questions"])
    assert "Social cartography" in str(affordance["source_evidence"])
    assert guard["runtime_policy"] == "do_not_promote"
    assert "incentive misalignment" in str(guard["reason"])


def test_pr77_game_theory_splits_credible_commitment_device() -> None:
    record = _load_record("game-theory-payoffs")
    affordance = _affordance_by_id(
        record,
        "game-theory-payoffs.credible-sequencing-commitment-device",
    )
    existing_guard = _absence_by_field(
        record,
        "commitment-threat-or-promise-without-credibility-device",
    )

    assert "changing the game" in str(affordance["mechanism"])
    assert "move first, wait, reveal information" in str(
        affordance["activation_shape"]
    )
    assert "test-credibility-device" in str(affordance["treatment_requirements"])
    assert "commitments, threats, promises" in str(affordance["source_evidence"])
    assert existing_guard["runtime_policy"] == "do_not_promote"
    assert "credible" in str(existing_guard["reason"])


def test_pr77_signaling_rejects_low_cost_commercial_signals() -> None:
    record = _load_record("signaling")
    affordance = _affordance_by_id(
        record,
        "signaling.costly-proof-of-intent-test",
    )
    guard = _absence_by_field(
        record,
        "low-cost-commercial-signal-as-actual-buying-intent",
    )

    assert "budget owner time" in str(affordance["activation_shape"])
    assert "costly proof of intent" in str(affordance["diagnostic_questions"])
    assert "actual authority, buying intent, or willingness to bear cost" in str(
        affordance["source_evidence"]
    )
    assert guard["runtime_policy"] == "do_not_promote"
    assert "preserve optionality" in str(guard["reason"])


def test_pr77_prisoners_dilemma_tests_competitive_frame() -> None:
    record = _load_record("prisoners-dilemma")
    affordance = _affordance_by_id(
        record,
        "prisoners-dilemma.defection-incentive-reframe-test",
    )
    requirement = _requirement_by_id(
        affordance,
        "test-competitive-frame-before-defection-diagnosis",
    )

    assert "cooperative frame" in str(requirement["description"])
    assert "future consequences" in str(affordance["diagnostic_questions"])
    assert "competitively" in str(affordance["source_evidence"])
    assert "cooperatively" in str(affordance["source_evidence"])


def test_pr77_moral_hazard_hardens_delayed_risk_externalization() -> None:
    record = _load_record("moral-hazard")
    affordance = _affordance_by_id(
        record,
        "moral-hazard.proxy-hidden-effort-with-noisy-outcomes",
    )
    requirement = _requirement_by_id(
        affordance,
        "check-delayed-risk-externalization",
    )

    assert "short-term gains" in str(requirement["description"])
    assert "ethical" in str(affordance["diagnostic_questions"])
    assert "externalizing long-term risk" in str(affordance["source_evidence"])
    assert "second-order consequences" in str(affordance["source_evidence"])


def test_pr77_v39_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v39", "model_affordances_v39")

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


def _absence_by_field(record: dict[str, object], attempted_field: str) -> dict[str, object]:
    return next(
        absence
        for absence in record["absence_records"]
        if absence["attempted_field"] == attempted_field
    )
