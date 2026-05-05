from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = REPO_ROOT / "data" / "model_affordances" / "batch_2"
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"

APPROVED_BATCH_MODEL_IDS = {
    "antifragility",
    "black-swan-events",
    "resilience",
    "adverse-selection",
    "margin-of-safety",
    "moral-hazard",
    "six-thinking-hats",
    "social-proof",
    "empathy",
    "psychological-safety",
    "comparative-advantage",
    "optimization-theory",
    "pareto-principle",
    "prioritization",
    "aleatory-epistemic-uncertainty-recognition",
    "correlation-vs-causation",
    "experimentation",
    "law-of-large-numbers",
    "statistical-discipline",
    "survivorship-bias",
}


def _load_record(model_id: str) -> dict[str, object]:
    return json.loads((BATCH_DIR / f"{model_id}.json").read_text(encoding="utf-8"))


def test_pr9_batch2_records_exist_for_approved_models_only() -> None:
    paths = sorted(BATCH_DIR.glob("*.json"))
    assert {path.stem for path in paths} == APPROVED_BATCH_MODEL_IDS


def test_pr9_batch2_records_validate_against_schema_and_sources() -> None:
    for model_id in sorted(APPROVED_BATCH_MODEL_IDS):
        validate_model_affordance_file(
            BATCH_DIR / f"{model_id}.json",
            source_roots=(SOURCE_DIR,),
        )


def test_pr9_batch2_records_match_source_manifest() -> None:
    manifest = json.loads((SOURCE_DIR / "manifest.json").read_text(encoding="utf-8"))
    source_by_model = {
        str(entry["model_id"]): entry for entry in manifest["files"]
    }

    for model_id in sorted(APPROVED_BATCH_MODEL_IDS):
        record = _load_record(model_id)
        source_entry = source_by_model[model_id]
        assert record["model_id"] == model_id
        assert record["source_file"] == source_entry["filename"]
        assert (SOURCE_DIR / str(record["source_file"])).exists()


def test_pr9_batch2_keeps_absence_records_first_class() -> None:
    absence_models = {
        model_id
        for model_id in APPROVED_BATCH_MODEL_IDS
        if _load_record(model_id)["absence_records"]
    }
    assert absence_models


def test_pr9_batch2_three_affordance_records_name_differentiation_test() -> None:
    missing = []
    for model_id in sorted(APPROVED_BATCH_MODEL_IDS):
        record = _load_record(model_id)
        if len(record["affordances"]) < 3:
            continue
        notes = json.dumps(record.get("review_notes", {})).lower()
        if "differentiation" not in notes and "merge" not in notes:
            missing.append(model_id)

    assert missing == []
