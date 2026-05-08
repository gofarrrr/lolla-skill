from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterable


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = REPO_ROOT / "data" / "model_affordances" / "batch_6"
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
SOURCE_MANIFEST_PATH = SOURCE_DIR / "manifest.json"
AFFORDANCES_V6_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v6.json"
)
AFFORDANCES_V7_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v7.json"
)

APPROVED_BATCH_MODEL_IDS = {
    "active-listening",
    "analogies-and-metaphors",
    "constructive-feedback-models",
    "feedback-models-sbi",
    "nash-equilibrium",
    "natural-selection-analogy",
    "prisoners-dilemma",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr34_batch6_records_exist_for_approved_models_only() -> None:
    paths = sorted(BATCH_DIR.glob("*.json"))

    assert {path.stem for path in paths} == APPROVED_BATCH_MODEL_IDS


def test_pr34_batch6_records_validate_against_schema_and_sources() -> None:
    for model_id in sorted(APPROVED_BATCH_MODEL_IDS):
        validate_model_affordance_file(
            BATCH_DIR / f"{model_id}.json",
            source_roots=(SOURCE_DIR,),
        )


def test_pr34_batch6_records_match_source_manifest() -> None:
    manifest = json.loads(SOURCE_MANIFEST_PATH.read_text(encoding="utf-8"))
    source_by_model = {str(entry["model_id"]): entry for entry in manifest["files"]}

    for model_id in sorted(APPROVED_BATCH_MODEL_IDS):
        record = _load_record(model_id)
        source_entry = source_by_model[model_id]
        assert record["model_id"] == model_id
        assert record["source_file"] == source_entry["filename"]
        assert (SOURCE_DIR / str(record["source_file"])).exists()


def test_pr34_batch6_source_quotes_are_repo_custodied_exact_substrings() -> None:
    for model_id in sorted(APPROVED_BATCH_MODEL_IDS):
        record = _load_record(model_id)
        source_file = SOURCE_DIR / str(record["source_file"])
        source_text = source_file.read_text(encoding="utf-8")

        evidence_items = list(_iter_source_evidence(record))
        assert evidence_items
        for evidence in evidence_items:
            assert evidence["source_file"] == record["source_file"]
            assert str(evidence["source_quote"]) in source_text


def test_pr34_batch6_keeps_absence_records_first_class() -> None:
    absence_counts = {
        model_id: len(_load_record(model_id)["absence_records"])
        for model_id in APPROVED_BATCH_MODEL_IDS
    }

    assert all(count >= 1 for count in absence_counts.values())
    assert sum(absence_counts.values()) >= len(APPROVED_BATCH_MODEL_IDS)


def test_pr34_batch6_models_were_graph_only_before_this_batch() -> None:
    affordances_v6 = _load_compiled(AFFORDANCES_V6_PATH)

    assert _model_ids(affordances_v6).isdisjoint(APPROVED_BATCH_MODEL_IDS)


def test_pr34_compiled_v7_includes_v6_plus_batch6_and_remains_dormant() -> None:
    affordances_v6 = _load_compiled(AFFORDANCES_V6_PATH)
    affordances_v7 = _load_compiled(AFFORDANCES_V7_PATH)
    v6_model_ids = _model_ids(affordances_v6)
    v7_model_ids = _model_ids(affordances_v7)

    assert affordances_v7["artifact"] == "model_affordances_v7"
    assert affordances_v7["status"] == "draft_review_only"
    assert v6_model_ids.issubset(v7_model_ids)
    assert APPROVED_BATCH_MODEL_IDS.issubset(v7_model_ids)
    assert len(v7_model_ids) == len(v6_model_ids) + len(APPROVED_BATCH_MODEL_IDS)

    metadata = affordances_v7["compile_metadata"]
    assert metadata["contributing_record_count"] == 88
    assert metadata["affordance_count"] == 124
    assert metadata["absence_record_count"] == 161
    assert metadata["validation"]["schema_validation_failure_count"] == 0
    assert metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr34_v7_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v7", "model_affordances_v7")

    for path in LIVE_RUNTIME_PATHS:
        text = path.read_text(encoding="utf-8")
        assert all(fragment not in text for fragment in forbidden)


def _load_record(model_id: str) -> dict[str, object]:
    return json.loads((BATCH_DIR / f"{model_id}.json").read_text(encoding="utf-8"))


def _load_compiled(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _model_ids(compiled: dict[str, object]) -> set[str]:
    return {
        str(record["model_id"])
        for record in compiled.get("model_records", [])
        if isinstance(record, dict)
    }


def _iter_source_evidence(payload: object) -> Iterable[dict[str, object]]:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key == "source_evidence" and isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        yield item
            else:
                yield from _iter_source_evidence(value)
    elif isinstance(payload, list):
        for item in payload:
            yield from _iter_source_evidence(item)
