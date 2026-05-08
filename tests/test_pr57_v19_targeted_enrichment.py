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
AFFORDANCES_V18_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v18.json"
)
AFFORDANCES_V19_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v19.json"
)

TARGET_RECORD_PATHS = {
    "commitment-bias": MODEL_AFFORDANCE_DIR / "batch_5" / "commitment-bias.json",
    "feedback-loops": MODEL_AFFORDANCE_DIR / "batch_8" / "feedback-loops.json",
    "redundancy": MODEL_AFFORDANCE_DIR / "batch_9" / "redundancy.json",
    "switching-costs": MODEL_AFFORDANCE_DIR / "batch_9" / "switching-costs.json",
}

TARGET_AFFORDANCE_IDS = {
    "commitment-bias.constructive-commitment-architecture",
    "feedback-loops.loop-polarity-intervention-map",
    "redundancy.cognitive-reinforcement-for-retention",
    "switching-costs.adoption-friction-incumbent-loyalty-map",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr57_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr57_compiled_v19_is_v18_plus_four_targeted_affordances() -> None:
    affordances_v18 = _load_compiled(AFFORDANCES_V18_PATH)
    affordances_v19 = _load_compiled(AFFORDANCES_V19_PATH)

    v18_model_ids = _model_ids(affordances_v18)
    v19_model_ids = _model_ids(affordances_v19)
    v18_affordance_ids = _affordance_ids(affordances_v18)
    v19_affordance_ids = _affordance_ids(affordances_v19)

    assert affordances_v19["artifact"] == "model_affordances_v19"
    assert affordances_v19["status"] == "draft_review_only"
    assert v19_model_ids == v18_model_ids
    assert len(v19_model_ids) == 222
    assert TARGET_AFFORDANCE_IDS.isdisjoint(v18_affordance_ids)
    assert TARGET_AFFORDANCE_IDS.issubset(v19_affordance_ids)
    assert v19_affordance_ids - v18_affordance_ids == TARGET_AFFORDANCE_IDS

    v18_metadata = affordances_v18["compile_metadata"]
    v19_metadata = affordances_v19["compile_metadata"]
    assert v19_metadata["contributing_record_count"] == 222
    assert v19_metadata["affordance_count"] == v18_metadata["affordance_count"] + 4
    assert v19_metadata["affordance_count"] == 262
    assert v19_metadata["absence_record_count"] == v18_metadata["absence_record_count"]
    assert v19_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v19_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr57_split_boundaries_are_not_simple_bloat() -> None:
    commitment = _load_record("commitment-bias")
    recommitment = _affordance(commitment, "commitment-bias.recommitment-stop-rule-review")
    constructive = _affordance(
        commitment, "commitment-bias.constructive-commitment-architecture"
    )
    assert "under-follow-through or over-escalation" not in json.dumps(recommitment)
    assert _contains(constructive["activation_shape"]["use_when"], "weak follow-through")
    assert _contains(
        constructive["activation_shape"]["do_not_use_when"],
        "use the stop-rule review affordance instead",
    )

    redundancy = _load_record("redundancy")
    failover = _affordance(redundancy, "redundancy.single-point-failure-backup-test")
    cognitive = _affordance(
        redundancy, "redundancy.cognitive-reinforcement-for-retention"
    )
    assert "memory, viewpoint" not in json.dumps(failover)
    assert _contains(failover["activation_shape"]["use_when"], "recovery")
    assert _contains(cognitive["activation_shape"]["do_not_use_when"], "cognitive load")

    switching_costs = _load_record("switching-costs")
    adoption = _affordance(
        switching_costs, "switching-costs.adoption-friction-incumbent-loyalty-map"
    )
    assert _contains(adoption["activation_shape"]["use_when"], "adoption lag")
    assert _contains(adoption["misuse_guards"], "fear, uncertainty, or doubt")

    feedback_loops = _load_record("feedback-loops")
    polarity = _affordance(feedback_loops, "feedback-loops.loop-polarity-intervention-map")
    assert _contains(polarity["activation_shape"]["use_when"], "output feeds back into input")
    assert _contains(polarity["misuse_guards"], "delays and nonlinear effects")


def test_pr57_v19_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v19", "model_affordances_v19")

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
