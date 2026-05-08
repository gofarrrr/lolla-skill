from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V31_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v31.json"
)
AFFORDANCES_V32_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v32.json"
)

TARGET_RECORD_PATHS = {
    "adverse-selection": MODEL_AFFORDANCE_DIR / "batch_2" / "adverse-selection.json",
    "batna": MODEL_AFFORDANCE_DIR / "batch_5" / "batna.json",
    "markov-chains": MODEL_AFFORDANCE_DIR / "batch_13" / "markov-chains.json",
    "principal-agent-problem": MODEL_AFFORDANCE_DIR
    / "batch_3a"
    / "principal-agent-problem.json",
    "six-thinking-hats": MODEL_AFFORDANCE_DIR
    / "batch_2"
    / "six-thinking-hats.json",
}

TARGET_ABSENCE_FIELDS = {
    "base-case-fallback-as-batna",
    "branching-novelty-as-markov-state-path",
    "formal-markov-math-or-transition-matrix-affordance",
    "formal-six-hats-taxonomy-or-color-sequence",
    "hat-rotation-before-problem-definition",
    "naive-rule-screening-as-adverse-selection-fix",
    "post-commitment-incentive-drift-as-adverse-selection",
    "reciprocal-competitive-choice-modeling-as-batna",
    "single-principal-agent-frame-for-wicked-multi-owner-conflict",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr70_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr70_compiled_v32_is_v31_plus_nine_absence_records() -> None:
    affordances_v31 = _load_compiled(AFFORDANCES_V31_PATH)
    affordances_v32 = _load_compiled(AFFORDANCES_V32_PATH)

    assert affordances_v32["artifact"] == "model_affordances_v32"
    assert affordances_v32["status"] == "draft_review_only"
    assert _model_ids(affordances_v32) == _model_ids(affordances_v31)
    assert len(_model_ids(affordances_v32)) == 222
    assert _affordance_ids(affordances_v32) == _affordance_ids(affordances_v31)
    assert TARGET_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v31))
    assert TARGET_ABSENCE_FIELDS.issubset(_absence_fields(affordances_v32))
    assert _absence_fields(affordances_v32) - _absence_fields(affordances_v31) == (
        TARGET_ABSENCE_FIELDS
    )

    v31_metadata = affordances_v31["compile_metadata"]
    v32_metadata = affordances_v32["compile_metadata"]
    assert v32_metadata["contributing_record_count"] == 222
    assert v32_metadata["affordance_count"] == v31_metadata["affordance_count"]
    assert v32_metadata["affordance_count"] == 268
    assert v32_metadata["absence_record_count"] == v31_metadata["absence_record_count"] + 9
    assert v32_metadata["absence_record_count"] == 486
    assert v32_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v32_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr70_medium_supported_absences_block_wrong_routing() -> None:
    adverse_selection = _load_record("adverse-selection")
    naive_screen_guard = _absence_by_field(
        adverse_selection,
        "naive-rule-screening-as-adverse-selection-fix",
    )
    assert naive_screen_guard["runtime_policy"] == "do_not_promote"
    assert "rule-based screening" in str(naive_screen_guard["reason"])
    assert "shift risk upstream or downstream" in str(
        naive_screen_guard["source_evidence"]
    )
    post_commitment_guard = _absence_by_field(
        adverse_selection,
        "post-commitment-incentive-drift-as-adverse-selection",
    )
    assert post_commitment_guard["runtime_policy"] == "do_not_promote"
    assert "before commitment" in str(post_commitment_guard["reason"])

    batna = _load_record("batna")
    base_case_guard = _absence_by_field(batna, "base-case-fallback-as-batna")
    assert base_case_guard["runtime_policy"] == "do_not_promote"
    assert "worst case" in str(base_case_guard["reason"])
    game_theory_guard = _absence_by_field(
        batna,
        "reciprocal-competitive-choice-modeling-as-batna",
    )
    assert game_theory_guard["runtime_policy"] == "do_not_promote"
    assert game_theory_guard["status"] == "duplicate_of_existing_field"
    assert "game theory" in str(game_theory_guard["reason"])

    markov = _load_record("markov-chains")
    formal_math_guard = _absence_by_field(
        markov,
        "formal-markov-math-or-transition-matrix-affordance",
    )
    assert formal_math_guard["runtime_policy"] == "do_not_promote"
    assert "formal Markov mathematics" in str(formal_math_guard["reason"])
    branching_guard = _absence_by_field(
        markov,
        "branching-novelty-as-markov-state-path",
    )
    assert branching_guard["runtime_policy"] == "do_not_promote"
    assert "state-space branching exceeds transition evidence quality" in str(
        branching_guard["source_evidence"]
    )

    principal_agent = _load_record("principal-agent-problem")
    wicked_guard = _absence_by_field(
        principal_agent,
        "single-principal-agent-frame-for-wicked-multi-owner-conflict",
    )
    assert wicked_guard["runtime_policy"] == "do_not_promote"
    assert "clear owner" in str(wicked_guard["reason"])

    six_hats = _load_record("six-thinking-hats")
    formal_hats_guard = _absence_by_field(
        six_hats,
        "formal-six-hats-taxonomy-or-color-sequence",
    )
    assert formal_hats_guard["runtime_policy"] == "do_not_promote"
    assert "formal color taxonomy" in str(formal_hats_guard["reason"])
    early_rotation_guard = _absence_by_field(
        six_hats,
        "hat-rotation-before-problem-definition",
    )
    assert early_rotation_guard["runtime_policy"] == "do_not_promote"
    assert "defining the problem" in str(early_rotation_guard["reason"])


