from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterable


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = REPO_ROOT / "data" / "model_affordances" / "batch_12"
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
SOURCE_MANIFEST_PATH = SOURCE_DIR / "manifest.json"
AFFORDANCES_V12_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v12.json"
)
AFFORDANCES_V13_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v13.json"
)

APPROVED_BATCH_MODEL_IDS = {
    "blooms-taxonomy",
    "cognitive-load-theory",
    "deliberate-practice",
    "desirable-difficulties",
    "expertise-reversal-effect",
    "feynman-technique",
    "generation-effect",
    "learning-curve",
    "scaffolding",
    "schema-acquisition",
    "varied-practice-interleaving",
    "zone-of-development",
}

EXPECTED_ABSENCE_FIELDS = {
    "classification-as-learning",
    "taxonomy-as-lesson-plan",
    "load-reduction-as-over-simplification",
    "generic-load-label-without-diagnosis",
    "repetition-without-feedback",
    "talent-story-substitute",
    "difficulty-as-virtue",
    "unwanted-difficulty-as-rigor",
    "novice-expert-treatment-collapse",
    "expertise-label-as-status",
    "explanation-fluency-as-understanding",
    "simple-explanation-as-complete-answer",
    "generation-as-guessing",
    "retrieval-without-feedback",
    "curve-as-destiny",
    "progress-without-measurement",
    "permanent-support",
    "support-without-fade-plan",
    "schema-as-label",
    "premature-abstraction",
    "interleaving-as-randomness",
    "variety-without-comparison",
    "comfort-zone-as-growth",
    "challenge-without-support",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr49_batch12_records_exist_for_approved_models_only() -> None:
    paths = sorted(BATCH_DIR.glob("*.json"))

    assert {path.stem for path in paths} == APPROVED_BATCH_MODEL_IDS


def test_pr49_batch12_records_validate_against_schema_and_sources() -> None:
    for model_id in sorted(APPROVED_BATCH_MODEL_IDS):
        validate_model_affordance_file(
            BATCH_DIR / f"{model_id}.json",
            source_roots=(SOURCE_DIR,),
        )


def test_pr49_batch12_records_match_source_manifest() -> None:
    manifest = json.loads(SOURCE_MANIFEST_PATH.read_text(encoding="utf-8"))
    source_by_model = {str(entry["model_id"]): entry for entry in manifest["files"]}

    for model_id in sorted(APPROVED_BATCH_MODEL_IDS):
        record = _load_record(model_id)
        source_entry = source_by_model[model_id]
        assert record["model_id"] == model_id
        assert record["source_file"] == source_entry["filename"]
        assert (SOURCE_DIR / str(record["source_file"])).exists()


def test_pr49_batch12_source_quotes_are_repo_custodied_exact_substrings() -> None:
    for model_id in sorted(APPROVED_BATCH_MODEL_IDS):
        record = _load_record(model_id)
        source_file = SOURCE_DIR / str(record["source_file"])
        source_text = source_file.read_text(encoding="utf-8")

        evidence_items = list(_iter_source_evidence(record))
        assert evidence_items
        for evidence in evidence_items:
            assert evidence["source_file"] == record["source_file"]
            assert str(evidence["source_quote"]) in source_text


def test_pr49_batch12_records_are_compact_and_absence_first() -> None:
    for model_id in sorted(APPROVED_BATCH_MODEL_IDS):
        record = _load_record(model_id)
        affordances = record["affordances"]
        absences = record["absence_records"]

        assert record["status"] == "supported"
        assert len(affordances) == 1
        assert len(absences) == 2
        assert affordances[0]["confidence"] in {"high", "medium"}
        assert all(absence["runtime_policy"] == "do_not_promote" for absence in absences)


def test_pr49_batch12_blocks_learning_theater() -> None:
    absence_fields = {
        absence["attempted_field"]
        for model_id in APPROVED_BATCH_MODEL_IDS
        for absence in _load_record(model_id)["absence_records"]
    }

    assert EXPECTED_ABSENCE_FIELDS.issubset(absence_fields)


def test_pr49_batch12_models_were_graph_only_before_this_batch() -> None:
    affordances_v12 = _load_compiled(AFFORDANCES_V12_PATH)

    assert _model_ids(affordances_v12).isdisjoint(APPROVED_BATCH_MODEL_IDS)


def test_pr49_compiled_v13_includes_v12_plus_batch12_and_remains_dormant() -> None:
    affordances_v12 = _load_compiled(AFFORDANCES_V12_PATH)
    affordances_v13 = _load_compiled(AFFORDANCES_V13_PATH)
    v12_model_ids = _model_ids(affordances_v12)
    v13_model_ids = _model_ids(affordances_v13)

    assert affordances_v13["artifact"] == "model_affordances_v13"
    assert affordances_v13["status"] == "draft_review_only"
    assert v12_model_ids.issubset(v13_model_ids)
    assert APPROVED_BATCH_MODEL_IDS.issubset(v13_model_ids)
    assert len(v13_model_ids) == len(v12_model_ids) + len(APPROVED_BATCH_MODEL_IDS)

    metadata = affordances_v13["compile_metadata"]
    assert metadata["contributing_record_count"] == 158
    assert metadata["affordance_count"] == 194
    assert metadata["absence_record_count"] == 301
    assert metadata["validation"]["schema_validation_failure_count"] == 0
    assert metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr49_v13_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v13", "model_affordances_v13")

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
