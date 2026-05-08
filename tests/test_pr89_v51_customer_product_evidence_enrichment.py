from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V50_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v50.json"
)
AFFORDANCES_V51_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v51.json"
)

TARGET_RECORD_PATHS = {
    "jobs-to-be-done": MODEL_AFFORDANCE_DIR / "batch_5" / "jobs-to-be-done.json",
    "user-centered-design": MODEL_AFFORDANCE_DIR
    / "batch_5"
    / "user-centered-design.json",
    "user-experience-research-methods": MODEL_AFFORDANCE_DIR
    / "batch_15"
    / "user-experience-research-methods.json",
    "usability-heuristics": MODEL_AFFORDANCE_DIR
    / "batch_15"
    / "usability-heuristics.json",
}

NEW_AFFORDANCE_IDS = {
    "user-centered-design.reframe-flawed-brief-from-user-observation",
    "user-experience-research-methods.digital-twin-screening-before-live-commitment",
}

NEW_ABSENCE_FIELDS = {
    "average-user-confirmation-as-sufficient-discovery",
    "nielsen-checklist-as-source-supported-ui-audit",
    "research-volume-as-rigor-affordance",
    "synthetic-persona-as-user-evidence-replacement",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr89_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr89_compiled_v51_adds_bounded_customer_product_delta() -> None:
    affordances_v50 = _load_compiled(AFFORDANCES_V50_PATH)
    affordances_v51 = _load_compiled(AFFORDANCES_V51_PATH)

    assert affordances_v51["artifact"] == "model_affordances_v51"
    assert affordances_v51["status"] == "draft_review_only"
    assert _model_ids(affordances_v51) == _model_ids(affordances_v50)
    assert len(_model_ids(affordances_v51)) == 222

    assert NEW_AFFORDANCE_IDS.isdisjoint(_affordance_ids(affordances_v50))
    assert _affordance_ids(affordances_v51) - _affordance_ids(affordances_v50) == (
        NEW_AFFORDANCE_IDS
    )
    assert NEW_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v50))
    assert _absence_fields(affordances_v51) - _absence_fields(affordances_v50) == (
        NEW_ABSENCE_FIELDS
    )

    v50_metadata = affordances_v50["compile_metadata"]
    v51_metadata = affordances_v51["compile_metadata"]
    assert v51_metadata["contributing_record_count"] == 222
    assert v51_metadata["affordance_count"] == v50_metadata["affordance_count"] + 2
    assert v51_metadata["affordance_count"] == 296
    assert (
        v51_metadata["absence_record_count"]
        == v50_metadata["absence_record_count"] + 4
    )
    assert v51_metadata["absence_record_count"] == 572
    assert v51_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v51_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr89_user_centered_design_split_preserves_transaction_identity() -> None:
    user_centered_design = _load_record("user-centered-design")
    reframe_card = _affordance_by_id(
        user_centered_design,
        "user-centered-design.reframe-flawed-brief-from-user-observation",
    )
    prototype_card = _affordance_by_id(
        user_centered_design,
        "user-centered-design.prototype-user-evidence-loop",
    )

    assert len(user_centered_design["affordances"]) == 2
    assert "convert-observation-into-user-point-of-view" in str(
        reframe_card["treatment_requirements"]
    )
    assert "**reframe it** through a Point of View" in str(
        reframe_card["source_evidence"]
    )
    assert "test-solution-assumptions-with-users" in str(
        prototype_card["treatment_requirements"]
    )
    assert "**Build and Test** iteratively with real people" in str(
        prototype_card["source_evidence"]
    )
    assert "reframe it" not in str(prototype_card["source_evidence"])
    assert "convert-observation-into-user-point-of-view" not in str(
        prototype_card["treatment_requirements"]
    )