def test_pr70_treatments_harden_existing_medium_affordances() -> None:
    adverse_selection = _load_record("adverse-selection")
    adverse_affordance = _affordance_by_id(
        adverse_selection,
        "adverse-selection.verify-hidden-type-selection",
    )
    filter_requirement = _requirement_by_id(
        adverse_affordance,
        "specify-filter-before-commitment",
    )
    assert "strategically shaped" in str(filter_requirement["evidence_required"])
    assert "amplifies hidden-information asymmetry" in str(
        filter_requirement["good_output_shape"]
    )

    batna = _load_record("batna")
    batna_affordance = _affordance_by_id(
        batna,
        "batna.credible-walk-away-alternative-test",
    )
    assert _requirement_by_id(
        batna_affordance,
        "stress-test-fallback-downside-before-leverage",
    )
    assert _requirement_by_id(
        batna_affordance,
        "separate-fallback-set-before-naming-best-alternative",
    )

    markov = _load_record("markov-chains")
    markov_affordance = _affordance_by_id(
        markov,
        "markov-chains.state-transition-boundary-check",
    )
    assert _requirement_by_id(
        markov_affordance,
        "stress-transition-chain-against-conjunctive-and-tail-risk",
    )

    principal_agent = _load_record("principal-agent-problem")
    principal_affordance = _affordance_by_id(
        principal_agent,
        "principal-agent-problem.delegated-alignment-drift-audit",
    )
    assert _requirement_by_id(
        principal_affordance,
        "verify-owner-success-criteria-and-delegation-structure",
    )

    six_hats = _load_record("six-thinking-hats")
    hats_affordance = _affordance_by_id(
        six_hats,
        "six-thinking-hats.separate-modes-before-synthesis",
    )
    assert _requirement_by_id(
        hats_affordance,
        "define-shared-output-before-mode-rotation",
    )


def test_pr70_v32_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v32", "model_affordances_v32")

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


def _requirement_by_id(
    affordance: dict[str, object],
    requirement_id: str,
) -> dict[str, object]:
    for requirement in affordance.get("treatment_requirements", []):
        if isinstance(requirement, dict) and requirement.get("requirement_id") == requirement_id:
            return requirement
    raise AssertionError(f"missing requirement: {requirement_id}")
