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
AFFORDANCES_V19_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v19.json"
)
AFFORDANCES_V20_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v20.json"
)

TARGET_RECORD_PATHS = {
    "lock-in": MODEL_AFFORDANCE_DIR / "batch_5" / "lock-in.json",
    "mental-simulation": MODEL_AFFORDANCE_DIR
    / "batch_11"
    / "mental-simulation.json",
    "path-dependence": MODEL_AFFORDANCE_DIR / "batch_5" / "path-dependence.json",
    "power-dynamics": MODEL_AFFORDANCE_DIR / "pilot" / "power-dynamics.json",
}

TARGET_AFFORDANCE_IDS = {
    "lock-in.productive-standardization-commitment",
    "mental-simulation.skill-rehearsal-response-prep",
    "path-dependence.old-behavior-reproduction-map",
    "power-dynamics.weakest-link-constraint-map",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr58_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr58_compiled_v20_is_v19_plus_four_targeted_affordances() -> None:
    affordances_v19 = _load_compiled(AFFORDANCES_V19_PATH)
    affordances_v20 = _load_compiled(AFFORDANCES_V20_PATH)

    v19_model_ids = _model_ids(affordances_v19)
    v20_model_ids = _model_ids(affordances_v20)
    v19_affordance_ids = _affordance_ids(affordances_v19)
    v20_affordance_ids = _affordance_ids(affordances_v20)

    assert affordances_v20["artifact"] == "model_affordances_v20"
    assert affordances_v20["status"] == "draft_review_only"
    assert v20_model_ids == v19_model_ids
    assert len(v20_model_ids) == 222
    assert TARGET_AFFORDANCE_IDS.isdisjoint(v19_affordance_ids)
    assert TARGET_AFFORDANCE_IDS.issubset(v20_affordance_ids)
    assert v20_affordance_ids - v19_affordance_ids == TARGET_AFFORDANCE_IDS

    v19_metadata = affordances_v19["compile_metadata"]
    v20_metadata = affordances_v20["compile_metadata"]
    assert v20_metadata["contributing_record_count"] == 222
    assert v20_metadata["affordance_count"] == v19_metadata["affordance_count"] + 4
    assert v20_metadata["affordance_count"] == 266
    assert v20_metadata["absence_record_count"] == v19_metadata["absence_record_count"]
    assert v20_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v20_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr58_split_boundaries_remain_transaction_specific() -> None:
    lock_in = _load_record("lock-in")
    productive = _affordance(lock_in, "lock-in.productive-standardization-commitment")
    assert _contains(productive["activation_shape"]["use_when"], "coordination cost")
    assert _contains(productive["activation_shape"]["do_not_use_when"], "reversal cost")
    assert _contains(productive["misuse_guards"], "make everything sticky")

    mental_simulation = _load_record("mental-simulation")
    rehearsal = _affordance(
        mental_simulation, "mental-simulation.skill-rehearsal-response-prep"
    )
    assert _contains(rehearsal["activation_shape"]["use_when"], "high-stakes conversation")
    assert _contains(rehearsal["activation_shape"]["do_not_use_when"], "strategic futures")
    assert _contains(rehearsal["misuse_guards"], "rehearsal as evidence")

    power_dynamics = _load_record("power-dynamics")
    weakest_link = _affordance(
        power_dynamics, "power-dynamics.weakest-link-constraint-map"
    )
    assert _contains(weakest_link["activation_shape"]["use_when"], "multi-party")
    assert _contains(weakest_link["activation_shape"]["do_not_use_when"], "bilateral")
    assert _contains(weakest_link["misuse_guards"], "loudest actor")

    path_dependence = _load_record("path-dependence")
    old_behavior = _affordance(
        path_dependence, "path-dependence.old-behavior-reproduction-map"
    )
    assert _contains(old_behavior["activation_shape"]["use_when"], "despite updated goals")
    assert _contains(old_behavior["activation_shape"]["do_not_use_when"], "migration")
    assert _contains(old_behavior["misuse_guards"], "history into destiny")


def test_pr58_v20_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v20", "model_affordances_v20")

    for path in LIVE_RUNTIME_PATHS:
        text = path.read_text(encoding="utf-8")
        assert all(fragment not in text for fragment in forbidden)


def test_pr58_rejects_category_synthesis_duplicate_affordance() -> None:
    category_decisions = _load_compiled(AFFORDANCES_V20_PATH)
    assert (
        "category-decisions.grouping-to-synthesis-insight"
        not in _affordance_ids(category_decisions)
    )


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
