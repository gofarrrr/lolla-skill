from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = REPO_ROOT / "data" / "model_affordances" / "batch_3a"
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"

APPROVED_BATCH_MODEL_IDS = {
    "opportunity-cost",
    "true-uncertainty-navigation",
    "falsifiability",
    "principal-agent-problem",
    "probabilistic-thinking",
}


def _load_record(model_id: str) -> dict[str, object]:
    return json.loads((BATCH_DIR / f"{model_id}.json").read_text(encoding="utf-8"))


def test_pr16_batch3a_records_exist_for_approved_models_only() -> None:
    paths = sorted(BATCH_DIR.glob("*.json"))
    assert {path.stem for path in paths} == APPROVED_BATCH_MODEL_IDS


def test_pr16_batch3a_records_validate_against_schema_and_sources() -> None:
    for model_id in sorted(APPROVED_BATCH_MODEL_IDS):
        validate_model_affordance_file(
            BATCH_DIR / f"{model_id}.json",
            source_roots=(SOURCE_DIR,),
        )


def test_pr16_batch3a_records_match_source_manifest() -> None:
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


def test_pr16_batch3a_keeps_targeted_patch_small() -> None:
    for model_id in sorted(APPROVED_BATCH_MODEL_IDS):
        record = _load_record(model_id)
        assert len(record["affordances"]) == 1
        assert record["absence_records"]


def test_pr16_batch3a_principal_agent_preserves_honesty_signal() -> None:
    record = _load_record("principal-agent-problem")
    affordance = record["affordances"][0]
    assert affordance["confidence"] == "medium"
    notes = json.dumps(record["review_notes"]).lower()
    assert "thin_narrow_affordance_record" in notes
    assert "medium" in notes
