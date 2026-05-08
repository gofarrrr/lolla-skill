from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = REPO_ROOT / "data" / "model_affordances" / "batch_1"
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"

APPROVED_BATCH_STRATA = {
    "high_confidence_practical": {
        "anchoring",
        "expected-value",
        "decomposition",
        "decision-trees",
        "sunk-cost-fallacy",
    },
    "broad_overlay": {
        "complex-adaptive-systems",
        "emergence",
        "leverage-points",
        "network-effects",
        "multi-criteria-decision-analysis",
    },
    "thin_abstract": {
        "circle-of-control",
        "lindy-effect",
        "johari-window",
        "occams-razor",
        "flow",
    },
    "lane4_frequent": {
        "calculated-risk-taking",
        "risk-assessment",
        "incentives",
        "trade-offs",
        "information-asymmetry",
    },
}
APPROVED_BATCH_MODEL_IDS = set().union(*APPROVED_BATCH_STRATA.values())


def _load_record(model_id: str) -> dict[str, object]:
    return json.loads((BATCH_DIR / f"{model_id}.json").read_text(encoding="utf-8"))


def test_pr7_batch_records_exist_for_approved_models_only() -> None:
    paths = sorted(BATCH_DIR.glob("*.json"))
    assert {path.stem for path in paths} == APPROVED_BATCH_MODEL_IDS


def test_pr7_batch_records_validate_against_schema_and_sources() -> None:
    for model_id in sorted(APPROVED_BATCH_MODEL_IDS):
        validate_model_affordance_file(
            BATCH_DIR / f"{model_id}.json",
            source_roots=(SOURCE_DIR,),
        )


def test_pr7_batch_records_match_source_manifest() -> None:
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


def test_pr7_batch_keeps_absence_records_first_class() -> None:
    absence_models = {
        model_id
        for model_id in APPROVED_BATCH_MODEL_IDS
        if _load_record(model_id)["absence_records"]
    }
    assert absence_models


def test_pr7_batch_flags_thin_abstract_overproduction_for_review() -> None:
    overproduced = []
    for model_id in sorted(APPROVED_BATCH_STRATA["thin_abstract"]):
        record = _load_record(model_id)
        if len(record["affordances"]) >= 3:
            overproduced.append(model_id)

    assert overproduced == []
