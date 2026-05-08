from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V52_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v52.json"
)
AFFORDANCES_V53_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v53.json"
)

TARGET_RECORD_PATHS = {
    "base-rates": MODEL_AFFORDANCE_DIR / "pilot" / "base-rates.json",
    "conjunction-fallacy": MODEL_AFFORDANCE_DIR
    / "batch_13"
    / "conjunction-fallacy.json",
    "hindsight-bias": MODEL_AFFORDANCE_DIR / "batch_14" / "hindsight-bias.json",
    "regression-to-the-mean": MODEL_AFFORDANCE_DIR
    / "batch_13"
    / "regression-to-the-mean.json",
    "representativeness-heuristic": MODEL_AFFORDANCE_DIR
    / "batch_13"
    / "representativeness-heuristic.json",
    "wysiati": MODEL_AFFORDANCE_DIR / "batch_10" / "wysiati.json",
}

NEW_ABSENCE_FIELDS = {
    "demographic-stereotype-as-behavioral-proof",
    "generic-missing-information-boilerplate",
    "invented-step-probabilities-as-rigor",
    "mean-reversion-as-tail-risk-dismissal",
    "single-optimistic-base-case-as-base-rate",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr91_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr91_compiled_v53_is_absence_only_delta() -> None:
    affordances_v52 = _load_compiled(AFFORDANCES_V52_PATH)
    affordances_v53 = _load_compiled(AFFORDANCES_V53_PATH)

    assert affordances_v53["artifact"] == "model_affordances_v53"
    assert affordances_v53["status"] == "draft_review_only"
    assert _model_ids(affordances_v53) == _model_ids(affordances_v52)
    assert len(_model_ids(affordances_v53)) == 222

    assert _affordance_ids(affordances_v53) == _affordance_ids(affordances_v52)
    assert NEW_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v52))
    assert _absence_fields(affordances_v53) - _absence_fields(affordances_v52) == (
        NEW_ABSENCE_FIELDS
    )

    v52_metadata = affordances_v52["compile_metadata"]
    v53_metadata = affordances_v53["compile_metadata"]
    assert v53_metadata["contributing_record_count"] == 222
    assert v53_metadata["affordance_count"] == v52_metadata["affordance_count"]
    assert v53_metadata["affordance_count"] == 298
    assert (
        v53_metadata["absence_record_count"]
        == v52_metadata["absence_record_count"] + 5
    )
    assert v53_metadata["absence_record_count"] == 583
    assert v53_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v53_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr91_probability_bias_ring_remains_compressed_after_full_reread() -> None:
    affordances_v52 = _load_compiled(AFFORDANCES_V52_PATH)
    affordances_v53 = _load_compiled(AFFORDANCES_V53_PATH)

    v52_counts = _affordance_counts_by_model(affordances_v52)
    v53_counts = _affordance_counts_by_model(affordances_v53)

    for model_id in TARGET_RECORD_PATHS:
        assert v53_counts[model_id] == v52_counts[model_id]
        assert v53_counts[model_id] == 1


def test_pr91_absence_rails_block_probability_bias_misuse_without_bloat() -> None:
    representativeness = _load_record("representativeness-heuristic")
    demographic_guard = _absence_by_field(
        representativeness,
        "demographic-stereotype-as-behavioral-proof",
    )
    assert demographic_guard["runtime_policy"] == "do_not_promote"
    assert "focusing *only* on demographics can lead to **stereotyping**" in str(
        demographic_guard["source_evidence"]
    )

    base_rates = _load_record("base-rates")
    base_case_guard = _absence_by_field(
        base_rates,
        "single-optimistic-base-case-as-base-rate",
    )
    assert base_case_guard["status"] == "not_supported_by_source"
    assert "single optimistic base case" in str(base_case_guard["source_evidence"])

    conjunction = _load_record("conjunction-fallacy")
    fake_probability_guard = _absence_by_field(
        conjunction,
        "invented-step-probabilities-as-rigor",
    )
    assert fake_probability_guard["runtime_policy"] == "do_not_promote"
    assert "probability logic becomes pseudo-precision" in str(
        fake_probability_guard["source_evidence"]
    )

    wysiati = _load_record("wysiati")
    boilerplate_guard = _absence_by_field(
        wysiati,
        "generic-missing-information-boilerplate",
    )
    assert "three most important pieces of evidence that are absent" in str(
        boilerplate_guard["source_evidence"]
    )

    regression = _load_record("regression-to-the-mean")
    tail_guard = _absence_by_field(
        regression,
        "mean-reversion-as-tail-risk-dismissal",
    )
    assert "one or two standard deviations from the mean" in str(
        tail_guard["source_evidence"]
    )
    assert "Is the worst case bad enough?" in str(tail_guard["source_evidence"])


def test_pr91_v53_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v53", "model_affordances_v53")

    for path in LIVE_RUNTIME_PATHS:
        text = path.read_text(encoding="utf-8")
        assert all(fragment not in text for fragment in forbidden)


def _load_record(model_id: str) -> dict[str, object]:
    return json.loads(TARGET_RECORD_PATHS[model_id].read_text(encoding="utf-8"))


def _load_compiled(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _model_ids(compiled: dict[str, object]) -> set[str]:
    return {record["model_id"] for record in compiled["model_records"]}


def _affordance_ids(compiled: dict[str, object]) -> set[str]:
    return {
        affordance["affordance_id"]
        for record in compiled["model_records"]
        for affordance in record["affordances"]
    }


def _absence_fields(compiled: dict[str, object]) -> set[str]:
    return {
        absence["attempted_field"]
        for record in compiled["model_records"]
        for absence in record["absence_records"]
    }


def _affordance_counts_by_model(compiled: dict[str, object]) -> dict[str, int]:
    return {
        record["model_id"]: len(record["affordances"])
        for record in compiled["model_records"]
    }


def _absence_by_field(record: dict[str, object], attempted_field: str) -> dict[str, object]:
    return next(
        absence
        for absence in record["absence_records"]
        if absence["attempted_field"] == attempted_field
    )
