from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V30_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v30.json"
)
AFFORDANCES_V31_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v31.json"
)

TARGET_RECORD_PATHS = {
    "devops-and-continuous-integration": MODEL_AFFORDANCE_DIR
    / "batch_8"
    / "devops-and-continuous-integration.json",
    "price-discrimination": MODEL_AFFORDANCE_DIR
    / "batch_16"
    / "price-discrimination.json",
}

TARGET_ABSENCE_FIELDS = {
    "abstract-continuous-improvement-as-devops-ci",
    "formal-economics-or-legal-price-discrimination-doctrine",
    "persona-or-archetype-as-willingness-to-pay-proof",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr69_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr69_compiled_v31_is_v30_plus_three_absence_records() -> None:
    affordances_v30 = _load_compiled(AFFORDANCES_V30_PATH)
    affordances_v31 = _load_compiled(AFFORDANCES_V31_PATH)

    assert affordances_v31["artifact"] == "model_affordances_v31"
    assert affordances_v31["status"] == "draft_review_only"
    assert _model_ids(affordances_v31) == _model_ids(affordances_v30)
    assert len(_model_ids(affordances_v31)) == 222
    assert _affordance_ids(affordances_v31) == _affordance_ids(affordances_v30)
    assert TARGET_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v30))
    assert TARGET_ABSENCE_FIELDS.issubset(_absence_fields(affordances_v31))
    assert _absence_fields(affordances_v31) - _absence_fields(affordances_v30) == (
        TARGET_ABSENCE_FIELDS
    )

    v30_metadata = affordances_v30["compile_metadata"]
    v31_metadata = affordances_v31["compile_metadata"]
    assert v31_metadata["contributing_record_count"] == 222
    assert v31_metadata["affordance_count"] == v30_metadata["affordance_count"]
    assert v31_metadata["affordance_count"] == 268
    assert v31_metadata["absence_record_count"] == v30_metadata["absence_record_count"] + 3
    assert v31_metadata["absence_record_count"] == 477
    assert v31_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v31_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr69_weak_support_absences_block_overpromotion() -> None:
    devops = _load_record("devops-and-continuous-integration")
    abstract_devops_guard = _absence_by_field(
        devops,
        "abstract-continuous-improvement-as-devops-ci",
    )
    assert abstract_devops_guard["status"] == "not_supported_by_source"
    assert abstract_devops_guard["runtime_policy"] == "do_not_promote"
    assert "concrete delivery system" in str(abstract_devops_guard["reason"])
    assert "cannot be done in the abstract" in str(abstract_devops_guard["source_evidence"])

    price_discrimination = _load_record("price-discrimination")
    persona_guard = _absence_by_field(
        price_discrimination,
        "persona-or-archetype-as-willingness-to-pay-proof",
    )
    assert persona_guard["status"] == "not_supported_by_source"
    assert persona_guard["runtime_policy"] == "do_not_promote"
    assert "persona language" in str(persona_guard["reason"])
    assert "willingness to pay" in str(persona_guard["source_evidence"])

    formal_doctrine_guard = _absence_by_field(
        price_discrimination,
        "formal-economics-or-legal-price-discrimination-doctrine",
    )
    assert formal_doctrine_guard["status"] == "not_supported_by_source"
    assert formal_doctrine_guard["runtime_policy"] == "do_not_promote"
    assert "formal economics" in str(formal_doctrine_guard["reason"])
    assert "term \"Price Discrimination\" is not found" in str(
        formal_doctrine_guard["source_evidence"]
    )


def test_pr69_weak_support_treatments_surface_use_conditions() -> None:
    devops = _load_record("devops-and-continuous-integration")
    devops_affordance = _affordance_by_id(
        devops,
        "devops-and-continuous-integration.build-observe-adjust-loop",
    )
    assert any(
        isinstance(requirement, dict)
        and requirement.get("requirement_id") == "verify-concrete-delivery-system-before-use"
        for requirement in devops_affordance["treatment_requirements"]
    )
    assert any(
        "generic systems thinking" in str(guard)
        for guard in devops_affordance["misuse_guards"]
    )

    price_discrimination = _load_record("price-discrimination")
    price_affordance = _affordance_by_id(
        price_discrimination,
        "price-discrimination.segment-offer-by-value-evidence",
    )
    assert any(
        isinstance(requirement, dict)
        and requirement.get("requirement_id")
        == "anchor-offer-differences-against-comparison-and-limits"
        for requirement in price_affordance["treatment_requirements"]
    )
    assert any(
        "Compared to what alternative" in str(question)
        for question in price_affordance["diagnostic_questions"]
    )
    assert any(
        "persona, archetype, or buyer-psychology" in str(guard)
        for guard in price_affordance["misuse_guards"]
    )


def test_pr69_v31_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v31", "model_affordances_v31")

    for path in LIVE_RUNTIME_PATHS:
        text = path.read_text(encoding="utf-8")
        assert all(fragment not in text for fragment in forbidden)


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


def _absence_fields(compiled: dict[str, object]) -> set[str]:
    return {
        str(absence["attempted_field"])
        for record in compiled.get("model_records", [])
        if isinstance(record, dict)
        for absence in record.get("absence_records", [])
        if isinstance(absence, dict)
    }


def _absence_by_field(
    record: dict[str, object],
    attempted_field: str,
) -> dict[str, object]:
    for absence in record.get("absence_records", []):
        if isinstance(absence, dict) and absence.get("attempted_field") == attempted_field:
            return absence
    raise AssertionError(f"missing absence record: {attempted_field}")


def _affordance_by_id(
    record: dict[str, object],
    affordance_id: str,
) -> dict[str, object]:
    for affordance in record.get("affordances", []):
        if isinstance(affordance, dict) and affordance.get("affordance_id") == affordance_id:
            return affordance
    raise AssertionError(f"missing affordance: {affordance_id}")
