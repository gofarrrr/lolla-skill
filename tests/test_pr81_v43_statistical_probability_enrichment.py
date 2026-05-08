from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
MODEL_AFFORDANCE_DIR = REPO_ROOT / "data" / "model_affordances"
AFFORDANCES_V42_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v42.json"
)
AFFORDANCES_V43_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v43.json"
)

TARGET_RECORD_PATHS = {
    "base-rates": MODEL_AFFORDANCE_DIR / "pilot" / "base-rates.json",
    "bayesian": MODEL_AFFORDANCE_DIR / "batch_13" / "bayesian.json",
    "data-science-reasoning-framework": MODEL_AFFORDANCE_DIR
    / "batch_13"
    / "data-science-reasoning-framework.json",
    "false-precision-avoidance": MODEL_AFFORDANCE_DIR
    / "batch_10"
    / "false-precision-avoidance.json",
    "law-of-large-numbers": MODEL_AFFORDANCE_DIR
    / "batch_2"
    / "law-of-large-numbers.json",
    "markov-chains": MODEL_AFFORDANCE_DIR / "batch_13" / "markov-chains.json",
    "monte-carlo-methods": MODEL_AFFORDANCE_DIR
    / "batch_13"
    / "monte-carlo-methods.json",
    "probabilistic-thinking": MODEL_AFFORDANCE_DIR
    / "batch_3a"
    / "probabilistic-thinking.json",
    "regression-to-the-mean": MODEL_AFFORDANCE_DIR
    / "batch_13"
    / "regression-to-the-mean.json",
    "risk-vs-uncertainty": MODEL_AFFORDANCE_DIR
    / "batch_9"
    / "risk-vs-uncertainty.json",
    "statistical-learning-theory": MODEL_AFFORDANCE_DIR
    / "batch_13"
    / "statistical-learning-theory.json",
    "statistics-concepts": MODEL_AFFORDANCE_DIR
    / "batch_13"
    / "statistics-concepts.json",
}

NEW_AFFORDANCE_IDS = {
    "data-science-reasoning-framework.assumption-pressure-before-analytic-output",
}

NEW_ABSENCE_FIELDS = {
    "confirmation-shaped-model-selection",
    "decorative-update-with-weak-priors",
    "emergent-social-system-as-mechanical-state-path",
    "headline-mean-as-full-distribution",
    "large-n-confidence-with-wrong-population",
    "old-frequency-after-regime-shift",
    "point-estimate-commitment-under-true-uncertainty",
    "precision-avoidance-in-exact-domain",
    "predictive-fit-as-causal-understanding",
    "proxy-metric-as-underlying-reality",
    "reversion-confidence-from-flawed-mean",
    "simulation-complexity-over-dominant-driver",
    "simulation-erases-unknown-unknowns-or-structural-breaks",
    "standalone-conjunctive-disjunctive-probability-affordance",
    "training-narrative-with-censored-failures",
    "unstable-transition-regime-as-stationary-risk",
}

LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet.py",
    REPO_ROOT / "engine" / "system_b" / "reasoning_substrate_packet_review.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_pr81_target_records_validate_against_schema_and_sources() -> None:
    for path in TARGET_RECORD_PATHS.values():
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_pr81_compiled_v43_adds_bounded_statistical_enrichment() -> None:
    affordances_v42 = _load_compiled(AFFORDANCES_V42_PATH)
    affordances_v43 = _load_compiled(AFFORDANCES_V43_PATH)

    assert affordances_v43["artifact"] == "model_affordances_v43"
    assert affordances_v43["status"] == "draft_review_only"
    assert _model_ids(affordances_v43) == _model_ids(affordances_v42)
    assert len(_model_ids(affordances_v43)) == 222

    assert NEW_AFFORDANCE_IDS.isdisjoint(_affordance_ids(affordances_v42))
    assert _affordance_ids(affordances_v43) - _affordance_ids(affordances_v42) == (
        NEW_AFFORDANCE_IDS
    )
    assert NEW_ABSENCE_FIELDS.isdisjoint(_absence_fields(affordances_v42))
    assert _absence_fields(affordances_v43) - _absence_fields(affordances_v42) == (
        NEW_ABSENCE_FIELDS
    )

    v42_metadata = affordances_v42["compile_metadata"]
    v43_metadata = affordances_v43["compile_metadata"]
    assert v43_metadata["contributing_record_count"] == 222
    assert v43_metadata["affordance_count"] == v42_metadata["affordance_count"] + 1
    assert v43_metadata["affordance_count"] == 278
    assert (
        v43_metadata["absence_record_count"]
        == v42_metadata["absence_record_count"] + 16
    )
    assert v43_metadata["absence_record_count"] == 536
    assert v43_metadata["validation"]["schema_validation_failure_count"] == 0
    assert v43_metadata["validation"]["source_quote_rejection_count"] == 0


