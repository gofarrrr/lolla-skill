from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterable


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = REPO_ROOT / "data" / "model_affordances" / "batch_13"
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
SOURCE_MANIFEST_PATH = SOURCE_DIR / "manifest.json"
AFFORDANCES_V13_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v13.json"
)
AFFORDANCES_V14_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v14.json"
)

APPROVED_BATCH_MODEL_IDS = {
    "bayesian",
    "compounding",
    "conjunction-fallacy",
    "data-science-reasoning-framework",
    "information-theory",
    "markov-chains",
    "monte-carlo-methods",
    "power-laws",
    "regression-to-the-mean",
    "representativeness-heuristic",
    "statistical-learning-theory",
    "statistics-concepts",
}

EXPECTED_ABSENCE_FIELDS = {
    "bayesian-as-certainty-machine",
    "prior-without-update-evidence",
    "growth-rate-as-guarantee",
    "compounding-without-time-horizon",
    "disjunctive-failure-risk-as-conjunctive-sequence",
    "expert-confidence-as-cumulative-risk-proof",
    "specific-story-as-probability-proof",
    "detail-rich-conjunction-as-more-likely",
    "data-science-as-algorithmic-authority",
    "model-output-without-question-design",
    "information-as-volume",
    "signal-without-decoding-context",
    "markov-memorylessness-overclaim",
    "state-model-without-transition-evidence",
    "simulation-as-forecast-certainty",
    "randomness-without-assumption-check",
    "power-law-as-universal-explanation",
    "average-as-tail-safe",
    "single-outcome-as-trend-proof",
    "regression-as-dismissal",
    "prototype-as-population",
    "similarity-as-base-rate-substitute",
    "statistical-learning-as-black-box-certainty",
    "training-fit-as-world-fit",
    "statistical-term-as-evidence",
    "number-without-sample-context",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)

APPROVED_EXTRA_ABSENCE_COUNTS = {
    "conjunction-fallacy": 4,
}


def test_pr50_batch13_records_exist_for_approved_models_only() -> None:
    paths = sorted(BATCH_DIR.glob("*.json"))

    assert {path.stem for path in paths} == APPROVED_BATCH_MODEL_IDS


def test_pr50_batch13_records_validate_against_schema_and_sources() -> None:
    for model_id in sorted(APPROVED_BATCH_MODEL_IDS):
        validate_model_affordance_file(
            BATCH_DIR / f"{model_id}.json",
            source_roots=(SOURCE_DIR,),
        )


def test_pr50_batch13_records_match_source_manifest() -> None:
    manifest = json.loads(SOURCE_MANIFEST_PATH.read_text(encoding="utf-8"))
    source_by_model = {str(entry["model_id"]): entry for entry in manifest["files"]}

    for model_id in sorted(APPROVED_BATCH_MODEL_IDS):
        record = _load_record(model_id)
        source_entry = source_by_model[model_id]
        assert record["model_id"] == model_id
        assert record["source_file"] == source_entry["filename"]
        assert (SOURCE_DIR / str(record["source_file"])).exists()


def test_pr50_batch13_source_quotes_are_repo_custodied_exact_substrings() -> None:
    for model_id in sorted(APPROVED_BATCH_MODEL_IDS):
        record = _load_record(model_id)
        source_file = SOURCE_DIR / str(record["source_file"])
        source_text = source_file.read_text(encoding="utf-8")

        evidence_items = list(_iter_source_evidence(record))
        assert evidence_items
        for evidence in evidence_items:
            assert evidence["source_file"] == record["source_file"]
            assert str(evidence["source_quote"]) in source_text


def test_pr50_batch13_records_are_compact_and_absence_first() -> None:
    for model_id in sorted(APPROVED_BATCH_MODEL_IDS):
        record = _load_record(model_id)
        affordances = record["affordances"]
        absences = record["absence_records"]

        assert record["status"] in {"supported", "weak_support"}
        assert len(affordances) == 1
        expected_absence_count = APPROVED_EXTRA_ABSENCE_COUNTS.get(model_id, 2)
        assert len(absences) == expected_absence_count
        assert affordances[0]["confidence"] in {"high", "medium"}
        assert all(absence["runtime_policy"] == "do_not_promote" for absence in absences)


def test_pr50_batch13_blocks_quantitative_theater() -> None:
    absence_fields = {
        absence["attempted_field"]
        for model_id in APPROVED_BATCH_MODEL_IDS
        for absence in _load_record(model_id)["absence_records"]
    }

    assert EXPECTED_ABSENCE_FIELDS.issubset(absence_fields)


def test_pr50_batch13_models_were_graph_only_before_this_batch() -> None:
    affordances_v13 = _load_compiled(AFFORDANCES_V13_PATH)

    assert _model_ids(affordances_v13).isdisjoint(APPROVED_BATCH_MODEL_IDS)


def test_pr50_compiled_v14_includes_v13_plus_batch13_and_remains_dormant() -> None:
    affordances_v13 = _load_compiled(AFFORDANCES_V13_PATH)
    affordances_v14 = _load_compiled(AFFORDANCES_V14_PATH)
    v13_model_ids = _model_ids(affordances_v13)
    v14_model_ids = _model_ids(affordances_v14)

    assert affordances_v14["artifact"] == "model_affordances_v14"
    assert affordances_v14["status"] == "draft_review_only"
    assert v13_model_ids.issubset(v14_model_ids)
    assert APPROVED_BATCH_MODEL_IDS.issubset(v14_model_ids)
    assert len(v14_model_ids) == len(v13_model_ids) + len(APPROVED_BATCH_MODEL_IDS)

    metadata = affordances_v14["compile_metadata"]
    assert metadata["contributing_record_count"] == 170
    assert metadata["affordance_count"] == 206
    assert metadata["absence_record_count"] == 325
    assert metadata["validation"]["schema_validation_failure_count"] == 0
    assert metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr50_v14_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v14", "model_affordances_v14")

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
