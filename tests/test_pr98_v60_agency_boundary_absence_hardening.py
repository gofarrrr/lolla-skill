from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V59_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v59.json"
)
AFFORDANCES_V60_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v60.json"
)

TARGET_RECORD_PATHS = {
    "authenticity": MODEL_AFFORDANCE_DIR / "batch_7" / "authenticity.json",
    "boundaries": MODEL_AFFORDANCE_DIR / "batch_7" / "boundaries.json",
    "circle-of-competence": MODEL_AFFORDANCE_DIR
    / "batch_17"
    / "circle-of-competence.json",
    "circle-of-control": MODEL_AFFORDANCE_DIR / "batch_1" / "circle-of-control.json",
    "internal-locus-of-control": MODEL_AFFORDANCE_DIR
    / "batch_14"
    / "internal-locus-of-control.json",
    "johari-window": MODEL_AFFORDANCE_DIR / "batch_1" / "johari-window.json",
}

NEW_ABSENCE_FIELDS = {
    "authentic-conviction-as-evidence",
    "clean-boundary-hiding-cross-boundary-dependencies",
    "curated-disclosure-as-openness",
    "deliberate-then-act-as-internal-locus-split",
    "dont-boil-ocean-as-boundaries-split",
    "emotional-overdrive-as-authentic-candor",
    "evidence-free-control-bucket-map",
    "expert-status-as-competence-evidence",
    "feedback-filtered-to-protect-self-image",
    "felt-control-as-causality",
    "feynman-or-analogy-as-competence-split",
    "five-step-process-as-internal-locus-split",
    "generic-socially-acceptable-feedback-as-blind-spot-reduction",
    "local-control-myopia-as-control-affordance",
    "no-control-label-before-indirect-influence-test",
    "overbroad-system-boundary-as-completeness",
    "self-script-inner-dialogue-as-internal-locus-split",
    "transparency-without-correction-or-accountability",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr98_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr98_compiled_v60_preserves_coverage_with_absence_only_delta() -> None:
    affordances_v59 = _load_compiled(AFFORDANCES_V59_PATH)
    affordances_v60 = _load_compiled(AFFORDANCES_V60_PATH)

    assert affordances_v60["artifact"] == "model_affordances_v60"
    assert affordances_v60["status"] == "draft_review_only"
    assert _model_ids(affordances_v60) == _model_ids(affordances_v59)
    assert len(_model_ids(affordances_v60)) == 222

    assert _affordance_ids(affordances_v60) == _affordance_ids(affordances_v59)
    assert NEW_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v59))
    assert _absence_fields(affordances_v60) - _absence_fields(affordances_v59) == (
        NEW_ABSENCE_FIELDS
    )

    v59_metadata = affordances_v59["compile_metadata"]
    v60_metadata = affordances_v60["compile_metadata"]
    assert v60_metadata["contributing_record_count"] == 222
    assert v60_metadata["affordance_count"] == v59_metadata["affordance_count"]
    assert v60_metadata["affordance_count"] == 306
    assert (
        v60_metadata["absence_record_count"]
        == v59_metadata["absence_record_count"] + len(NEW_ABSENCE_FIELDS)
    )
    assert v60_metadata["absence_record_count"] == 697
    assert v60_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v60_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr98_scope_and_authenticity_richness_stays_as_absence_rails() -> None:
    boundaries = _load_record("boundaries")
    assert len(boundaries["affordances"]) == 1
    assert "artificially narrow system boundaries hide feedback loops" in str(
        _absence_by_field(
            boundaries,
            "clean-boundary-hiding-cross-boundary-dependencies",
        )["source_evidence"]
    )
    assert _absence_by_field(
        boundaries,
        "dont-boil-ocean-as-boundaries-split",
    )["status"] == "duplicate_of_existing_field"
    assert "only serve to obscure the answers" in str(
        _absence_by_field(boundaries, "overbroad-system-boundary-as-completeness")[
            "source_evidence"
        ]
    )

    authenticity = _load_record("authenticity")
    assert len(authenticity["affordances"]) == 1
    assert "perceived as genuine" in str(
        _absence_by_field(authenticity, "authentic-conviction-as-evidence")[
            "source_evidence"
        ]
    )
    assert "strong emotions... driving your thinking process" in str(
        _absence_by_field(authenticity, "emotional-overdrive-as-authentic-candor")[
            "source_evidence"
        ]
    )
    assert "avoid evidence, preparation, or accountability" in str(
        _absence_by_field(
            authenticity,
            "transparency-without-correction-or-accountability",
        )["source_evidence"]
    )


def test_pr98_johari_and_control_maps_reject_performative_or_unsupported_use() -> None:
    johari = _load_record("johari-window")
    assert len(johari["affordances"]) == 1
    assert "generic or \"socially acceptable\" feedback" in str(
        _absence_by_field(
            johari,
            "generic-socially-acceptable-feedback-as-blind-spot-reduction",
        )["source_evidence"]
    )
    assert "curated, socially safe observations" in str(
        _absence_by_field(johari, "curated-disclosure-as-openness")[
            "source_evidence"
        ]
    )
    assert "feedback intake is filtered to protect existing self-image" in str(
        _absence_by_field(johari, "feedback-filtered-to-protect-self-image")[
            "source_evidence"
        ]
    )

    control = _load_record("circle-of-control")
    assert len(control["affordances"]) == 1
    assert "outside control" in str(
        _absence_by_field(control, "no-control-label-before-indirect-influence-test")[
            "source_evidence"
        ]
    )
    assert "explicit evidence for each classification decision" in str(
        _absence_by_field(control, "evidence-free-control-bucket-map")[
            "source_evidence"
        ]
    )
    assert "Local control myopia" in str(
        _absence_by_field(control, "local-control-myopia-as-control-affordance")[
            "source_evidence"
        ]
    )


def test_pr98_competence_and_internal_locus_owner_boundaries_prevent_bloat() -> None:
    competence = _load_record("circle-of-competence")
    assert len(competence["affordances"]) == 1
    assert _absence_by_field(
        competence,
        "expert-status-as-competence-evidence",
    )["status"] == "duplicate_of_existing_field"
    assert "What variables matter in this situation and why?" in str(
        _absence_by_field(competence, "expert-status-as-competence-evidence")[
            "source_evidence"
        ]
    )
    assert _absence_by_field(
        competence,
        "feynman-or-analogy-as-competence-split",
    )["status"] == "duplicate_of_existing_field"

    agency = _load_record("internal-locus-of-control")
    assert len(agency["affordances"]) == 1
    assert "retrospectively creates a narrative of control and causality" in str(
        _absence_by_field(agency, "felt-control-as-causality")["source_evidence"]
    )
    assert _absence_by_field(
        agency,
        "deliberate-then-act-as-internal-locus-split",
    )["status"] == "duplicate_of_existing_field"
    assert _absence_by_field(
        agency,
        "five-step-process-as-internal-locus-split",
    )["status"] == "duplicate_of_existing_field"
    assert _absence_by_field(
        agency,
        "self-script-inner-dialogue-as-internal-locus-split",
    )["status"] == "source_too_thin"


def test_pr98_v60_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v60", "model_affordances_v60")

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


def _absence_by_field(
    record: dict[str, object],
    attempted_field: str,
) -> dict[str, object]:
    return next(
        absence
        for absence in record["absence_records"]
        if absence["attempted_field"] == attempted_field
    )