def test_pr81_data_science_split_preserves_assumption_transaction() -> None:
    record = _load_record("data-science-reasoning-framework")
    affordance = _affordance_by_id(
        record,
        "data-science-reasoning-framework.assumption-pressure-before-analytic-output",
    )
    proxy_guard = _absence_by_field(record, "proxy-metric-as-underlying-reality")

    assert "pressure the assumptions under an analytic thesis" in str(
        affordance["review_notes"]
    )
    assert "what must be believed" in affordance["mechanism"]
    assert "surface-beliefs-and-resolution-facts" in str(
        affordance["treatment_requirements"]
    )
    assert "What facts would unambiguously resolve this issue?" in str(
        affordance["source_evidence"]
    )
    assert "Every idea (thesis) must be met with its counter-argument" in str(
        affordance["source_evidence"]
    )
    assert proxy_guard["runtime_policy"] == "do_not_promote"
    assert "convenient proxy metrics are treated as the underlying reality" in str(
        proxy_guard["source_evidence"]
    )


def test_pr81_probability_and_sample_guards_block_false_statistical_authority() -> None:
    base_rates = _load_record("base-rates")
    bayesian = _load_record("bayesian")
    lln = _load_record("law-of-large-numbers")
    probability = _load_record("probabilistic-thinking")
    regression = _load_record("regression-to-the-mean")
    risk = _load_record("risk-vs-uncertainty")

    assert "regime shift or causal break" in str(
        _absence_by_field(base_rates, "old-frequency-after-regime-shift")
    )
    assert "false precision, weak priors, or low-quality evidence" in str(
        _absence_by_field(bayesian, "decorative-update-with-weak-priors")
    )
    assert "biased, non-comparable, or structurally mismatched" in str(
        _absence_by_field(lln, "large-n-confidence-with-wrong-population")
    )
    assert "conjunctive events" in str(
        _absence_by_field(
            probability,
            "standalone-conjunctive-disjunctive-probability-affordance",
        )
    )
    assert "flawed, biased, or too small" in str(
        _absence_by_field(regression, "reversion-confidence-from-flawed-mean")
    )
    assert "precise-looking forecast" in str(
        _absence_by_field(
            risk,
            "point-estimate-commitment-under-true-uncertainty",
        )
    )


def test_pr81_model_simulation_and_precision_guards_prevent_bloat_theater() -> None:
    false_precision = _load_record("false-precision-avoidance")
    markov = _load_record("markov-chains")
    monte_carlo = _load_record("monte-carlo-methods")
    slt = _load_record("statistical-learning-theory")
    statistics = _load_record("statistics-concepts")

    assert "precision and accuracy are absolute requirements" in str(
        _absence_by_field(false_precision, "precision-avoidance-in-exact-domain")
    )
    assert "unstable transition regimes are treated as stationary risk" in str(
        _absence_by_field(markov, "unstable-transition-regime-as-stationary-risk")
    )
    assert "Implementation is often **emergent**" in str(
        _absence_by_field(markov, "emergent-social-system-as-mechanical-state-path")
    )
    assert "model can only sample from what it was told to imagine" in str(
        _absence_by_field(
            monte_carlo,
            "simulation-erases-unknown-unknowns-or-structural-breaks",
        )
    )
    assert "dominant variables a simpler closed-form analysis would reveal" in str(
        _absence_by_field(monte_carlo, "simulation-complexity-over-dominant-driver")
    )
    assert "causal understanding matters more than prediction" in str(
        _absence_by_field(slt, "predictive-fit-as-causal-understanding")
    )
    assert "out-of-sample generalization performance" in str(
        _absence_by_field(slt, "confirmation-shaped-model-selection")
    )
    assert "training narratives ignore censored failures" in str(
        _absence_by_field(slt, "training-narrative-with-censored-failures")
    )
    assert "headline numbers discards variance" in str(
        _absence_by_field(statistics, "headline-mean-as-full-distribution")
    )


def test_pr81_v43_is_not_imported_by_live_runtime_paths() -> None:
    forbidden = ("affordances_v43", "model_affordances_v43")

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


def _affordance_by_id(
    record: dict[str, object],
    affordance_id: str,
) -> dict[str, object]:
    return next(
        affordance
        for affordance in record["affordances"]
        if affordance["affordance_id"] == affordance_id
    )


def _absence_by_field(
    record: dict[str, object],
    attempted_field: str,
) -> dict[str, object]:
    return next(
        absence
        for absence in record["absence_records"]
        if absence["attempted_field"] == attempted_field
    )
