from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterable


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = REPO_ROOT / "data" / "model_affordances" / "batch_17"
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
SOURCE_MANIFEST_PATH = SOURCE_DIR / "manifest.json"
AFFORDANCES_V17_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v17.json"
)
AFFORDANCES_V18_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v18.json"
)

APPROVED_BATCH_MODEL_IDS = {
    "agile-methodologies",
    "causal-attribution-resistance",
    "chain-of-thought",
    "circle-of-competence",
    "complexity-bias-resistance",
    "endowment-effect",
    "latticework-of-mental-models",
    "logical-fallacies",
    "mental-models-of-reality",
    "meta-cognitive-reflection",
    "perceptual-learning",
    "scaffolding-educational",
    "system-1",
    "system-2",
    "tier-2-high-value",
    "time-tested-validation",
}

EXPECTED_ABSENCE_FIELDS = {
    "agile-without-feedback-loop",
    "analysis-without-cost-or-trigger",
    "attribution-without-observed-mechanism",
    "blame-label-as-cause",
    "ceremony-as-agility",
    "chain-of-thought-as-truth",
    "circle-of-competence-as-permanent-boundary",
    "competence-claim-without-edge-evidence",
    "complexity-bias-as-simplicity-worship",
    "endowment-as-ownership-label",
    "fallacy-label-as-argument",
    "fallacy-spotting-without-premise-check",
    "high-value-without-case-fit",
    "intuition-without-context",
    "latticework-as-model-name-dropping",
    "map-without-feedback",
    "metacognition-as-rumination",
    "perception-as-objective-proof",
    "perceptual-learning-without-feedback",
    "reality-model-as-reality",
    "reasoning-transcript-without-verification",
    "reflection-without-action-loop",
    "scaffolding-as-handholding",
    "scaffolding-without-fading",
    "simple-answer-as-proof",
    "single-model-certainty",
    "system-1-as-bad-thinking",
    "system-2-as-automatic-correctness",
    "tier-2-as-quality-rank",
    "time-tested-as-proof",
    "tradition-without-current-fit",
    "unearned-endowment-premium",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr54_batch17_records_exist_for_approved_models_only() -> None:
    paths = sorted(BATCH_DIR.glob("*.json"))

    assert {path.stem for path in paths} == APPROVED_BATCH_MODEL_IDS


def test_pr54_batch17_records_validate_against_schema_and_sources() -> None:
    for model_id in sorted(APPROVED_BATCH_MODEL_IDS):
        validate_model_affordance_file(
            BATCH_DIR / f"{model_id}.json",
            source_roots=(SOURCE_DIR,),
        )


def test_pr54_batch17_records_match_source_manifest() -> None:
    manifest = json.loads(SOURCE_MANIFEST_PATH.read_text(encoding="utf-8"))
    source_by_model = {str(entry["model_id"]): entry for entry in manifest["files"]}

    for model_id in sorted(APPROVED_BATCH_MODEL_IDS):
        record = _load_record(model_id)
        source_entry = source_by_model[model_id]
        assert record["model_id"] == model_id
        assert record["source_file"] == source_entry["filename"]
        assert (SOURCE_DIR / str(record["source_file"])).exists()


def test_pr54_batch17_source_quotes_are_repo_custodied_exact_substrings() -> None:
    for model_id in sorted(APPROVED_BATCH_MODEL_IDS):
        record = _load_record(model_id)
        source_file = SOURCE_DIR / str(record["source_file"])
        source_text = source_file.read_text(encoding="utf-8")

        evidence_items = list(_iter_source_evidence(record))
        assert evidence_items
        for evidence in evidence_items:
            assert evidence["source_file"] == record["source_file"]
            assert str(evidence["source_quote"]) in source_text


def test_pr54_batch17_records_are_compact_and_absence_first() -> None:
    for model_id in sorted(APPROVED_BATCH_MODEL_IDS):
        record = _load_record(model_id)
        affordances = record["affordances"]
        absences = record["absence_records"]

        assert record["status"] in {"supported", "weak_support", "source_too_thin"}
        assert len(affordances) == 1
        assert len(absences) == 2
        assert affordances[0]["confidence"] in {"high", "medium", "weak"}
        assert all(absence["runtime_policy"] == "do_not_promote" for absence in absences)


def test_pr54_batch17_blocks_final_set_theater() -> None:
    absence_fields = {
        absence["attempted_field"]
        for model_id in APPROVED_BATCH_MODEL_IDS
        for absence in _load_record(model_id)["absence_records"]
    }

    assert absence_fields == EXPECTED_ABSENCE_FIELDS


def test_pr54_batch17_models_were_graph_only_before_this_batch() -> None:
    affordances_v17 = _load_compiled(AFFORDANCES_V17_PATH)

    assert _model_ids(affordances_v17).isdisjoint(APPROVED_BATCH_MODEL_IDS)


def test_pr54_compiled_v18_includes_all_runtime_models_and_remains_dormant() -> None:
    affordances_v17 = _load_compiled(AFFORDANCES_V17_PATH)
    affordances_v18 = _load_compiled(AFFORDANCES_V18_PATH)
    v17_model_ids = _model_ids(affordances_v17)
    v18_model_ids = _model_ids(affordances_v18)

    assert affordances_v18["artifact"] == "model_affordances_v18"
    assert affordances_v18["status"] == "draft_review_only"
    assert v17_model_ids.issubset(v18_model_ids)
    assert APPROVED_BATCH_MODEL_IDS.issubset(v18_model_ids)
    assert len(v18_model_ids) == 222
    assert len(v18_model_ids) == len(v17_model_ids) + len(APPROVED_BATCH_MODEL_IDS)

    metadata = affordances_v18["compile_metadata"]
    assert metadata["contributing_record_count"] == 222
    assert metadata["affordance_count"] == 258
    assert metadata["absence_record_count"] == 429
    assert metadata["validation"]["schema_validation_failure_count"] == 0
    assert metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr54_v18_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v18", "model_affordances_v18")

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
