from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterable


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V20_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v20.json"
)
AFFORDANCES_V21_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v21.json"
)

TARGET_RECORD_PATHS = {
    "emotional-intelligence": MODEL_AFFORDANCE_DIR
    / "batch_7"
    / "emotional-intelligence.json",
    "metacognitive-questioning": MODEL_AFFORDANCE_DIR
    / "batch_10"
    / "metacognitive-questioning.json",
}

TARGET_AFFORDANCE_IDS = {
    "emotional-intelligence.self-regulation-under-emotional-activation",
    "metacognitive-questioning.expert-process-elicitation",
}

REJECTED_DUPLICATE_AFFORDANCE_IDS = {
    "conjunction-fallacy.disjunctive-failure-risk-check",
    "critical-thinking.problem-structure-discipline",
    "evolutionary-pressure.threat-filter-communication-packaging",
    "international-negotiation-and-diplomacy-models.adversarial-countermove-simulation",
    "mental-models-of-reality.actor-mental-model-inference",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr59_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr59_compiled_v21_is_v20_plus_two_targeted_affordances() -> None:
    affordances_v20 = _load_compiled(AFFORDANCES_V20_PATH)
    affordances_v21 = _load_compiled(AFFORDANCES_V21_PATH)

    v20_model_ids = _model_ids(affordances_v20)
    v21_model_ids = _model_ids(affordances_v21)
    v20_affordance_ids = _affordance_ids(affordances_v20)
    v21_affordance_ids = _affordance_ids(affordances_v21)

    assert affordances_v21["artifact"] == "model_affordances_v21"
    assert affordances_v21["status"] == "draft_review_only"
    assert v21_model_ids == v20_model_ids
    assert len(v21_model_ids) == 222
    assert TARGET_AFFORDANCE_IDS.isdisjoint(v20_affordance_ids)
    assert TARGET_AFFORDANCE_IDS.issubset(v21_affordance_ids)
    assert v21_affordance_ids - v20_affordance_ids == TARGET_AFFORDANCE_IDS

    v20_metadata = affordances_v20["compile_metadata"]
    v21_metadata = affordances_v21["compile_metadata"]
    assert v21_metadata["contributing_record_count"] == 222
    assert v21_metadata["affordance_count"] == v20_metadata["affordance_count"] + 2
    assert v21_metadata["affordance_count"] == 268
    assert v21_metadata["absence_record_count"] == v20_metadata["absence_record_count"]
    assert v21_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v21_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr59_split_boundaries_are_source_specific_not_generic_richness() -> None:
    emotional_intelligence = _load_record("emotional-intelligence")
    self_regulation = _affordance(
        emotional_intelligence,
        "emotional-intelligence.self-regulation-under-emotional-activation",
    )
    assert _contains(self_regulation["activation_shape"]["use_when"], "emotional hijacking")
    assert _contains(self_regulation["activation_shape"]["do_not_use_when"], "stakeholder adoption")
    assert _contains(
        self_regulation["activation_shape"]["case_evidence_needed"],
        "user's emotional state",
    )
    assert _contains(self_regulation["misuse_guards"], "niceness")

    metacognitive_questioning = _load_record("metacognitive-questioning")
    expert_elicitation = _affordance(
        metacognitive_questioning,
        "metacognitive-questioning.expert-process-elicitation",
    )
    assert _contains(expert_elicitation["activation_shape"]["use_when"], "expert")
    assert _contains(expert_elicitation["activation_shape"]["do_not_use_when"], "direct factual answer")
    assert _contains(
        expert_elicitation["activation_shape"]["case_evidence_needed"],
        "skill, criterion, variable",
    )
    assert _contains(expert_elicitation["misuse_guards"], "expert-interview workflow")


def test_pr59_rejected_duplicates_stay_out_of_v21() -> None:
    affordances_v21 = _load_compiled(AFFORDANCES_V21_PATH)
    v21_affordance_ids = _affordance_ids(affordances_v21)

    assert REJECTED_DUPLICATE_AFFORDANCE_IDS.isdisjoint(v21_affordance_ids)


def test_pr59_v21_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v21", "model_affordances_v21")

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


def _affordance(record: dict[str, object], affordance_id: str) -> dict[str, object]:
    for affordance in record["affordances"]:
        if isinstance(affordance, dict) and affordance["affordance_id"] == affordance_id:
            return affordance
    raise AssertionError(f"missing affordance: {affordance_id}")


def _contains(items: object, needle: str) -> bool:
    assert isinstance(items, Iterable)
    return any(needle in str(item) for item in items)