def test_pr89_user_centered_design_new_absence_rails_are_visible() -> None:
    user_centered_design = _load_record("user-centered-design")
    average_user_guard = _absence_by_field(
        user_centered_design,
        "average-user-confirmation-as-sufficient-discovery",
    )
    synthetic_persona_guard = _absence_by_field(
        user_centered_design,
        "synthetic-persona-as-user-evidence-replacement",
    )

    assert average_user_guard["runtime_policy"] == "do_not_promote"
    assert "confirm what we already know" in str(average_user_guard["source_evidence"])
    assert "Focus on **extreme users**" in str(average_user_guard["source_evidence"])

    assert synthetic_persona_guard["status"] == "not_supported_by_source"
    assert "digital twin personas" in str(synthetic_persona_guard["source_evidence"])
    assert "evidence from users" in str(synthetic_persona_guard["source_evidence"])
    assert "**Build and Test** iteratively with real people" in str(
        synthetic_persona_guard["source_evidence"]
    )


def test_pr89_uxrm_digital_twin_split_is_guarded_not_runtime_permission() -> None:
    uxrm = _load_record("user-experience-research-methods")
    research_card = _affordance_by_id(
        uxrm,
        "user-experience-research-methods.test-user-assumptions-before-commitment",
    )
    digital_twin_card = _affordance_by_id(
        uxrm,
        "user-experience-research-methods.digital-twin-screening-before-live-commitment",
    )
    research_volume_guard = _absence_by_field(
        uxrm,
        "research-volume-as-rigor-affordance",
    )

    assert len(uxrm["affordances"]) == 2
    assert "validate-twin-before-screening-commitment" in str(
        digital_twin_card["treatment_requirements"]
    )
    assert "AI Agents as Digital Twins" in str(digital_twin_card["source_evidence"])
    assert "validating twins for accuracy" in str(
        digital_twin_card["source_evidence"]
    )
    assert "pre-validate decisions in silico" in str(
        digital_twin_card["source_evidence"]
    )
    assert "transparency, privacy, and avoiding manipulation or bias" in str(
        digital_twin_card["source_evidence"]
    )
    assert "Do not treat simulated persona output as direct market proof." in str(
        digital_twin_card["misuse_guards"]
    )
    assert "Did not interpret digital twins as runtime permission for LLM model calls." in str(
        digital_twin_card["review_notes"]
    )
    assert "validate-twin-before-screening-commitment" not in str(
        research_card["treatment_requirements"]
    )

    assert research_volume_guard["runtime_policy"] == "do_not_promote"
    assert "Gathering data for research's sake" in str(
        research_volume_guard["source_evidence"]
    )


def test_pr89_usability_heuristics_remains_compressed_with_nielsen_guard() -> None:
    usability_heuristics = _load_record("usability-heuristics")
    nielsen_guard = _absence_by_field(
        usability_heuristics,
        "nielsen-checklist-as-source-supported-ui-audit",
    )

    assert len(usability_heuristics["affordances"]) == 1
    assert nielsen_guard["runtime_policy"] == "do_not_promote"
    assert "mental shortcuts, rules of thumb" in str(nielsen_guard["source_evidence"])
    assert "Occam's Razor" in str(nielsen_guard["source_evidence"])
    assert "The Rule of Three" in str(nielsen_guard["source_evidence"])
    assert "decision aids, interface conventions, or triage rules" in str(
        nielsen_guard["source_evidence"]
    )


def test_pr89_jobs_to_be_done_remains_compressed_after_full_reread() -> None:
    affordances_v50 = _load_compiled(AFFORDANCES_V50_PATH)
    affordances_v51 = _load_compiled(AFFORDANCES_V51_PATH)

    v50_jtbd = _record_by_model(affordances_v50, "jobs-to-be-done")
    v51_jtbd = _record_by_model(affordances_v51, "jobs-to-be-done")

    assert len(v51_jtbd["affordances"]) == len(v50_jtbd["affordances"]) == 1
    assert len(v51_jtbd["absence_records"]) == len(v50_jtbd["absence_records"]) == 2
    assert v51_jtbd["affordances"][0]["affordance_id"] == (
        "jobs-to-be-done.real-progress-job-discovery"
    )


def test_pr89_v51_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v51", "model_affordances_v51")

    for path in LIVE_RUNTIME_PATHS:
        text = path.read_text(encoding="utf-8")
        assert all(fragment not in text for fragment in forbidden)


def _load_record(model_id: str) -> dict[str, object]:
    return json.loads(TARGET_RECORD_PATHS[model_id].read_text(encoding="utf-8"))


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
