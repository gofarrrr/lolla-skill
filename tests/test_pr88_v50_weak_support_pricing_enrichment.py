from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V49_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v49.json"
)
AFFORDANCES_V50_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v50.json"
)

PRICE_DISCRIMINATION_RECORD = (
    MODEL_AFFORDANCE_DIR / "batch_16" / "price-discrimination.json"
)
DEVOPS_RECORD = (
    MODEL_AFFORDANCE_DIR / "batch_8" / "devops-and-continuous-integration.json"
)

NEW_AFFORDANCE_IDS = {
    "price-discrimination.justify-offer-differences-against-alternatives",
}

NEW_ABSENCE_FIELDS = {
    "price-discrimination-demand-response-from-persona-or-story",
}

UNCHANGED_NEIGHBOR_MODEL_IDS = {
    "agile-methodologies",
    "auditability-traceability",
    "debugging-strategies",
    "devops-and-continuous-integration",
    "elasticity",
    "iteration",
    "lean-startup-methodology",
    "scale-economies",
    "supply-and-demand",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr88_target_records_validate_against_schema_and_sources() -> None:
    validate_model_affordance_file(PRICE_DISCRIMINATION_RECORD, source_roots=(SOURCE_DIR,))
    validate_model_affordance_file(DEVOPS_RECORD, source_roots=(SOURCE_DIR,))


def test_pr88_compiled_v50_adds_only_bounded_weak_support_pricing_delta() -> None:
    affordances_v49 = _load_compiled(AFFORDANCES_V49_PATH)
    affordances_v50 = _load_compiled(AFFORDANCES_V50_PATH)

    assert affordances_v50["artifact"] == "model_affordances_v50"
    assert affordances_v50["status"] == "draft_review_only"
    assert _model_ids(affordances_v50) == _model_ids(affordances_v49)
    assert len(_model_ids(affordances_v50)) == 222

    assert NEW_AFFORDANCE_IDS.isdisjoint(_affordance_ids(affordances_v49))
    assert _affordance_ids(affordances_v50) - _affordance_ids(affordances_v49) == (
        NEW_AFFORDANCE_IDS
    )
    assert NEW_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v49))
    assert _absence_fields(affordances_v50) - _absence_fields(affordances_v49) == (
        NEW_ABSENCE_FIELDS
    )

    v49_metadata = affordances_v49["compile_metadata"]
    v50_metadata = affordances_v50["compile_metadata"]
    assert v50_metadata["contributing_record_count"] == 222
    assert v50_metadata["affordance_count"] == v49_metadata["affordance_count"] + 1
    assert v50_metadata["affordance_count"] == 294
    assert (
        v50_metadata["absence_record_count"]
        == v49_metadata["absence_record_count"] + 1
    )
    assert v50_metadata["absence_record_count"] == 568
    assert v50_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v50_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr88_price_discrimination_remains_weak_support_after_split() -> None:
    price_discrimination = _load_record(PRICE_DISCRIMINATION_RECORD)

    assert price_discrimination["status"] == "weak_support"
    assert len(price_discrimination["affordances"]) == 2
    assert {
        affordance["affordance_id"]
        for affordance in price_discrimination["affordances"]
    } == {
        "price-discrimination.segment-offer-by-value-evidence",
        "price-discrimination.justify-offer-differences-against-alternatives",
    }
    assert {
        affordance["status"] for affordance in price_discrimination["affordances"]
    } == {"weak_support"}
    assert {
        affordance["confidence"] for affordance in price_discrimination["affordances"]
    } == {"medium"}

    segment_card = _affordance_by_id(
        price_discrimination,
        "price-discrimination.segment-offer-by-value-evidence",
    )
    comparison_card = _affordance_by_id(
        price_discrimination,
        "price-discrimination.justify-offer-differences-against-alternatives",
    )

    assert "separate-value-segments-with-trust-check" in str(
        segment_card["treatment_requirements"]
    )
    assert "anchor-offer-differences-against-comparison-and-limits" not in str(
        segment_card["treatment_requirements"]
    )
    assert "anchor-offer-differences-against-comparison-and-limits" in str(
        comparison_card["treatment_requirements"]
    )
    assert "Compared to what?" in str(comparison_card["source_evidence"])
    assert "explicitly outline the limitations" in str(
        comparison_card["source_evidence"]
    )
    assert "formal economics, legal, or regulatory" in str(
        comparison_card["misuse_guards"]
    )


def test_pr88_new_absence_blocks_persona_story_demand_response() -> None:
    price_discrimination = _load_record(PRICE_DISCRIMINATION_RECORD)
    demand_response_guard = _absence_by_field(
        price_discrimination,
        "price-discrimination-demand-response-from-persona-or-story",
    )
    formal_doctrine_guard = _absence_by_field(
        price_discrimination,
        "formal-economics-or-legal-price-discrimination-doctrine",
    )

    assert demand_response_guard["runtime_policy"] == "do_not_promote"
    assert "customer's true willingness to pay" in str(
        demand_response_guard["source_evidence"]
    )
    assert "story-led demand assumptions replace observed response curves" in str(
        demand_response_guard["source_evidence"]
    )
    assert "slope estimation" in str(demand_response_guard["source_evidence"])

    assert "first/second/third-degree price discrimination" in str(
        formal_doctrine_guard["reason"]
    )
    assert "consumer-welfare" in str(formal_doctrine_guard["reason"])


def test_pr88_devops_and_adjacent_supported_records_remain_unchanged() -> None:
    affordances_v49 = _load_compiled(AFFORDANCES_V49_PATH)
    affordances_v50 = _load_compiled(AFFORDANCES_V50_PATH)

    v49_counts = _affordance_counts_by_model(affordances_v49)
    v50_counts = _affordance_counts_by_model(affordances_v50)
    v49_absence_counts = _absence_counts_by_model(affordances_v49)
    v50_absence_counts = _absence_counts_by_model(affordances_v50)

    for model_id in UNCHANGED_NEIGHBOR_MODEL_IDS:
        assert v50_counts[model_id] == v49_counts[model_id]
        assert v50_absence_counts[model_id] == v49_absence_counts[model_id]

    devops = _record_by_model(affordances_v50, "devops-and-continuous-integration")
    assert devops["status"] == "weak_support"
    assert len(devops["affordances"]) == 1
    assert devops["affordances"][0]["status"] == "weak_support"


def test_pr88_v50_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v50", "model_affordances_v50")

    for path in LIVE_RUNTIME_PATHS:
        text = path.read_text(encoding="utf-8")
        assert all(fragment not in text for fragment in forbidden)


def _load_record(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_compiled(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _model_ids(compiled: dict[str, object]) -> set[str]:
    return {record["model_id"] for record in compiled["model_records"]}


def _record_by_model(
    compiled: dict[str, object],
    model_id: str,
) -> dict[str, object]:
    return next(
        record
        for record in compiled["model_records"]
        if record["model_id"] == model_id
    )


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


def _absence_counts_by_model(compiled: dict[str, object]) -> dict[str, int]:
    return {
        record["model_id"]: len(record["absence_records"])
        for record in compiled["model_records"]
    }


def _affordance_by_id(
    record: dict[str, object],
    affordance_id: str,
) -> dict[str, object]:
    return next(
        affordance
        for affordance in record["affordances"]
        if affordance["affordance_id"] == affordance_id
    )


def _absence_by_field(record: dict[str, object], attempted_field: str) -> dict[str, object]:
    return next(
        absence
        for absence in record["absence_records"]
        if absence["attempted_field"] == attempted_field
    )
